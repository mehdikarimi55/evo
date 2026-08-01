import json
import os
import unittest
from unittest.mock import patch

from evo.config import ConfigurationError, Settings
from evo.providers.nvidia import NvidiaProvider
from evo.providers.nvidia_generation import (
    PROFILE_BALANCED,
    PROFILE_EXPLORATORY,
    PROFILE_PRECISE,
    NvidiaGenerationProfile,
    extract_json_object,
)


class FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return self._body


class NvidiaGenerationProfileTests(unittest.TestCase):
    def test_balanced_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            profile = NvidiaGenerationProfile.from_environment()
        self.assertEqual(profile.mode, PROFILE_BALANCED)
        self.assertEqual(profile.temperature, 0.7)
        self.assertEqual(profile.top_p, 0.95)
        self.assertEqual(profile.json_mode, "extract")

    def test_exploratory_profile(self):
        with patch.dict(
            os.environ,
            {"EVO_NVIDIA_GENERATION_PROFILE": PROFILE_EXPLORATORY},
            clear=True,
        ):
            profile = NvidiaGenerationProfile.from_environment()
        self.assertEqual(profile.temperature, 1.0)
        self.assertEqual(profile.reasoning_effort, "high")

    def test_rejects_invalid_profile(self):
        with patch.dict(
            os.environ,
            {"EVO_NVIDIA_GENERATION_PROFILE": "wild"},
            clear=True,
        ):
            with self.assertRaises(ConfigurationError):
                NvidiaGenerationProfile.from_environment()

    def test_extract_json_from_reasoning_text(self):
        text = (
            "Thinking...\n"
            "```json\n"
            '{"target_path": "organisms/a.py", "summary": "x", '
            '"rationale": "y", "expected_benefit": "z", "risk": "r"}\n'
            "```\n"
        )
        extracted = extract_json_object(text)
        payload = json.loads(extracted)
        self.assertEqual(payload["target_path"], "organisms/a.py")

    def test_reasoning_enabled_only_for_matching_models(self):
        profile = NvidiaGenerationProfile(
            mode=PROFILE_BALANCED,
            temperature=0.7,
            top_p=0.95,
            json_mode="extract",
            reasoning_effort="medium",
        )
        self.assertTrue(profile.should_enable_reasoning("deepseek-ai/deepseek-r1"))
        self.assertFalse(
            profile.should_enable_reasoning("meta/llama-3.1-70b-instruct")
        )


class NvidiaProviderProfileTests(unittest.TestCase):
    def test_generate_json_uses_balanced_sampling_and_extracts_object(self):
        response = {
            "id": "request-1",
            "model": "vendor/test-model",
            "choices": [
                {
                    "message": {
                        "content": 'notes\n{"ok": true}\n',
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4},
        }
        provider = NvidiaProvider(
            api_key="secret",
            model="vendor/test-model",
            base_url="https://example.invalid/v1",
            max_output_tokens=4096,
            generation_profile=NvidiaGenerationProfile(
                mode=PROFILE_BALANCED,
                temperature=0.7,
                top_p=0.95,
                json_mode="extract",
                reasoning_effort="none",
            ),
        )
        with patch(
            "evo.providers.nvidia.urlopen",
            return_value=FakeResponse(response),
        ) as mocked:
            reply = provider.generate_json(system="system", user="user")
        self.assertEqual(json.loads(reply.text), {"ok": True})
        request = mocked.call_args.args[0]
        body = json.loads(request.data.decode())
        self.assertEqual(body["temperature"], 0.7)
        self.assertEqual(body["top_p"], 0.95)
        self.assertEqual(body["max_tokens"], 4096)
        self.assertNotIn("response_format", body)

    def test_precise_profile_keeps_json_object_mode(self):
        response = {
            "id": "request-2",
            "model": "vendor/test-model",
            "choices": [{"message": {"content": '{"ok": true}'}}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 2},
        }
        provider = NvidiaProvider(
            api_key="secret",
            model="vendor/test-model",
            base_url="https://example.invalid/v1",
            generation_profile=NvidiaGenerationProfile(
                mode=PROFILE_PRECISE,
                temperature=0.2,
                top_p=0.9,
                json_mode="strict",
                reasoning_effort="none",
            ),
        )
        with patch(
            "evo.providers.nvidia.urlopen",
            return_value=FakeResponse(response),
        ) as mocked:
            provider.generate_json(system="system", user="user")
        body = json.loads(mocked.call_args.args[0].data.decode())
        self.assertEqual(body["response_format"], {"type": "json_object"})
        self.assertEqual(body["temperature"], 0.2)

    def test_reasoning_effort_attached_for_r1_models(self):
        response = {
            "id": "request-3",
            "model": "deepseek-ai/deepseek-r1",
            "choices": [{"message": {"content": '{"ok": true}'}}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 2},
        }
        provider = NvidiaProvider(
            api_key="secret",
            model="deepseek-ai/deepseek-r1",
            base_url="https://example.invalid/v1",
            generation_profile=NvidiaGenerationProfile(
                mode=PROFILE_BALANCED,
                temperature=0.7,
                top_p=0.95,
                json_mode="extract",
                reasoning_effort="medium",
            ),
        )
        with patch(
            "evo.providers.nvidia.urlopen",
            return_value=FakeResponse(response),
        ) as mocked:
            provider.generate_json(system="system", user="user")
        body = json.loads(mocked.call_args.args[0].data.decode())
        self.assertEqual(body["reasoning_effort"], "medium")


class NvidiaSettingsDefaultsTests(unittest.TestCase):
    def test_nvidia_defaults_raise_output_budget(self):
        environment = {
            "EVO_PROVIDER": "nvidia",
            "NVIDIA_API_KEY": "test-key",
            "EVO_NVIDIA_MODEL": "meta/llama-3.1-70b-instruct",
        }
        with patch.dict(os.environ, environment, clear=True):
            settings = Settings.from_environment()
        self.assertEqual(settings.max_output_tokens, 4096)
        self.assertEqual(settings.request_timeout_seconds, 90)
        self.assertEqual(settings.nvidia_generation.mode, PROFILE_BALANCED)


if __name__ == "__main__":
    unittest.main()
