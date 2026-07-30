"""Core domain contracts. These contain no provider or filesystem secrets."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
import hashlib
import json


class CandidateStatus(StrEnum):
    PROPOSED = "proposed"
    ELIGIBLE = "eligible"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class Genome:
    organism_id: str
    generation: int = 0
    mutable_paths: tuple[str, ...] = ("organisms/",)
    parent_ids: tuple[str, ...] = ()
    traits: dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        payload = json.dumps(
            {
                "organism_id": self.organism_id,
                "generation": self.generation,
                "mutable_paths": self.mutable_paths,
                "parent_ids": self.parent_ids,
                "traits": self.traits,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class EvolutionTask:
    task_id: str
    objective: str
    acceptance_criteria: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MutationProposal:
    target_path: str
    summary: str
    rationale: str
    expected_benefit: str
    risk: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "MutationProposal":
        required = (
            "target_path",
            "summary",
            "rationale",
            "expected_benefit",
            "risk",
        )
        missing = [name for name in required if not str(data.get(name, "")).strip()]
        if missing:
            raise ValueError(f"Missing proposal fields: {', '.join(missing)}")
        return cls(**{name: str(data[name]).strip() for name in required})


@dataclass(frozen=True, slots=True)
class FitnessScore:
    schema_validity: float
    policy_compliance: float
    rationale_quality: float

    @property
    def total(self) -> float:
        return round(
            0.40 * self.schema_validity
            + 0.40 * self.policy_compliance
            + 0.20 * self.rationale_quality,
            4,
        )


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    genome_fingerprint: str
    proposal: MutationProposal | None
    score: FitnessScore
    status: CandidateStatus
    rejection_reason: str | None = None

