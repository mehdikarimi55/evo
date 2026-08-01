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
from evo.trust_authority import create_reviewer_identity


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
        self.assertIn('data-i18n-help="helpHostStatus"', html)
        self.assertIn('data-i18n-help="helpDigitalPetriDish"', html)
        self.assertIn('id="journey-modal"', html)
        self.assertIn('id="journey-synopsis"', html)
        self.assertIn('id="journey-modal-body"', html)
        self.assertIn('id="achievement-gallery"', html)
        self.assertIn('id="lineage-map"', html)
        self.assertIn('id="lineage-viewport"', html)
        self.assertIn('id="lineage-zoom-in"', html)
        self.assertIn('id="lineage-zoom-out"', html)
        self.assertIn('id="lineage-zoom-reset"', html)
        self.assertIn('id="population-roster"', html)
        self.assertIn('id="resource-pools"', html)
        self.assertIn('id="niche-distribution"', html)
        self.assertIn('id="cooperation-network"', html)
        self.assertIn('id="ecology-metrics"', html)
        self.assertIn('id="evaluation-evidence"', html)
        self.assertIn('id="team-observatory"', html)
        self.assertIn('id="evidence-control-status"', html)
        self.assertIn('id="create-evidence-bundle"', html)
        self.assertIn('id="approval-form"', html)
        self.assertIn('id="trust-authority-status"', html)
        self.assertIn('id="attest-evidence"', html)
        self.assertIn('id="authorize-promotion"', html)
        self.assertIn('id="promotion-control-status"', html)
        self.assertIn('id="deployment-control-status"', html)
        self.assertIn("Digital Petri Dish", html)
        self.assertIn("v1.0.0", html)
        self.assertIn('id="sandbox_image"', html)
        self.assertIn('id="evaluation_command"', html)
        self.assertIn('class="organism-visual"', html)
        self.assertIn('id="evolve-thinking"', html)
        self.assertIn('aria-busy="false"', html)
        self.assertEqual(html.count('<details class="panel'), 8)
        self.assertNotIn('<details class="panel" open', html)
        self.assertNotIn('<details class="panel status-panel" open', html)
        self.assertNotIn('<details class="panel evolve-panel" open', html)
        self.assertNotIn('<details class="panel autonomy-panel" open', html)
        self.assertNotIn('<details class="panel petri-panel" open', html)
        self.assertNotIn('<details class="panel evidence-gate-panel" open', html)
        self.assertNotIn('<details class="panel journal-panel" open', html)
        self.assertIn('class="panel-summary"', html)
        self.assertIn('class="panel-body"', html)
        self.assertIn('data-stop-toggle', html)
        self.assertIn('id="global-search"', html)
        self.assertIn('id="settings-form"', html)
        self.assertIn('id="autonomy-badge"', html)
        self.assertIn('id="autonomy-stats"', html)
        self.assertIn('id="audit-body"', html)

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
        self.assertIn("GROQ_MODEL_FALLBACK", javascript)
        self.assertIn("loadProviderModels", javascript)
        self.assertIn("PROVIDER_MODEL_FALLBACK", javascript)
        self.assertIn('api("/api/autonomy")', javascript)
        self.assertIn("/api/evolution-journey", javascript)
        self.assertIn('api("/api/evolution-journey"', javascript)
        self.assertIn("localizeNumber", javascript)
        self.assertIn('journeyModal.setAttribute("dir"', javascript)
        self.assertIn("renderJourneySynopsis", javascript)
        self.assertIn("renderJourneyChapters", javascript)
        self.assertIn("journey-badge", javascript)
        self.assertIn("openEvolutionJourney", javascript)
        self.assertIn("readJourney", javascript)
        self.assertIn('api("/api/petri-dish")', javascript)
        self.assertIn('api("/api/evidence-control")', javascript)
        self.assertIn('api("/api/evidence/bundle"', javascript)
        self.assertIn('api("/api/evidence/approve"', javascript)
        self.assertIn('api("/api/trust-authority")', javascript)
        self.assertIn('api("/api/trust/attest"', javascript)
        self.assertIn('api("/api/trust/authorize"', javascript)
        self.assertIn('api("/api/promotion-control")', javascript)
        self.assertIn('api("/api/deployment-control")', javascript)
        self.assertIn("renderPetriDish", javascript)
        self.assertIn("initLineageInteractions", javascript)
        self.assertIn("applyLineageZoom", javascript)
        self.assertNotIn(".slice(-80)", javascript)
        self.assertIn('/api/achievements', javascript)
        self.assertIn("cachedAchievementCatalog", javascript)
        self.assertNotIn("ACHIEVEMENT_CATALOG", javascript)
        self.assertIn("initHelpTooltips", javascript)
        self.assertIn("helpHostStatus", javascript)
        self.assertIn("formatOrganismHelp", javascript)
        self.assertIn("helpOrganismDetail", javascript)
        self.assertIn("data-i18n-help", javascript)
        self.assertIn("achievementUnlocked", javascript)
        self.assertIn("response.text()", javascript)
        self.assertIn("invalidServerResponse", javascript)
        self.assertIn("@keyframes heartbeat", stylesheet)
        self.assertIn("white-space: pre-wrap", stylesheet)
        self.assertIn("overflow-wrap: anywhere", stylesheet)
        self.assertIn("font-size: 12px", stylesheet)
        self.assertIn('[dir="rtl"] textarea', stylesheet)
        self.assertIn(".achievement-card", stylesheet)
        self.assertIn(".journey-modal", stylesheet)
        self.assertIn("width: 80vw", stylesheet)
        self.assertIn("height: 80vh", stylesheet)
        self.assertIn(".journey-timeline", stylesheet)
        self.assertIn(".journey-synopsis", stylesheet)
        self.assertIn(".journey-chapter", stylesheet)
        self.assertIn(".journey-badge", stylesheet)
        self.assertIn(".journey-button", stylesheet)
        self.assertIn(".help-tooltip", stylesheet)
        self.assertIn(".has-help", stylesheet)
        self.assertIn(".cell-core", stylesheet)
        self.assertIn(".lineage-map", stylesheet)
        self.assertIn(".lineage-explorer", stylesheet)
        self.assertIn("cursor: grab", stylesheet)
        self.assertIn(".lineage-viewport.is-panning", stylesheet)
        self.assertIn("height: min(48rem, 82vh)", stylesheet)
        self.assertIn(".organism-card", stylesheet)
        self.assertIn(".resource-track", stylesheet)
        self.assertIn(".niche-chip", stylesheet)
        self.assertIn(".cooperation-edge", stylesheet)
        self.assertIn(".metric-card", stylesheet)
        self.assertIn(".evidence-state", stylesheet)
        self.assertIn(".gate-status-grid", stylesheet)
        self.assertIn(".trust-authority", stylesheet)
        self.assertIn(".release-control", stylesheet)
        self.assertIn(".deployment-handoff", stylesheet)

    def test_autonomy_status_and_journal_endpoints(self):
        status, payload = self._request("GET", "/api/autonomy")
        self.assertEqual(status, 200)
        self.assertFalse(payload["enabled"])
        status, payload = self._request("GET", "/api/evolution-journal")
        self.assertEqual(status, 200)
        self.assertEqual(payload["entries"], [])

    def test_evolution_journey_endpoint_requires_cutoff(self):
        with self.assertRaises(HTTPError) as context:
            self._request("GET", "/api/evolution-journey")
        self.assertEqual(context.exception.code, 400)
        payload = json.loads(context.exception.read().decode())
        self.assertIn("timestamp", str(payload).lower())

    def test_evolution_journey_endpoint_narrates_recorded_entries(self):
        journal = self.runtime.workspace / ".evo/evolution-journal.jsonl"
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_text(
            "\n".join(
                [
                    '{"timestamp":"2026-07-31T10:00:00+00:00","event_type":"autonomy.started","payload":{"objective":"Seed the dish","max_generations":3,"interval_seconds":5,"mutable_paths":["organisms/"]}}',
                    '{"timestamp":"2026-07-31T10:01:00+00:00","event_type":"autonomy.generation","payload":{"generation":1,"attempt":1,"status":"eligible","score":0.9,"summary":"Grow a safer founder","rationale":"Protect the founders","expected_benefit":"Stronger lineage","risk":"Low","target_path":"organisms/prompt.md","evaluation_evidence":{"status":"proposal_only"},"ecology":{"organism_id":"gnome-0001","epoch":1,"emergent_role":"explorer","fitness":0.8,"energy":70.0,"environment_phase":"balanced","offspring_id":"gnome-0007"},"achievements":[{"id":"first_spark"}]}}',
                    '{"timestamp":"2026-07-31T10:02:00+00:00","event_type":"autonomy.stopped","payload":{}}',
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        status, payload = self._request(
            "POST",
            "/api/evolution-journey",
            {
                "until": "2026-07-31T10:01:00+00:00",
                "language": "en",
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["entry_count"], 2)
        self.assertIn("Seed the dish", payload["story"])
        self.assertIn("Grow a safer founder", payload["story"])
        self.assertIn("Protect the founders", payload["story"])
        self.assertIn("First Spark", payload["story"])
        self.assertIn("gnome-0007", payload["story"])
        self.assertNotIn("paused", payload["story"].lower())
        self.assertTrue(payload["chapters"])
        self.assertIn("summary", payload)
        self.assertIn("synopsis", payload)
        self.assertIn("Seed the dish", payload["synopsis"])
        self.assertIn("Grow a safer founder", payload["synopsis"])
        generation = next(
            chapter
            for chapter in payload["chapters"]
            if chapter["kind"] == "generation"
        )
        self.assertTrue(generation["badges"])
        self.assertTrue(generation["tags"])
        self.assertEqual(generation["tone"], "success")

        status, get_payload = self._request(
            "GET",
            "/api/evolution-journey?until=2026-07-31T10:01:00%2B00:00&language=en",
        )
        self.assertEqual(status, 200)
        self.assertEqual(get_payload["entry_count"], 2)
        self.assertIn("complete chronicle", get_payload["story"])
        self.assertTrue(get_payload["chapters"])

    def test_achievements_catalog_endpoint(self):
        status, payload = self._request("GET", "/api/achievements")
        self.assertEqual(status, 200)
        self.assertEqual(payload["total"], 8)
        self.assertEqual(len(payload["milestones"]), 8)
        self.assertEqual(payload["milestones"][0]["id"], "first_spark")
        self.assertEqual(payload["milestones"][0]["threshold"], 1)
        self.assertIn("symbol", payload["milestones"][0])
        self.assertEqual(payload["unlocked_count"], 0)

    def test_evolution_journey_translates_latin_payload_for_fa(self):
        journal = self.runtime.workspace / ".evo/evolution-journal.jsonl"
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_text(
            '{"timestamp":"2026-07-31T10:00:00+00:00","event_type":"autonomy.started","payload":{"objective":"Explore digital abiogenesis safely","max_generations":3,"interval_seconds":5,"mutable_paths":["organisms/"]}}\n'
            '{"timestamp":"2026-07-31T10:01:00+00:00","event_type":"autonomy.generation","payload":{"generation":1,"attempt":1,"status":"eligible","score":0.9,"summary":"Grow a safer founder","rationale":"Protect the founders","expected_benefit":"Stronger lineage","risk":"Low reversible change","target_path":"organisms/prompt.md"}}\n',
            encoding="utf-8",
        )

        def fake_translate(texts, *, cache, provider, chunk_size=12):
            mapping = {
                text: f"FA::{text}"
                for text in texts
            }
            cache.put_many(mapping)
            return mapping

        with patch("evo.runtime.translate_missing", side_effect=fake_translate):
            status, payload = self._request(
                "POST",
                "/api/evolution-journey",
                {
                    "until": "2026-07-31T10:01:00+00:00",
                    "language": "fa",
                },
            )
        self.assertEqual(status, 200)
        self.assertIn("FA::Explore digital abiogenesis safely", payload["synopsis"])
        self.assertIn("FA::Grow a safer founder", payload["story"])
        self.assertIn("FA::Protect the founders", payload["story"])
        self.assertIn("داستان تا اینجا", payload["synopsis_title"])
        self.assertTrue(
            payload["synopsis"].startswith("از هدف «FA::Explore digital abiogenesis safely»")
        )

        status, journal_payload = self._request(
            "GET",
            "/api/evolution-journal?limit=10&language=fa",
        )
        self.assertEqual(status, 200)
        generation = next(
            entry
            for entry in journal_payload["entries"]
            if entry["event_type"] == "autonomy.generation"
        )
        self.assertEqual(generation["payload"]["summary"], "FA::Grow a safer founder")

    def test_petri_dish_endpoint_has_founder_population(self):
        status, payload = self._request("GET", "/api/petri-dish")
        self.assertEqual(status, 200)
        self.assertEqual(payload["summary"]["living"], 6)
        self.assertEqual(payload["summary"]["epoch"], 0)
        self.assertEqual(len(payload["organisms"]), 6)
        self.assertEqual(payload["environment"]["phase"], "balanced")
        self.assertEqual(payload["summary"]["cooperation_links"], 0)
        self.assertIn("open_endedness_proxy", payload["metrics"])

    def test_evidence_bundle_and_human_gate_endpoints(self):
        status, payload = self._request("GET", "/api/evidence-control")
        self.assertEqual(status, 200)
        self.assertIsNone(payload["latest_bundle"])
        self.assertFalse(payload["deployment_authorized"])

        status, bundle = self._request("POST", "/api/evidence/bundle", {})
        self.assertEqual(status, 200)
        self.assertTrue(bundle["verified"])
        self.assertTrue(bundle["replay_verified"])

        status, approval = self._request(
            "POST",
            "/api/evidence/approve",
            {
                "approver": "Local reviewer",
                "decision": "approve",
                "note": "Replay and host signature inspected.",
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(approval["decision"], "approve")
        self.assertFalse(approval["deploy_authorized"])

        _, gate = self._request("GET", "/api/evidence-control")
        self.assertTrue(gate["approval_signature_valid"])
        self.assertFalse(gate["deployment_authorized"])

    def test_v08_public_trust_endpoints_fail_closed_until_signed_review(self):
        _, initial = self._request("GET", "/api/trust-authority")
        self.assertEqual(initial["authority"]["algorithm"], "Ed25519")
        self.assertFalse(initial["policy"]["satisfied"])
        self.assertFalse(initial["deployment_authorized"])

        self._request("POST", "/api/evidence/bundle", {})
        _, attestation = self._request("POST", "/api/trust/attest", {})
        self.assertTrue(attestation["verified"])

        root = Path(self._directory.name)
        private_key = root / "external-reviewer.key"
        public_key = root / "external-reviewer.pub"
        create_reviewer_identity(
            reviewer_id="ui-reviewer",
            private_key_path=private_key,
            public_key_path=public_key,
        )
        self.server.trust_authority.register_reviewer(
            reviewer_id="ui-reviewer",
            public_key_path=public_key,
            display_name="UI Reviewer",
        )
        self.server.trust_authority.record_review(
            reviewer_id="ui-reviewer",
            private_key_path=private_key,
            decision="approve",
            note="Independent evidence review.",
        )
        _, authorization = self._request("POST", "/api/trust/authorize", {})
        self.assertTrue(authorization["verified"])
        self.assertFalse(authorization["repository_mutation_performed"])
        self.assertFalse(authorization["deployment_authorized"])

    def test_v09_promotion_status_is_read_only_and_denies_deployment(self):
        status, payload = self._request("GET", "/api/promotion-control")
        self.assertEqual(status, 200)
        self.assertIsNone(payload["latest_artifact"])
        self.assertFalse(payload["authorization_current"])
        self.assertFalse(payload["commit_performed"])
        self.assertFalse(payload["push_performed"])
        self.assertFalse(payload["deployment_authorized"])

    def test_v10_deployment_status_is_read_only_and_external(self):
        status, payload = self._request("GET", "/api/deployment-control")
        self.assertEqual(status, 200)
        self.assertEqual(payload["phase"], "no_release")
        self.assertFalse(payload["network_request_performed"])
        self.assertFalse(payload["cloud_credentials_held"])
        self.assertFalse(payload["deployment_performed_by_evo"])
        self.assertTrue(payload["external_execution_required"])

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
