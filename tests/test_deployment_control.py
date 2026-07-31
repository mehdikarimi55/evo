from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import json
import unittest

from evo.candidate_lifecycle import CandidateLifecycle
from evo.deployment_control import (
    DeploymentControlError,
    DeploymentHandoff,
    create_operator_identity,
    create_operator_receipt,
)
from evo.evidence_control import EvidenceControl, EvidenceSigner, ReplayService
from evo.petri import PetriDish
from evo.release_control import CandidateArtifactStore, PromotionController
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
    if result.returncode:
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


class DeploymentControlTests(unittest.TestCase):
    def _system(self, root: Path):
        repository = root / "repository"
        (repository / "organisms").mkdir(parents=True)
        (repository / "organisms/prompt.md").write_text("baseline\n")
        git(repository, "init")
        git(repository, "config", "user.name", "EVO Tests")
        git(repository, "config", "user.email", "evo@example.invalid")
        git(repository, "add", ".")
        git(repository, "commit", "-m", "baseline")
        authority = Ed25519Identity(
            private_key_path=root / "trust" / "authority.key"
        )
        artifacts = CandidateArtifactStore(root=root / "artifacts", identity=authority)
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
        evidence_control = EvidenceControl(
            replay=ReplayService(
                petri_dish=PetriDish(
                    state_path=root / "petri.json", initial_population=3, capacity=8
                )
            ),
            signer=EvidenceSigner(key_path=root / "hmac.key"),
            bundle_dir=root / "bundles",
            candidate_evidence_path=candidate_ledger,
            approval_path=root / "local-approvals.jsonl",
        )
        trust = TrustAuthority(
            evidence_control=evidence_control,
            authority_identity=authority,
            trust_dir=root / "trust",
        )
        evidence_control.create_bundle()
        trust.attest_latest_bundle()
        reviewer_private = root / "reviewer/reviewer.key"
        reviewer_public = root / "reviewer/reviewer.pub"
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
        promotion = PromotionController(
            repository=repository,
            artifacts=artifacts,
            trust=trust,
            identity=authority,
            ledger_path=root / "promotion-ledger.jsonl",
        )
        promoted = promotion.promote(
            artifact_id=str(evidence.artifact_id),
            confirmation=f"APPLY-{evidence.artifact_id}",
        )
        git(repository, "add", ".")
        git(repository, "commit", "-m", "promote verified candidate")
        handoff = DeploymentHandoff(
            repository=repository,
            promotion=promotion,
            artifacts=artifacts,
            identity=authority,
            root=root / "deployment",
        )
        private_key = root / "operator/operator.key"
        public_key = root / "operator/operator.pub"
        create_operator_identity(
            operator_id="operator-1",
            private_key_path=private_key,
            public_key_path=public_key,
        )
        handoff.register_operator(
            operator_id="operator-1", public_key_path=public_key
        )
        return handoff, private_key, promoted

    def _receipt(
        self,
        root: Path,
        handoff: DeploymentHandoff,
        private_key: Path,
        intent: dict,
        status: str,
    ) -> dict:
        output = root / f"external/{intent['intent_id']}-{status}.json"
        receipt = create_operator_receipt(
            intent_path=Path(str(intent["path"])),
            authority_public_key_path=handoff.authority_public_key_path,
            operator_id="operator-1",
            private_key_path=private_key,
            status=status,
            output_path=output,
            deployment_ref=f"deployment/{status}",
        )
        return handoff.import_receipt(receipt_path=output)

    def _intent(self, handoff: DeploymentHandoff, release_id: str, action: str):
        return handoff.create_intent(
            action=action,
            release_id=release_id,
            confirmation=f"{action.upper()}-{release_id}",
        )

    def test_full_signed_stage_health_promote_and_rollback_flow(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, private_key, _ = self._system(root)
            release = handoff.prepare_release()
            self.assertTrue(release["verified"])
            self.assertFalse(release["network_request_performed"])
            release_id = str(release["release_id"])

            for action, receipt_status, expected_phase in (
                ("stage", "staged", "staged"),
                ("health", "healthy", "healthy"),
                ("promote", "promoted", "promoted"),
                ("rollback", "rolled_back", "rolled_back"),
            ):
                intent = self._intent(handoff, release_id, action)
                self.assertTrue(intent["verified"])
                self.assertFalse(intent["network_request_performed"])
                receipt = self._receipt(
                    root, handoff, private_key, intent, receipt_status
                )
                self.assertTrue(receipt["verified"])
                self.assertEqual(handoff.status()["phase"], expected_phase)

            status = handoff.status()
            self.assertFalse(status["cloud_credentials_held"])
            self.assertFalse(status["deployment_performed_by_evo"])
            self.assertTrue(status["external_execution_required"])

    def test_latest_unhealthy_receipt_blocks_production_until_recovery(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, private_key, _ = self._system(root)
            release_id = str(handoff.prepare_release()["release_id"])
            stage = self._intent(handoff, release_id, "stage")
            self._receipt(root, handoff, private_key, stage, "staged")
            health = self._intent(handoff, release_id, "health")
            self._receipt(root, handoff, private_key, health, "unhealthy")
            self.assertEqual(handoff.status()["phase"], "unhealthy")
            with self.assertRaisesRegex(DeploymentControlError, "healthy receipt"):
                self._intent(handoff, release_id, "promote")

            recovered = self._intent(handoff, release_id, "health")
            self._receipt(root, handoff, private_key, recovered, "healthy")
            self.assertEqual(handoff.status()["phase"], "healthy")
            self.assertTrue(self._intent(handoff, release_id, "promote")["verified"])

    def test_receipts_fail_closed_after_tampering_or_operator_revocation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, private_key, _ = self._system(root)
            release_id = str(handoff.prepare_release()["release_id"])
            intent = self._intent(handoff, release_id, "stage")
            output = root / "external/stage.json"
            receipt = create_operator_receipt(
                intent_path=Path(str(intent["path"])),
                authority_public_key_path=handoff.authority_public_key_path,
                operator_id="operator-1",
                private_key_path=private_key,
                status="staged",
                output_path=output,
                deployment_ref="deployment/staging-1",
            )
            tampered = dict(receipt)
            tampered["deployment_ref"] = "deployment/forged"
            self.assertFalse(handoff.verify_receipt(tampered))
            imported = handoff.import_receipt(receipt_path=output)
            self.assertTrue(imported["verified"])
            handoff.revoke_operator(operator_id="operator-1", reason="rotated")
            self.assertFalse(handoff.verify_receipt(receipt))
            self.assertEqual(handoff.status()["phase"], "ready_to_stage")
            self.assertTrue(self._intent(handoff, release_id, "stage")["verified"])

    def test_release_capsule_refuses_unrelated_commit_content(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, _, _ = self._system(root)
            (handoff.repository / "README.md").write_text("unrelated\n")
            git(handoff.repository, "add", ".")
            git(handoff.repository, "commit", "--amend", "--no-edit")
            with self.assertRaisesRegex(DeploymentControlError, "changed paths"):
                handoff.prepare_release()

    def test_success_receipt_requires_external_deployment_reference(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, private_key, _ = self._system(root)
            release_id = str(handoff.prepare_release()["release_id"])
            intent = self._intent(handoff, release_id, "stage")
            with self.assertRaisesRegex(DeploymentControlError, "reference"):
                create_operator_receipt(
                    intent_path=Path(str(intent["path"])),
                    authority_public_key_path=handoff.authority_public_key_path,
                    operator_id="operator-1",
                    private_key_path=private_key,
                    status="staged",
                    output_path=root / "receipt.json",
                )

    def test_operator_refuses_intent_without_valid_evo_signature(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            handoff, private_key, _ = self._system(root)
            release_id = str(handoff.prepare_release()["release_id"])
            intent = self._intent(handoff, release_id, "stage")
            tampered_path = root / "tampered-intent.json"
            tampered = dict(intent)
            tampered["commit"] = "0" * 40
            tampered_path.write_text(json.dumps(tampered))
            with self.assertRaisesRegex(DeploymentControlError, "signature"):
                create_operator_receipt(
                    intent_path=tampered_path,
                    authority_public_key_path=handoff.authority_public_key_path,
                    operator_id="operator-1",
                    private_key_path=private_key,
                    status="staged",
                    output_path=root / "receipt.json",
                    deployment_ref="deployment/staging-1",
                )


if __name__ == "__main__":
    unittest.main()
