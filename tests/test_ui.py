from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
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
        self.assertEqual(payload["api_key"], "تنظیم‌شده")
        self.assertNotIn("test-groq-key", json.dumps(payload))

    def test_index_is_served(self):
        with urlopen(f"{self.base}/", timeout=5) as response:
            html = response.read().decode()
        self.assertIn("EVO", html)
        self.assertIn('lang="en"', html)
        self.assertIn('dir="ltr"', html)
        self.assertIn("Evolutionary Terrarium", html)
        self.assertIn('data-language="fa"', html)
        self.assertIn('id="autonomy-form"', html)
        self.assertIn('id="evolution-journal"', html)
        self.assertIn('id="achievement-gallery"', html)
        self.assertIn('id="lineage-map"', html)
        self.assertIn('id="population-roster"', html)
        self.assertIn('id="resource-pools"', html)
        self.assertIn('id="niche-distribution"', html)
        self.assertIn('id="cooperation-network"', html)
        self.assertIn('id="ecology-metrics"', html)
        self.assertIn('id="evaluation-evidence"', html)
        self.assertIn('id="team-observatory"', html)
        self.assertIn("Digital Petri Dish", html)
        self.assertIn("v0.6.0", html)
        self.assertIn('id="sandbox_image"', html)
        self.assertIn('id="evaluation_command"', html)
        self.assertIn('class="organism-visual"', html)
        self.assertIn('id="evolve-thinking"', html)
        self.assertIn('aria-busy="false"', html)

    def test_ui_assets_include_thinking_state_and_wrapped_results(self):
        with urlopen(f"{self.base}/static/app.js", timeout=5) as response:
            javascript = response.read().decode()
        with urlopen(f"{self.base}/static/app.css", timeout=5) as response:
            stylesheet = response.read().decode()

        self.assertIn("setEvolveThinking(true)", javascript)
        self.assertIn("setEvolveThinking(false)", javascript)
        self.assertIn("Thinking…", javascript)
        self.assertIn("در حال فکر کردن", javascript)
        self.assertIn('localStorage.getItem("evo-language") || "en"', javascript)
        self.assertIn('api("/api/autonomy")', javascript)
        self.assertIn('api("/api/petri-dish")', javascript)
        self.assertIn("renderPetriDish", javascript)
        self.assertIn("ACHIEVEMENT_CATALOG", javascript)
        self.assertIn("achievementUnlocked", javascript)
        self.assertIn("response.text()", javascript)
        self.assertIn("invalidServerResponse", javascript)
        self.assertIn("@keyframes heartbeat", stylesheet)
        self.assertIn("white-space: pre-wrap", stylesheet)
        self.assertIn("overflow-wrap: anywhere", stylesheet)
        self.assertIn("font-size: 12px", stylesheet)
        self.assertIn('[dir="rtl"] textarea', stylesheet)
        self.assertIn(".achievement-card", stylesheet)
        self.assertIn(".cell-core", stylesheet)
        self.assertIn(".lineage-map", stylesheet)
        self.assertIn(".organism-card", stylesheet)
        self.assertIn(".resource-track", stylesheet)
        self.assertIn(".niche-chip", stylesheet)
        self.assertIn(".cooperation-edge", stylesheet)
        self.assertIn(".metric-card", stylesheet)
        self.assertIn(".evidence-state", stylesheet)

    def test_autonomy_status_and_journal_endpoints(self):
        status, payload = self._request("GET", "/api/autonomy")
        self.assertEqual(status, 200)
        self.assertFalse(payload["enabled"])
        status, payload = self._request("GET", "/api/evolution-journal")
        self.assertEqual(status, 200)
        self.assertEqual(payload["entries"], [])

    def test_petri_dish_endpoint_has_founder_population(self):
        status, payload = self._request("GET", "/api/petri-dish")
        self.assertEqual(status, 200)
        self.assertEqual(payload["summary"]["living"], 6)
        self.assertEqual(payload["summary"]["epoch"], 0)
        self.assertEqual(len(payload["organisms"]), 6)
        self.assertEqual(payload["environment"]["phase"], "balanced")
        self.assertEqual(payload["summary"]["cooperation_links"], 0)
        self.assertIn("open_endedness_proxy", payload["metrics"])

    def test_probe_endpoint_uses_runtime(self):
        with patch.object(self.runtime, "probe", return_value="ok"):
            status, payload = self._request("POST", "/api/probe", {})
        self.assertEqual(status, 200)
        self.assertEqual(payload["message"], "ok")

    def test_doctor_endpoint_returns_json(self):
        with patch.object(
            self.runtime,
            "doctor",
            return_value={"provider": "groq", "model": "test-model"},
        ):
            status, payload = self._request("GET", "/api/doctor")
        self.assertEqual(status, 200)
        self.assertEqual(payload["provider"], "groq")

    def test_unexpected_doctor_failure_is_json(self):
        with patch.object(
            self.runtime,
            "doctor",
            side_effect=RuntimeError("private internal detail"),
        ):
            with self.assertRaises(HTTPError) as context:
                urlopen(f"{self.base}/api/doctor", timeout=5)
        self.assertEqual(context.exception.code, 500)
        self.assertEqual(
            context.exception.headers.get_content_type(),
            "application/json",
        )
        payload = json.loads(context.exception.read().decode())
        self.assertEqual(payload["error"], "خطای پیش‌بینی‌نشده در EVO")
        self.assertNotIn("private internal detail", json.dumps(payload))

    def test_unknown_api_endpoint_returns_json(self):
        with self.assertRaises(HTTPError) as context:
            urlopen(f"{self.base}/api/not-found", timeout=5)
        self.assertEqual(context.exception.code, 404)
        self.assertEqual(
            context.exception.headers.get_content_type(),
            "application/json",
        )
        self.assertIn("error", json.loads(context.exception.read().decode()))


if __name__ == "__main__":
    unittest.main()
