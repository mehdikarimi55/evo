"""Public evidence attestations and independently signed human reviews."""

from __future__ import annotations

from base64 import b64decode, b64encode
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from stat import S_IMODE
from typing import Any, Iterable
import json
import os
import re
import secrets

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from evo.evidence_control import EvidenceControl, EvidenceControlError


TRUST_SCHEMA_VERSION = 1
IDENTIFIER = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


class TrustAuthorityError(ValueError):
    """A fail-closed trust, identity, policy, or authorization error."""


class Ed25519Identity:
    """A file-backed Ed25519 identity with a non-exporting public interface."""

    def __init__(self, *, private_key_path: Path) -> None:
        self.private_key_path = private_key_path

    def initialize(self) -> dict[str, str]:
        private_key = self._private_key()
        public_key = _public_bytes(private_key.public_key())
        return {
            "algorithm": "Ed25519",
            "public_key": b64encode(public_key).decode("ascii"),
            "fingerprint": _fingerprint(public_key),
        }

    def sign(self, payload: dict[str, object]) -> str:
        return b64encode(self._private_key().sign(_canonical(payload))).decode(
            "ascii"
        )

    def verify(self, payload: dict[str, object], signature: object) -> bool:
        if not isinstance(signature, str):
            return False
        public_key = self.initialize()["public_key"]
        try:
            Ed25519PublicKey.from_public_bytes(
                _decode_public_key(public_key)
            ).verify(b64decode(signature, validate=True), _canonical(payload))
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True

    def _private_key(self) -> Ed25519PrivateKey:
        if not self.private_key_path.exists():
            self.private_key_path.parent.mkdir(parents=True, exist_ok=True)
            raw = Ed25519PrivateKey.generate().private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            try:
                descriptor = os.open(
                    self.private_key_path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
            except FileExistsError:
                pass
            else:
                try:
                    os.write(descriptor, raw)
                finally:
                    os.close(descriptor)
        try:
            raw = self.private_key_path.read_bytes()
        except OSError as exc:
            raise TrustAuthorityError("Ed25519 private key is unavailable.") from exc
        if len(raw) != 32:
            raise TrustAuthorityError("Ed25519 private key is invalid.")
        if S_IMODE(self.private_key_path.stat().st_mode) & 0o077:
            raise TrustAuthorityError("Ed25519 private key permissions are insecure.")
        return Ed25519PrivateKey.from_private_bytes(raw)


def create_reviewer_identity(
    *, reviewer_id: str, private_key_path: Path, public_key_path: Path
) -> dict[str, str]:
    """Create an external reviewer keypair without returning private material."""

    _validate_identifier(reviewer_id, "Reviewer ID")
    if private_key_path.exists() or public_key_path.exists():
        raise TrustAuthorityError("Reviewer key output already exists.")
    identity = Ed25519Identity(private_key_path=private_key_path)
    public = identity.initialize()
    try:
        _atomic_text(public_key_path, public["public_key"] + "\n", mode=0o644)
    except Exception:
        private_key_path.unlink(missing_ok=True)
        raise
    return {"reviewer_id": reviewer_id, "public_key_path": str(public_key_path), **public}


class TrustAuthority:
    """Verify evidence and human identity before manual repository promotion."""

    def __init__(
        self,
        *,
        evidence_control: EvidenceControl,
        authority_identity: Ed25519Identity,
        trust_dir: Path,
    ) -> None:
        self.evidence_control = evidence_control
        self.authority_identity = authority_identity
        self.trust_dir = trust_dir
        self.registry_path = trust_dir / "reviewers.json"
        self.policy_path = trust_dir / "promotion-policy.json"
        self.review_path = trust_dir / "signed-reviews.jsonl"
        self.attestation_dir = trust_dir / "attestations"
        self.authorization_dir = trust_dir / "authorizations"

    def initialize(self) -> dict[str, object]:
        authority = self.authority_identity.initialize()
        self._policy()
        self._registry()
        return {
            "schema_version": TRUST_SCHEMA_VERSION,
            "authority": authority,
            "policy_path": str(self.policy_path),
            "registry_path": str(self.registry_path),
        }

    def register_reviewer(
        self, *, reviewer_id: str, public_key_path: Path, display_name: str = ""
    ) -> dict[str, object]:
        _validate_identifier(reviewer_id, "Reviewer ID")
        clean_name = display_name.strip() or reviewer_id
        if len(clean_name) > 120:
            raise TrustAuthorityError("Reviewer display name is too long.")
        public_key = _read_public_key(public_key_path)
        registry = self._registry()
        reviewers = registry["reviewers"]
        existing = reviewers.get(reviewer_id)
        if isinstance(existing, dict) and existing.get("revoked_at"):
            raise TrustAuthorityError(
                "A revoked reviewer identity cannot be reactivated."
            )
        if existing and existing.get("public_key") != public_key:
            raise TrustAuthorityError(
                "Reviewer ID already belongs to a different public key."
            )
        if any(
            known_id != reviewer_id
            and isinstance(known, dict)
            and known.get("public_key") == public_key
            for known_id, known in reviewers.items()
        ):
            raise TrustAuthorityError(
                "Reviewer public key is already registered to another identity."
            )
        entry = {
            "reviewer_id": reviewer_id,
            "display_name": clean_name,
            "algorithm": "Ed25519",
            "public_key": public_key,
            "fingerprint": _fingerprint(_decode_public_key(public_key)),
            "registered_at": (
                existing.get("registered_at")
                if isinstance(existing, dict)
                else datetime.now(UTC).isoformat()
            ),
            "revoked_at": None,
            "revocation_reason": None,
        }
        reviewers[reviewer_id] = entry
        _atomic_json(self.registry_path, registry)
        return _public_reviewer(entry)

    def revoke_reviewer(self, *, reviewer_id: str, reason: str) -> dict[str, object]:
        _validate_identifier(reviewer_id, "Reviewer ID")
        clean_reason = reason.strip()
        if not clean_reason or len(clean_reason) > 500:
            raise TrustAuthorityError("A bounded revocation reason is required.")
        registry = self._registry()
        entry = registry["reviewers"].get(reviewer_id)
        if not isinstance(entry, dict):
            raise TrustAuthorityError("Reviewer is not registered.")
        entry["revoked_at"] = datetime.now(UTC).isoformat()
        entry["revocation_reason"] = clean_reason
        _atomic_json(self.registry_path, registry)
        return _public_reviewer(entry)

    def attest_latest_bundle(self) -> dict[str, object]:
        status = self.evidence_control.status()
        bundle = status.get("latest_bundle")
        path_value = status.get("latest_bundle_path")
        if not isinstance(bundle, dict) or not bundle.get("verified") or not path_value:
            raise TrustAuthorityError("Create a verified evidence bundle first.")
        bundle_path = Path(str(path_value))
        digest = _file_digest(bundle_path)
        payload = {
            "schema_version": TRUST_SCHEMA_VERSION,
            "attestation_id": f"attestation-{digest[:16]}",
            "bundle_id": str(bundle.get("bundle_id", "")),
            "bundle_sha256": digest,
            "replay_verified": True,
            "epochs_replayed": int(bundle.get("epochs_replayed", 0)),
            "candidate_evidence_count": int(
                bundle.get("candidate_evidence_count", 0)
            ),
            "authority_fingerprint": self.initialize()["authority"]["fingerprint"],
            "attested_at": datetime.now(UTC).isoformat(),
        }
        record = _signed_record(payload, self.authority_identity)
        self.attestation_dir.mkdir(parents=True, exist_ok=True)
        _atomic_json(self.attestation_dir / f"{payload['bundle_id']}.json", record)
        return {**record, "verified": self.verify_attestation(record)}

    def record_review(
        self,
        *,
        reviewer_id: str,
        private_key_path: Path,
        decision: str,
        note: str = "",
    ) -> dict[str, object]:
        _validate_identifier(reviewer_id, "Reviewer ID")
        clean_decision = decision.strip().lower()
        if clean_decision not in {"approve", "reject"}:
            raise TrustAuthorityError("Decision must be approve or reject.")
        if len(note) > 2_000:
            raise TrustAuthorityError("Review note is too long.")
        reviewer = self._active_reviewer(reviewer_id)
        attestation = self._latest_attestation()
        if not attestation or not self._attestation_is_current(attestation):
            raise TrustAuthorityError("A valid public evidence attestation is required.")
        identity = Ed25519Identity(private_key_path=private_key_path)
        identity_public = identity.initialize()["public_key"]
        if identity_public != reviewer["public_key"]:
            raise TrustAuthorityError("Reviewer private key does not match the registry.")
        payload = {
            "schema_version": TRUST_SCHEMA_VERSION,
            "review_id": f"review-{secrets.token_hex(8)}",
            "attestation_id": attestation["attestation_id"],
            "bundle_id": attestation["bundle_id"],
            "bundle_sha256": attestation["bundle_sha256"],
            "reviewer_id": reviewer_id,
            "reviewer_fingerprint": reviewer["fingerprint"],
            "decision": clean_decision,
            "note": note.strip(),
            "reviewed_at": datetime.now(UTC).isoformat(),
        }
        record = _signed_record(payload, identity)
        _append_jsonl(self.review_path, record)
        return {**record, "verified": self.verify_review(record)}

    def authorize_latest(self) -> dict[str, object]:
        evaluation = self.evaluate_policy()
        if not evaluation["satisfied"]:
            reasons = "; ".join(evaluation["reasons"])
            raise TrustAuthorityError(f"Promotion policy is not satisfied: {reasons}")
        attestation = self._latest_attestation()
        assert attestation is not None
        policy = self._policy()
        payload = {
            "schema_version": TRUST_SCHEMA_VERSION,
            "authorization_id": f"authorization-{secrets.token_hex(8)}",
            "bundle_id": attestation["bundle_id"],
            "bundle_sha256": attestation["bundle_sha256"],
            "attestation_id": attestation["attestation_id"],
            "policy_sha256": sha256(_canonical(policy)).hexdigest(),
            "qualifying_review_ids": evaluation["qualifying_review_ids"],
            "scope": "manual_repository_promotion_only",
            "repository_mutation_performed": False,
            "push_performed": False,
            "deployment_authorized": False,
            "authorized_at": datetime.now(UTC).isoformat(),
            "authority_fingerprint": self.initialize()["authority"]["fingerprint"],
        }
        record = _signed_record(payload, self.authority_identity)
        self.authorization_dir.mkdir(parents=True, exist_ok=True)
        path = self.authorization_dir / f"{payload['authorization_id']}.json"
        _atomic_json(path, record)
        return {**record, "verified": self.verify_authorization(record), "path": str(path)}

    def evaluate_policy(self) -> dict[str, object]:
        policy = self._policy()
        attestation = self._latest_attestation()
        reasons: list[str] = []
        if not attestation or not self._attestation_is_current(attestation):
            reasons.append("valid public attestation missing")
        qualifying: list[str] = []
        seen_reviewers: set[str] = set()
        if attestation:
            for review in reversed(list(_read_jsonl(self.review_path))):
                reviewer_id = str(review.get("reviewer_id", ""))
                if reviewer_id in seen_reviewers:
                    continue
                if review.get("attestation_id") != attestation.get("attestation_id"):
                    continue
                if (
                    review.get("bundle_id") != attestation.get("bundle_id")
                    or review.get("bundle_sha256")
                    != attestation.get("bundle_sha256")
                ):
                    continue
                seen_reviewers.add(reviewer_id)
                if review.get("decision") != "approve":
                    continue
                if self.verify_review(review):
                    qualifying.append(str(review.get("review_id", "")))
        required = int(policy["minimum_independent_approvals"])
        if len(qualifying) < required:
            reasons.append(f"requires {required} trusted approval(s)")
        return {
            "satisfied": not reasons,
            "reasons": reasons,
            "minimum_independent_approvals": required,
            "qualifying_review_ids": qualifying,
            "deployment_authorized": False,
        }

    def verify_attestation(self, record: dict[str, object]) -> bool:
        return self._verify_authority_record(record, expected_kind="attestation_id")

    def verify_authorization(self, record: dict[str, object]) -> bool:
        return self._verify_authority_record(record, expected_kind="authorization_id")

    def verify_review(self, record: dict[str, object]) -> bool:
        reviewer_id = str(record.get("reviewer_id", ""))
        try:
            reviewer = self._active_reviewer(reviewer_id)
        except TrustAuthorityError:
            return False
        return _verify_signed_record(record, str(reviewer["public_key"]))

    def status(self) -> dict[str, object]:
        initialized = self.initialize()
        registry = self._registry()
        reviewers = list(registry["reviewers"].values())
        attestation = self._latest_attestation()
        latest_review = next(reversed(list(_read_jsonl(self.review_path))), None)
        latest_authorization = self._latest_json(self.authorization_dir)
        policy = self.evaluate_policy()
        return {
            **initialized,
            "trusted_reviewer_count": sum(
                1 for reviewer in reviewers if not reviewer.get("revoked_at")
            ),
            "revoked_reviewer_count": sum(
                1 for reviewer in reviewers if reviewer.get("revoked_at")
            ),
            "latest_attestation": _with_verification(
                attestation, self.verify_attestation
            ),
            "latest_review": _with_verification(latest_review, self.verify_review),
            "policy": policy,
            "latest_authorization": _with_verification(
                latest_authorization, self.verify_authorization
            ),
            "authorization_current": bool(self.current_authorization()),
            "repository_mutation_performed": False,
            "deployment_authorized": False,
        }

    def current_authorization(self) -> dict[str, Any] | None:
        """Return the latest authorization only while every prerequisite holds."""

        authorization = self._latest_json(self.authorization_dir)
        attestation = self._latest_attestation()
        if (
            not authorization
            or not attestation
            or not self.verify_authorization(authorization)
            or not self._attestation_is_current(attestation)
            or not self.evaluate_policy()["satisfied"]
            or authorization.get("bundle_id") != attestation.get("bundle_id")
            or authorization.get("bundle_sha256")
            != attestation.get("bundle_sha256")
            or authorization.get("attestation_id")
            != attestation.get("attestation_id")
        ):
            return None
        return authorization

    def _verify_authority_record(
        self, record: dict[str, object], *, expected_kind: str
    ) -> bool:
        if expected_kind not in record:
            return False
        public_key = self.authority_identity.initialize()["public_key"]
        return _verify_signed_record(record, public_key)

    def _attestation_is_current(self, record: dict[str, object]) -> bool:
        if not self.verify_attestation(record):
            return False
        status = self.evidence_control.status()
        bundle = status.get("latest_bundle")
        path_value = status.get("latest_bundle_path")
        if (
            not isinstance(bundle, dict)
            or not bundle.get("verified")
            or not path_value
            or record.get("bundle_id") != bundle.get("bundle_id")
        ):
            return False
        try:
            return record.get("bundle_sha256") == _file_digest(Path(str(path_value)))
        except TrustAuthorityError:
            return False

    def _active_reviewer(self, reviewer_id: str) -> dict[str, object]:
        entry = self._registry()["reviewers"].get(reviewer_id)
        if not isinstance(entry, dict):
            raise TrustAuthorityError("Reviewer is not registered.")
        if entry.get("revoked_at"):
            raise TrustAuthorityError("Reviewer identity is revoked.")
        return entry

    def _latest_attestation(self) -> dict[str, Any] | None:
        status = self.evidence_control.status()
        bundle = status.get("latest_bundle")
        if not isinstance(bundle, dict):
            return None
        path = self.attestation_dir / f"{bundle.get('bundle_id')}.json"
        return _read_json(path) if path.exists() else None

    def _latest_json(self, directory: Path) -> dict[str, Any] | None:
        if not directory.exists():
            return None
        path = max(directory.glob("*.json"), key=lambda item: item.stat().st_mtime_ns, default=None)
        return _read_json(path) if path else None

    def _registry(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            value = {"schema_version": TRUST_SCHEMA_VERSION, "reviewers": {}}
            _atomic_json(self.registry_path, value)
            return value
        value = _read_json(self.registry_path)
        if value.get("schema_version") != TRUST_SCHEMA_VERSION or not isinstance(
            value.get("reviewers"), dict
        ):
            raise TrustAuthorityError("Reviewer registry is invalid.")
        return value

    def _policy(self) -> dict[str, Any]:
        if not self.policy_path.exists():
            value = {
                "schema_version": TRUST_SCHEMA_VERSION,
                "minimum_independent_approvals": 1,
                "require_public_attestation": True,
                "deny_revoked_reviewers": True,
                "authorization_scope": "manual_repository_promotion_only",
                "deployment_authorized": False,
            }
            _atomic_json(self.policy_path, value)
            return value
        value = _read_json(self.policy_path)
        try:
            required = int(value["minimum_independent_approvals"])
        except (KeyError, TypeError, ValueError) as exc:
            raise TrustAuthorityError("Promotion policy is invalid.") from exc
        if (
            value.get("schema_version") != TRUST_SCHEMA_VERSION
            or not 1 <= required <= 5
            or value.get("require_public_attestation") is not True
            or value.get("deny_revoked_reviewers") is not True
            or value.get("authorization_scope")
            != "manual_repository_promotion_only"
            or value.get("deployment_authorized") is not False
        ):
            raise TrustAuthorityError("Promotion policy weakens immutable safeguards.")
        return value


def _signed_record(
    payload: dict[str, object], identity: Ed25519Identity
) -> dict[str, object]:
    return {
        **payload,
        "signature_algorithm": "Ed25519",
        "signature": identity.sign(payload),
    }


def _verify_signed_record(record: dict[str, object], public_key: str) -> bool:
    payload = dict(record)
    signature = payload.pop("signature", None)
    algorithm = payload.pop("signature_algorithm", None)
    if algorithm != "Ed25519" or not isinstance(signature, str):
        return False
    try:
        Ed25519PublicKey.from_public_bytes(_decode_public_key(public_key)).verify(
            b64decode(signature, validate=True), _canonical(payload)
        )
    except (InvalidSignature, ValueError, TypeError):
        return False
    return True


def _with_verification(
    value: dict[str, Any] | None, verifier: Any
) -> dict[str, Any] | None:
    return {**value, "verified": verifier(value)} if value else None


def _public_reviewer(entry: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in entry.items() if key != "public_key"}


def _validate_identifier(value: str, label: str) -> None:
    if value != value.strip() or not IDENTIFIER.fullmatch(value):
        raise TrustAuthorityError(f"{label} is invalid.")


def _read_public_key(path: Path) -> str:
    try:
        encoded = path.read_text(encoding="ascii").strip()
    except OSError as exc:
        raise TrustAuthorityError("Reviewer public key is unavailable.") from exc
    _decode_public_key(encoded)
    return encoded


def _decode_public_key(encoded: str) -> bytes:
    try:
        raw = b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise TrustAuthorityError("Ed25519 public key is invalid.") from exc
    if len(raw) != 32:
        raise TrustAuthorityError("Ed25519 public key is invalid.")
    return raw


def _public_bytes(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _fingerprint(public_key: bytes) -> str:
    return f"SHA256:{b64encode(sha256(public_key).digest()).decode('ascii').rstrip('=')}"


def _file_digest(path: Path) -> str:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise TrustAuthorityError("Evidence bundle is unavailable.") from exc


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    _atomic_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        mode=0o600,
    )


def _atomic_text(path: Path, value: str, *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        try:
            os.write(descriptor, value.encode("utf-8"))
        finally:
            os.close(descriptor)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrustAuthorityError("Trust record is unreadable.") from exc
    if not isinstance(value, dict):
        raise TrustAuthorityError("Trust record is invalid.")
    return value


def _read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists():
        return ()
    entries = []
    try:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise TrustAuthorityError("Signed review ledger is invalid.")
                    entries.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise TrustAuthorityError("Signed review ledger is unreadable.") from exc
    return entries
