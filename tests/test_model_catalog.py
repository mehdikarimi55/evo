from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch
import json
import unittest

from evo.providers.groq import GroqProvider
from evo.providers.groq_models import GROQ_MODEL_CATALOG
from evo.providers.nvidia_models import NVIDIA_MODEL_CATALOG
from evo.runtime import TerrariumRuntime


class ModelCatalogTests(unittest.TestCase):
    def test_nvidia_catalog_is_selectable_without_network(self):
        with TemporaryDirectory() as directory:
            runtime = TerrariumRuntime(workspace=Path(directory))
            with patch.dict("os.environ", {"EVO_PROVIDER": "nvidia"}, clear=False):
                payload = runtime.list_models("nvidia")
        self.assertTrue(payload["selectable"])
        self.assertEqual(payload["provider"], "nvidia")
        self.assertEqual(payload["source"], "catalog")
        self.assertIn("meta/llama-3.1-70b-instruct", payload["models"])
        self.assertEqual(
            set(NVIDIA_MODEL_CATALOG).issubset(set(payload["models"])),
            True,
        )

    def test_groq_catalog_is_selectable_without_network(self):
        with TemporaryDirectory() as directory:
            runtime = TerrariumRuntime(workspace=Path(directory))
            payload = runtime.list_models("groq")
        self.assertTrue(payload["selectable"])
        self.assertEqual(payload["provider"], "groq")
        self.assertEqual(payload["source"], "catalog")
        self.assertIn("openai/gpt-oss-20b", payload["models"])
        self.assertEqual(
            set(GROQ_MODEL_CATALOG).issubset(set(payload["models"])),
            True,
        )

    def test_groq_list_models_filters_non_chat_entries(self):
        provider = GroqProvider(
            api_key="test-key",
            model="openai/gpt-oss-20b",
            base_url="https://api.groq.com/openai/v1",
        )
        payload = {
            "data": [
                {"id": "openai/gpt-oss-20b"},
                {"id": "whisper-large-v3"},
                {"id": "llama-3.1-8b-instant"},
                {"id": "playai-tts"},
            ]
        }
        response = MagicMock()
        response.read.return_value = json.dumps(payload).encode()
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        with patch("evo.providers.groq.urlopen", return_value=response):
            models = provider.list_models()
        self.assertEqual(
            models,
            ["llama-3.1-8b-instant", "openai/gpt-oss-20b"],
        )
        self.assertNotIn("whisper-large-v3", models)


if __name__ == "__main__":
    unittest.main()
