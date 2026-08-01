import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from evo.providers.groq import ProviderError
from evo.providers.nvidia import NvidiaProvider


class FakeResponse:
    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return self._body


class NvidiaProviderTests(unittest.TestCase):
    def test_generate_json_maps_openai_compatible_response(self):
        response = {
            "id": "request-1",
            "model": "vendor/test-model",
            "choices": [{"message": {"content": '{"ok": true}'}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4},
        }
        provider = NvidiaProvider(
            api_key="secret",
            model="vendor/test-model",
            base_url="https://example.invalid/v1",
        )
        with patch(
            "evo.providers.nvidia.urlopen",
            return_value=FakeResponse(response),
        ):
            reply = provider.generate_json(system="system", user="user")
        self.assertEqual(reply.text, '{"ok": true}')
        self.assertEqual(reply.input_tokens, 10)
        self.assertEqual(reply.output_tokens, 4)
        self.assertEqual(reply.request_id, "request-1")

    def test_urlerror_includes_underlying_reason(self):
        provider = NvidiaProvider(
            api_key="secret",
            model="vendor/test-model",
            base_url="https://example.invalid/v1",
        )
        with patch(
            "evo.providers.nvidia.urlopen",
            side_effect=URLError(OSError("Network is unreachable")),
        ):
            with self.assertRaises(ProviderError) as context:
                provider.healthcheck()
        message = str(context.exception)
        self.assertIn("انویدیا", message)
        self.assertIn("Network is unreachable", message)


if __name__ == "__main__":
    unittest.main()
