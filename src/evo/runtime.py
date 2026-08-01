"""Shared host-facing operations used by the CLI and local UI."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json
import os
import shlex

from evo.candidate_lifecycle import CandidateLifecycle
from evo.config import ConfigurationError, Settings, load_env_file
from evo.content_i18n import (
    TranslationCache,
    TranslationError,
    apply_translations,
    collect_translatable_texts,
    translate_missing,
)
from evo.domain import EvolutionTask, Genome
from evo.evidence_control import EvidenceControl, EvidenceSigner, ReplayService
from evo.trust_authority import Ed25519Identity, TrustAuthority
from evo.release_control import CandidateArtifactStore, PromotionController
from evo.deployment_control import DeploymentHandoff
from evo.evolution import EvolutionEngine
from evo.kernel.audit import AuditLog
from evo.kernel.budget import BudgetExceeded, RunBudget
from evo.kernel.policy import KernelPolicy
from evo.mutation import MutationApplicator
from evo.petri import PetriDish
from evo.providers.base import ModelProvider
from evo.providers.groq import GroqProvider, ProviderError
from evo.providers.groq_models import GROQ_MODEL_CATALOG
from evo.providers.nvidia import NvidiaProvider
from evo.providers.nvidia_generation import (
    PROFILE_BALANCED,
    SUPPORTED_PROFILES,
    NvidiaGenerationProfile,
)
from evo.providers.nvidia_models import NVIDIA_MODEL_CATALOG
from evo.sandbox import RootlessSandbox, SandboxLimits

PROVIDER_MODEL_CATALOGS: dict[str, tuple[str, ...]] = {
    "groq": GROQ_MODEL_CATALOG,
    "nvidia": NVIDIA_MODEL_CATALOG,
}

SUPPORTED_PROVIDERS = ("groq", "nvidia")
DEFAULT_AUDIT_PATH = Path(".evo/audit.jsonl")
DEFAULT_ENV_FILE = Path(".env.local")

PROVIDER_KEY_NAMES = {
    "groq": "GROQ_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
}

PROVIDER_MODEL_NAMES = {
    "groq": "EVO_GROQ_MODEL",
    "nvidia": "EVO_NVIDIA_MODEL",
}

PROVIDER_BASE_URL_NAMES = {
    "groq": "EVO_GROQ_BASE_URL",
    "nvidia": "EVO_NVIDIA_BASE_URL",
}

PROVIDER_DEFAULTS = {
    "groq": {
        "model": "openai/gpt-oss-20b",
        "base_url": "https://api.groq.com/openai/v1",
    },
    "nvidia": {
        "model": "meta/llama-3.1-70b-instruct",
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
}

BUDGET_KEYS = (
    "EVO_MAX_INPUT_TOKENS",
    "EVO_MAX_OUTPUT_TOKENS",
    "EVO_MAX_CALLS_PER_RUN",
    "EVO_REQUEST_TIMEOUT_SECONDS",
)
MAX_CANDIDATE_SOURCE_BYTES = 32_768


class TerrariumRuntime:
    """Coordinates configuration, providers, evolution, and audit access."""

    def __init__(
        self,
        *,
        env_file: Path | None = None,
        audit_path: Path | None = None,
        workspace: Path | None = None,
    ) -> None:
        self.workspace = (workspace or Path.cwd()).resolve()
        self.env_file = (
            env_file if env_file is not None else self.workspace / DEFAULT_ENV_FILE
        )
        self.audit_path = (
            audit_path
            if audit_path is not None
            else self.workspace / DEFAULT_AUDIT_PATH
        )

    def load_settings(self) -> Settings:
        if self.env_file.exists():
            load_env_file(self.env_file)
        return Settings.from_environment()

    def build_provider(self, settings: Settings | None = None) -> ModelProvider:
        resolved = settings or self.load_settings()
        if resolved.provider == "groq":
            return GroqProvider(
                api_key=resolved.api_key,
                model=resolved.model,
                base_url=resolved.base_url,
                timeout_seconds=resolved.request_timeout_seconds,
                max_output_tokens=resolved.max_output_tokens,
            )
        return NvidiaProvider(
            api_key=resolved.api_key,
            model=resolved.model,
            base_url=resolved.base_url,
            timeout_seconds=resolved.request_timeout_seconds,
            max_output_tokens=resolved.max_output_tokens,
            generation_profile=resolved.nvidia_generation
            or NvidiaGenerationProfile.from_environment(),
        )

    def localize_journal_entries(
        self,
        entries: list[dict[str, object]],
        *,
        allow_provider: bool = True,
    ) -> list[dict[str, object]]:
        """Return journal entries with Latin free-text localized to Persian."""
        texts = collect_translatable_texts(entries)
        if not texts:
            return [dict(entry) for entry in entries]
        cache = TranslationCache(self.workspace / ".evo/i18n-cache-fa.json")
        mapping: dict[str, str] = {}
        if allow_provider:
            try:
                provider = self.build_provider()
                mapping = translate_missing(
                    texts,
                    cache=cache,
                    provider=provider,
                )
            except (
                ConfigurationError,
                TranslationError,
                ProviderError,
                ValueError,
                OSError,
            ):
                mapping = {}
        if not mapping:
            for text in texts:
                mapping[text] = cache.get(text) or text
        return [apply_translations(dict(entry), mapping) for entry in entries]

    def public_settings(self) -> dict[str, object]:
        try:
            settings = self.load_settings()
            sandbox_timeout = _bounded_integer_environment(
                "EVO_SANDBOX_TIMEOUT_SECONDS",
                default=60,
                minimum=1,
                maximum=600,
            )
        except ConfigurationError as exc:
            return {
                "configured": False,
                "error": str(exc),
                "env_file": str(self.env_file),
                "env_file_exists": self.env_file.exists(),
                "provider": os.getenv("EVO_PROVIDER", "groq"),
                "supported_providers": list(SUPPORTED_PROVIDERS),
            }
        return {
            "configured": True,
            "env_file": str(self.env_file),
            "env_file_exists": self.env_file.exists(),
            "provider": settings.provider,
            "model": settings.model,
            "base_url": settings.base_url,
            "api_key": "تنظیم‌شده",
            "max_input_tokens": settings.max_input_tokens,
            "max_output_tokens": settings.max_output_tokens,
            "max_calls_per_run": settings.max_calls_per_run,
            "request_timeout_seconds": settings.request_timeout_seconds,
            "supported_providers": list(SUPPORTED_PROVIDERS),
            "audit_path": str(self.audit_path),
            "sandbox_image": os.getenv("EVO_SANDBOX_IMAGE", ""),
            "sandbox_engine": os.getenv("EVO_SANDBOX_ENGINE", "podman"),
            "evaluation_command": os.getenv(
                "EVO_EVALUATION_COMMAND",
                "python -m unittest discover -s tests",
            ),
            "sandbox_timeout_seconds": sandbox_timeout,
            "nvidia_generation_profile": (
                settings.nvidia_generation.mode
                if settings.nvidia_generation is not None
                else None
            ),
            "nvidia_generation": (
                settings.nvidia_generation.public_dict()
                if settings.nvidia_generation is not None
                else None
            ),
            "supported_nvidia_generation_profiles": list(SUPPORTED_PROFILES),
        }

    def doctor(self) -> dict[str, object]:
        settings = self.load_settings()
        return {
            "configuration": "معتبر",
            "provider": settings.provider,
            "model": settings.model,
            "api_key": "تنظیم‌شده",
        }

    def probe(self) -> str:
        return self.build_provider().healthcheck()

    def list_models(self, provider: str | None = None) -> dict[str, object]:
        selected = (provider or os.getenv("EVO_PROVIDER", "groq")).strip().lower()
        if selected not in SUPPORTED_PROVIDERS:
            try:
                selected = self.load_settings().provider
            except ConfigurationError:
                selected = "groq"
        catalog = PROVIDER_MODEL_CATALOGS.get(selected, GROQ_MODEL_CATALOG)
        models = list(catalog)
        source = "catalog"
        try:
            settings = self.load_settings()
            if settings.provider == selected:
                live = self.build_provider(settings).list_models()
                if live:
                    models = sorted(set(models) | set(live))
                    source = "provider"
        except (ConfigurationError, ProviderError, ValueError, AttributeError):
            pass
        return {
            "provider": selected,
            "models": models,
            "source": source,
            "selectable": True,
        }

    def evidence_control(
        self,
        *,
        petri_dish: PetriDish | None = None,
    ) -> EvidenceControl:
        dish = petri_dish or PetriDish(
            state_path=self.workspace / ".evo/petri-dish.json"
        )
        return EvidenceControl(
            replay=ReplayService(petri_dish=dish),
            signer=EvidenceSigner(
                key_path=self.workspace / ".evo/evidence-signing.key"
            ),
            bundle_dir=self.workspace / ".evo/evidence-bundles",
            candidate_evidence_path=(
                self.workspace / ".evo/candidate-evidence.jsonl"
            ),
            approval_path=self.workspace / ".evo/promotion-approvals.jsonl",
        )

    def trust_authority(
        self,
        *,
        evidence_control: EvidenceControl | None = None,
        petri_dish: PetriDish | None = None,
    ) -> TrustAuthority:
        """Build the host-owned public trust boundary for v0.8."""

        return TrustAuthority(
            evidence_control=evidence_control
            or self.evidence_control(petri_dish=petri_dish),
            authority_identity=self._authority_identity(),
            trust_dir=self.workspace / ".evo/trust",
        )

    def candidate_artifacts(self) -> CandidateArtifactStore:
        return CandidateArtifactStore(
            root=self.workspace / ".evo/candidate-artifacts",
            identity=self._authority_identity(),
        )

    def promotion_controller(
        self,
        *,
        evidence_control: EvidenceControl | None = None,
        petri_dish: PetriDish | None = None,
    ) -> PromotionController:
        trust = self.trust_authority(
            evidence_control=evidence_control,
            petri_dish=petri_dish,
        )
        return PromotionController(
            repository=self.workspace,
            artifacts=self.candidate_artifacts(),
            trust=trust,
            identity=self._authority_identity(),
            ledger_path=self.workspace / ".evo/promotion-ledger.jsonl",
        )

    def deployment_handoff(
        self,
        *,
        evidence_control: EvidenceControl | None = None,
        petri_dish: PetriDish | None = None,
    ) -> DeploymentHandoff:
        """Build the credential-free external deployment boundary for v1.0."""

        return DeploymentHandoff(
            repository=self.workspace,
            promotion=self.promotion_controller(
                evidence_control=evidence_control,
                petri_dish=petri_dish,
            ),
            artifacts=self.candidate_artifacts(),
            identity=self._authority_identity(),
            root=self.workspace / ".evo/deployment",
        )

    def _authority_identity(self) -> Ed25519Identity:
        return Ed25519Identity(
            private_key_path=self.workspace / ".evo/trust/authority-ed25519.key"
        )

    def evolve(
        self,
        *,
        task: str,
        mutable_paths: list[str] | None = None,
        organism_id: str = "cell-0001",
        task_id: str = "interactive",
        generation: int = 0,
        language: str = "en",
        traits: dict[str, Any] | None = None,
    ) -> dict[str, object]:
        objective = task.strip()
        if not objective:
            raise ValueError("وارد کردن هدف الزامی است")
        paths = mutable_paths or ["organisms/"]
        cleaned = [path.strip() for path in paths if path and path.strip()]
        if not cleaned:
            raise ValueError("حداقل یک مسیر قابل‌تغییر لازم است")
        if generation < 0:
            raise ValueError("Generation cannot be negative.")
        language_name = {"en": "English", "fa": "Persian"}.get(language)
        if language_name is None:
            raise ValueError("Language must be en or fa.")
        settings = self.load_settings()
        budget = RunBudget(
            max_calls=settings.max_calls_per_run,
            max_input_tokens=settings.max_input_tokens,
            max_output_tokens=settings.max_output_tokens,
        )
        image = os.getenv("EVO_SANDBOX_IMAGE", "").strip()
        engine = EvolutionEngine(
            provider=self.build_provider(settings),
            policy=KernelPolicy(),
            budget=budget,
            audit=AuditLog(self.audit_path),
            source_reader=self._read_candidate_source if image else None,
        )
        candidate = engine.run_generation(
            Genome(
                organism_id=organism_id,
                generation=generation,
                mutable_paths=tuple(dict.fromkeys(cleaned)),
                traits=traits or {},
            ),
            EvolutionTask(task_id=task_id, objective=objective),
            language=language_name,
        )
        result = asdict(candidate)
        proposal = result.get("proposal")
        patch = proposal.get("patch") if isinstance(proposal, dict) else None
        evidence: dict[str, object] = {
            "candidate_id": candidate.candidate_id,
            "status": "proposal_only",
            "verified": False,
            "promotion_eligible": False,
            "reason": "No executable candidate patch was available.",
        }
        if isinstance(patch, str) and patch.strip() and image:
            command = tuple(
                shlex.split(
                    os.getenv(
                        "EVO_EVALUATION_COMMAND",
                        "python -m unittest discover -s tests",
                    )
                )
            )
            if not command:
                raise ConfigurationError(
                    "EVO_EVALUATION_COMMAND cannot be empty."
                )
            engine_name = os.getenv("EVO_SANDBOX_ENGINE", "").strip() or None
            timeout = _bounded_integer_environment(
                "EVO_SANDBOX_TIMEOUT_SECONDS",
                default=60,
                minimum=1,
                maximum=600,
            )
            team_ids = _team_ids(traits)
            comparison = CandidateLifecycle(
                repository=self.workspace,
                evidence_path=(
                    self.workspace / ".evo/candidate-evidence.jsonl"
                ),
                sandbox_factory=lambda workspace: RootlessSandbox(
                    workspace=workspace,
                    image=image,
                    engine=engine_name,
                    limits=SandboxLimits(timeout_seconds=timeout),
                    allowed_commands=(command[0],),
                ),
                mutation=MutationApplicator(audit=AuditLog(self.audit_path)),
                artifact_store=self.candidate_artifacts(),
            ).evaluate(
                candidate_id=candidate.candidate_id,
                team_ids=team_ids,
                patch=patch,
                mutable_paths=tuple(dict.fromkeys(cleaned)),
                command=command,
            )
            evidence = asdict(comparison)
        elif isinstance(patch, str) and patch.strip():
            evidence["reason"] = (
                "A patch was generated, but EVO_SANDBOX_IMAGE is not configured."
            )
        result["evaluation_evidence"] = evidence
        result["promotion_eligible"] = bool(
            evidence.get("promotion_eligible", False)
        )
        return result

    def _read_candidate_source(self, relative: str) -> str:
        target = (self.workspace / relative).resolve()
        if not target.is_relative_to(self.workspace):
            raise ValueError("Candidate source path escapes the workspace.")
        unresolved = self.workspace / relative
        if unresolved.is_symlink():
            raise ValueError("Candidate source cannot be a symbolic link.")
        if not target.exists():
            return ""
        if not target.is_file():
            raise ValueError("Candidate source must be a regular file.")
        raw = target.read_bytes()
        if len(raw) > MAX_CANDIDATE_SOURCE_BYTES:
            raise ValueError("Candidate source exceeds the bounded context size.")
        if b"\0" in raw:
            raise ValueError("Candidate source cannot be binary.")
        return raw.decode("utf-8")

    def read_audit(self, *, limit: int = 50, query: str = "") -> list[dict[str, object]]:
        if limit <= 0:
            raise ValueError("محدوده گزارش رویدادها باید بزرگ‌تر از صفر باشد")
        if not self.audit_path.exists():
            return []
        needle = query.strip().lower()
        events: list[dict[str, object]] = []
        with self.audit_path.open(encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                if needle and needle not in json.dumps(event, sort_keys=True).lower():
                    continue
                events.append(event)
        return events[-limit:][::-1]

    def save_settings(self, values: dict[str, object]) -> dict[str, object]:
        provider = str(values.get("provider", "groq")).strip().lower()
        if provider not in SUPPORTED_PROVIDERS:
            raise ConfigurationError(
                "EVO_PROVIDER باید یکی از این موارد باشد: "
                + "، ".join(SUPPORTED_PROVIDERS)
            )

        defaults = PROVIDER_DEFAULTS[provider]
        model = str(values.get("model", defaults["model"])).strip()
        if not model:
            raise ConfigurationError("مدل پیکربندی‌شده نمی‌تواند خالی باشد")
        base_url = str(values.get("base_url", defaults["base_url"])).strip().rstrip("/")
        if not base_url.startswith("https://"):
            raise ConfigurationError(
                "نشانی پایه ارائه‌دهنده باید از HTTPS استفاده کند"
            )

        api_key = str(values.get("api_key", "")).strip()
        existing = _read_env_map(self.env_file)
        key_name = PROVIDER_KEY_NAMES[provider]
        if not api_key:
            api_key = existing.get(key_name, os.getenv(key_name, "")).strip()
        if not api_key:
            raise ConfigurationError(
                f"وارد کردن {key_name} برای {provider} الزامی است"
            )

        payload = {
            "EVO_PROVIDER": provider,
            key_name: api_key,
            PROVIDER_MODEL_NAMES[provider]: model,
            PROVIDER_BASE_URL_NAMES[provider]: base_url,
            "EVO_MAX_INPUT_TOKENS": _positive_setting(
                values, "max_input_tokens", existing, "EVO_MAX_INPUT_TOKENS", 6000
            ),
            "EVO_MAX_OUTPUT_TOKENS": _positive_setting(
                values,
                "max_output_tokens",
                existing,
                "EVO_MAX_OUTPUT_TOKENS",
                4096 if provider == "nvidia" else 1200,
            ),
            "EVO_MAX_CALLS_PER_RUN": _positive_setting(
                values, "max_calls_per_run", existing, "EVO_MAX_CALLS_PER_RUN", 4
            ),
            "EVO_REQUEST_TIMEOUT_SECONDS": _positive_setting(
                values,
                "request_timeout_seconds",
                existing,
                "EVO_REQUEST_TIMEOUT_SECONDS",
                90 if provider == "nvidia" else 45,
            ),
            "EVO_SANDBOX_IMAGE": str(
                values.get(
                    "sandbox_image",
                    existing.get("EVO_SANDBOX_IMAGE", ""),
                )
            ).strip(),
            "EVO_SANDBOX_ENGINE": _sandbox_engine_setting(
                values.get(
                    "sandbox_engine",
                    existing.get("EVO_SANDBOX_ENGINE", "podman"),
                )
            ),
            "EVO_EVALUATION_COMMAND": str(
                values.get(
                    "evaluation_command",
                    existing.get(
                        "EVO_EVALUATION_COMMAND",
                        "python -m unittest discover -s tests",
                    ),
                )
            ).strip(),
            "EVO_SANDBOX_TIMEOUT_SECONDS": str(
                _bounded_integer_value(
                    values.get(
                        "sandbox_timeout_seconds",
                        existing.get("EVO_SANDBOX_TIMEOUT_SECONDS", 60),
                    ),
                    name="EVO_SANDBOX_TIMEOUT_SECONDS",
                    minimum=1,
                    maximum=600,
                )
            ),
            "EVO_NVIDIA_GENERATION_PROFILE": _nvidia_profile_setting(
                values.get(
                    "nvidia_generation_profile",
                    existing.get("EVO_NVIDIA_GENERATION_PROFILE", PROFILE_BALANCED),
                )
            ),
        }
        if payload["EVO_SANDBOX_IMAGE"] and not payload["EVO_EVALUATION_COMMAND"]:
            raise ConfigurationError(
                "EVO_EVALUATION_COMMAND cannot be empty when sandboxing is enabled."
            )
        for other in SUPPORTED_PROVIDERS:
            if other == provider:
                continue
            other_key = PROVIDER_KEY_NAMES[other]
            if other_key in existing:
                payload[other_key] = existing[other_key]
            other_model = PROVIDER_MODEL_NAMES[other]
            if other_model in existing:
                payload[other_model] = existing[other_model]
            other_base = PROVIDER_BASE_URL_NAMES[other]
            if other_base in existing:
                payload[other_base] = existing[other_base]
        for optional in (
            "EVO_NVIDIA_TEMPERATURE",
            "EVO_NVIDIA_TOP_P",
            "EVO_NVIDIA_JSON_MODE",
            "EVO_NVIDIA_REASONING_EFFORT",
        ):
            if optional in existing and existing[optional].strip():
                payload[optional] = existing[optional]

        _write_env_file(self.env_file, payload)
        for name, value in payload.items():
            os.environ[name] = value
        return self.public_settings()


def _positive_setting(
    values: dict[str, object],
    field_name: str,
    existing: dict[str, str],
    env_name: str,
    default: int,
) -> str:
    raw = values.get(field_name, existing.get(env_name, default))
    try:
        number = int(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{env_name} باید یک عدد صحیح باشد") from exc
    if number <= 0:
        raise ConfigurationError(f"{env_name} باید بزرگ‌تر از صفر باشد")
    return str(number)


def _bounded_integer_environment(
    name: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ConfigurationError(f"{name} باید یک عدد صحیح باشد") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(
            f"{name} must be between {minimum} and {maximum}."
        )
    return value


def _bounded_integer_value(
    raw: object,
    *,
    name: str,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{name} باید یک عدد صحیح باشد") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(
            f"{name} must be between {minimum} and {maximum}."
        )
    return value


def _sandbox_engine_setting(raw: object) -> str:
    value = str(raw).strip().lower()
    if value not in {"podman", "docker"}:
        raise ConfigurationError("Sandbox engine must be podman or docker.")
    return value


def _nvidia_profile_setting(raw: object) -> str:
    value = str(raw).strip().lower()
    if value not in SUPPORTED_PROFILES:
        raise ConfigurationError(
            "EVO_NVIDIA_GENERATION_PROFILE must be one of: "
            + ", ".join(SUPPORTED_PROFILES)
        )
    return value


def _team_ids(traits: dict[str, Any] | None) -> tuple[str, ...]:
    plan = (traits or {}).get("team_plan")
    members = plan.get("members", []) if isinstance(plan, dict) else []
    identifiers = [
        str(member.get("organism_id", "")).strip()
        for member in members
        if isinstance(member, dict)
    ]
    return tuple(identifier for identifier in identifiers if identifier)[:3] or (
        "cell-0001",
    )


def _read_env_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        values[name.strip()] = value.strip().strip("\"'")
    return values


def _write_env_file(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# مدیریت‌شده توسط رابط کاربری و خط فرمان EVO؛ کلیدهای واقعی را فقط در این فایل نگه دارید.",
        f"EVO_PROVIDER={values['EVO_PROVIDER']}",
        "",
        "# Groq",
        f"GROQ_API_KEY={values.get('GROQ_API_KEY', '')}",
        f"EVO_GROQ_MODEL={values.get('EVO_GROQ_MODEL', PROVIDER_DEFAULTS['groq']['model'])}",
        (
            "EVO_GROQ_BASE_URL="
            f"{values.get('EVO_GROQ_BASE_URL', PROVIDER_DEFAULTS['groq']['base_url'])}"
        ),
        "",
        "# NVIDIA NIM",
        f"NVIDIA_API_KEY={values.get('NVIDIA_API_KEY', '')}",
        (
            "EVO_NVIDIA_MODEL="
            f"{values.get('EVO_NVIDIA_MODEL', PROVIDER_DEFAULTS['nvidia']['model'])}"
        ),
        (
            "EVO_NVIDIA_BASE_URL="
            f"{values.get('EVO_NVIDIA_BASE_URL', PROVIDER_DEFAULTS['nvidia']['base_url'])}"
        ),
        (
            "EVO_NVIDIA_GENERATION_PROFILE="
            f"{values.get('EVO_NVIDIA_GENERATION_PROFILE', PROFILE_BALANCED)}"
        ),
        *[
            f"{name}={values[name]}"
            for name in (
                "EVO_NVIDIA_TEMPERATURE",
                "EVO_NVIDIA_TOP_P",
                "EVO_NVIDIA_JSON_MODE",
                "EVO_NVIDIA_REASONING_EFFORT",
            )
            if name in values and str(values[name]).strip()
        ],
        "",
        f"EVO_MAX_INPUT_TOKENS={values['EVO_MAX_INPUT_TOKENS']}",
        f"EVO_MAX_OUTPUT_TOKENS={values['EVO_MAX_OUTPUT_TOKENS']}",
        f"EVO_MAX_CALLS_PER_RUN={values['EVO_MAX_CALLS_PER_RUN']}",
        f"EVO_REQUEST_TIMEOUT_SECONDS={values['EVO_REQUEST_TIMEOUT_SECONDS']}",
        "",
        "# Rootless candidate evaluation (leave image empty to disable)",
        f"EVO_SANDBOX_IMAGE={values.get('EVO_SANDBOX_IMAGE', '')}",
        f"EVO_SANDBOX_ENGINE={values.get('EVO_SANDBOX_ENGINE', 'podman')}",
        f"EVO_EVALUATION_COMMAND={values.get('EVO_EVALUATION_COMMAND', '')}",
        (
            "EVO_SANDBOX_TIMEOUT_SECONDS="
            f"{values.get('EVO_SANDBOX_TIMEOUT_SECONDS', '60')}"
        ),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def serialize_error(exc: Exception) -> dict[str, str]:
    if isinstance(exc, (ConfigurationError, ProviderError, BudgetExceeded, ValueError)):
        return {"error": str(exc)}
    return {"error": "خطای پیش‌بینی‌نشده در EVO"}
