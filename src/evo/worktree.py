"""Ephemeral Git worktrees for isolated candidate mutations."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired, run
from typing import Iterator, Sequence
from uuid import uuid4
import os
import re
import tempfile

from evo.kernel.policy import KernelPolicy


_CANDIDATE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class WorktreeError(RuntimeError):
    """A sanitized Git worktree failure safe to expose to host clients."""


@dataclass(frozen=True, slots=True)
class ChangeValidation:
    allowed: bool
    changed_paths: tuple[str, ...]
    violations: tuple[str, ...] = ()


@dataclass(slots=True)
class CandidateWorktree:
    repository: Path
    path: Path
    branch: str
    manager: "GitWorktreeManager"
    _cleaned: bool = False

    def changed_paths(self) -> tuple[str, ...]:
        tracked = self.manager._git(
            "-C",
            str(self.path),
            "diff",
            "--name-only",
            "--no-renames",
            "-z",
            "HEAD",
            "--",
        ).stdout
        untracked = self.manager._git(
            "-C",
            str(self.path),
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
        ).stdout
        paths = {
            item
            for item in (*tracked.split("\0"), *untracked.split("\0"))
            if item
        }
        return tuple(sorted(paths))

    def validate_changes(
        self,
        mutable_paths: Sequence[str],
        *,
        policy: KernelPolicy | None = None,
    ) -> ChangeValidation:
        prefixes = tuple(path for path in mutable_paths if path)
        if not prefixes:
            raise WorktreeError("حداقل یک مسیر قابل‌تغییر لازم است")
        resolved_policy = policy or KernelPolicy()
        changed = self.changed_paths()
        violations: list[str] = []

        for relative in changed:
            decision = resolved_policy.authorize_mutation(relative, prefixes)
            if not decision.allowed:
                violations.append(f"{relative}: {decision.reason}")
                continue

            candidate_path = self.path / relative
            if not candidate_path.exists() and not candidate_path.is_symlink():
                continue
            if candidate_path.is_symlink():
                violations.append(f"{relative}: پیوند نمادین مجاز نیست")
                continue
            if candidate_path.is_file():
                if candidate_path.stat().st_mode & 0o111:
                    violations.append(
                        f"{relative}: تغییر فایل اجرایی مجاز نیست"
                    )
                elif _looks_binary(candidate_path):
                    violations.append(
                        f"{relative}: تغییر فایل باینری مجاز نیست"
                    )

        return ChangeValidation(
            allowed=not violations,
            changed_paths=changed,
            violations=tuple(violations),
        )

    def cleanup(self) -> None:
        if self._cleaned:
            return
        failures: list[str] = []
        removal = self.manager._git_result(
            "-C",
            str(self.repository),
            "worktree",
            "remove",
            "--force",
            str(self.path),
        )
        if removal.returncode != 0 and self.path.exists():
            failures.append("حذف محیط کار نامزد ممکن نشد")

        self.manager._git_result(
            "-C", str(self.repository), "worktree", "prune"
        )
        branch_removal = self.manager._git_result(
            "-C",
            str(self.repository),
            "branch",
            "-D",
            self.branch,
        )
        if branch_removal.returncode != 0 and self.manager.branch_exists(self.branch):
            failures.append("حذف شاخه نامزد ممکن نشد")

        self._cleaned = not failures
        self.manager._remove_owned_root_if_empty()
        if failures:
            raise WorktreeError("; ".join(failures))


class GitWorktreeManager:
    """Create and destroy candidate branches outside the trusted repository."""

    def __init__(
        self,
        repository: Path,
        *,
        temp_root: Path | None = None,
    ) -> None:
        requested = repository.resolve()
        result = self._git_result("-C", str(requested), "rev-parse", "--show-toplevel")
        if result.returncode != 0:
            raise WorktreeError("محیط کار نامزد باید یک مخزن گیت باشد")
        self.repository = Path(result.stdout.strip()).resolve()
        self._owns_temp_root = temp_root is None
        self.temp_root = (
            Path(tempfile.mkdtemp(prefix="evo-worktrees-")).resolve()
            if temp_root is None
            else temp_root.resolve()
        )
        if self.temp_root == self.repository or self.temp_root.is_relative_to(
            self.repository
        ):
            raise WorktreeError("محیط کار موقت باید خارج از مخزن اصلی باشد")
        self.temp_root.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        candidate_id: str,
        *,
        base_ref: str = "HEAD",
    ) -> CandidateWorktree:
        if not _CANDIDATE_ID.fullmatch(candidate_id):
            raise WorktreeError("شناسه نامزد دارای نویسه‌های ناامن است")
        if (
            not base_ref
            or base_ref.startswith("-")
            or any(character.isspace() for character in base_ref)
        ):
            raise WorktreeError("مرجع پایه گیت نامعتبر است")
        self._git(
            "-C",
            str(self.repository),
            "rev-parse",
            "--verify",
            f"{base_ref}^{{commit}}",
        )

        self.temp_root.mkdir(parents=True, exist_ok=True)
        suffix = uuid4().hex[:12]
        branch = f"evo/candidate-{candidate_id}-{suffix}"
        path = self.temp_root / f"{candidate_id}-{suffix}"
        self._git(
            "-C",
            str(self.repository),
            "worktree",
            "add",
            "-b",
            branch,
            str(path),
            base_ref,
        )
        return CandidateWorktree(
            repository=self.repository,
            path=path,
            branch=branch,
            manager=self,
        )

    @contextmanager
    def candidate(
        self,
        candidate_id: str,
        *,
        base_ref: str = "HEAD",
    ) -> Iterator[CandidateWorktree]:
        worktree = self.create(candidate_id, base_ref=base_ref)
        try:
            yield worktree
        except BaseException as original:
            try:
                worktree.cleanup()
            except WorktreeError as cleanup_error:
                original.add_note(f"پاک‌سازی محیط کار نیز ناموفق بود: {cleanup_error}")
            raise
        else:
            worktree.cleanup()

    def branch_exists(self, branch: str) -> bool:
        result = self._git_result(
            "-C",
            str(self.repository),
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
        )
        return result.returncode == 0

    def _git(self, *arguments: str) -> CompletedProcess[str]:
        result = self._git_result(*arguments)
        if result.returncode != 0:
            raise WorktreeError(_git_failure(result))
        return result

    @staticmethod
    def _git_result(*arguments: str) -> CompletedProcess[str]:
        environment = {
            name: os.environ[name]
            for name in ("PATH", "HOME", "TMPDIR")
            if name in os.environ
        }
        environment["GIT_TERMINAL_PROMPT"] = "0"
        try:
            return run(
                ("git", *arguments),
                capture_output=True,
                text=True,
                timeout=30,
                env=environment,
                check=False,
            )
        except (OSError, TimeoutExpired) as exc:
            raise WorktreeError("اجرای عملیات محیط کار گیت ممکن نیست") from exc

    def _remove_owned_root_if_empty(self) -> None:
        if not self._owns_temp_root:
            return
        try:
            self.temp_root.rmdir()
        except OSError:
            pass


def _looks_binary(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return b"\0" in stream.read(8192)
    except OSError as exc:
        raise WorktreeError(f"بررسی فایل نامزد ممکن نیست: {path.name}") from exc


def _git_failure(result: CompletedProcess[str]) -> str:
    message = result.stderr.strip()
    if "not a git repository" in message.lower():
        return "محیط کار نامزد باید یک مخزن گیت باشد"
    if (
        "not a valid object name" in message.lower()
        or "needed a single revision" in message.lower()
    ):
        return "مرجع پایه گیت به هیچ commit معتبری اشاره نمی‌کند"
    return "عملیات محیط کار گیت ناموفق بود"
