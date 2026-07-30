"""NVIDIA NIM adapter using its OpenAI-compatible HTTPS endpoint."""

from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

from evo.providers.base import ModelReply
from evo.providers.groq import ProviderError


class NvidiaProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: int = 45,
        max_output_tokens: int = 1200,
    ) -> None:
        if not api_key:
            raise ValueError("NVIDIA API key is required")
        self._api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        method = "POST" if payload is not None else "GET"
        body = json.dumps(payload).encode() if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "evo-terrarium/0.1",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode())
        except HTTPError as exc:
            detail = ""
            try:
                error_body = json.loads(exc.read().decode())
                error = error_body.get("error", {})
                detail = (
                    str(error.get("message", ""))
                    if isinstance(error, dict)
                    else str(error)
                )
            except (ValueError, AttributeError):
                pass
            suffix = f": {detail[:240]}" if detail else ""
            raise ProviderError(
                f"NVIDIA returned HTTP {exc.code}{suffix}"
            ) from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(
                f"NVIDIA request failed: {type(exc).__name__}"
            ) from exc

    def healthcheck(self) -> str:
        payload = self._request("/models")
        model_ids = {
            str(item.get("id")) for item in payload.get("data", []) if item.get("id")
        }
        if self.model not in model_ids:
            raise ProviderError(
                "Configured model is not available to this NVIDIA project: "
                f"{self.model}"
            )
        return f"NVIDIA reachable; configured model available: {self.model}"

    def generate_json(self, *, system: str, user: str) -> ModelReply:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "max_tokens": self.max_output_tokens,
            "response_format": {"type": "json_object"},
        }
        result = self._request("/chat/completions", payload)
        try:
            choice = result["choices"][0]
            usage = result.get("usage", {})
            return ModelReply(
                text=choice["message"]["content"],
                input_tokens=int(usage.get("prompt_tokens", 0)),
                output_tokens=int(usage.get("completion_tokens", 0)),
                model=str(result.get("model", self.model)),
                request_id=result.get("id"),
            )
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(
                "NVIDIA returned an unexpected response schema"
            ) from exc
