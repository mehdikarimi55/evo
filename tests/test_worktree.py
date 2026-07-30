from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import unittest

from evo.worktree import GitWorktreeManager, WorktreeError


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


class WorktreeTests(unittest.TestCase):
    def _repository(self, directory: str) -> Path:
        repository = Path(directory) / "repository"
        repository.mkdir()
        git(repository, "init")
        git(repository, "config", "user.name", "EVO Tests")
        git(repository, "config", "user.email", "evo-tests@example.invalid")
        (repository / "organisms").mkdir()
        (repository / "organisms" / "prompt.md").write_text(
            "baseline\n", encoding="utf-8"
        )
        (repository / "src" / "evo" / "kernel").mkdir(parents=True)
        (repository / "src" / "evo" / "kernel" / "policy.py").write_text(
            "IMMUTABLE = True\n", encoding="utf-8"
        )
        git(repository, "add", ".")
        git(repository, "commit", "-m", "baseline")
        return repository

    def test_candidate_is_created_from_head_and_always_removed(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)
            worktree_path = None
            branch = None

            with manager.candidate("candidate-1") as candidate:
                worktree_path = candidate.path
                branch = candidate.branch
                self.assertTrue(worktree_path.is_dir())
                self.assertTrue(manager.branch_exists(branch))
                self.assertEqual(
                    (worktree_path / "organisms" / "prompt.md").read_text(),
                    "baseline\n",
                )

            self.assertFalse(worktree_path.exists())
            self.assertFalse(manager.branch_exists(branch))

    def test_cleanup_runs_when_candidate_evaluation_raises(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)
            worktree_path = None

            with self.assertRaisesRegex(RuntimeError, "evaluation failed"):
                with manager.candidate("candidate-2") as candidate:
                    worktree_path = candidate.path
                    raise RuntimeError("evaluation failed")

            self.assertFalse(worktree_path.exists())

    def test_manager_can_create_multiple_sequential_candidates(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("first") as first:
                first_path = first.path
                self.assertTrue(first_path.exists())
            with manager.candidate("second") as second:
                second_path = second.path
                self.assertTrue(second_path.exists())

            self.assertFalse(first_path.exists())
            self.assertFalse(second_path.exists())

    def test_allows_only_text_changes_under_mutable_paths(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("candidate-3") as candidate:
                target = candidate.path / "organisms" / "prompt.md"
                target.write_text("improved\n", encoding="utf-8")
                validation = candidate.validate_changes(("organisms/",))

            self.assertTrue(validation.allowed)
            self.assertEqual(validation.changed_paths, ("organisms/prompt.md",))

    def test_rejects_protected_symlink_and_binary_mutations(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("candidate-4") as candidate:
                kernel = candidate.path / "src" / "evo" / "kernel" / "policy.py"
                kernel.write_text("IMMUTABLE = False\n", encoding="utf-8")
                symlink = candidate.path / "organisms" / "escape"
                symlink.symlink_to("../../.env.local")
                binary = candidate.path / "organisms" / "payload.bin"
                binary.write_bytes(b"EVO\0binary")
                validation = candidate.validate_changes(
                    ("organisms/", "src/")
                )

            self.assertFalse(validation.allowed)
            self.assertEqual(
                validation.changed_paths,
                (
                    "organisms/escape",
                    "organisms/payload.bin",
                    "src/evo/kernel/policy.py",
                ),
            )
            reasons = "\n".join(validation.violations)
            self.assertIn("symbolic links", reasons)
            self.assertIn("binary mutations", reasons)
            self.assertIn("immutable kernel", reasons)

    def test_rejects_non_repository_and_unsafe_candidate_id(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(WorktreeError, "Git repository"):
                GitWorktreeManager(Path(directory))

            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)
            with self.assertRaisesRegex(WorktreeError, "unsafe"):
                manager.create("../escape")


if __name__ == "__main__":
    unittest.main()
