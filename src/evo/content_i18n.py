"""Cached batch translation for public journey and journal display text."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence
import hashlib
import json
import re

from evo.providers.base import ModelProvider
from evo.providers.groq import ProviderError

TranslateFn = Callable[[Sequence[str]], list[str]]

_LATIN_RE = re.compile(r"[A-Za-z]")
_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

TRANSLATION_SYSTEM = (
    "You translate research-journal text into fluent Persian (Farsi). "
    "Return ONLY a JSON object shaped as "
    '{"translations":["..."]} with the same number of strings, same order. '
    "Keep organism IDs, file paths, timestamps, code identifiers, and numbers "
    "unchanged. Do not add commentary."
)


class TranslationError(RuntimeError):
    """Raised when a translation batch cannot be completed safely."""


def looks_latin_dominant(value: object) -> bool:
    """Return True when text is mostly Latin and likely needs FA localization."""
    text = str(value or "").strip()
    if len(text) < 3:
        return False
    latin = len(_LATIN_RE.findall(text))
    arabic = len(_ARABIC_RE.findall(text))
    return latin >= 3 and latin > arabic


def text_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class TranslationCache:
    """Persistent source→Persian map keyed by content fingerprint."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._entries: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if isinstance(payload, dict):
            self._entries = {
                str(key): str(value)
                for key, value in payload.items()
                if isinstance(value, str)
            }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self._entries, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def get(self, source: str) -> str | None:
        return self._entries.get(text_fingerprint(source))

    def put_many(self, mapping: dict[str, str]) -> None:
        changed = False
        for source, translated in mapping.items():
            key = text_fingerprint(source)
            if self._entries.get(key) != translated:
                self._entries[key] = translated
                changed = True
        if changed:
            self._save()


def translate_missing(
    texts: Sequence[str],
    *,
    cache: TranslationCache,
    provider: ModelProvider,
    chunk_size: int = 12,
) -> dict[str, str]:
    """Translate Latin-dominant strings to Persian, using cache when possible."""
    unique: list[str] = []
    seen: set[str] = set()
    resolved: dict[str, str] = {}
    for raw in texts:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        if not looks_latin_dominant(text):
            resolved[text] = text
            continue
        cached = cache.get(text)
        if cached is not None:
            resolved[text] = cached
            continue
        unique.append(text)

    for offset in range(0, len(unique), max(1, chunk_size)):
        chunk = unique[offset : offset + max(1, chunk_size)]
        translated = _translate_chunk(provider, chunk)
        batch = dict(zip(chunk, translated, strict=True))
        cache.put_many(batch)
        resolved.update(batch)
    return resolved


def _translate_chunk(provider: ModelProvider, chunk: list[str]) -> list[str]:
    user = json.dumps({"texts": chunk}, ensure_ascii=False)
    try:
        reply = provider.generate_json(system=TRANSLATION_SYSTEM, user=user)
        payload = json.loads(reply.text)
    except (ProviderError, ValueError, json.JSONDecodeError, TypeError, OSError) as exc:
        raise TranslationError("Persian translation request failed.") from exc
    translations = payload.get("translations") if isinstance(payload, dict) else None
    if not isinstance(translations, list) or len(translations) != len(chunk):
        raise TranslationError("Persian translation returned an invalid batch.")
    cleaned: list[str] = []
    for index, item in enumerate(translations):
        text = str(item or "").strip()
        cleaned.append(text or chunk[index])
    return cleaned


def apply_translations(value: object, mapping: dict[str, str]) -> object:
    """Replace Latin-dominant strings inside nested JSON-like structures."""
    if isinstance(value, str):
        if not looks_latin_dominant(value):
            return value
        if value in mapping:
            return mapping[value]
        stripped = value.strip()
        return mapping.get(stripped, value)
    if isinstance(value, list):
        return [apply_translations(item, mapping) for item in value]
    if isinstance(value, dict):
        return {
            key: apply_translations(item, mapping)
            for key, item in value.items()
        }
    return value


def collect_translatable_texts(entries: Sequence[dict[str, object]]) -> list[str]:
    """Collect free-text journal fields that may need Persian localization."""
    fields = (
        "objective",
        "summary",
        "rationale",
        "expected_benefit",
        "risk",
        "rejection_reason",
        "message",
    )
    collected: list[str] = []
    for entry in entries:
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            continue
        for field in fields:
            value = payload.get(field)
            if isinstance(value, str) and looks_latin_dominant(value):
                collected.append(value.strip())
    return collected
