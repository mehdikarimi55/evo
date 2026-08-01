"""NVIDIA NIM adapter using its OpenAI-compatible HTTPS endpoint."""

from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

from evo.providers.base import ModelReply
from evo.providers.groq import ProviderError, network_failure_detail
from evo.providers.nvidia_generation import (
    JSON_MODE_STRICT,
    NvidiaGenerationProfile,
    extract_json_object,
)
from evo.providers.nvidia_models import NVIDIA_MODEL_CATALOG


class NvidiaProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: int = 45,
        max_output_tokens: int = 1200,
        generation_profile: NvidiaGenerationProfile | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("وارد کردن کلید API انویدیا الزامی است")
        self._api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens
        self.generation_profile = generation_profile or NvidiaGenerationProfile()

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
                f"انویدیا خطای HTTP {exc.code} برگرداند{suffix}"
            ) from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(
                f"درخواست از انویدیا ناموفق بود: {network_failure_detail(exc)}"
            ) from exc

    def list_models(self) -> list[str]:
        payload = self._request("/models")
        model_ids = sorted(
            {
                str(item.get("id"))
                for item in payload.get("data", [])
                if item.get("id")
            }
        )
        if model_ids:
            return model_ids
        return list(NVIDIA_MODEL_CATALOG)

    def healthcheck(self) -> str:
        model_ids = set(self.list_models())
        if self.model not in model_ids:
            raise ProviderError(
                "مدل انتخاب‌شده در این پروژه انویدیا در دسترس نیست: "
                f"{self.model}"
            )
        return f"اتصال به انویدیا برقرار است؛ مدل در دسترس: {self.model}"

    def generate_json(self, *, system: str, user: str) -> ModelReply:
        profile = self.generation_profile
        system_prompt = system
        if profile.json_mode != JSON_MODE_STRICT:
            system_prompt = (
                f"{system.rstrip()}\n\n"
                "You may reason privately first. End with exactly one JSON object "
                "and no trailing commentary. Prefer a ```json fenced block for the "
                "final object when reasoning is present."
            )
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
            ],
            "temperature": profile.temperature,
            "top_p": profile.top_p,
            "max_tokens": self.max_output_tokens,
        }
        if profile.json_mode == JSON_MODE_STRICT:
            payload["response_format"] = {"type": "json_object"}
        if profile.should_enable_reasoning(self.model):
            payload["reasoning_effort"] = profile.reasoning_effort
        result = self._request("/chat/completions", payload)
        try:
            choice = result["choices"][0]
            message = choice.get("message", {})
            content = message.get("content")
            if content is None and isinstance(message.get("reasoning_content"), str):
                content = message.get("reasoning_content")
            text = extract_json_object(str(content or ""))
            usage = result.get("usage", {})
            return ModelReply(
                text=text,
                input_tokens=int(usage.get("prompt_tokens", 0)),
                output_tokens=int(usage.get("completion_tokens", 0)),
                model=str(result.get("model", self.model)),
                request_id=result.get("id"),
            )
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderError(
                "ساختار پاسخ انویدیا با قالب مورد انتظار سازگار نیست"
            ) from exc
