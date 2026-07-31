"""Sealed candidate artifacts and explicit local promotion/rollback control."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from stat import S_IMODE
from subprocess import CompletedProcess, TimeoutExpired, run
from threading import Lock
from typing import Any, Iterable, Mapping, Sequence
import json
import os
import re
import secrets

from evo.trust_authority import Ed25519Identity, TrustAuthority


ARTIFACT_SCHEMA_VERSION = 1
PROMOTION_SCHEMA_VERSION = 1
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
COMMIT_ID = re.compile(r"^[0-9a-f]{40,64}$")


class ReleaseControlError(RuntimeError):
    """A sanitized artifact, promotion, or rollback failure."""


class CandidateArtifactStore:
    """Retain only sandbox-verified patches as authority-signed artifacts."""

    def __init__(self, *, root: Path, identity: Ed25519Identity) -> None:
        self.root = root
        self.identity = identity

    def seal(
        self,
        *,
        candidate_id: str,
        patch: str,
        base_commit: str,
        evidence: Mapping[str, object],
        mutable_paths: Sequence[str],
    ) -> dict[str, object]:
        _validate_id(candidate_id, "Candidate ID")
        if not COMMIT_ID.fullmatch(base_commit):
            raise ReleaseControlError("Candidate base commit is invalid.")
        patch_bytes = patch.encode("utf-8")
        patch_sha256 = sha256(patch_bytes).hexdigest()
        if (
            not patch
            or len(patch_bytes) > 65_536
            or evidence.get("verified") is not True
            or evidence.get("promotion_eligible") is not True
            or evidence.get("patch_sha256") != patch_sha256
        ):
            raise ReleaseControlError(
                "Only the exact sandbox-verified candidate patch can be sealed."
            )
        changed_paths = evidence.get("changed_paths")
        if not isinstance(changed_paths, (list, tuple)) or not changed_paths:
            raise ReleaseControlError("Candidate changed paths are unavailable.")
        artifact_seed = {
            "candidate_id": candidate_id,
            "base_commit": base_commit,
            "patch_sha256": patch_sha256,
            "evidence_sha256": sha256(_canonical(dict(evidence))).hexdigest(),
        }
        artifact_id = f"artifact-{sha256(_canonical(artifact_seed)).hexdigest()[:20]}"
        authority = self.identity.initialize()
        payload = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "artifact_id": artifact_id,
            **artifact_seed,
            "patch_bytes": len(patch_bytes),
            "changed_paths": sorted(str(path) for path in changed_paths),
            "mutable_paths": sorted(set(str(path) for path in mutable_paths)),
            "evaluation_status": str(evidence.get("status", "")),
            "evaluation_classification": str(
                evidence.get("classification", "")
            ),
            "evaluation_command": list(evidence.get("command", ())),
            "authority_fingerprint": authority["fingerprint"],
            "sealed_at": datetime.now(UTC).isoformat(),
        }
        record = _sign(payload, self.identity)
        artifact_dir = self._artifact_dir(artifact_id)
        if artifact_dir.exists():
            existing = self.verify(artifact_id)
            if existing["verified"] and existing["patch_sha256"] == patch_sha256:
                return existing
            raise ReleaseControlError("Candidate artifact ID collision detected.")
        artifact_dir.mkdir(parents=True, mode=0o700)
        try:
            _atomic_bytes(artifact_dir / "candidate.patch", patch_bytes, mode=0o600)
            _atomic_json(artifact_dir / "manifest.json", record, mode=0o600)
        except Exception:
            for child in artifact_dir.iterdir():
                child.unlink(missing_ok=True)
            artifact_dir.rmdir()
            raise
        return self.verify(artifact_id)

    def verify(self, artifact_id: str) -> dict[str, object]:
        artifact_dir = self._artifact_dir(artifact_id)
        manifest_path = artifact_dir / "manifest.json"
        patch_path = artifact_dir / "candidate.patch"
        manifest = _read_json(manifest_path, "Candidate artifact manifest")
        payload = dict(manifest)
        signature = payload.pop("signature", None)
        algorithm = payload.pop("signature_algorithm", None)
        try:
            patch = patch_path.read_bytes()
        except OSError as exc:
            raise ReleaseControlError("Candidate artifact patch is unavailable.") from exc
        manifest_digest = sha256(_canonical(manifest)).hexdigest()
        secure_permissions = all(
            S_IMODE(path.stat().st_mode) & 0o077 == 0
            for path in (artifact_dir, manifest_path, patch_path)
        )
        verified = bool(
            algorithm == "Ed25519"
            and self.identity.verify(payload, signature)
            and payload.get("schema_version") == ARTIFACT_SCHEMA_VERSION
            and payload.get("artifact_id") == artifact_id
            and payload.get("patch_sha256") == sha256(patch).hexdigest()
            and payload.get("patch_bytes") == len(patch)
            and secure_permissions
        )
        return {
            **manifest,
            "verified": verified,
            "artifact_manifest_sha256": manifest_digest,
            "manifest_path": str(manifest_path),
            "patch_path": str(patch_path),
        }

    def latest(self) -> dict[str, object] | None:
        if not self.root.exists():
            return None
        manifests = list(self.root.glob("artifact-*/manifest.json"))
        latest = max(
            manifests,
            key=lambda path: path.stat().st_mtime_ns,
            default=None,
        )
        return self.verify(latest.parent.name) if latest else None

    def read_patch(self, artifact_id: str) -> str:
        verification = self.verify(artifact_id)
        if not verification["verified"]:
            raise ReleaseControlError("Candidate artifact signature is invalid.")
        try:
            return Path(str(verification["patch_path"])).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ReleaseControlError("Candidate artifact patch is unreadable.") from exc

    def _artifact_dir(self, artifact_id: str) -> Path:
        _validate_id(artifact_id, "Artifact ID")
        resolved_root = self.root.resolve()
        target = (resolved_root / artifact_id).resolve()
        if target.parent != resolved_root:
            raise ReleaseControlError("Candidate artifact path escapes its store.")
        return target


class PromotionController:
    """Apply one authorized artifact locally and support exact-state rollback."""

    def __init__(
        self,
        *,
        repository: Path,
        artifacts: CandidateArtifactStore,
        trust: TrustAuthority,
        identity: Ed25519Identity,
        ledger_path: Path,
    ) -> None:
        self.repository = repository.resolve()
        self.artifacts = artifacts
        self.trust = trust
        self.identity = identity
        self.ledger_path = ledger_path
        self._lock = Lock()

    def promote(self, *, artifact_id: str, confirmation: str) -> dict[str, object]:
        if confirmation != f"APPLY-{artifact_id}":
            raise ReleaseControlError("Exact local-promotion confirmation is required.")
        with self._lock:
            artifact = self.artifacts.verify(artifact_id)
            if not artifact["verified"]:
                raise ReleaseControlError("Candidate artifact is not verified.")
            authorization = self.trust.current_authorization()
            if not authorization:
                raise ReleaseControlError(
                    "A current independent promotion authorization is required."
                )
            authorization_id = str(authorization.get("authorization_id", ""))
            if self._authorization_consumed(authorization_id):
                raise ReleaseControlError("Promotion authorization was already consumed.")
            self._verify_bundle_binding(artifact, authorization)
            if not self._repository_is_clean():
                raise ReleaseControlError(
                    "Local promotion requires a completely clean repository."
                )
            head = self._head()
            if head != artifact.get("base_commit"):
                raise ReleaseControlError(
                    "Repository HEAD no longer matches the tested candidate base."
                )
            patch_path = Path(str(artifact["patch_path"]))
            self._git_apply(patch_path, check=True, reverse=False)
            self._git_apply(patch_path, check=False, reverse=False)
            changed_paths = self._changed_paths()
            expected_paths = tuple(sorted(str(item) for item in artifact["changed_paths"]))
            if changed_paths != expected_paths:
                self._reverse_or_raise(patch_path)
                raise ReleaseControlError(
                    "Promoted repository state does not match the sealed artifact."
                )
            post_state_sha256 = self._state_digest(changed_paths)
            payload = {
                "schema_version": PROMOTION_SCHEMA_VERSION,
                "record_id": f"promotion-{secrets.token_hex(8)}",
                "action": "promote",
                "artifact_id": artifact_id,
                "artifact_manifest_sha256": artifact[
                    "artifact_manifest_sha256"
                ],
                "candidate_id": artifact["candidate_id"],
                "authorization_id": authorization_id,
                "bundle_id": authorization["bundle_id"],
                "base_commit": head,
                "patch_sha256": artifact["patch_sha256"],
                "changed_paths": list(changed_paths),
                "post_state_sha256": post_state_sha256,
                "scope": "local_worktree_only",
                "commit_performed": False,
                "push_performed": False,
                "deployment_authorized": False,
                "recorded_at": datetime.now(UTC).isoformat(),
            }
            record = _sign(payload, self.identity)
            try:
                _append_jsonl(self.ledger_path, record)
            except Exception as exc:
                self._reverse_or_raise(patch_path)
                raise ReleaseControlError(
                    "Promotion record failed; repository state was restored."
                ) from exc
            return {**record, "verified": True}

    def rollback(self, *, promotion_id: str, confirmation: str) -> dict[str, object]:
        if confirmation != f"ROLLBACK-{promotion_id}":
            raise ReleaseControlError("Exact rollback confirmation is required.")
        with self._lock:
            promotion = self._promotion_record(promotion_id)
            if not promotion or not self._verify_record(promotion):
                raise ReleaseControlError("Verified promotion record was not found.")
            if self._promotion_rolled_back(promotion_id):
                raise ReleaseControlError("Promotion has already been rolled back.")
            if self._head() != promotion.get("base_commit"):
                raise ReleaseControlError(
                    "Repository HEAD changed after promotion; automatic rollback is denied."
                )
            changed_paths = tuple(str(item) for item in promotion["changed_paths"])
            if (
                self._changed_paths() != tuple(sorted(changed_paths))
                or self._state_digest(changed_paths)
                != promotion.get("post_state_sha256")
            ):
                raise ReleaseControlError(
                    "Repository changed after promotion; automatic rollback is denied."
                )
            artifact_id = str(promotion["artifact_id"])
            artifact = self.artifacts.verify(artifact_id)
            if not artifact["verified"]:
                raise ReleaseControlError("Rollback artifact is not verified.")
            patch_path = Path(str(artifact["patch_path"]))
            self._git_apply(patch_path, check=True, reverse=True)
            self._git_apply(patch_path, check=False, reverse=True)
            if not self._repository_is_clean():
                raise ReleaseControlError(
                    "Rollback did not restore the original clean repository."
                )
            payload = {
                "schema_version": PROMOTION_SCHEMA_VERSION,
                "record_id": f"rollback-{secrets.token_hex(8)}",
                "action": "rollback",
                "promotion_id": promotion_id,
                "artifact_id": artifact_id,
                "base_commit": promotion["base_commit"],
                "restored_clean_state": True,
                "commit_performed": False,
                "push_performed": False,
                "deployment_authorized": False,
                "recorded_at": datetime.now(UTC).isoformat(),
            }
            record = _sign(payload, self.identity)
            try:
                _append_jsonl(self.ledger_path, record)
            except Exception as exc:
                try:
                    self._git_apply(patch_path, check=True, reverse=False)
                    self._git_apply(patch_path, check=False, reverse=False)
                except ReleaseControlError as restore_error:
                    raise ReleaseControlError(
                        "Rollback recording and promoted-state restoration failed."
                    ) from restore_error
                raise ReleaseControlError(
                    "Rollback record failed; promoted state was restored."
                ) from exc
            return {**record, "verified": True}

    def status(self) -> dict[str, object]:
        artifact = self.artifacts.latest()
        authorization = self.trust.current_authorization()
        entries = list(_read_jsonl(self.ledger_path))
        latest = entries[-1] if entries else None
        active = next(
            (
                entry
                for entry in reversed(entries)
                if entry.get("action") == "promote"
                and self._verify_record(entry)
                and not self._promotion_rolled_back(str(entry.get("record_id", "")))
            ),
            None,
        )
        try:
            repository_clean = self._repository_is_clean()
        except ReleaseControlError:
            repository_clean = False
        return {
            "latest_artifact": artifact,
            "authorization_current": bool(authorization),
            "authorization_id": (
                authorization.get("authorization_id") if authorization else None
            ),
            "authorization_consumed": bool(
                authorization
                and self._authorization_consumed(
                    str(authorization.get("authorization_id", ""))
                )
            ),
            "latest_record": (
                {**latest, "verified": self._verify_record(latest)}
                if latest
                else None
            ),
            "active_promotion": (
                {**active, "verified": self._verify_record(active)}
                if active
                else None
            ),
            "apply_confirmation": (
                f"APPLY-{artifact['artifact_id']}"
                if artifact and artifact.get("verified")
                else None
            ),
            "rollback_confirmation": (
                f"ROLLBACK-{active['record_id']}" if active else None
            ),
            "repository_clean": repository_clean,
            "commit_performed": False,
            "push_performed": False,
            "deployment_authorized": False,
        }

    def latest_active_promotion(self) -> dict[str, Any] | None:
        """Return the latest verified promotion that has not been rolled back."""

        return next(
            (
                entry
                for entry in reversed(list(_read_jsonl(self.ledger_path)))
                if entry.get("action") == "promote"
                and self._verify_record(entry)
                and not self._promotion_rolled_back(
                    str(entry.get("record_id", ""))
                )
            ),
            None,
        )

    def verify_record(self, record: Mapping[str, object]) -> bool:
        return self._verify_record(record)

    def _verify_bundle_binding(
        self,
        artifact: Mapping[str, object],
        authorization: Mapping[str, object],
    ) -> None:
        evidence_status = self.trust.evidence_control.status()
        bundle_path_value = evidence_status.get("latest_bundle_path")
        if not bundle_path_value:
            raise ReleaseControlError("Authorized evidence bundle is unavailable.")
        bundle = _read_json(Path(str(bundle_path_value)), "Evidence bundle")
        if bundle.get("bundle_id") != authorization.get("bundle_id"):
            raise ReleaseControlError("Authorization targets a different bundle.")
        candidate_evidence = bundle.get("candidate_evidence")
        if not isinstance(candidate_evidence, list):
            raise ReleaseControlError("Candidate evidence is unavailable.")
        matched = any(
            isinstance(entry, dict)
            and entry.get("candidate_id") == artifact.get("candidate_id")
            and entry.get("artifact_id") == artifact.get("artifact_id")
            and entry.get("artifact_manifest_sha256")
            == artifact.get("artifact_manifest_sha256")
            and entry.get("patch_sha256") == artifact.get("patch_sha256")
            and entry.get("verified") is True
            and entry.get("promotion_eligible") is True
            for entry in candidate_evidence
        )
        if not matched:
            raise ReleaseControlError(
                "Sealed artifact is not covered by the authorized evidence bundle."
            )

    def _authorization_consumed(self, authorization_id: str) -> bool:
        return any(
            entry.get("action") == "promote"
            and entry.get("authorization_id") == authorization_id
            for entry in _read_jsonl(self.ledger_path)
        )

    def _promotion_record(self, promotion_id: str) -> dict[str, Any] | None:
        _validate_id(promotion_id, "Promotion ID")
        return next(
            (
                entry
                for entry in _read_jsonl(self.ledger_path)
                if entry.get("action") == "promote"
                and entry.get("record_id") == promotion_id
            ),
            None,
        )

    def _promotion_rolled_back(self, promotion_id: str) -> bool:
        return any(
            entry.get("action") == "rollback"
            and entry.get("promotion_id") == promotion_id
            and self._verify_record(entry)
            for entry in _read_jsonl(self.ledger_path)
        )

    def _verify_record(self, record: Mapping[str, object]) -> bool:
        payload = dict(record)
        signature = payload.pop("signature", None)
        algorithm = payload.pop("signature_algorithm", None)
        return bool(
            algorithm == "Ed25519"
            and payload.get("schema_version") == PROMOTION_SCHEMA_VERSION
            and self.identity.verify(payload, signature)
        )

    def _head(self) -> str:
        return self._git("rev-parse", "HEAD").stdout.strip()

    def _repository_is_clean(self) -> bool:
        return not self._git(
            "status", "--porcelain=v1", "--untracked-files=all"
        ).stdout.strip()

    def _changed_paths(self) -> tuple[str, ...]:
        tracked = self._git(
            "diff", "--name-only", "--no-renames", "-z", "HEAD", "--"
        ).stdout
        untracked = self._git(
            "ls-files", "--others", "--exclude-standard", "-z", "--"
        ).stdout
        return tuple(
            sorted(
                {
                    item
                    for item in (*tracked.split("\0"), *untracked.split("\0"))
                    if item
                }
            )
        )

    def _state_digest(self, paths: Sequence[str]) -> str:
        state = []
        for relative in sorted(paths):
            target = (self.repository / relative).resolve()
            if not target.is_relative_to(self.repository) or target.is_symlink():
                raise ReleaseControlError("Promoted path is unsafe.")
            if not target.exists():
                state.append({"path": relative, "state": "deleted"})
                continue
            if not target.is_file():
                raise ReleaseControlError("Promoted path is not a regular file.")
            state.append(
                {
                    "path": relative,
                    "state": "file",
                    "sha256": sha256(target.read_bytes()).hexdigest(),
                    "mode": target.stat().st_mode & 0o777,
                }
            )
        return sha256(_canonical(state)).hexdigest()

    def _git_apply(self, patch: Path, *, check: bool, reverse: bool) -> None:
        arguments = ["apply", "--whitespace=nowarn"]
        if check:
            arguments.append("--check")
        if reverse:
            arguments.append("--reverse")
        arguments.extend(("--", str(patch)))
        self._git(*arguments)

    def _reverse_or_raise(self, patch: Path) -> None:
        try:
            self._git_apply(patch, check=True, reverse=True)
            self._git_apply(patch, check=False, reverse=True)
        except ReleaseControlError as exc:
            raise ReleaseControlError(
                "Promotion failed and automatic restoration also failed."
            ) from exc

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
            raise ReleaseControlError("Local Git operation failed safely.") from exc
        if result.returncode != 0:
            raise ReleaseControlError("Local Git operation failed safely.")
        return result


def _sign(payload: dict[str, object], identity: Ed25519Identity) -> dict[str, object]:
    return {
        **payload,
        "signature_algorithm": "Ed25519",
        "signature": identity.sign(payload),
    }


def _validate_id(value: str, label: str) -> None:
    if value != value.strip() or not SAFE_ID.fullmatch(value):
        raise ReleaseControlError(f"{label} is invalid.")


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
        finally:
            os.close(descriptor)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    except OSError as exc:
        raise ReleaseControlError("Promotion ledger is unavailable.") from exc
    try:
        if S_IMODE(os.fstat(descriptor).st_mode) & 0o077:
            raise ReleaseControlError("Promotion ledger permissions are insecure.")
        line = json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"
        os.write(descriptor, line.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseControlError(f"{label} is unreadable.") from exc
    if not isinstance(value, dict):
        raise ReleaseControlError(f"{label} is invalid.")
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
                        raise ReleaseControlError("Promotion ledger is invalid.")
                    entries.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseControlError("Promotion ledger is unreadable.") from exc
    return entries
