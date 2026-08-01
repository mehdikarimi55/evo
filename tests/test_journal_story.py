"""Unit tests for evolution journey storytelling."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from evo.autonomy import AutonomyController, AutonomyError
from evo.journal_story import (
    JournalStoryError,
    build_journey_story,
    entries_until,
    narrate_journey,
    normalize_language,
    normalize_timestamp,
)


class JournalStoryTests(unittest.TestCase):
    def test_narrate_journey_tells_story_from_beginning(self):
        entries = [
            {
                "timestamp": "2026-07-31T10:00:00+00:00",
                "event_type": "autonomy.started",
                "payload": {
                    "objective": "Explore digital life",
                    "max_generations": 10,
                    "interval_seconds": 30,
                },
            },
            {
                "timestamp": "2026-07-31T10:01:00+00:00",
                "event_type": "autonomy.generation",
                "payload": {
                    "generation": 1,
                    "attempt": 1,
                    "status": "eligible",
                    "score": 0.82,
                    "summary": "Sharpen validation without changing public behavior",
                    "expected_benefit": "Safer proposals",
                    "achievements": [{"id": "first_spark"}],
                    "ecology": {
                        "organism_id": "gnome-0001",
                        "epoch": 1,
                        "emergent_role": "explorer",
                        "offspring_id": "gnome-0007",
                    },
                },
            },
            {
                "timestamp": "2026-07-31T10:02:00+00:00",
                "event_type": "autonomy.error",
                "payload": {"message": "temporary timeout", "retrying": True},
            },
        ]

        story = narrate_journey(entries, language="en")

        self.assertIn("chronicle of the gnome", story)
        self.assertIn("Explore digital life", story)
        self.assertIn("selected generation 1", story.lower())
        self.assertIn("Sharpen validation", story)
        self.assertIn("First Spark", story)
        self.assertIn("gnome-0007", story)
        self.assertIn("temporary timeout", story)
        self.assertIn("story stands", story)

    def test_build_journey_cuts_off_at_selected_point(self):
        entries = [
            {
                "timestamp": "2026-07-31T12:00:00+00:00",
                "event_type": "autonomy.completed",
                "payload": {"generation": 2, "attempts": 2},
            },
            {
                "timestamp": "2026-07-31T11:00:00+00:00",
                "event_type": "autonomy.generation",
                "payload": {
                    "generation": 1,
                    "attempt": 1,
                    "status": "rejected",
                    "score": 0.1,
                    "rejection_reason": "policy mismatch",
                },
            },
            {
                "timestamp": "2026-07-31T10:00:00+00:00",
                "event_type": "autonomy.started",
                "payload": {"objective": "Begin"},
            },
        ]

        payload = build_journey_story(
            entries,
            until_timestamp="2026-07-31T11:00:00+00:00",
            language="en",
        )

        self.assertEqual(payload["entry_count"], 2)
        self.assertIn("Begin", payload["story"])
        self.assertIn("policy mismatch", payload["story"])
        self.assertNotIn("generation limit", payload["story"].lower())
        self.assertGreaterEqual(len(payload["chapters"]), 3)
        self.assertEqual(payload["summary"]["rejected"], 1)
        self.assertIn("Begin", payload["synopsis"])
        self.assertIn("Story so far", payload["synopsis_title"])
        kinds = [chapter["kind"] for chapter in payload["chapters"]]
        self.assertIn("started", kinds)
        self.assertIn("generation", kinds)

    def test_persian_story_is_fluent(self):
        entries = [
            {
                "timestamp": "2026-07-31T10:00:00+00:00",
                "event_type": "autonomy.started",
                "payload": {"objective": "کاوش حیات"},
            },
            {
                "timestamp": "2026-07-31T10:01:00+00:00",
                "event_type": "autonomy.generation",
                "payload": {
                    "generation": 1,
                    "attempt": 2,
                    "status": "eligible",
                    "score": 0.9,
                    "summary": "بهبود ایمنی",
                    "evaluation_evidence": {"status": "proposal_only"},
                    "ecology": {
                        "organism_id": "gnome-0001",
                        "epoch": 3,
                        "emergent_role": "explorer",
                        "fitness": 0.8,
                        "energy": 70,
                        "environment_phase": "balanced",
                    },
                    "achievements": [{"id": "first_spark"}],
                },
            },
        ]
        payload = build_journey_story(
            entries,
            until_timestamp="2026-07-31T10:01:00+00:00",
            language="fa",
        )
        story = payload["story"]
        self.assertEqual(payload["language"], "fa")
        self.assertIn("روایت کامل تکامل", story)
        self.assertIn("کاوش حیات", story)
        self.assertIn("داستان تا این ایستگاه", story)
        self.assertIn("نسل ۱", payload["chapters"][2]["title"])
        badge_labels = " ".join(
            badge["label"] for badge in payload["chapters"][2]["badges"]
        )
        self.assertIn("واجد شرایط", badge_labels)
        self.assertIn("کاوشگر", badge_labels)
        self.assertIn("فقط پیشنهاد", badge_labels)
        self.assertIn("نخستین جرقه", story)
        self.assertIn("داستان تا اینجا", payload["synopsis_title"])
        self.assertIn("۱", payload["synopsis"])

    def test_empty_journal_returns_quiet_story(self):
        self.assertIn("quiet", narrate_journey([], language="en").lower())

    def test_missing_cutoff_raises(self):
        with self.assertRaises(JournalStoryError):
            entries_until([], until_timestamp="")

    def test_normalize_timestamp_repairs_query_plus_as_space(self):
        self.assertEqual(
            normalize_timestamp("2026-07-31T10:01:00 00:00"),
            "2026-07-31T10:01:00+00:00",
        )

    def test_normalize_language_accepts_fa_variants(self):
        self.assertEqual(normalize_language("fa"), "fa")
        self.assertEqual(normalize_language("fa-IR"), "fa")
        self.assertEqual(normalize_language("en-US"), "en")


class AutonomyJournalThroughTests(unittest.TestCase):
    def test_read_journal_through_is_chronological_and_inclusive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            journal = root / "journal.jsonl"
            journal.write_text(
                "\n".join(
                    [
                        '{"timestamp":"2026-07-31T10:00:00+00:00","event_type":"autonomy.started","payload":{"objective":"A"}}',
                        '{"timestamp":"2026-07-31T11:00:00+00:00","event_type":"autonomy.generation","payload":{"generation":1,"attempt":1,"status":"eligible","score":1}}',
                        '{"timestamp":"2026-07-31T12:00:00+00:00","event_type":"autonomy.stopped","payload":{}}',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            controller = AutonomyController(
                evolve=MagicMock(),
                state_path=root / "state.json",
                journal_path=journal,
            )
            entries = controller.read_journal_through(
                until_timestamp="2026-07-31T11:00:00+00:00"
            )
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0]["event_type"], "autonomy.started")
            self.assertEqual(entries[1]["event_type"], "autonomy.generation")

    def test_read_journal_through_requires_timestamp(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            controller = AutonomyController(
                evolve=MagicMock(),
                state_path=root / "state.json",
                journal_path=root / "journal.jsonl",
            )
            with self.assertRaises(AutonomyError):
                controller.read_journal_through(until_timestamp="")


if __name__ == "__main__":
    unittest.main()
