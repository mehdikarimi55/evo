from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.request import Request, urlopen
import json
import unittest
from unittest.mock import patch

from evo.runtime import TerrariumRuntime
from evo.ui.server import TerrariumUIServer


class UIServerTests(unittest.TestCase):
    def setUp(self):
        self._directory = TemporaryDirectory()
        root = Path(self._directory.name)
        self.env_file = root / ".env.local"
        self.audit_path = root / "audit.jsonl"
        self.runtime = TerrariumRuntime(
            env_file=self.env_file,
            audit_path=self.audit_path,
            workspace=root,
        )
        self.runtime.save_settings(
            {
                "provider": "groq",
                "api_key": "test-groq-key",
                "model": "openai/gpt-oss-20b",
                "base_url": "https://api.groq.com/openai/v1",
            }
        )
        self.server = TerrariumUIServer(("127.0.0.1", 0), self.runtime)
        host, port = self.server.server_address
        self.base = f"http://{host}:{port}"
        self._thread = Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self._directory.cleanup()

    def _request(self, method: str, path: str, payload: dict | None = None):
        body = None if payload is None else json.dumps(payload).encode()
        request = Request(
            f"{self.base}{path}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode())

    def test_settings_endpoint_hides_api_key(self):
        status, payload = self._request("GET", "/api/settings")
        self.assertEqual(status, 200)
        self.assertEqual(payload["api_key"], "configured")
        self.assertNotIn("test-groq-key", json.dumps(payload))

    def test_index_is_served(self):
        with urlopen(f"{self.base}/", timeout=5) as response:
            html = response.read().decode()
        self.assertIn("EVO", html)
        self.assertIn("Terrarium", html)
        self.assertIn('id="evolve-thinking"', html)
        self.assertIn('aria-busy="false"', html)

    def test_ui_assets_include_thinking_state_and_wrapped_results(self):
        with urlopen(f"{self.base}/static/app.js", timeout=5) as response:
            javascript = response.read().decode()
        with urlopen(f"{self.base}/static/app.css", timeout=5) as response:
            stylesheet = response.read().decode()

        self.assertIn("setEvolveThinking(true)", javascript)
        self.assertIn("setEvolveThinking(false)", javascript)
        self.assertIn("@keyframes heartbeat", stylesheet)
        self.assertIn("white-space: pre-wrap", stylesheet)
        self.assertIn("overflow-wrap: anywhere", stylesheet)

    def test_probe_endpoint_uses_runtime(self):
        with patch.object(self.runtime, "probe", return_value="ok"):
            status, payload = self._request("POST", "/api/probe", {})
        self.assertEqual(status, 200)
        self.assertEqual(payload["message"], "ok")


if __name__ == "__main__":
    unittest.main()
