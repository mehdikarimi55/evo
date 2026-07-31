from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import json
import unittest

from evo.candidate_lifecycle import CandidateLifecycle
from evo.sandbox import SandboxResult


PATCH = """\
diff --git a/organisms/prompt.md b/organisms/prompt.md
--- a/organisms/prompt.md
+++ b/organisms/prompt.md
@@ -1 +1 @@
-baseline
+improved
"""


def git(repository: Path, *arguments: str) -> str:
    result = run(
        ("git", "-C", str(repository), *arguments),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout


class ContentSandbox:
    def __init__(self, workspace: Path, *, regress: bool = False):
        self.workspace = workspace
        self.regress = regress

    def run(self, command):
        content = (self.workspace / "organisms/prompt.md").read_text()
        candidate = content == "improved\n"
        exit_code = 1 if candidate and self.regress else 0
        return SandboxResult(
            command=tuple(command),
            exit_code=exit_code,
            stdout="pass\n" if exit_code == 0 else "fail\n",
            stderr="",
            duration_seconds=0.1,
        )


class CandidateLifecycleTests(unittest.TestCase):
    def _repository(self, directory: str) -> Path:
        repository = Path(directory) / "repository"
        (repository / "organisms").mkdir(parents=True)
        (repository / "organisms/prompt.md").write_text("baseline\n")
        git(repository, "init")
        git(repository, "config", "user.name", "EVO Tests")
        git(repository, "config", "user.email", "evo@example.invalid")
        git(repository, "add", ".")
        git(repository, "commit", "-m", "baseline")
        return repository

    def test_verified_comparison_is_hash_only_and_ephemeral(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            ledger = Path(directory) / "evidence.jsonl"
            evidence = CandidateLifecycle(
                repository=repository,
                evidence_path=ledger,
                sandbox_factory=lambda workspace: ContentSandbox(workspace),
            ).evaluate(
                candidate_id="candidate-1",
                team_ids=("gnome-1", "gnome-2"),
                patch=PATCH,
                mutable_paths=("organisms/",),
                command=("python", "-m", "unittest"),
            )
            stored = json.loads(ledger.read_text())
            self.assertTrue(evidence.verified)
            self.assertTrue(evidence.promotion_eligible)
            self.assertEqual(evidence.classification, "preserved_baseline")
            self.assertEqual(evidence.changed_paths, ("organisms/prompt.md",))
            self.assertNotIn("stdout", stored)
            self.assertNotIn(PATCH, ledger.read_text())
            self.assertEqual(
                (repository / "organisms/prompt.md").read_text(),
                "baseline\n",
            )
            self.assertEqual(len(git(repository, "worktree", "list").splitlines()), 1)

    def test_regression_is_not_promotion_eligible(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            evidence = CandidateLifecycle(
                repository=repository,
                evidence_path=Path(directory) / "evidence.jsonl",
                sandbox_factory=lambda workspace: ContentSandbox(
                    workspace, regress=True
                ),
            ).evaluate(
                candidate_id="candidate-2",
                team_ids=("gnome-1",),
                patch=PATCH,
                mutable_paths=("organisms/",),
                command=("python", "-m", "unittest"),
            )
            self.assertEqual(evidence.classification, "regression")
            self.assertFalse(evidence.verified)
            self.assertFalse(evidence.promotion_eligible)

    def test_invalid_patch_is_recorded_without_candidate_execution(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            evidence = CandidateLifecycle(
                repository=repository,
                evidence_path=Path(directory) / "evidence.jsonl",
                sandbox_factory=lambda workspace: ContentSandbox(workspace),
            ).evaluate(
                candidate_id="candidate-3",
                team_ids=("gnome-1",),
                patch="not a patch\n",
                mutable_paths=("organisms/",),
                command=("python", "-m", "unittest"),
            )
            self.assertEqual(evidence.classification, "patch_rejected")
            self.assertEqual(evidence.status, "invalid")
            self.assertFalse(evidence.promotion_eligible)

    def test_dirty_repository_fails_closed_before_evaluation(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            (repository / "organisms/prompt.md").write_text("user edit\n")
            evidence = CandidateLifecycle(
                repository=repository,
                evidence_path=Path(directory) / "evidence.jsonl",
                sandbox_factory=lambda workspace: ContentSandbox(workspace),
            ).evaluate(
                candidate_id="candidate-4",
                team_ids=("gnome-1",),
                patch=PATCH,
                mutable_paths=("organisms/",),
                command=("python", "-m", "unittest"),
            )
            self.assertEqual(evidence.classification, "patch_rejected")
            self.assertIn("clean repository", evidence.reason)


if __name__ == "__main__":
    unittest.main()
