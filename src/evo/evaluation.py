"""Tamper-evident records for explicit rootless sandbox evaluations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Protocol, Sequence
import json

from evo.sandbox import SandboxResult


class SandboxRunner(Protocol):
    def run(self, command: Sequence[str]) -> SandboxResult: ...


@dataclass(frozen=True, slots=True)
class EvaluationEvidence:
    source: str
    candidate_id: str
    team_ids: tuple[str, ...]
    status: str
    command: tuple[str, ...]
    exit_code: int
    duration_seconds: float
    timed_out: bool
    output_truncated: bool
    stdout_sha256: str
    stderr_sha256: str
    recorded_at: str

    @property
    def verified(self) -> bool:
        return self.status == "sandbox_verified"


class EvidenceRecorder:
    """Run an evaluator and append bounded evidence without storing raw output."""

    def __init__(self, *, sandbox: SandboxRunner, evidence_path: Path) -> None:
        self.sandbox = sandbox
        self.evidence_path = evidence_path
        self._lock = Lock()

    def evaluate(
        self,
        *,
        candidate_id: str,
        team_ids: Sequence[str],
        command: Sequence[str],
    ) -> EvaluationEvidence:
        clean_candidate_id = candidate_id.strip()
        clean_team_ids = tuple(
            dict.fromkeys(item.strip() for item in team_ids if item.strip())
        )
        if not clean_candidate_id:
            raise ValueError("Candidate ID cannot be empty.")
        if not 1 <= len(clean_team_ids) <= 3:
            raise ValueError(
                "Evaluation teams must contain between one and three organisms."
            )

        result = self.sandbox.run(command)
        evidence = EvaluationEvidence(
            source="rootless_sandbox",
            candidate_id=clean_candidate_id,
            team_ids=clean_team_ids,
            status="sandbox_verified" if result.succeeded else "sandbox_failed",
            command=result.command,
            exit_code=result.exit_code,
            duration_seconds=result.duration_seconds,
            timed_out=result.timed_out,
            output_truncated=result.output_truncated,
            stdout_sha256=_digest(result.stdout),
            stderr_sha256=_digest(result.stderr),
            recorded_at=datetime.now(UTC).isoformat(),
        )
        self._append(evidence)
        return evidence

    def _append(self, evidence: EvaluationEvidence) -> None:
        self.evidence_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(asdict(evidence), ensure_ascii=False, sort_keys=True)
        with self._lock:
            with self.evidence_path.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")


def proposal_only_evidence(candidate_id: object) -> dict[str, object]:
    """Describe the honest default before a candidate has executable artifacts."""
    return {
        "candidate_id": candidate_id,
        "status": "proposal_only",
        "verified": False,
        "reason": "No executable candidate patch or sandbox result was supplied.",
    }


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()
