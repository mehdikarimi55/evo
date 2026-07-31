from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import json
import unittest

from evo.candidate_lifecycle import CandidateLifecycle
from evo.evidence_control import EvidenceControl, EvidenceSigner, ReplayService
from evo.petri import PetriDish
from evo.release_control import (
    CandidateArtifactStore,
    PromotionController,
    ReleaseControlError,
)
from evo.sandbox import SandboxResult
from evo.trust_authority import (
    Ed25519Identity,
    TrustAuthority,
    create_reviewer_identity,
)


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


class PassingSandbox:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    def run(self, command):
        return SandboxResult(
            command=tuple(command),
            exit_code=0,
            stdout="pass\n",
            stderr="",
            duration_seconds=0.01,
        )


class ReleaseControlTests(unittest.TestCase):
    def _repository(self, root: Path) -> Path:
        repository = root / "repository"
        (repository / "organisms").mkdir(parents=True)
        (repository / "organisms/prompt.md").write_text("baseline\n")
        git(repository, "init")
        git(repository, "config", "user.name", "EVO Tests")
        git(repository, "config", "user.email", "evo@example.invalid")
        git(repository, "add", ".")
        git(repository, "commit", "-m", "baseline")
        return repository

    def _system(self, root: Path):
        repository = self._repository(root)
        authority_identity = Ed25519Identity(
            private_key_path=root / "trust" / "authority.key"
        )
        artifacts = CandidateArtifactStore(
            root=root / "artifacts", identity=authority_identity
        )
        candidate_ledger = root / "candidate-evidence.jsonl"
        evidence = CandidateLifecycle(
            repository=repository,
            evidence_path=candidate_ledger,
            sandbox_factory=lambda workspace: PassingSandbox(workspace),
            artifact_store=artifacts,
        ).evaluate(
            candidate_id="candidate-1",
            team_ids=("gnome-1",),
            patch=PATCH,
            mutable_paths=("organisms/",),
            command=("python", "-m", "unittest"),
        )
        dish = PetriDish(
            state_path=root / "petri.json", initial_population=3, capacity=8
        )
        evidence_control = EvidenceControl(
            replay=ReplayService(petri_dish=dish),
            signer=EvidenceSigner(key_path=root / "hmac.key"),
            bundle_dir=root / "bundles",
            candidate_evidence_path=candidate_ledger,
            approval_path=root / "local-approvals.jsonl",
        )
        trust = TrustAuthority(
            evidence_control=evidence_control,
            authority_identity=authority_identity,
            trust_dir=root / "trust",
        )
        evidence_control.create_bundle()
        trust.attest_latest_bundle()
        reviewer_private = root / "reviewer" / "reviewer.key"
        reviewer_public = root / "reviewer" / "reviewer.pub"
        create_reviewer_identity(
            reviewer_id="reviewer-1",
            private_key_path=reviewer_private,
            public_key_path=reviewer_public,
        )
        trust.register_reviewer(
            reviewer_id="reviewer-1", public_key_path=reviewer_public
        )
        trust.record_review(
            reviewer_id="reviewer-1",
            private_key_path=reviewer_private,
            decision="approve",
        )
        trust.authorize_latest()
        controller = PromotionController(
            repository=repository,
            artifacts=artifacts,
            trust=trust,
            identity=authority_identity,
            ledger_path=root / "promotion-ledger.jsonl",
        )
        return repository, evidence, artifacts, trust, controller

    def test_verified_candidate_is_sealed_promoted_and_rolled_back(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repository, evidence, artifacts, _, controller = self._system(root)
            self.assertTrue(evidence.promotion_eligible)
            self.assertIsNotNone(evidence.artifact_id)
            artifact = artifacts.verify(str(evidence.artifact_id))
            self.assertTrue(artifact["verified"])
            self.assertEqual(
                Path(str(artifact["patch_path"])).stat().st_mode & 0o777,
                0o600,
            )

            promotion = controller.promote(
                artifact_id=str(evidence.artifact_id),
                confirmation=f"APPLY-{evidence.artifact_id}",
            )
            self.assertEqual(
                (repository / "organisms/prompt.md").read_text(), "improved\n"
            )
            self.assertTrue(promotion["verified"])
            self.assertFalse(promotion["commit_performed"])
            self.assertFalse(promotion["push_performed"])
            self.assertFalse(promotion["deployment_authorized"])
            self.assertEqual(controller.ledger_path.stat().st_mode & 0o777, 0o600)

            rollback = controller.rollback(
                promotion_id=str(promotion["record_id"]),
                confirmation=f"ROLLBACK-{promotion['record_id']}",
            )
            self.assertTrue(rollback["restored_clean_state"])
            self.assertEqual(
                (repository / "organisms/prompt.md").read_text(), "baseline\n"
            )
            self.assertEqual(git(repository, "status", "--porcelain"), "")

    def test_authorization_is_single_use_even_after_rollback(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, evidence, _, _, controller = self._system(root)
            promotion = controller.promote(
                artifact_id=str(evidence.artifact_id),
                confirmation=f"APPLY-{evidence.artifact_id}",
            )
            controller.rollback(
                promotion_id=str(promotion["record_id"]),
                confirmation=f"ROLLBACK-{promotion['record_id']}",
            )
            with self.assertRaisesRegex(ReleaseControlError, "already consumed"):
                controller.promote(
                    artifact_id=str(evidence.artifact_id),
                    confirmation=f"APPLY-{evidence.artifact_id}",
                )

    def test_rollback_refuses_repository_changes_after_promotion(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repository, evidence, _, _, controller = self._system(root)
            promotion = controller.promote(
                artifact_id=str(evidence.artifact_id),
                confirmation=f"APPLY-{evidence.artifact_id}",
            )
            (repository / "organisms/prompt.md").write_text("user edit\n")
            with self.assertRaisesRegex(ReleaseControlError, "changed after"):
                controller.rollback(
                    promotion_id=str(promotion["record_id"]),
                    confirmation=f"ROLLBACK-{promotion['record_id']}",
                )

    def test_tampered_artifact_and_wrong_confirmation_fail_closed(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, evidence, artifacts, _, controller = self._system(root)
            with self.assertRaisesRegex(ReleaseControlError, "confirmation"):
                controller.promote(
                    artifact_id=str(evidence.artifact_id), confirmation="yes"
                )
            artifact = artifacts.verify(str(evidence.artifact_id))
            Path(str(artifact["patch_path"])).write_text(PATCH + "# tampered\n")
            self.assertFalse(artifacts.verify(str(evidence.artifact_id))["verified"])
            with self.assertRaisesRegex(ReleaseControlError, "not verified"):
                controller.promote(
                    artifact_id=str(evidence.artifact_id),
                    confirmation=f"APPLY-{evidence.artifact_id}",
                )

    def test_insecure_artifact_permissions_fail_verification(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, evidence, artifacts, _, _ = self._system(root)
            artifact = artifacts.verify(str(evidence.artifact_id))
            Path(str(artifact["patch_path"])).chmod(0o640)
            self.assertFalse(artifacts.verify(str(evidence.artifact_id))["verified"])

    def test_bundle_must_cover_exact_artifact_manifest(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, evidence, _, trust, controller = self._system(root)
            bundle_path = Path(
                str(trust.evidence_control.status()["latest_bundle_path"])
            )
            bundle = json.loads(bundle_path.read_text())
            bundle["candidate_evidence"][0]["artifact_manifest_sha256"] = "0" * 64
            bundle_path.write_text(json.dumps(bundle))
            with self.assertRaisesRegex(
                ReleaseControlError, "current independent promotion authorization"
            ):
                controller.promote(
                    artifact_id=str(evidence.artifact_id),
                    confirmation=f"APPLY-{evidence.artifact_id}",
                )


if __name__ == "__main__":
    unittest.main()
