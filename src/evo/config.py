"""Host-owned runtime configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


class ConfigurationError(ValueError):
    """Raised when required host configuration is missing or invalid."""


def load_env_file(path: Path) -> None:
    """Load a minimal dotenv file without overwriting existing environment."""
    if not path.exists():
        raise ConfigurationError(f"Environment file does not exist: {path}")

    for line_number, raw_line in enumerate(path.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigurationError(
                f"Invalid environment entry at {path}:{line_number}"
            )
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip("\"'")
        if not name:
            raise ConfigurationError(
                f"Empty environment name at {path}:{line_number}"
            )
        os.environ.setdefault(name, value)


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be positive")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable settings owned by the host kernel."""

    provider: str
    api_key: str
    model: str
    base_url: str
    max_input_tokens: int = 6000
    max_output_tokens: int = 1200
    max_calls_per_run: int = 4
    request_timeout_seconds: int = 45

    @classmethod
    def from_environment(cls) -> "Settings":
        provider = os.getenv("EVO_PROVIDER", "groq").strip().lower()
        providers = {
            "groq": {
                "key_name": "GROQ_API_KEY",
                "model": "openai/gpt-oss-20b",
                "base_url": "https://api.groq.com/openai/v1",
                "base_url_name": "EVO_GROQ_BASE_URL",
            },
            "nvidia": {
                "key_name": "NVIDIA_API_KEY",
                "model": "meta/llama-3.1-70b-instruct",
                "base_url": "https://integrate.api.nvidia.com/v1",
                "base_url_name": "EVO_NVIDIA_BASE_URL",
            },
        }
        if provider not in providers:
            raise ConfigurationError(
                "EVO_PROVIDER must be one of: " + ", ".join(sorted(providers))
            )
        selected = providers[provider]
        key_name = selected["key_name"]
        key = os.getenv(key_name, "").strip()
        if not key:
            raise ConfigurationError(f"{key_name} is required for {provider}")
        base_url = os.getenv(
            selected["base_url_name"], selected["base_url"]
        ).rstrip("/")
        if not base_url.startswith("https://"):
            raise ConfigurationError(
                f"{selected['base_url_name']} must use HTTPS"
            )
        model = os.getenv(
            f"EVO_{provider.upper()}_MODEL",
            os.getenv("EVO_MODEL", selected["model"]),
        ).strip()
        if not model:
            raise ConfigurationError("Configured model cannot be empty")
        return cls(
            provider=provider,
            api_key=key,
            model=model,
            base_url=base_url,
            max_input_tokens=_positive_int("EVO_MAX_INPUT_TOKENS", 6000),
            max_output_tokens=_positive_int("EVO_MAX_OUTPUT_TOKENS", 1200),
            max_calls_per_run=_positive_int("EVO_MAX_CALLS_PER_RUN", 4),
            request_timeout_seconds=_positive_int(
                "EVO_REQUEST_TIMEOUT_SECONDS", 45
            ),
        )
