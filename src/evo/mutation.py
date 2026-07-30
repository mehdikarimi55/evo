"""Validation and application of structured candidate patches."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from subprocess import CompletedProcess, TimeoutExpired, run
from typing import Sequence
import hashlib
import os

from evo.kernel.audit import AuditLog
from evo.kernel.policy import KernelPolicy
from evo.worktree import CandidateWorktree


class PatchError(RuntimeError):
    """A sanitized patch rejection safe to expose at host boundaries."""


@dataclass(frozen=True, slots=True)
class PatchLimits:
    max_bytes: int = 65_536
    max_files: int = 8
    max_changed_lines: int = 500

    def __post_init__(self) -> None:
        if self.max_bytes <= 0:
            raise ValueError("Patch byte limit must be positive")
        if self.max_files <= 0:
            raise ValueError("Patch file limit must be positive")
        if self.max_changed_lines <= 0:
            raise ValueError("Patch line limit must be positive")


@dataclass(frozen=True, slots=True)
class PatchApplication:
    patch_sha256: str
    changed_paths: tuple[str, ...]
    patch_bytes: int
    changed_lines: int


@dataclass(frozen=True, slots=True)
class _PatchAnalysis:
    paths: tuple[str, ...]
    patch_bytes: int
    changed_lines: int


class MutationApplicator:
    """Apply a bounded text patch only inside a clean candidate worktree."""

    def __init__(
        self,
        *,
        limits: PatchLimits | None = None,
        policy: KernelPolicy | None = None,
        audit: AuditLog | None = None,
    ) -> None:
        self.limits = limits or PatchLimits()
        self.policy = policy or KernelPolicy()
        self.audit = audit

    def apply(
        self,
        *,
        candidate: CandidateWorktree,
        patch: str,
        mutable_paths: Sequence[str],
        candidate_id: str,
    ) -> PatchApplication:
        patch_bytes = patch.encode("utf-8")
        patch_sha256 = hashlib.sha256(patch_bytes).hexdigest()
        try:
            result = self._apply(
                candidate=candidate,
                patch=patch,
                patch_bytes=patch_bytes,
                patch_sha256=patch_sha256,
                mutable_paths=mutable_paths,
            )
        except PatchError as exc:
            self._audit(
                "mutation.rejected",
                {
                    "candidate_id": candidate_id,
                    "patch_sha256": patch_sha256,
                    "reason": str(exc),
                },
            )
            raise

        self._audit(
            "mutation.applied",
            {
                "candidate_id": candidate_id,
                "patch_sha256": result.patch_sha256,
                "patch_bytes": result.patch_bytes,
                "changed_lines": result.changed_lines,
                "changed_paths": result.changed_paths,
            },
        )
        return result

    def _apply(
        self,
        *,
        candidate: CandidateWorktree,
        patch: str,
        patch_bytes: bytes,
        patch_sha256: str,
        mutable_paths: Sequence[str],
    ) -> PatchApplication:
        if candidate._cleaned or not candidate.path.is_dir():
            raise PatchError("Candidate worktree is unavailable")
        if candidate.changed_paths():
            raise PatchError("Candidate worktree must be clean before applying a patch")

        analysis = _analyze_patch(patch, patch_bytes, self.limits)
        prefixes = tuple(path for path in mutable_paths if path)
        if not prefixes:
            raise PatchError("At least one mutable path is required")
        for relative in analysis.paths:
            decision = self.policy.authorize_mutation(relative, prefixes)
            if not decision.allowed:
                raise PatchError("Patch targets a path outside the allowed mutation scope")
            target = candidate.path / relative
            if target.is_symlink():
                raise PatchError("Patches may not modify symbolic links")
            if target.is_file() and target.stat().st_mode & 0o111:
                raise PatchError("Patches may not modify executable files")

        checked = _git_apply(candidate.path, patch, check=True)
        if checked.returncode != 0:
            raise PatchError("Patch does not apply cleanly")

        applied = _git_apply(candidate.path, patch, check=False)
        if applied.returncode != 0:
            _restore(candidate)
            raise PatchError("Patch application failed")

        validation = candidate.validate_changes(prefixes, policy=self.policy)
        expected = tuple(sorted(analysis.paths))
        if not validation.allowed or validation.changed_paths != expected:
            _restore(candidate)
            raise PatchError("Applied patch failed post-application validation")

        return PatchApplication(
            patch_sha256=patch_sha256,
            changed_paths=validation.changed_paths,
            patch_bytes=len(patch_bytes),
            changed_lines=analysis.changed_lines,
        )

    def _audit(self, event_type: str, payload: dict[str, object]) -> None:
        if self.audit is not None:
            self.audit.append(event_type, payload)


def _analyze_patch(
    patch: str,
    patch_bytes: bytes,
    limits: PatchLimits,
) -> _PatchAnalysis:
    if not patch or not patch.endswith("\n"):
        raise PatchError("Patch must be non-empty and end with a newline")
    if len(patch_bytes) > limits.max_bytes:
        raise PatchError("Patch exceeds the configured byte limit")
    if b"\0" in patch_bytes:
        raise PatchError("Binary patch content is not allowed")

    lines = patch.splitlines()
    if not lines or not lines[0].startswith("diff --git "):
        raise PatchError("Patch must be a raw Git unified diff")

    prohibited_prefixes = (
        "GIT binary patch",
        "Binary files ",
        "rename from ",
        "rename to ",
        "copy from ",
        "copy to ",
        "similarity index ",
        "dissimilarity index ",
        "old mode ",
        "new mode ",
    )
    paths: list[str] = []
    section: list[str] = []
    changed_lines = 0
    in_hunk = False

    def finish_section() -> None:
        if not section:
            return
        path = _validate_section(section)
        if path in paths:
            raise PatchError("Patch contains duplicate file sections")
        paths.append(path)

    for line in lines:
        if line.startswith("diff --git "):
            finish_section()
            section = [line]
            in_hunk = False
            continue
        if not section:
            raise PatchError("Patch contains content outside a file section")
        if line.startswith(prohibited_prefixes):
            raise PatchError("Patch contains a prohibited binary, rename, or mode change")
        if line.startswith("new file mode ") and line != "new file mode 100644":
            raise PatchError("New files must use regular non-executable mode 100644")
        if line.startswith("deleted file mode ") and line != "deleted file mode 100644":
            raise PatchError("Deleted files must use regular mode 100644")
        if line.startswith("@@ "):
            in_hunk = True
        elif in_hunk and line.startswith(("+", "-")):
            changed_lines += 1
        section.append(line)

    finish_section()
    if not paths:
        raise PatchError("Patch does not contain any file changes")
    if len(paths) > limits.max_files:
        raise PatchError("Patch exceeds the configured file limit")
    if changed_lines == 0:
        raise PatchError("Patch does not contain any changed lines")
    if changed_lines > limits.max_changed_lines:
        raise PatchError("Patch exceeds the configured changed-line limit")

    return _PatchAnalysis(
        paths=tuple(paths),
        patch_bytes=len(patch_bytes),
        changed_lines=changed_lines,
    )


def _validate_section(lines: list[str]) -> str:
    header = lines[0].split(" ")
    if len(header) != 4 or not header[2].startswith("a/") or not header[3].startswith(
        "b/"
    ):
        raise PatchError("Patch contains an invalid Git file header")
    old_path = header[2][2:]
    new_path = header[3][2:]
    if old_path != new_path:
        raise PatchError("Patch renames and copies are not allowed")
    _validate_relative_path(old_path)

    try:
        first_hunk = next(
            index for index, line in enumerate(lines) if line.startswith("@@ ")
        )
    except StopIteration as exc:
        raise PatchError("Patch file section must contain a unified diff hunk") from exc
    metadata = lines[1:first_hunk]
    old_headers = [
        line[4:].split("\t", 1)[0]
        for line in metadata
        if line.startswith("--- ")
    ]
    new_headers = [
        line[4:].split("\t", 1)[0]
        for line in metadata
        if line.startswith("+++ ")
    ]
    if len(old_headers) != 1 or len(new_headers) != 1:
        raise PatchError("Patch must contain exactly one old and new file header")
    if old_headers[0] not in (f"a/{old_path}", "/dev/null"):
        raise PatchError("Patch old-file header does not match its target")
    if new_headers[0] not in (f"b/{new_path}", "/dev/null"):
        raise PatchError("Patch new-file header does not match its target")
    if old_headers[0] == "/dev/null" and new_headers[0] == "/dev/null":
        raise PatchError("Patch file headers cannot both target /dev/null")
    return old_path


def _validate_relative_path(path: str) -> None:
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or any(ord(character) < 32 for character in path)
        or any(character.isspace() for character in path)
    ):
        raise PatchError("Patch contains an unsafe file path")
    normalized = PurePosixPath(path)
    if normalized.as_posix() != path or ".." in normalized.parts:
        raise PatchError("Patch contains an unsafe file path")


def _git_apply(worktree: Path, patch: str, *, check: bool) -> CompletedProcess[str]:
    arguments = ["git", "-C", str(worktree), "apply"]
    if check:
        arguments.append("--check")
    arguments.extend(("--whitespace=error-all", "-"))
    try:
        return run(
            tuple(arguments),
            input=patch,
            capture_output=True,
            text=True,
            timeout=30,
            env=_git_environment(),
            check=False,
        )
    except (OSError, TimeoutExpired) as exc:
        raise PatchError("Unable to execute Git patch validation") from exc


def _restore(candidate: CandidateWorktree) -> None:
    reset = candidate.manager._git_result(
        "-C", str(candidate.path), "reset", "--hard", "HEAD"
    )
    clean = candidate.manager._git_result(
        "-C", str(candidate.path), "clean", "-fdx"
    )
    if reset.returncode != 0 or clean.returncode != 0:
        raise PatchError("Candidate worktree could not be restored after rejection")


def _git_environment() -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in ("PATH", "HOME", "TMPDIR")
        if name in os.environ
    }
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return environment
