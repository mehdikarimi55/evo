"""A bounded, non-mutating first-generation evolution loop."""

from __future__ import annotations

from uuid import uuid4
import json

from evo.domain import (
    Candidate,
    CandidateStatus,
    EvolutionTask,
    FitnessScore,
    Genome,
    MutationProposal,
)
from evo.kernel.audit import AuditLog
from evo.kernel.budget import RunBudget
from evo.kernel.policy import KernelPolicy
from evo.providers.base import ModelProvider


SYSTEM_PROMPT = """\
You are an organism inside EVO Terrarium.
Propose exactly one safe, reversible improvement for the given objective.
You cannot execute tools, modify files, request credentials, create accounts,
spend money, or deploy. Return one JSON object with exactly these string fields:
target_path, summary, rationale, expected_benefit, risk.
The target_path must be within one of the supplied mutable path prefixes.
"""


class EvolutionEngine:
    def __init__(
        self,
        *,
        provider: ModelProvider,
        policy: KernelPolicy,
        budget: RunBudget,
        audit: AuditLog,
    ) -> None:
        self.provider = provider
        self.policy = policy
        self.budget = budget
        self.audit = audit

    def run_generation(self, genome: Genome, task: EvolutionTask) -> Candidate:
        self.budget.reserve_call()
        request = json.dumps(
            {
                "objective": task.objective,
                "acceptance_criteria": task.acceptance_criteria,
                "mutable_paths": genome.mutable_paths,
                "generation": genome.generation,
                "traits": genome.traits,
            },
            sort_keys=True,
        )
        reply = self.provider.generate_json(system=SYSTEM_PROMPT, user=request)
        self.budget.record_usage(reply.input_tokens, reply.output_tokens)

        rejection_reason: str | None = None
        proposal: MutationProposal | None = None
        schema_score = 0.0
        policy_score = 0.0
        rationale_score = 0.0

        try:
            proposal = MutationProposal.from_mapping(json.loads(reply.text))
            schema_score = 1.0
            decision = self.policy.authorize_mutation(
                proposal.target_path, genome.mutable_paths
            )
            policy_score = 1.0 if decision.allowed else 0.0
            rationale_score = min(len(proposal.rationale.split()) / 20.0, 1.0)
            if not decision.allowed:
                rejection_reason = decision.reason
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            rejection_reason = f"Invalid proposal: {exc}"

        score = FitnessScore(schema_score, policy_score, rationale_score)
        status = (
            CandidateStatus.ELIGIBLE
            if proposal is not None and rejection_reason is None and score.total >= 0.85
            else CandidateStatus.REJECTED
        )
        candidate = Candidate(
            candidate_id=f"candidate-{uuid4().hex[:12]}",
            genome_fingerprint=genome.fingerprint(),
            proposal=proposal,
            score=score,
            status=status,
            rejection_reason=rejection_reason,
        )
        self.audit.append(
            "generation.completed",
            {
                "task_id": task.task_id,
                "candidate_id": candidate.candidate_id,
                "status": candidate.status,
                "score": candidate.score.total,
                "model": reply.model,
                "request_id": reply.request_id,
                "budget": self.budget.snapshot().__dict__
                if hasattr(self.budget.snapshot(), "__dict__")
                else {
                    "calls_used": self.budget.snapshot().calls_used,
                    "input_tokens_used": self.budget.snapshot().input_tokens_used,
                    "output_tokens_used": self.budget.snapshot().output_tokens_used,
                },
                "rejection_reason": candidate.rejection_reason,
            },
        )
        return candidate

