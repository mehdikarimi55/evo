from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from evo.evidence_control import (
    EvidenceControl,
    EvidenceControlError,
    EvidenceSigner,
    ReplayService,
)
from evo.petri import PetriDish


def candidate(index: int, *, status: str = "eligible") -> dict[str, object]:
    return {
        "candidate_id": f"candidate-{index}",
        "status": status,
        "score": {
            "schema_validity": 1.0,
            "policy_compliance": 1.0,
            "rationale_quality": 1.0,
        },
        "proposal": {
            "target_path": "organisms/memory.json",
            "summary": f"Bounded adaptation {index}",
            "rationale": "Evidence guides inherited behavior.",
            "expected_benefit": "Improved adaptation.",
            "risk": "Bounded state growth.",
        },
        "rejection_reason": None if status == "eligible" else "rejected",
    }


class EvidenceControlTests(unittest.TestCase):
    def _dish(self, root: Path, *, epochs: int = 3) -> PetriDish:
        dish = PetriDish(
            state_path=root / "petri.json",
            initial_population=4,
            capacity=8,
        )
        for index in range(epochs):
            selected = dish.select_for_evaluation()
            dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(
                    index,
                    status="rejected" if index == 1 else "eligible",
                ),
            )
        return dish

    def _control(self, root: Path, dish: PetriDish) -> EvidenceControl:
        return EvidenceControl(
            replay=ReplayService(petri_dish=dish),
            signer=EvidenceSigner(key_path=root / "signing.key"),
            bundle_dir=root / "bundles",
            candidate_evidence_path=root / "candidate-evidence.jsonl",
            approval_path=root / "approvals.jsonl",
        )

    def test_replay_manifest_reproduces_timestamp_free_state(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            replay = ReplayService(petri_dish=self._dish(root))
            first = replay.export_manifest()
            second = replay.export_manifest()
            result = replay.verify_manifest(first)
            self.assertEqual(first, second)
            self.assertTrue(result["verified"])
            self.assertEqual(result["epochs_replayed"], 3)

    def test_replay_detects_tampered_outcome(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            replay = ReplayService(petri_dish=self._dish(root))
            manifest = replay.export_manifest()
            tampered = deepcopy(manifest)
            tampered["outcomes"][0]["candidate"]["proposal"]["summary"] = (
                "tampered adaptation"
            )
            self.assertFalse(replay.verify_manifest(tampered)["verified"])

    def test_replay_rejects_divergent_selection_history(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            replay = ReplayService(petri_dish=self._dish(root))
            manifest = replay.export_manifest()
            recorded = manifest["outcomes"][0]["organism_id"]
            manifest["outcomes"][0]["organism_id"] = (
                "gnome-0001" if recorded != "gnome-0001" else "gnome-0002"
            )
            with self.assertRaisesRegex(EvidenceControlError, "selection diverged"):
                replay.verify_manifest(manifest)

    def test_bundle_signature_and_replay_are_tamper_evident(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            control = self._control(root, self._dish(root))
            result = control.create_bundle()
            bundle_path = Path(result["path"])
            self.assertTrue(result["verified"])
            self.assertEqual(oct((root / "signing.key").stat().st_mode & 0o777), "0o600")

            bundle = json.loads(bundle_path.read_text())
            bundle["candidate_evidence"].append({"tampered": True})
            bundle_path.write_text(json.dumps(bundle))
            verification = control.verify_bundle(bundle_path)
            self.assertFalse(verification["verified"])
            self.assertFalse(verification["signature_valid"])

    def test_malformed_replay_is_reported_unverified_without_breaking_status(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            control = self._control(root, self._dish(root, epochs=1))
            result = control.create_bundle()
            bundle_path = Path(result["path"])
            bundle = json.loads(bundle_path.read_text())
            bundle["replay_manifest"]["outcomes"][0]["organism_id"] = "missing"
            bundle_path.write_text(json.dumps(bundle))

            status = control.status()
            self.assertFalse(status["latest_bundle"]["verified"])
            self.assertFalse(status["latest_bundle"]["replay_verified"])

    def test_human_approval_requires_verified_bundle_and_never_deploys(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            control = self._control(root, self._dish(root, epochs=1))
            bundle = control.create_bundle()
            approval = control.approve(
                bundle_path=Path(bundle["path"]),
                approver="Local reviewer",
                decision="approve",
                note="Reviewed replay and sandbox evidence.",
            )
            self.assertEqual(approval["decision"], "approve")
            self.assertFalse(approval["deploy_authorized"])
            self.assertEqual(approval["authority"], "local_human_assertion_only")
            status = control.status()
            self.assertTrue(status["approval_signature_valid"])
            self.assertFalse(status["deployment_authorized"])

            path = Path(bundle["path"])
            payload = json.loads(path.read_text())
            payload["signature"] = "0" * 64
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(EvidenceControlError, "verified bundle"):
                control.approve(
                    bundle_path=path,
                    approver="Reviewer",
                    decision="approve",
                )

    def test_prior_approval_does_not_approve_a_new_bundle(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            dish = self._dish(root, epochs=1)
            control = self._control(root, dish)
            first = control.create_bundle()
            control.approve(
                bundle_path=Path(first["path"]),
                approver="Local reviewer",
                decision="approve",
            )
            selected = dish.select_for_evaluation()
            dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(2),
            )
            second = control.create_bundle()
            self.assertNotEqual(first["bundle_id"], second["bundle_id"])
            status = control.status()
            self.assertIsNone(status["latest_approval"])
            self.assertFalse(status["approval_signature_valid"])

    def test_rejects_unbounded_or_invalid_approval_fields(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            control = self._control(root, self._dish(root, epochs=0))
            bundle = control.create_bundle()
            with self.assertRaisesRegex(EvidenceControlError, "Approver"):
                control.approve(
                    bundle_path=Path(bundle["path"]),
                    approver="",
                    decision="approve",
                )
            with self.assertRaisesRegex(EvidenceControlError, "approve or reject"):
                control.approve(
                    bundle_path=Path(bundle["path"]),
                    approver="Reviewer",
                    decision="deploy",
                )

    def test_signer_rejects_group_readable_key(self):
        with TemporaryDirectory() as directory:
            key_path = Path(directory) / "signing.key"
            key_path.write_bytes(b"x" * 32)
            key_path.chmod(0o640)
            signer = EvidenceSigner(key_path=key_path)
            with self.assertRaisesRegex(EvidenceControlError, "permissions"):
                signer.sign({"evidence": "bounded"})


if __name__ == "__main__":
    unittest.main()
