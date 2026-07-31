"""Deterministic replay, authenticated evidence, and human approval records."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from hmac import compare_digest, new as hmac_new
from pathlib import Path
from stat import S_IMODE
from tempfile import TemporaryDirectory
from typing import Any, Iterable
import json
import os
import secrets

from evo.petri import PetriDish


REPLAY_SCHEMA_VERSION = 1
BUNDLE_SCHEMA_VERSION = 1
APPROVAL_SCHEMA_VERSION = 1


class EvidenceControlError(ValueError):
    """A safe replay, signature, or approval validation error."""


class ReplayService:
    def __init__(self, *, petri_dish: PetriDish) -> None:
        self.petri_dish = petri_dish

    def export_manifest(self) -> dict[str, object]:
        state = self.petri_dish.status()
        founders = [
            item
            for item in state["organisms"]
            if not item.get("parent_ids") and int(item.get("generation", 0)) == 0
        ]
        outcomes = []
        events = state.get("events", [])
        if len(events) != int(state["epoch"]):
            raise EvidenceControlError(
                "Replay is unavailable because the complete epoch history is missing."
            )
        for event in events:
            replay_input = event.get("replay_input")
            if not isinstance(replay_input, dict):
                raise EvidenceControlError(
                    "Replay is unavailable because an epoch lacks replay input."
                )
            outcomes.append(
                {
                    "epoch": event["epoch"],
                    "organism_id": event["organism_id"],
                    "candidate": deepcopy(replay_input),
                }
            )
        return {
            "schema_version": REPLAY_SCHEMA_VERSION,
            "initial_population": len(founders),
            "capacity": int(state["capacity"]),
            "outcomes": outcomes,
            "expected_state_sha256": normalized_state_digest(state),
        }

    @staticmethod
    def verify_manifest(manifest: dict[str, object]) -> dict[str, object]:
        if manifest.get("schema_version") != REPLAY_SCHEMA_VERSION:
            raise EvidenceControlError("Unsupported replay manifest version.")
        outcomes = manifest.get("outcomes")
        if not isinstance(outcomes, list):
            raise EvidenceControlError("Replay outcomes are invalid.")
        try:
            initial_population = int(manifest["initial_population"])
            capacity = int(manifest["capacity"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceControlError("Replay population settings are invalid.") from exc

        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=initial_population,
                capacity=capacity,
            )
            for expected_epoch, outcome in enumerate(outcomes, start=1):
                if not isinstance(outcome, dict):
                    raise EvidenceControlError("Replay outcome is invalid.")
                if int(outcome.get("epoch", -1)) != expected_epoch:
                    raise EvidenceControlError("Replay epochs are not contiguous.")
                candidate = outcome.get("candidate")
                if not isinstance(candidate, dict):
                    raise EvidenceControlError("Replay candidate is invalid.")
                selected = dish.select_for_evaluation()
                organism_id = str(outcome.get("organism_id", ""))
                if selected["organism_id"] != organism_id:
                    raise EvidenceControlError(
                        "Replay selection diverged from the recorded ecology."
                    )
                dish.record_outcome(
                    organism_id=organism_id,
                    candidate=deepcopy(candidate),
                )
            actual = normalized_state_digest(dish.status())
        expected = str(manifest.get("expected_state_sha256", ""))
        return {
            "verified": compare_digest(actual, expected),
            "expected_state_sha256": expected,
            "actual_state_sha256": actual,
            "epochs_replayed": len(outcomes),
        }


class EvidenceSigner:
    """Authenticate bundles using a host-owned symmetric key."""

    def __init__(self, *, key_path: Path) -> None:
        self.key_path = key_path

    def sign(self, payload: dict[str, object]) -> str:
        return hmac_new(self._key(), _canonical(payload), "sha256").hexdigest()

    def verify(self, payload: dict[str, object], signature: object) -> bool:
        return isinstance(signature, str) and compare_digest(
            self.sign(payload), signature
        )

    def _key(self) -> bytes:
        if not self.key_path.exists():
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                descriptor = os.open(
                    self.key_path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
            except FileExistsError:
                pass
            else:
                try:
                    os.write(descriptor, secrets.token_bytes(32))
                finally:
                    os.close(descriptor)
        try:
            key = self.key_path.read_bytes()
        except OSError as exc:
            raise EvidenceControlError("Evidence signing key is unavailable.") from exc
        if len(key) != 32:
            raise EvidenceControlError("Evidence signing key is invalid.")
        if S_IMODE(self.key_path.stat().st_mode) & 0o077:
            raise EvidenceControlError("Evidence signing key permissions are insecure.")
        return key


class EvidenceControl:
    def __init__(
        self,
        *,
        replay: ReplayService,
        signer: EvidenceSigner,
        bundle_dir: Path,
        candidate_evidence_path: Path,
        approval_path: Path,
    ) -> None:
        self.replay = replay
        self.signer = signer
        self.bundle_dir = bundle_dir
        self.candidate_evidence_path = candidate_evidence_path
        self.approval_path = approval_path

    def create_bundle(self) -> dict[str, object]:
        replay_manifest = self.replay.export_manifest()
        replay_result = self.replay.verify_manifest(replay_manifest)
        if not replay_result["verified"]:
            raise EvidenceControlError("Ecological replay did not reproduce state.")
        payload = {
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "replay_manifest": replay_manifest,
            "candidate_evidence": list(self._candidate_evidence()),
        }
        bundle_id = f"bundle-{sha256(_canonical(payload)).hexdigest()[:16]}"
        signed_payload = {"bundle_id": bundle_id, **payload}
        bundle = {
            **signed_payload,
            "signature_algorithm": "HMAC-SHA256",
            "signature": self.signer.sign(signed_payload),
        }
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
        path = self.bundle_dir / f"{bundle_id}.json"
        _atomic_json(path, bundle)
        return {**self.verify_bundle(path), "path": str(path)}

    def verify_bundle(self, path: Path) -> dict[str, object]:
        bundle = _read_json(path, label="Evidence bundle")
        signature = bundle.pop("signature", None)
        algorithm = bundle.pop("signature_algorithm", None)
        signature_valid = (
            algorithm == "HMAC-SHA256" and self.signer.verify(bundle, signature)
        )
        replay_manifest = bundle.get("replay_manifest")
        try:
            replay_result = (
                self.replay.verify_manifest(replay_manifest)
                if isinstance(replay_manifest, dict)
                else {"verified": False, "epochs_replayed": 0}
            )
        except EvidenceControlError:
            replay_result = {"verified": False, "epochs_replayed": 0}
        candidate_evidence = bundle.get("candidate_evidence")
        evidence_count = (
            len(candidate_evidence) if isinstance(candidate_evidence, list) else 0
        )
        verified = bool(signature_valid and replay_result["verified"])
        return {
            "bundle_id": bundle.get("bundle_id"),
            "verified": verified,
            "signature_valid": signature_valid,
            "replay_verified": replay_result["verified"],
            "epochs_replayed": replay_result.get("epochs_replayed", 0),
            "candidate_evidence_count": evidence_count,
        }

    def approve(
        self,
        *,
        bundle_path: Path,
        approver: str,
        decision: str,
        note: str = "",
    ) -> dict[str, object]:
        clean_approver = approver.strip()
        clean_decision = decision.strip().lower()
        if not clean_approver or len(clean_approver) > 120:
            raise EvidenceControlError("Approver name is required and bounded.")
        if clean_decision not in {"approve", "reject"}:
            raise EvidenceControlError("Decision must be approve or reject.")
        if len(note) > 2_000:
            raise EvidenceControlError("Approval note is too long.")
        verification = self.verify_bundle(bundle_path)
        if not verification["verified"]:
            raise EvidenceControlError("Only a verified bundle can be reviewed.")
        payload = {
            "schema_version": APPROVAL_SCHEMA_VERSION,
            "approval_id": f"approval-{secrets.token_hex(8)}",
            "bundle_id": verification["bundle_id"],
            "decision": clean_decision,
            "approver": clean_approver,
            "note": note.strip(),
            "authority": "local_human_assertion_only",
            "deploy_authorized": False,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        record = {**payload, "signature": self.signer.sign(payload)}
        _append_jsonl(self.approval_path, record)
        return record

    def approve_latest(
        self,
        *,
        approver: str,
        decision: str,
        note: str = "",
    ) -> dict[str, object]:
        bundle_path = self._latest_bundle_path()
        if bundle_path is None:
            raise EvidenceControlError("Create a verified evidence bundle first.")
        return self.approve(
            bundle_path=bundle_path,
            approver=approver,
            decision=decision,
            note=note,
        )

    def status(self) -> dict[str, object]:
        bundle_path = self._latest_bundle_path()
        latest_bundle = self.verify_bundle(bundle_path) if bundle_path else None
        approvals = list(_read_jsonl(self.approval_path))
        latest_bundle_id = latest_bundle.get("bundle_id") if latest_bundle else None
        latest_approval = next(
            (
                approval
                for approval in reversed(approvals)
                if approval.get("bundle_id") == latest_bundle_id
            ),
            None,
        )
        approval_valid = False
        if latest_approval:
            signature = latest_approval.pop("signature", None)
            approval_valid = self.signer.verify(latest_approval, signature)
            latest_approval["signature"] = signature
            latest_approval["signature_valid"] = approval_valid
        return {
            "latest_bundle": latest_bundle,
            "latest_bundle_path": str(bundle_path) if bundle_path else None,
            "latest_approval": latest_approval,
            "approval_signature_valid": approval_valid,
            "deployment_authorized": False,
        }

    def _candidate_evidence(self) -> Iterable[dict[str, Any]]:
        return _read_jsonl(self.candidate_evidence_path)

    def _latest_bundle_path(self) -> Path | None:
        if not self.bundle_dir.exists():
            return None
        bundles = list(self.bundle_dir.glob("bundle-*.json"))
        return max(bundles, key=lambda path: path.stat().st_mtime_ns, default=None)


def normalized_state_digest(state: dict[str, object]) -> str:
    return sha256(_canonical(_without_time(state))).hexdigest()


def _without_time(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_time(item)
            for key, item in value.items()
            if key not in {"created_at", "updated_at", "timestamp", "recorded_at"}
            and not key.endswith("_at")
        }
    if isinstance(value, list):
        return [_without_time(item) for item in value]
    return value


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceControlError(f"{label} is unreadable.") from exc
    if not isinstance(value, dict):
        raise EvidenceControlError(f"{label} is invalid.")
    return value


def _append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


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
                        raise EvidenceControlError("Evidence ledger entry is invalid.")
                    entries.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceControlError("Evidence ledger is unreadable.") from exc
    return entries
