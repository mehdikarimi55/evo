"""Ephemeral patch application and baseline-versus-candidate evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Callable, Sequence
import json

from evo.mutation import MutationApplicator, PatchApplication, PatchError
from evo.release_control import CandidateArtifactStore, ReleaseControlError
from evo.sandbox import RootlessSandbox, SandboxError, SandboxResult
from evo.worktree import GitWorktreeManager, WorktreeError


SandboxFactory = Callable[[Path], RootlessSandbox]


@dataclass(frozen=True, slots=True)
class ComparativeEvidence:
    source: str
    candidate_id: str
    team_ids: tuple[str, ...]
    status: str
    classification: str
    verified: bool
    promotion_eligible: bool
    command: tuple[str, ...]
    patch_sha256: str | None
    changed_paths: tuple[str, ...]
    baseline_exit_code: int | None
    candidate_exit_code: int | None
    baseline_stdout_sha256: str | None
    baseline_stderr_sha256: str | None
    candidate_stdout_sha256: str | None
    candidate_stderr_sha256: str | None
    duration_seconds: float
    reason: str | None
    recorded_at: str
    artifact_id: str | None
    artifact_manifest_sha256: str | None


class CandidateLifecycle:
    """Evaluate ephemerally and optionally seal only a verified patch."""

    def __init__(
        self,
        *,
        repository: Path,
        sandbox_factory: SandboxFactory,
        evidence_path: Path,
        mutation: MutationApplicator | None = None,
        artifact_store: CandidateArtifactStore | None = None,
    ) -> None:
        self.repository = repository.resolve()
        self.sandbox_factory = sandbox_factory
        self.evidence_path = evidence_path
        self.mutation = mutation or MutationApplicator()
        self.artifact_store = artifact_store
        self._lock = Lock()

    def evaluate(
        self,
        *,
        candidate_id: str,
        team_ids: Sequence[str],
        patch: str,
        mutable_paths: Sequence[str],
        command: Sequence[str],
    ) -> ComparativeEvidence:
        started = datetime.now(UTC)
        baseline: SandboxResult | None = None
        candidate_result: SandboxResult | None = None
        application: PatchApplication | None = None
        reason: str | None = None
        manager: GitWorktreeManager | None = None
        base_commit: str | None = None
        try:
            manager = GitWorktreeManager(self.repository)
            if not manager.repository_is_clean():
                raise WorktreeError(
                    "Candidate comparison requires a clean repository."
                )
            base_commit = manager.head_commit()
            baseline = self.sandbox_factory(self.repository).run(command)
            with manager.candidate(candidate_id) as worktree:
                application = self.mutation.apply(
                    candidate=worktree,
                    patch=patch,
                    mutable_paths=mutable_paths,
                    candidate_id=candidate_id,
                )
                candidate_result = self.sandbox_factory(worktree.path).run(command)
        except (PatchError, SandboxError, WorktreeError) as exc:
            reason = str(exc)
        finally:
            if manager is not None:
                manager.cleanup()

        classification, status, verified = _classify(
            baseline,
            candidate_result,
            application,
        )
        evidence = ComparativeEvidence(
            source="rootless_sandbox_comparison",
            candidate_id=candidate_id,
            team_ids=tuple(dict.fromkeys(team_ids))[:3],
            status=status,
            classification=classification,
            verified=verified,
            promotion_eligible=verified,
            command=tuple(command),
            patch_sha256=(application.patch_sha256 if application else None),
            changed_paths=(application.changed_paths if application else ()),
            baseline_exit_code=(baseline.exit_code if baseline else None),
            candidate_exit_code=(
                candidate_result.exit_code if candidate_result else None
            ),
            baseline_stdout_sha256=_result_digest(baseline, "stdout"),
            baseline_stderr_sha256=_result_digest(baseline, "stderr"),
            candidate_stdout_sha256=_result_digest(candidate_result, "stdout"),
            candidate_stderr_sha256=_result_digest(candidate_result, "stderr"),
            duration_seconds=round(
                (datetime.now(UTC) - started).total_seconds(), 4
            ),
            reason=reason,
            recorded_at=datetime.now(UTC).isoformat(),
            artifact_id=None,
            artifact_manifest_sha256=None,
        )
        if verified and self.artifact_store and base_commit:
            try:
                artifact = self.artifact_store.seal(
                    candidate_id=candidate_id,
                    patch=patch,
                    base_commit=base_commit,
                    evidence=asdict(evidence),
                    mutable_paths=mutable_paths,
                )
            except ReleaseControlError:
                evidence = replace(
                    evidence,
                    promotion_eligible=False,
                    reason=(
                        "Sandbox evaluation passed, but the reproducible "
                        "candidate artifact could not be sealed."
                    ),
                )
            else:
                evidence = replace(
                    evidence,
                    artifact_id=str(artifact["artifact_id"]),
                    artifact_manifest_sha256=str(
                        artifact["artifact_manifest_sha256"]
                    ),
                )
        self._append(evidence)
        return evidence

    def _append(self, evidence: ComparativeEvidence) -> None:
        self.evidence_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(asdict(evidence), ensure_ascii=False, sort_keys=True)
        with self._lock:
            with self.evidence_path.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")


def _classify(
    baseline: SandboxResult | None,
    candidate: SandboxResult | None,
    application: PatchApplication | None,
) -> tuple[str, str, bool]:
    if application is None:
        return "patch_rejected", "invalid", False
    if baseline is None or candidate is None:
        return "incomplete", "sandbox_failed", False
    if candidate.succeeded and baseline.succeeded:
        return "preserved_baseline", "sandbox_verified", True
    if candidate.succeeded and not baseline.succeeded:
        return "repaired_baseline", "sandbox_verified", True
    if baseline.succeeded and not candidate.succeeded:
        return "regression", "sandbox_failed", False
    return "still_failing", "sandbox_failed", False


def _result_digest(result: SandboxResult | None, field: str) -> str | None:
    if result is None:
        return None
    value = getattr(result, field)
    return sha256(value.encode("utf-8")).hexdigest()
