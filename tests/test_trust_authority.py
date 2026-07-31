from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from evo.evidence_control import EvidenceControl, EvidenceSigner, ReplayService
from evo.petri import PetriDish
from evo.trust_authority import (
    Ed25519Identity,
    TrustAuthority,
    TrustAuthorityError,
    create_reviewer_identity,
)


class TrustAuthorityTests(unittest.TestCase):
    def _authority(self, root: Path) -> tuple[TrustAuthority, EvidenceControl]:
        dish = PetriDish(
            state_path=root / "petri.json",
            initial_population=3,
            capacity=8,
        )
        evidence = EvidenceControl(
            replay=ReplayService(petri_dish=dish),
            signer=EvidenceSigner(key_path=root / "hmac.key"),
            bundle_dir=root / "bundles",
            candidate_evidence_path=root / "candidate-evidence.jsonl",
            approval_path=root / "local-approvals.jsonl",
        )
        authority = TrustAuthority(
            evidence_control=evidence,
            authority_identity=Ed25519Identity(
                private_key_path=root / "trust" / "authority.key"
            ),
            trust_dir=root / "trust",
        )
        return authority, evidence

    def _reviewer(self, root: Path, authority: TrustAuthority) -> Path:
        private_key = root / "external" / "reviewer.key"
        public_key = root / "external" / "reviewer.pub"
        created = create_reviewer_identity(
            reviewer_id="reviewer-1",
            private_key_path=private_key,
            public_key_path=public_key,
        )
        self.assertNotIn("private_key", created)
        authority.register_reviewer(
            reviewer_id="reviewer-1",
            public_key_path=public_key,
            display_name="Independent Reviewer",
        )
        return private_key

    def test_authority_and_reviewer_keys_are_ed25519_and_private(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, _ = self._authority(root)
            initialized = authority.initialize()
            self.assertEqual(initialized["authority"]["algorithm"], "Ed25519")
            self.assertTrue(
                initialized["authority"]["fingerprint"].startswith("SHA256:")
            )
            self.assertEqual(
                (root / "trust" / "authority.key").stat().st_mode & 0o777,
                0o600,
            )
            private_key = self._reviewer(root, authority)
            self.assertEqual(private_key.stat().st_mode & 0o777, 0o600)
            self.assertEqual(authority.status()["trusted_reviewer_count"], 1)

    def test_public_attestation_signed_review_and_policy_authorization(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, evidence = self._authority(root)
            evidence.create_bundle()
            attestation = authority.attest_latest_bundle()
            self.assertTrue(attestation["verified"])
            self.assertEqual(attestation["signature_algorithm"], "Ed25519")

            private_key = self._reviewer(root, authority)
            review = authority.record_review(
                reviewer_id="reviewer-1",
                private_key_path=private_key,
                decision="approve",
                note="Replay and candidate evidence independently inspected.",
            )
            self.assertTrue(review["verified"])
            self.assertTrue(authority.evaluate_policy()["satisfied"])

            authorization = authority.authorize_latest()
            self.assertTrue(authorization["verified"])
            self.assertEqual(
                authorization["scope"], "manual_repository_promotion_only"
            )
            self.assertFalse(authorization["repository_mutation_performed"])
            self.assertFalse(authorization["push_performed"])
            self.assertFalse(authorization["deployment_authorized"])
            status = authority.status()
            self.assertTrue(status["latest_authorization"]["verified"])
            self.assertFalse(status["deployment_authorized"])

    def test_tampering_and_revocation_fail_closed(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, evidence = self._authority(root)
            evidence.create_bundle()
            attestation = authority.attest_latest_bundle()
            tampered = deepcopy(attestation)
            tampered.pop("verified")
            tampered["bundle_sha256"] = "0" * 64
            self.assertFalse(authority.verify_attestation(tampered))

            private_key = self._reviewer(root, authority)
            authority.record_review(
                reviewer_id="reviewer-1",
                private_key_path=private_key,
                decision="approve",
            )
            authority.revoke_reviewer(
                reviewer_id="reviewer-1", reason="Reviewer key retired."
            )
            evaluation = authority.evaluate_policy()
            self.assertFalse(evaluation["satisfied"])
            with self.assertRaisesRegex(TrustAuthorityError, "not satisfied"):
                authority.authorize_latest()
            with self.assertRaisesRegex(TrustAuthorityError, "cannot be reactivated"):
                authority.register_reviewer(
                    reviewer_id="reviewer-1",
                    public_key_path=root / "external" / "reviewer.pub",
                )

    def test_policy_binds_attestation_and_review_to_exact_current_bundle(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, evidence = self._authority(root)
            bundle = evidence.create_bundle()
            authority.attest_latest_bundle()
            private_key = self._reviewer(root, authority)
            authority.record_review(
                reviewer_id="reviewer-1",
                private_key_path=private_key,
                decision="approve",
            )
            path = Path(bundle["path"])
            value = json.loads(path.read_text())
            value["candidate_evidence"].append({"tampered": True})
            path.write_text(json.dumps(value))
            self.assertFalse(authority.evaluate_policy()["satisfied"])
            with self.assertRaisesRegex(TrustAuthorityError, "not satisfied"):
                authority.authorize_latest()

    def test_one_public_key_cannot_create_multiple_reviewer_identities(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, _ = self._authority(root)
            self._reviewer(root, authority)
            with self.assertRaisesRegex(TrustAuthorityError, "another identity"):
                authority.register_reviewer(
                    reviewer_id="reviewer-2",
                    public_key_path=root / "external" / "reviewer.pub",
                )

    def test_policy_cannot_enable_deployment_or_disable_revocation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, _ = self._authority(root)
            authority.initialize()
            policy = json.loads(authority.policy_path.read_text())
            policy["deployment_authorized"] = True
            authority.policy_path.write_text(json.dumps(policy))
            with self.assertRaisesRegex(TrustAuthorityError, "weakens"):
                authority.status()

    def test_wrong_reviewer_private_key_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            authority, evidence = self._authority(root)
            evidence.create_bundle()
            authority.attest_latest_bundle()
            self._reviewer(root, authority)
            wrong_private = root / "external" / "wrong.key"
            Ed25519Identity(private_key_path=wrong_private).initialize()
            with self.assertRaisesRegex(TrustAuthorityError, "does not match"):
                authority.record_review(
                    reviewer_id="reviewer-1",
                    private_key_path=wrong_private,
                    decision="approve",
                )


if __name__ == "__main__":
    unittest.main()
