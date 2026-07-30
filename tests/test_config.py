import os
import unittest
from unittest.mock import patch

from evo.config import ConfigurationError, Settings


class SettingsTests(unittest.TestCase):
    def test_selects_nvidia_without_requiring_groq_key(self):
        environment = {
            "EVO_PROVIDER": "nvidia",
            "NVIDIA_API_KEY": "test-nvidia-key",
            "EVO_NVIDIA_MODEL": "vendor/test-model",
        }
        with patch.dict(os.environ, environment, clear=True):
            settings = Settings.from_environment()
        self.assertEqual(settings.provider, "nvidia")
        self.assertEqual(settings.api_key, "test-nvidia-key")
        self.assertEqual(settings.model, "vendor/test-model")
        self.assertEqual(
            settings.base_url, "https://integrate.api.nvidia.com/v1"
        )

    def test_rejects_unknown_provider(self):
        with patch.dict(os.environ, {"EVO_PROVIDER": "unknown"}, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_environment()


if __name__ == "__main__":
    unittest.main()
