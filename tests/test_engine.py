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
        self.last_system = ""

    def generate_json(self, *, system: str, user: str) -> ModelReply:
        self.last_system = system
        return ModelReply(
            text=json.dumps(self.response),
            input_tokens=40,
            output_tokens=30,
            model="fake-model",
        )

    def healthcheck(self) -> str:
        return "ok"


class SequenceProvider(FakeProvider):
    def __init__(self, responses: list[dict]):
        super().__init__(responses[0])
        self.responses = list(responses)

    def generate_json(self, *, system: str, user: str) -> ModelReply:
        self.response = self.responses.pop(0)
        return super().generate_json(system=system, user=user)


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

    def test_generation_requests_the_selected_output_language(self):
        response = {
            "target_path": "organisms/cell/prompt.md",
            "summary": "خلاصه",
            "rationale": " ".join(["استدلال"] * 20),
            "expected_benefit": "فایده",
            "risk": "ریسک",
        }
        with TemporaryDirectory() as directory:
            provider = FakeProvider(response)
            engine = EvolutionEngine(
                provider=provider,
                policy=KernelPolicy(),
                budget=RunBudget(
                    max_calls=1,
                    max_input_tokens=100,
                    max_output_tokens=100,
                ),
                audit=AuditLog(Path(directory) / "audit.jsonl"),
            )
            engine.run_generation(
                Genome("cell-1"),
                EvolutionTask("task-1", "بهبود"),
                language="Persian",
            )
        self.assertIn("fluent Persian", provider.last_system)

    def test_generates_bounded_patch_when_source_reader_is_available(self):
        proposal = {
            "target_path": "organisms/prompt.md",
            "summary": "Clarify one instruction.",
            "rationale": " ".join(["bounded"] * 20),
            "expected_benefit": "More reliable behavior.",
            "risk": "Wording may be too strict.",
        }
        patch = """diff --git a/organisms/prompt.md b/organisms/prompt.md
--- a/organisms/prompt.md
+++ b/organisms/prompt.md
@@ -1 +1 @@
-baseline
+improved
"""
        with TemporaryDirectory() as directory:
            provider = SequenceProvider([proposal, {"patch": patch}])
            candidate = EvolutionEngine(
                provider=provider,
                policy=KernelPolicy(),
                budget=RunBudget(
                    max_calls=2,
                    max_input_tokens=100,
                    max_output_tokens=100,
                ),
                audit=AuditLog(Path(directory) / "audit.jsonl"),
                source_reader=lambda path: "baseline\n",
            ).run_generation(
                Genome("cell-1"),
                EvolutionTask("task-1", "Improve prompt"),
            )
        self.assertEqual(candidate.proposal.patch, patch)
        self.assertEqual(provider.responses, [])


if __name__ == "__main__":
    unittest.main()
