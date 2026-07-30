"""Shared host-facing operations used by the CLI and local UI."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import os

from evo.config import ConfigurationError, Settings, load_env_file
from evo.domain import EvolutionTask, Genome
from evo.evolution import EvolutionEngine
from evo.kernel.audit import AuditLog
from evo.kernel.budget import BudgetExceeded, RunBudget
from evo.kernel.policy import KernelPolicy
from evo.providers.base import ModelProvider
from evo.providers.groq import GroqProvider, ProviderError
from evo.providers.nvidia import NvidiaProvider

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
        provider_type = GroqProvider if resolved.provider == "groq" else NvidiaProvider
        return provider_type(
            api_key=resolved.api_key,
            model=resolved.model,
            base_url=resolved.base_url,
            timeout_seconds=resolved.request_timeout_seconds,
            max_output_tokens=resolved.max_output_tokens,
        )

    def public_settings(self) -> dict[str, object]:
        try:
            settings = self.load_settings()
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
            "api_key": "configured",
            "max_input_tokens": settings.max_input_tokens,
            "max_output_tokens": settings.max_output_tokens,
            "max_calls_per_run": settings.max_calls_per_run,
            "request_timeout_seconds": settings.request_timeout_seconds,
            "supported_providers": list(SUPPORTED_PROVIDERS),
            "audit_path": str(self.audit_path),
        }

    def doctor(self) -> dict[str, object]:
        settings = self.load_settings()
        return {
            "configuration": "valid",
            "provider": settings.provider,
            "model": settings.model,
            "api_key": "configured",
        }

    def probe(self) -> str:
        return self.build_provider().healthcheck()

    def evolve(
        self,
        *,
        task: str,
        mutable_paths: list[str] | None = None,
        organism_id: str = "cell-0001",
        task_id: str = "interactive",
    ) -> dict[str, object]:
        objective = task.strip()
        if not objective:
            raise ValueError("Task objective is required")
        paths = mutable_paths or ["organisms/"]
        cleaned = [path.strip() for path in paths if path and path.strip()]
        if not cleaned:
            raise ValueError("At least one mutable path is required")
        settings = self.load_settings()
        budget = RunBudget(
            max_calls=settings.max_calls_per_run,
            max_input_tokens=settings.max_input_tokens,
            max_output_tokens=settings.max_output_tokens,
        )
        engine = EvolutionEngine(
            provider=self.build_provider(settings),
            policy=KernelPolicy(),
            budget=budget,
            audit=AuditLog(self.audit_path),
        )
        candidate = engine.run_generation(
            Genome(
                organism_id=organism_id,
                mutable_paths=tuple(dict.fromkeys(cleaned)),
            ),
            EvolutionTask(task_id=task_id, objective=objective),
        )
        return asdict(candidate)

    def read_audit(self, *, limit: int = 50, query: str = "") -> list[dict[str, object]]:
        if limit <= 0:
            raise ValueError("Audit limit must be positive")
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
                "EVO_PROVIDER must be one of: " + ", ".join(SUPPORTED_PROVIDERS)
            )

        defaults = PROVIDER_DEFAULTS[provider]
        model = str(values.get("model", defaults["model"])).strip()
        if not model:
            raise ConfigurationError("Configured model cannot be empty")
        base_url = str(values.get("base_url", defaults["base_url"])).strip().rstrip("/")
        if not base_url.startswith("https://"):
            raise ConfigurationError("Provider base URL must use HTTPS")

        api_key = str(values.get("api_key", "")).strip()
        existing = _read_env_map(self.env_file)
        key_name = PROVIDER_KEY_NAMES[provider]
        if not api_key:
            api_key = existing.get(key_name, os.getenv(key_name, "")).strip()
        if not api_key:
            raise ConfigurationError(f"{key_name} is required for {provider}")

        payload = {
            "EVO_PROVIDER": provider,
            key_name: api_key,
            PROVIDER_MODEL_NAMES[provider]: model,
            PROVIDER_BASE_URL_NAMES[provider]: base_url,
            "EVO_MAX_INPUT_TOKENS": _positive_setting(
                values, "max_input_tokens", existing, "EVO_MAX_INPUT_TOKENS", 6000
            ),
            "EVO_MAX_OUTPUT_TOKENS": _positive_setting(
                values, "max_output_tokens", existing, "EVO_MAX_OUTPUT_TOKENS", 1200
            ),
            "EVO_MAX_CALLS_PER_RUN": _positive_setting(
                values, "max_calls_per_run", existing, "EVO_MAX_CALLS_PER_RUN", 4
            ),
            "EVO_REQUEST_TIMEOUT_SECONDS": _positive_setting(
                values,
                "request_timeout_seconds",
                existing,
                "EVO_REQUEST_TIMEOUT_SECONDS",
                45,
            ),
        }
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
        raise ConfigurationError(f"{env_name} must be an integer") from exc
    if number <= 0:
        raise ConfigurationError(f"{env_name} must be positive")
    return str(number)


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
        "# Managed by EVO Terrarium UI/CLI. Keep real keys only in this file.",
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
        "",
        f"EVO_MAX_INPUT_TOKENS={values['EVO_MAX_INPUT_TOKENS']}",
        f"EVO_MAX_OUTPUT_TOKENS={values['EVO_MAX_OUTPUT_TOKENS']}",
        f"EVO_MAX_CALLS_PER_RUN={values['EVO_MAX_CALLS_PER_RUN']}",
        f"EVO_REQUEST_TIMEOUT_SECONDS={values['EVO_REQUEST_TIMEOUT_SECONDS']}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def serialize_error(exc: Exception) -> dict[str, str]:
    if isinstance(exc, (ConfigurationError, ProviderError, BudgetExceeded, ValueError)):
        return {"error": str(exc)}
    return {"error": "Unexpected EVO failure"}
