from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from evo.domain import CandidateStatus, EvolutionTask, Genome
from evo.evolution import EvolutionEngine
from evo.kernel.audit import AuditLog
from evo.kernel.budget import RunBudget
from evo.kernel.policy import KernelPolicy
from evo.providers.base import ModelReply


class FakeProvider:
    def __init__(self, response: dict):
        self.response = response

    def generate_json(self, *, system: str, user: str) -> ModelReply:
        return ModelReply(
            text=json.dumps(self.response),
            input_tokens=40,
            output_tokens=30,
            model="fake-model",
        )

    def healthcheck(self) -> str:
        return "ok"


class EngineTests(unittest.TestCase):
    def _engine(self, path: Path, response: dict) -> EvolutionEngine:
        return EvolutionEngine(
            provider=FakeProvider(response),
            policy=KernelPolicy(),
            budget=RunBudget(
                max_calls=1, max_input_tokens=100, max_output_tokens=100
            ),
            audit=AuditLog(path),
        )

    def test_safe_proposal_becomes_eligible(self):
        response = {
            "target_path": "organisms/cell/prompt.md",
            "summary": "Clarify the evaluator instructions.",
            "rationale": " ".join(["verified"] * 20),
            "expected_benefit": "More consistent structured proposals.",
            "risk": "May make the prompt too restrictive.",
        }
        with TemporaryDirectory() as directory:
            candidate = self._engine(
                Path(directory) / "audit.jsonl", response
            ).run_generation(
                Genome("cell-1"),
                EvolutionTask("task-1", "Improve proposal consistency"),
            )
        self.assertEqual(candidate.status, CandidateStatus.ELIGIBLE)

    def test_protected_target_is_rejected(self):
        response = {
            "target_path": "src/evo/kernel/policy.py",
            "summary": "Remove a restriction.",
            "rationale": " ".join(["unsafe"] * 20),
            "expected_benefit": "More access.",
            "risk": "Policy bypass.",
        }
        with TemporaryDirectory() as directory:
            candidate = self._engine(
                Path(directory) / "audit.jsonl", response
            ).run_generation(
                Genome("cell-1", mutable_paths=("src/",)),
                EvolutionTask("task-1", "Improve yourself"),
            )
        self.assertEqual(candidate.status, CandidateStatus.REJECTED)


if __name__ == "__main__":
    unittest.main()
