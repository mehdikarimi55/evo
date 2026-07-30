from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from evo.kernel.audit import AuditLog
from evo.mutation import MutationApplicator, PatchError, PatchLimits
from evo.worktree import GitWorktreeManager


VALID_PATCH = """\
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


class MutationApplicatorTests(unittest.TestCase):
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

    def test_applies_valid_patch_only_to_candidate_and_audits_hash(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            audit_path = Path(directory) / "audit.jsonl"
            manager = GitWorktreeManager(repository)

            with manager.candidate("valid") as candidate:
                result = MutationApplicator(
                    audit=AuditLog(audit_path)
                ).apply(
                    candidate=candidate,
                    patch=VALID_PATCH,
                    mutable_paths=("organisms/",),
                    candidate_id="valid",
                )
                candidate_text = (
                    candidate.path / "organisms" / "prompt.md"
                ).read_text(encoding="utf-8")

            self.assertEqual(candidate_text, "improved\n")
            self.assertEqual(
                (repository / "organisms" / "prompt.md").read_text(),
                "baseline\n",
            )
            self.assertEqual(result.changed_paths, ("organisms/prompt.md",))
            self.assertEqual(
                result.patch_sha256,
                hashlib.sha256(VALID_PATCH.encode()).hexdigest(),
            )
            event = json.loads(audit_path.read_text())
            self.assertEqual(event["event_type"], "mutation.applied")
            self.assertEqual(
                event["payload"]["patch_sha256"], result.patch_sha256
            )
            self.assertNotIn(VALID_PATCH, audit_path.read_text())

    def test_rejects_protected_path_without_modifying_candidate(self):
        patch = VALID_PATCH.replace(
            "organisms/prompt.md", "src/evo/kernel/policy.py"
        ).replace("-baseline", "-IMMUTABLE = True").replace(
            "+improved", "+IMMUTABLE = False"
        )
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("protected") as candidate:
                with self.assertRaisesRegex(PatchError, "allowed mutation"):
                    MutationApplicator().apply(
                        candidate=candidate,
                        patch=patch,
                        mutable_paths=("organisms/", "src/"),
                        candidate_id="protected",
                    )
                self.assertEqual(candidate.changed_paths(), ())

    def test_rejects_traversal_rename_binary_and_symlink_patches(self):
        unsafe_patches = (
            VALID_PATCH.replace(
                "organisms/prompt.md", "../outside.txt"
            ),
            VALID_PATCH.replace(
                "diff --git a/organisms/prompt.md b/organisms/prompt.md",
                (
                    "diff --git a/organisms/prompt.md "
                    "b/organisms/renamed.md\n"
                    "similarity index 100%\n"
                    "rename from organisms/prompt.md\n"
                    "rename to organisms/renamed.md"
                ),
            ),
            VALID_PATCH.replace(
                "--- a/organisms/prompt.md",
                "GIT binary patch\n--- a/organisms/prompt.md",
            ),
            VALID_PATCH.replace(
                "--- a/organisms/prompt.md",
                "new file mode 120000\n--- a/organisms/prompt.md",
            ),
        )
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            for index, patch in enumerate(unsafe_patches):
                with manager.candidate(f"unsafe-{index}") as candidate:
                    with self.assertRaises(PatchError):
                        MutationApplicator().apply(
                            candidate=candidate,
                            patch=patch,
                            mutable_paths=("organisms/",),
                            candidate_id=f"unsafe-{index}",
                        )
                    self.assertEqual(candidate.changed_paths(), ())

    def test_rejects_oversized_and_multi_file_patches(self):
        second = VALID_PATCH.replace(
            "organisms/prompt.md", "organisms/other.md"
        ).replace("--- a/organisms/other.md", "--- /dev/null").replace(
            "@@ -1 +1 @@", "@@ -0,0 +1 @@"
        ).replace("-baseline\n", "").replace("+improved", "+other")
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("limits") as candidate:
                with self.assertRaisesRegex(PatchError, "file limit"):
                    MutationApplicator(
                        limits=PatchLimits(max_files=1)
                    ).apply(
                        candidate=candidate,
                        patch=VALID_PATCH + second,
                        mutable_paths=("organisms/",),
                        candidate_id="limits",
                    )
                with self.assertRaisesRegex(PatchError, "byte limit"):
                    MutationApplicator(
                        limits=PatchLimits(max_bytes=32)
                    ).apply(
                        candidate=candidate,
                        patch=VALID_PATCH,
                        mutable_paths=("organisms/",),
                        candidate_id="limits",
                    )

    def test_counts_header_like_hunk_content_and_enforces_line_limit(self):
        patch = VALID_PATCH.replace("+improved", "+++value")
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("header-content") as candidate:
                result = MutationApplicator().apply(
                    candidate=candidate,
                    patch=patch,
                    mutable_paths=("organisms/",),
                    candidate_id="header-content",
                )
                self.assertEqual(result.changed_lines, 2)
                self.assertEqual(
                    (candidate.path / "organisms" / "prompt.md").read_text(),
                    "++value\n",
                )

            with manager.candidate("line-limit") as candidate:
                with self.assertRaisesRegex(PatchError, "changed-line limit"):
                    MutationApplicator(
                        limits=PatchLimits(max_changed_lines=1)
                    ).apply(
                        candidate=candidate,
                        patch=patch,
                        mutable_paths=("organisms/",),
                        candidate_id="line-limit",
                    )

    def test_rejects_mutation_of_existing_executable(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            executable = repository / "organisms" / "tool.sh"
            executable.write_text("echo baseline\n", encoding="utf-8")
            executable.chmod(0o755)
            git(repository, "add", "organisms/tool.sh")
            git(repository, "commit", "-m", "add executable")
            patch = """\
