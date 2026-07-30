"""Provider-neutral model capability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ModelReply:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    request_id: str | None = None


class ModelProvider(Protocol):
    def generate_json(self, *, system: str, user: str) -> ModelReply:
        """Generate one JSON object without exposing provider credentials."""

    def healthcheck(self) -> str:
        """Return a non-secret provider health summary."""

