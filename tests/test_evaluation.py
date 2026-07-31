from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from evo.evaluation import EvidenceRecorder, proposal_only_evidence
from evo.sandbox import SandboxResult


class FakeSandbox:
    def __init__(self, *, exit_code: int = 0):
        self.exit_code = exit_code

    def run(self, command):
        return SandboxResult(
            command=tuple(command),
            exit_code=self.exit_code,
            stdout="67 tests passed\n",
            stderr="",
            duration_seconds=0.25,
        )


class EvaluationEvidenceTests(unittest.TestCase):
    def test_records_verified_hash_only_evidence(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            evidence = EvidenceRecorder(
                sandbox=FakeSandbox(),
                evidence_path=path,
            ).evaluate(
                candidate_id="candidate-1",
                team_ids=("gnome-0001", "gnome-0002"),
                command=("python", "-m", "unittest"),
            )
            self.assertTrue(evidence.verified)
            self.assertEqual(evidence.status, "sandbox_verified")
            self.assertEqual(evidence.source, "rootless_sandbox")
            stored = json.loads(path.read_text().strip())
            self.assertIn("stdout_sha256", stored)
            self.assertNotIn("stdout", stored)

    def test_failed_result_is_evidence_but_not_verified(self):
        with TemporaryDirectory() as directory:
            evidence = EvidenceRecorder(
                sandbox=FakeSandbox(exit_code=1),
                evidence_path=Path(directory) / "evidence.jsonl",
            ).evaluate(
                candidate_id="candidate-2",
                team_ids=("gnome-0001",),
                command=("pytest",),
            )
            self.assertEqual(evidence.status, "sandbox_failed")
            self.assertFalse(evidence.verified)

    def test_rejects_unbounded_team_and_marks_plain_proposal(self):
        with TemporaryDirectory() as directory:
            recorder = EvidenceRecorder(
                sandbox=FakeSandbox(),
                evidence_path=Path(directory) / "evidence.jsonl",
            )
            with self.assertRaisesRegex(ValueError, "one and three"):
                recorder.evaluate(
                    candidate_id="candidate-3",
                    team_ids=("a", "b", "c", "d"),
                    command=("pytest",),
                )
        evidence = proposal_only_evidence("candidate-4")
        self.assertEqual(evidence["status"], "proposal_only")
        self.assertFalse(evidence["verified"])


if __name__ == "__main__":
    unittest.main()