diff --git a/organisms/tool.sh b/organisms/tool.sh
--- a/organisms/tool.sh
+++ b/organisms/tool.sh
@@ -1 +1 @@
-echo baseline
+echo changed
"""
            manager = GitWorktreeManager(repository)

            with manager.candidate("executable") as candidate:
                with self.assertRaisesRegex(PatchError, "executable"):
                    MutationApplicator().apply(
                        candidate=candidate,
                        patch=patch,
                        mutable_paths=("organisms/",),
                        candidate_id="executable",
                    )
                self.assertEqual(candidate.changed_paths(), ())

    def test_rejects_patch_that_does_not_apply_and_records_rejection(self):
        invalid = VALID_PATCH.replace("-baseline", "-missing")
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            audit_path = Path(directory) / "audit.jsonl"
            manager = GitWorktreeManager(repository)

            with manager.candidate("invalid") as candidate:
                with self.assertRaisesRegex(PatchError, "cleanly"):
                    MutationApplicator(audit=AuditLog(audit_path)).apply(
                        candidate=candidate,
                        patch=invalid,
                        mutable_paths=("organisms/",),
                        candidate_id="invalid",
                    )
                self.assertEqual(candidate.changed_paths(), ())

            event = json.loads(audit_path.read_text())
            self.assertEqual(event["event_type"], "mutation.rejected")
            self.assertEqual(
                event["payload"]["patch_sha256"],
                hashlib.sha256(invalid.encode()).hexdigest(),
            )

    def test_requires_clean_worktree_and_raw_unfenced_diff(self):
        with TemporaryDirectory() as directory:
            repository = self._repository(directory)
            manager = GitWorktreeManager(repository)

            with manager.candidate("dirty") as candidate:
                target = candidate.path / "organisms" / "prompt.md"
                target.write_text("dirty\n", encoding="utf-8")
                with self.assertRaisesRegex(PatchError, "must be clean"):
                    MutationApplicator().apply(
                        candidate=candidate,
                        patch=VALID_PATCH,
                        mutable_paths=("organisms/",),
                        candidate_id="dirty",
                    )

            with manager.candidate("fenced") as candidate:
                with self.assertRaisesRegex(PatchError, "raw Git"):
                    MutationApplicator().apply(
                        candidate=candidate,
                        patch=f"```diff\n{VALID_PATCH}```\n",
                        mutable_paths=("organisms/",),
                        candidate_id="fenced",
                    )


if __name__ == "__main__":
    unittest.main()
