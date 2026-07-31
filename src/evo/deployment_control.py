"""Signed, credential-free handoff to an independent deployment operator."""

from __future__ import annotations

from base64 import b64decode, b64encode
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from stat import S_IMODE
from subprocess import CompletedProcess, TimeoutExpired, run
from typing import Any, Iterable, Mapping
import json
import os
import re
import secrets

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from evo.release_control import (
    CandidateArtifactStore,
    PromotionController,
    ReleaseControlError,
)
from evo.trust_authority import Ed25519Identity


DEPLOYMENT_SCHEMA_VERSION = 1
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
RECEIPT_STATUSES = {
    "stage": {"staged", "failed"},
    "health": {"healthy", "unhealthy", "failed"},
    "promote": {"promoted", "failed"},
    "rollback": {"rolled_back", "failed"},
}


class DeploymentControlError(RuntimeError):
    """A sanitized release handoff, operator, or receipt validation error."""


def create_operator_identity(
    *, operator_id: str, private_key_path: Path, public_key_path: Path
) -> dict[str, str]:
    """Create an operator identity at explicit paths outside EVO state."""

    _validate_id(operator_id, "Operator ID")
    if private_key_path.exists() or public_key_path.exists():
        raise DeploymentControlError("Operator key output already exists.")
    identity = Ed25519Identity(private_key_path=private_key_path)
    metadata = identity.initialize()
    try:
        _atomic_bytes(
            public_key_path,
            (metadata["public_key"] + "\n").encode("ascii"),
            mode=0o644,
        )
    except Exception:
        private_key_path.unlink(missing_ok=True)
        raise
    return {
        "operator_id": operator_id,
        "public_key_path": str(public_key_path),
        **metadata,
    }


def create_operator_receipt(
    *,
    intent_path: Path,
    authority_public_key_path: Path,
    operator_id: str,
    private_key_path: Path,
    status: str,
    output_path: Path,
    deployment_ref: str = "",
    note: str = "",
) -> dict[str, object]:
    """Sign an external execution receipt without contacting EVO."""

    _validate_id(operator_id, "Operator ID")
    intent = _read_json(intent_path, "Deployment intent")
    authority_public_key = _read_public_key(
        authority_public_key_path, label="Authority public key"
    )
    if not _verify_external_intent(intent, authority_public_key):
        raise DeploymentControlError("Deployment intent signature is not trusted.")
    action = str(intent.get("action", ""))
    clean_status = status.strip().lower()
    if clean_status not in RECEIPT_STATUSES.get(action, set()):
        raise DeploymentControlError("Receipt status is invalid for its intent.")
    clean_ref = deployment_ref.strip()
    if len(clean_ref) > 200 or len(note) > 2_000:
        raise DeploymentControlError("Operator receipt metadata is too long.")
    if clean_status != "failed" and not clean_ref:
        raise DeploymentControlError(
            "A deployment reference is required for a successful receipt."
        )
    identity = Ed25519Identity(private_key_path=private_key_path)
    operator = identity.initialize()
    payload = {
        "schema_version": DEPLOYMENT_SCHEMA_VERSION,
        "receipt_id": f"receipt-{secrets.token_hex(8)}",
        "intent_id": str(intent.get("intent_id", "")),
        "intent_sha256": sha256(_canonical(intent)).hexdigest(),
        "release_id": str(intent.get("release_id", "")),
        "action": action,
        "status": clean_status,
        "operator_id": operator_id,
        "operator_fingerprint": operator["fingerprint"],
        "deployment_ref": clean_ref,
        "note": note.strip(),
        "executed_by_external_operator": True,
        "evo_network_request_performed": False,
        "evo_cloud_credentials_used": False,
        "observed_at": datetime.now(UTC).isoformat(),
    }
    record = _sign(payload, identity)
    if output_path.exists():
        raise DeploymentControlError("Operator receipt output already exists.")
    _atomic_json(output_path, record, mode=0o600)
    return record


