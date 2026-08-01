"""Host-owned NVIDIA NIM decoding profiles for proposal generation."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re

from evo.config import ConfigurationError

PROFILE_PRECISE = "precise"
PROFILE_BALANCED = "balanced"
PROFILE_EXPLORATORY = "exploratory"
SUPPORTED_PROFILES = (PROFILE_PRECISE, PROFILE_BALANCED, PROFILE_EXPLORATORY)

JSON_MODE_STRICT = "strict"
JSON_MODE_EXTRACT = "extract"
SUPPORTED_JSON_MODES = (JSON_MODE_STRICT, JSON_MODE_EXTRACT)

REASONING_NONE = "none"
REASONING_LOW = "low"
REASONING_MEDIUM = "medium"
REASONING_HIGH = "high"
SUPPORTED_REASONING = (
    REASONING_NONE,
    REASONING_LOW,
    REASONING_MEDIUM,
    REASONING_HIGH,
)

REASONING_MODEL_MARKERS = (
    "r1",
    "reasoning",
    "qwq",
    "nemotron",
    "deepseek-r1",
    "o1",
    "o3",
)

_FENCED_JSON = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class NvidiaGenerationProfile:
    """Sampling and structuring knobs owned by the host, not the organism."""

    mode: str = PROFILE_BALANCED
    temperature: float = 0.7
    top_p: float = 0.95
    json_mode: str = JSON_MODE_EXTRACT
    reasoning_effort: str = REASONING_NONE

    @classmethod
    def from_environment(cls) -> "NvidiaGenerationProfile":
        mode = os.getenv("EVO_NVIDIA_GENERATION_PROFILE", PROFILE_BALANCED).strip().lower()
        if mode not in SUPPORTED_PROFILES:
            raise ConfigurationError(
                "EVO_NVIDIA_GENERATION_PROFILE must be one of: "
                + ", ".join(SUPPORTED_PROFILES)
            )
        presets = {
            PROFILE_PRECISE: (0.2, 0.9, JSON_MODE_STRICT, REASONING_NONE),
            PROFILE_BALANCED: (0.7, 0.95, JSON_MODE_EXTRACT, REASONING_MEDIUM),
            PROFILE_EXPLORATORY: (1.0, 0.95, JSON_MODE_EXTRACT, REASONING_HIGH),
        }
        temperature, top_p, json_mode, reasoning = presets[mode]
        temperature = _bounded_float(
            "EVO_NVIDIA_TEMPERATURE",
            default=temperature,
            minimum=0.0,
            maximum=2.0,
        )
        top_p = _bounded_float(
            "EVO_NVIDIA_TOP_P",
            default=top_p,
            minimum=0.0,
            maximum=1.0,
        )
        json_mode = os.getenv("EVO_NVIDIA_JSON_MODE", json_mode).strip().lower()
        if json_mode not in SUPPORTED_JSON_MODES:
            raise ConfigurationError(
                "EVO_NVIDIA_JSON_MODE must be one of: "
                + ", ".join(SUPPORTED_JSON_MODES)
            )
        reasoning = os.getenv(
            "EVO_NVIDIA_REASONING_EFFORT", reasoning
        ).strip().lower()
        if reasoning not in SUPPORTED_REASONING:
            raise ConfigurationError(
                "EVO_NVIDIA_REASONING_EFFORT must be one of: "
                + ", ".join(SUPPORTED_REASONING)
            )
        return cls(
            mode=mode,
            temperature=temperature,
            top_p=top_p,
            json_mode=json_mode,
            reasoning_effort=reasoning,
        )

    def public_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "json_mode": self.json_mode,
            "reasoning_effort": self.reasoning_effort,
        }

    def should_enable_reasoning(self, model: str) -> bool:
        if self.reasoning_effort == REASONING_NONE:
            return False
        lowered = model.lower()
        return any(marker in lowered for marker in REASONING_MODEL_MARKERS)


def default_max_output_tokens_for_provider(provider: str) -> int:
    return 4096 if provider == "nvidia" else 1200


def default_timeout_seconds_for_provider(provider: str) -> int:
    return 90 if provider == "nvidia" else 45


def extract_json_object(text: str) -> str:
    """Extract one JSON object from model text; fail closed if ambiguous."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Model response did not contain JSON.")
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
    fenced = _FENCED_JSON.findall(raw)
    for candidate in reversed(fenced):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return json.dumps(parsed, ensure_ascii=False)
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Model response did not contain a JSON object.")
    candidate = raw[start : end + 1]
    parsed = json.loads(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("Extracted JSON must be an object.")
    return json.dumps(parsed, ensure_ascii=False)


def _bounded_float(
    name: str,
    *,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        value = float(str(raw).strip())
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(
            f"{name} must be between {minimum} and {maximum}"
        )
    return value
