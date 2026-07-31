from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import unittest
from unittest.mock import patch

from evo.config import ConfigurationError
from evo.runtime import TerrariumRuntime


class RuntimeTests(unittest.TestCase):
    def test_save_settings_persists_provider_without_exposing_key(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            env_file = root / ".env.local"
            runtime = TerrariumRuntime(env_file=env_file, workspace=root)
            public = runtime.save_settings(
                {
                    "provider": "nvidia",
                    "api_key": "test-nvidia-key",
                    "model": "vendor/test-model",
                    "base_url": "https://integrate.api.nvidia.com/v1",
                    "max_input_tokens": 1000,
                    "max_output_tokens": 200,
                    "max_calls_per_run": 2,
                    "request_timeout_seconds": 30,
                    "sandbox_image": "python:3.13-alpine",
                    "sandbox_engine": "podman",
                    "evaluation_command": "python -m unittest",
                    "sandbox_timeout_seconds": 90,
                }
            )
            self.assertTrue(public["configured"])
            self.assertEqual(public["provider"], "nvidia")
            self.assertEqual(public["api_key"], "تنظیم‌شده")
            self.assertIn("NVIDIA_API_KEY=test-nvidia-key", env_file.read_text())
            self.assertEqual(public["sandbox_image"], "python:3.13-alpine")
            self.assertIn("EVO_SANDBOX_ENGINE=podman", env_file.read_text())
            self.assertIn(
                "EVO_EVALUATION_COMMAND=python -m unittest",
                env_file.read_text(),
            )

    def test_rejects_invalid_sandbox_settings(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = TerrariumRuntime(
                env_file=root / ".env.local", workspace=root
            )
            base = {
                "provider": "groq",
                "api_key": "test-key",
                "model": "openai/gpt-oss-20b",
                "base_url": "https://api.groq.com/openai/v1",
                "sandbox_image": "python:3.13-alpine",
            }
            with self.assertRaisesRegex(ConfigurationError, "podman or docker"):
                runtime.save_settings({**base, "sandbox_engine": "rootful"})
            with self.assertRaisesRegex(ConfigurationError, "cannot be empty"):
                runtime.save_settings(
                    {
                        **base,
                        "sandbox_engine": "podman",
                        "evaluation_command": "",
                    }
                )

    def test_read_audit_supports_search(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            audit = root / "audit.jsonl"
            audit.write_text(
                json.dumps(
                    {
                        "timestamp": "2026-01-01T00:00:00+00:00",
                        "event_type": "generation.completed",
                        "payload": {"status": "eligible", "model": "alpha"},
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "timestamp": "2026-01-01T00:01:00+00:00",
                        "event_type": "generation.completed",
                        "payload": {"status": "rejected", "model": "beta"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            runtime = TerrariumRuntime(
                env_file=root / ".env.local",
                audit_path=audit,
                workspace=root,
            )
            matches = runtime.read_audit(query="rejected")
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["payload"]["model"], "beta")

    def test_public_settings_reports_missing_key(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = TerrariumRuntime(
                env_file=root / ".env.local", workspace=root
            )
            with patch.dict(os.environ, {"EVO_PROVIDER": "groq"}, clear=True):
                public = runtime.public_settings()
            self.assertFalse(public["configured"])
            self.assertIn("GROQ_API_KEY", public["error"])

    def test_save_settings_rejects_http_base_url(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = TerrariumRuntime(
                env_file=root / ".env.local", workspace=root
            )
            with self.assertRaises(ConfigurationError):
                runtime.save_settings(
                    {
                        "provider": "groq",
                        "api_key": "test-key",
                        "model": "openai/gpt-oss-20b",
                        "base_url": "http://example.com",
                    }
                )


if __name__ == "__main__":
    unittest.main()