class DeploymentHandoff:
    """Build releases and verify an external operator's signed state changes."""

    def __init__(
        self,
        *,
        repository: Path,
        promotion: PromotionController,
        artifacts: CandidateArtifactStore,
        identity: Ed25519Identity,
        root: Path,
    ) -> None:
        self.repository = repository.resolve()
        self.promotion = promotion
        self.artifacts = artifacts
        self.identity = identity
        self.root = root
        self.release_dir = root / "releases"
        self.outbox_dir = root / "outbox"
        self.inbox_dir = root / "inbox"
        self.registry_path = root / "operators.json"
        self.authority_public_key_path = root / "authority-ed25519.pub"

    def initialize(self) -> dict[str, object]:
        authority = self.identity.initialize()
        encoded_public_key = str(authority["public_key"])
        if self.authority_public_key_path.exists():
            if _read_public_key(
                self.authority_public_key_path, label="Authority public key"
            ) != encoded_public_key:
                raise DeploymentControlError(
                    "Published deployment authority key does not match."
                )
        else:
            _atomic_bytes(
                self.authority_public_key_path,
                (encoded_public_key + "\n").encode("ascii"),
                mode=0o644,
            )
        self._registry()
        return {
            "schema_version": DEPLOYMENT_SCHEMA_VERSION,
            "authority": authority,
            "registry_path": str(self.registry_path),
            "authority_public_key_path": str(self.authority_public_key_path),
            "release_dir": str(self.release_dir),
            "outbox_dir": str(self.outbox_dir),
            "inbox_dir": str(self.inbox_dir),
            "network_execution_available": False,
            "cloud_credentials_held": False,
        }

    def register_operator(
        self,
        *,
        operator_id: str,
        public_key_path: Path,
        display_name: str = "",
    ) -> dict[str, object]:
        _validate_id(operator_id, "Operator ID")
        clean_name = display_name.strip() or operator_id
        if len(clean_name) > 120:
            raise DeploymentControlError("Operator display name is too long.")
        public_key = _read_public_key(public_key_path)
        registry = self._registry()
        operators = registry["operators"]
        existing = operators.get(operator_id)
        if isinstance(existing, dict) and existing.get("revoked_at"):
            raise DeploymentControlError(
                "A revoked operator identity cannot be reactivated."
            )
        if existing and existing.get("public_key") != public_key:
            raise DeploymentControlError(
                "Operator ID already belongs to a different public key."
            )
        if any(
            known_id != operator_id
            and isinstance(known, dict)
            and known.get("public_key") == public_key
            for known_id, known in operators.items()
        ):
            raise DeploymentControlError(
                "Operator public key is already registered to another identity."
            )
        raw = _decode_public_key(public_key)
        entry = {
            "operator_id": operator_id,
            "display_name": clean_name,
            "algorithm": "Ed25519",
            "public_key": public_key,
            "fingerprint": _fingerprint(raw),
            "registered_at": (
                existing.get("registered_at")
                if isinstance(existing, dict)
                else datetime.now(UTC).isoformat()
            ),
            "revoked_at": None,
            "revocation_reason": None,
        }
        operators[operator_id] = entry
        _atomic_json(self.registry_path, registry, mode=0o600)
        return _public_operator(entry)

    def revoke_operator(self, *, operator_id: str, reason: str) -> dict[str, object]:
        _validate_id(operator_id, "Operator ID")
        clean_reason = reason.strip()
        if not clean_reason or len(clean_reason) > 500:
            raise DeploymentControlError("A bounded revocation reason is required.")
        registry = self._registry()
        entry = registry["operators"].get(operator_id)
        if not isinstance(entry, dict):
            raise DeploymentControlError("Operator is not registered.")
        entry["revoked_at"] = datetime.now(UTC).isoformat()
        entry["revocation_reason"] = clean_reason
        _atomic_json(self.registry_path, registry, mode=0o600)
        return _public_operator(entry)

    def prepare_release(self) -> dict[str, object]:
        self.initialize()
        if not self._repository_is_clean():
            raise DeploymentControlError(
                "Release preparation requires a completely clean repository."
            )
        promotion = self.promotion.latest_active_promotion()
        if not promotion or not self.promotion.verify_record(promotion):
            raise DeploymentControlError(
                "A verified local promotion must be committed first."
            )
        artifact = self.artifacts.verify(str(promotion.get("artifact_id", "")))
        if not artifact["verified"]:
            raise DeploymentControlError("Release candidate artifact is invalid.")
        head = self._git("rev-parse", "HEAD").stdout.strip()
        parents = self._git("rev-list", "--parents", "-n", "1", head).stdout.split()
        base_commit = str(promotion.get("base_commit", ""))
        if len(parents) != 2 or parents[1] != base_commit:
            raise DeploymentControlError(
                "Release commit must be one direct non-merge commit above the tested base."
            )
        changed_paths = self._changed_paths(base_commit, head)
        expected_paths = tuple(sorted(str(item) for item in promotion["changed_paths"]))
        if changed_paths != expected_paths:
            raise DeploymentControlError(
                "Release commit changed paths differ from the promoted artifact."
            )
        if self._workspace_state_digest(changed_paths) != promotion.get(
            "post_state_sha256"
        ):
            raise DeploymentControlError(
                "Release commit content differs from the promoted artifact."
            )
        tree_sha256 = self._git("rev-parse", f"{head}^{{tree}}").stdout.strip()
        promotion_sha256 = sha256(_canonical(promotion)).hexdigest()
        seed = {
            "commit": head,
            "artifact_manifest_sha256": artifact["artifact_manifest_sha256"],
            "promotion_record_sha256": promotion_sha256,
        }
        release_id = f"release-{sha256(_canonical(seed)).hexdigest()[:20]}"
        authority = self.identity.initialize()
        payload = {
            "schema_version": DEPLOYMENT_SCHEMA_VERSION,
            "release_id": release_id,
            "commit": head,
            "tree": tree_sha256,
            "rollback_commit": base_commit,
            "changed_paths": list(changed_paths),
            "artifact_id": artifact["artifact_id"],
            "artifact_manifest_sha256": artifact["artifact_manifest_sha256"],
            "promotion_id": promotion["record_id"],
            "promotion_record_sha256": promotion_sha256,
            "authorization_id": promotion["authorization_id"],
            "bundle_id": promotion["bundle_id"],
            "authority_fingerprint": authority["fingerprint"],
            "execution_authority": "external_operator_only",
            "network_request_performed": False,
            "cloud_credentials_held": False,
            "prepared_at": datetime.now(UTC).isoformat(),
        }
        record = _sign(payload, self.identity)
        self.release_dir.mkdir(parents=True, exist_ok=True)
        path = self.release_dir / f"{release_id}.json"
        if path.exists():
            existing = self.verify_release(path)
            if existing["verified"]:
                return existing
            raise DeploymentControlError("Release capsule ID collision detected.")
        _atomic_json(path, record, mode=0o600)
        return self.verify_release(path)

    def verify_release(self, path: Path) -> dict[str, object]:
        record = _read_json(path, "Release capsule")
        payload = dict(record)
        signature = payload.pop("signature", None)
        algorithm = payload.pop("signature_algorithm", None)
        secure = S_IMODE(path.stat().st_mode) & 0o077 == 0
        verified = bool(
            algorithm == "Ed25519"
            and payload.get("schema_version") == DEPLOYMENT_SCHEMA_VERSION
            and payload.get("execution_authority") == "external_operator_only"
            and payload.get("network_request_performed") is False
            and payload.get("cloud_credentials_held") is False
            and self.identity.verify(payload, signature)
            and secure
        )
        return {**record, "verified": verified, "path": str(path)}

    def create_intent(
        self, *, action: str, release_id: str, confirmation: str
    ) -> dict[str, object]:
        clean_action = action.strip().lower()
        if clean_action not in RECEIPT_STATUSES:
            raise DeploymentControlError("Deployment action is invalid.")
        _validate_id(release_id, "Release ID")
        expected_confirmation = f"{clean_action.upper()}-{release_id}"
        if confirmation != expected_confirmation:
            raise DeploymentControlError("Exact deployment confirmation is required.")
        release = self.verify_release(self.release_dir / f"{release_id}.json")
        if not release["verified"]:
            raise DeploymentControlError("Release capsule is not verified.")
        state = self._release_state(release_id)
        self._authorize_transition(clean_action, state)
        pending = state["pending_actions"]
        if clean_action in pending:
            raise DeploymentControlError("A matching deployment intent is pending.")
        prior_receipts = [
            receipt["receipt_id"] for receipt in state["valid_receipts"]
        ]
        target_environment = {
            "stage": "staging",
            "health": "staging",
            "promote": "production",
            "rollback": "production_or_staging",
        }[clean_action]
        payload = {
            "schema_version": DEPLOYMENT_SCHEMA_VERSION,
            "intent_id": f"intent-{secrets.token_hex(8)}",
            "release_id": release_id,
            "release_sha256": sha256(
                _canonical(
                    {
                        key: value
                        for key, value in release.items()
                        if key not in {"verified", "path"}
                    }
                )
            ).hexdigest(),
            "commit": release["commit"],
            "rollback_commit": release["rollback_commit"],
            "action": clean_action,
            "target_environment": target_environment,
            "prior_receipt_ids": prior_receipts,
            "authority_fingerprint": release["authority_fingerprint"],
            "execution_authority": "external_operator_only",
            "network_request_performed": False,
            "cloud_credentials_forwarded": False,
            "requested_at": datetime.now(UTC).isoformat(),
        }
        record = _sign(payload, self.identity)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        path = self.outbox_dir / f"{payload['intent_id']}.json"
        _atomic_json(path, record, mode=0o600)
        return {**record, "verified": self.verify_intent(record), "path": str(path)}

    def verify_intent(self, record: Mapping[str, object]) -> bool:
        return _verify_external_intent(
            record,
            str(self.identity.initialize()["public_key"]),
        )

    def import_receipt(self, *, receipt_path: Path) -> dict[str, object]:
        receipt = _read_json(receipt_path, "Operator receipt")
        if not self.verify_receipt(receipt):
            raise DeploymentControlError("Operator receipt is not trusted.")
        receipt_id = str(receipt.get("receipt_id", ""))
        _validate_id(receipt_id, "Receipt ID")
        target = self.inbox_dir / f"{receipt_id}.json"
        if target.exists():
            raise DeploymentControlError("Operator receipt was already imported.")
        intent_id = str(receipt.get("intent_id", ""))
        if any(
            existing.get("intent_id") == intent_id
            for existing in self._receipts(include_invalid=True)
        ):
            raise DeploymentControlError("Deployment intent already has a receipt.")
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        _atomic_json(target, receipt, mode=0o600)
        return {**receipt, "verified": True, "path": str(target)}

    def verify_receipt(self, receipt: Mapping[str, object]) -> bool:
        operator_id = str(receipt.get("operator_id", ""))
        try:
            operator = self._active_operator(operator_id)
        except DeploymentControlError:
            return False
        intent_id = str(receipt.get("intent_id", ""))
        if not SAFE_ID.fullmatch(intent_id):
            return False
        intent_path = self.outbox_dir / f"{intent_id}.json"
        if not intent_path.exists():
            return False
        try:
            intent = _read_json(intent_path, "Deployment intent")
        except DeploymentControlError:
            return False
        payload = dict(receipt)
        payload.pop("verified", None)
        payload.pop("path", None)
        signature = payload.pop("signature", None)
        algorithm = payload.pop("signature_algorithm", None)
        action = str(payload.get("action", ""))
        status = str(payload.get("status", ""))
        return bool(
            algorithm == "Ed25519"
            and payload.get("schema_version") == DEPLOYMENT_SCHEMA_VERSION
            and self.verify_intent(intent)
            and payload.get("intent_sha256")
            == sha256(_canonical(intent)).hexdigest()
            and payload.get("release_id") == intent.get("release_id")
            and action == intent.get("action")
            and status in RECEIPT_STATUSES.get(action, set())
            and (
                status == "failed"
                or bool(str(payload.get("deployment_ref", "")).strip())
            )
            and payload.get("executed_by_external_operator") is True
            and payload.get("evo_network_request_performed") is False
            and payload.get("evo_cloud_credentials_used") is False
            and payload.get("operator_fingerprint") == operator.get("fingerprint")
            and _verify_public_signature(
                payload, signature, str(operator["public_key"])
            )
        )

    def status(self) -> dict[str, object]:
        initialized = self.initialize()
        release = self._latest_release()
        state = self._release_state(str(release["release_id"])) if release else None
        registry = self._registry()
        operators = list(registry["operators"].values())
        return {
            **initialized,
            "latest_release": release,
            "phase": state["phase"] if state else "no_release",
            "pending_actions": state["pending_actions"] if state else [],
            "latest_receipt": state["latest_receipt"] if state else None,
            "trusted_operator_count": sum(
                1 for operator in operators if not operator.get("revoked_at")
            ),
            "revoked_operator_count": sum(
                1 for operator in operators if operator.get("revoked_at")
            ),
            "next_action": self._next_action(state),
            "action_confirmations": (
                {
                    action: f"{action.upper()}-{release['release_id']}"
                    for action in RECEIPT_STATUSES
                }
                if release
                else {}
            ),
            "external_execution_required": True,
            "network_request_performed": False,
            "cloud_credentials_held": False,
            "deployment_performed_by_evo": False,
        }

    def _authorize_transition(self, action: str, state: dict[str, Any]) -> None:
        successful = state["successful_statuses"]
        latest = state["latest_action_statuses"]
        if action == "stage" and latest.get("stage") == "staged":
            raise DeploymentControlError("Release is already staged.")
        if action == "health" and latest.get("stage") != "staged":
            raise DeploymentControlError("A trusted staged receipt is required.")
        if action == "promote" and latest.get("health") != "healthy":
            raise DeploymentControlError("A trusted healthy receipt is required.")
        if action == "promote" and latest.get("promote") == "promoted":
            raise DeploymentControlError("Release is already promoted.")
        if action == "rollback" and not successful.intersection(
            {"staged", "promoted"}
        ):
            raise DeploymentControlError("A staged or promoted release is required.")
        if action == "rollback" and latest.get("rollback") == "rolled_back":
            raise DeploymentControlError("Release is already rolled back.")

    def _release_state(self, release_id: str) -> dict[str, Any]:
        intents = [
            intent
            for intent in self._intents()
            if intent.get("release_id") == release_id and self.verify_intent(intent)
        ]
        valid_receipts = [
            receipt
            for receipt in self._receipts()
            if receipt.get("release_id") == release_id
        ]
        receipt_intents = {
            str(item.get("intent_id", ""))
            for item in self._receipts(include_invalid=True)
            if item.get("release_id") == release_id
        }
        pending_actions = sorted(
            {
                str(intent.get("action", ""))
                for intent in intents
                if str(intent.get("intent_id", "")) not in receipt_intents
            }
        )
        successful = {
            str(receipt.get("status", ""))
            for receipt in valid_receipts
            if receipt.get("status") != "failed"
        }
        latest_by_action = {
            action: next(
                (
                    str(receipt.get("status", ""))
                    for receipt in reversed(valid_receipts)
                    if receipt.get("action") == action
                ),
                None,
            )
            for action in RECEIPT_STATUSES
        }
        latest_receipt = valid_receipts[-1] if valid_receipts else None
        phase = "ready_to_stage"
        if latest_by_action["rollback"] == "rolled_back":
            phase = "rolled_back"
        elif "rollback" in pending_actions:
            phase = "rollback_requested"
        elif latest_receipt and latest_receipt.get("status") == "failed":
            phase = "failed"
        elif latest_by_action["promote"] == "promoted":
            phase = "promoted"
        elif "promote" in pending_actions:
            phase = "promotion_requested"
        elif latest_by_action["health"] == "unhealthy":
            phase = "unhealthy"
        elif latest_by_action["health"] == "healthy":
            phase = "healthy"
        elif "health" in pending_actions:
            phase = "health_requested"
        elif latest_by_action["stage"] == "staged":
            phase = "staged"
        elif "stage" in pending_actions:
            phase = "stage_requested"
        return {
            "phase": phase,
            "intents": intents,
            "valid_receipts": valid_receipts,
            "latest_receipt": latest_receipt,
            "pending_actions": pending_actions,
            "successful_statuses": successful,
            "latest_action_statuses": latest_by_action,
        }

    def _next_action(self, state: dict[str, Any] | None) -> str:
        if state is None:
            return "prepare_release"
        phase = state["phase"]
        return {
            "ready_to_stage": "request_stage",
            "failed": "retry_failed_action",
            "stage_requested": "await_operator_receipt",
            "staged": "request_health",
            "health_requested": "await_health_receipt",
            "unhealthy": "request_health_or_rollback",
            "healthy": "request_promote",
            "promotion_requested": "await_promotion_receipt",
            "promoted": "monitor_or_request_rollback",
            "rollback_requested": "await_rollback_receipt",
            "rolled_back": "complete",
        }.get(phase, "inspect_state")

    def _active_operator(self, operator_id: str) -> dict[str, object]:
        entry = self._registry()["operators"].get(operator_id)
        if not isinstance(entry, dict):
            raise DeploymentControlError("Operator is not registered.")
        if entry.get("revoked_at"):
            raise DeploymentControlError("Operator identity is revoked.")
        return entry

    def _registry(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            value = {
                "schema_version": DEPLOYMENT_SCHEMA_VERSION,
                "operators": {},
            }
            _atomic_json(self.registry_path, value, mode=0o600)
            return value
        value = _read_json(self.registry_path, "Operator registry")
        if (
            value.get("schema_version") != DEPLOYMENT_SCHEMA_VERSION
            or not isinstance(value.get("operators"), dict)
            or S_IMODE(self.registry_path.stat().st_mode) & 0o077
        ):
            raise DeploymentControlError("Operator registry is invalid or insecure.")
        return value

    def _latest_release(self) -> dict[str, object] | None:
        if not self.release_dir.exists():
            return None
        paths = list(self.release_dir.glob("release-*.json"))
        path = max(paths, key=lambda item: item.stat().st_mtime_ns, default=None)
        return self.verify_release(path) if path else None

    def _intents(self) -> list[dict[str, Any]]:
        if not self.outbox_dir.exists():
            return []
        return [
            _read_json(path, "Deployment intent")
            for path in sorted(
                self.outbox_dir.glob("intent-*.json"),
                key=lambda item: item.stat().st_mtime_ns,
            )
        ]

    def _receipts(self, *, include_invalid: bool = False) -> list[dict[str, Any]]:
        if not self.inbox_dir.exists():
            return []
        receipts = [
            _read_json(path, "Operator receipt")
            for path in sorted(
                self.inbox_dir.glob("receipt-*.json"),
                key=lambda item: item.stat().st_mtime_ns,
            )
        ]
        return receipts if include_invalid else [
            receipt for receipt in receipts if self.verify_receipt(receipt)
        ]

    def _repository_is_clean(self) -> bool:
        return not self._git(
            "status", "--porcelain=v1", "--untracked-files=all"
        ).stdout.strip()

    def _changed_paths(self, base: str, head: str) -> tuple[str, ...]:
        output = self._git(
            "diff", "--name-only", "--no-renames", "-z", base, head, "--"
        ).stdout
        return tuple(sorted(item for item in output.split("\0") if item))

    def _workspace_state_digest(self, paths: Iterable[str]) -> str:
        state = []
        for relative in sorted(paths):
            target = (self.repository / relative).resolve()
            if not target.is_relative_to(self.repository) or target.is_symlink():
                raise DeploymentControlError("Release path is unsafe.")
            if not target.exists():
                state.append({"path": relative, "state": "deleted"})
                continue
            if not target.is_file():
                raise DeploymentControlError("Release path is not a regular file.")
            state.append(
                {
                    "path": relative,
                    "state": "file",
                    "sha256": sha256(target.read_bytes()).hexdigest(),
                    "mode": target.stat().st_mode & 0o777,
                }
            )
        return sha256(_canonical(state)).hexdigest()

    def _git(self, *arguments: str) -> CompletedProcess[str]:
        environment = {
            name: os.environ[name]
            for name in ("PATH", "HOME", "TMPDIR")
            if name in os.environ
        }
        environment["GIT_TERMINAL_PROMPT"] = "0"
        try:
            result = run(
                ("git", "-C", str(self.repository), *arguments),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                env=environment,
                check=False,
            )
        except (OSError, TimeoutExpired) as exc:
            raise DeploymentControlError(
                "Local Git verification failed safely."
            ) from exc
        if result.returncode != 0:
            raise DeploymentControlError("Local Git verification failed safely.")
        return result


def _sign(payload: dict[str, object], identity: Ed25519Identity) -> dict[str, object]:
    return {
        **payload,
        "signature_algorithm": "Ed25519",
        "signature": identity.sign(payload),
    }


def _verify_public_signature(
    payload: Mapping[str, object], signature: object, public_key: str
) -> bool:
    if not isinstance(signature, str):
        return False
    try:
        Ed25519PublicKey.from_public_bytes(_decode_public_key(public_key)).verify(
            b64decode(signature, validate=True), _canonical(dict(payload))
        )
    except (InvalidSignature, ValueError, TypeError):
        return False
    return True


def _verify_external_intent(
    record: Mapping[str, object], public_key: str
) -> bool:
    payload = dict(record)
    payload.pop("verified", None)
    payload.pop("path", None)
    signature = payload.pop("signature", None)
    algorithm = payload.pop("signature_algorithm", None)
    return bool(
        algorithm == "Ed25519"
        and payload.get("schema_version") == DEPLOYMENT_SCHEMA_VERSION
        and payload.get("action") in RECEIPT_STATUSES
        and payload.get("authority_fingerprint")
        == _fingerprint(_decode_public_key(public_key))
        and payload.get("execution_authority") == "external_operator_only"
        and payload.get("network_request_performed") is False
        and payload.get("cloud_credentials_forwarded") is False
        and _verify_public_signature(payload, signature, public_key)
    )


def _read_public_key(path: Path, *, label: str = "Operator public key") -> str:
    try:
        encoded = path.read_text(encoding="ascii").strip()
    except OSError as exc:
        raise DeploymentControlError(f"{label} is unavailable.") from exc
    _decode_public_key(encoded)
    return encoded


def _decode_public_key(encoded: str) -> bytes:
    try:
        raw = b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise DeploymentControlError("Operator public key is invalid.") from exc
    if len(raw) != 32:
        raise DeploymentControlError("Operator public key is invalid.")
    return raw


def _fingerprint(public_key: bytes) -> str:
    return f"SHA256:{b64encode(sha256(public_key).digest()).decode('ascii').rstrip('=')}"


def _public_operator(entry: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in entry.items() if key != "public_key"}


def _validate_id(value: str, label: str) -> None:
    if value != value.strip() or not SAFE_ID.fullmatch(value):
        raise DeploymentControlError(f"{label} is invalid.")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _atomic_json(path: Path, value: dict[str, object], *, mode: int) -> None:
    _atomic_bytes(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
        mode=mode,
    )


def _atomic_bytes(path: Path, value: bytes, *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        try:
            os.write(descriptor, value)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DeploymentControlError(f"{label} is unreadable.") from exc
    if not isinstance(value, dict):
        raise DeploymentControlError(f"{label} is invalid.")
    return value
