from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import time
import unittest

from evo.autonomy import AutonomyController, AutonomyError
from evo.petri import PetriDish


def eligible_candidate() -> dict[str, object]:
    return {
        "candidate_id": "candidate-test",
        "status": "eligible",
        "score": {
            "schema_validity": 1.0,
            "policy_compliance": 1.0,
            "rationale_quality": 1.0,
        },
        "proposal": {
            "target_path": "organisms/cell.json",
            "summary": "Increase adaptive diversity.",
            "rationale": "Variation supports open-ended exploration.",
            "expected_benefit": "More emergent behavior.",
            "risk": "Added state complexity.",
        },
        "rejection_reason": None,
    }


class AutonomyTests(unittest.TestCase):
    def test_runs_generation_persists_progress_and_completes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            evolved = Event()
            calls = []

            def evolve(**kwargs):
                calls.append(kwargs)
                evolved.set()
                return eligible_candidate()

            controller = AutonomyController(
                evolve=evolve,
                state_path=root / "state.json",
                journal_path=root / "journal.jsonl",
            )
            controller.start(
                {
                    "objective": "Explore digital abiogenesis.",
                    "mutable_paths": "organisms/",
                    "interval_seconds": 30,
                    "max_generations": 1,
                    "language": "en",
                }
            )
            self.assertTrue(evolved.wait(2))
            deadline = time.monotonic() + 2
            while controller.status()["phase"] != "completed":
                self.assertLess(time.monotonic(), deadline)
                time.sleep(0.01)

            state = controller.status()
            self.assertFalse(state["enabled"])
            self.assertEqual(state["generation"], 1)
            self.assertEqual(state["attempts"], 1)
            self.assertEqual(calls[0]["organism_id"], "gnome-0001")
            self.assertEqual(calls[0]["language"], "en")
            self.assertEqual(calls[0]["traits"], {"selected_adaptations": []})
            self.assertEqual(
                state["selected_adaptations"][0]["summary"],
                "Increase adaptive diversity.",
            )
            self.assertEqual(state["achievements"][0]["id"], "first_spark")
            entries = controller.read_journal()
            event_types = [entry["event_type"] for entry in entries]
            self.assertIn("autonomy.generation", event_types)
            self.assertIn("autonomy.completed", event_types)
            generation_entry = next(
                entry
                for entry in entries
                if entry["event_type"] == "autonomy.generation"
            )
            self.assertEqual(
                generation_entry["payload"]["achievements"][0]["id"],
                "first_spark",
            )
            controller.shutdown()

    def test_provider_failure_enters_backoff_and_can_be_stopped(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            attempted = Event()

            def evolve(**kwargs):
                attempted.set()
                raise RuntimeError("provider offline")

            controller = AutonomyController(
                evolve=evolve,
                state_path=root / "state.json",
                journal_path=root / "journal.jsonl",
            )
            controller.start(
                {
                    "interval_seconds": 30,
                    "max_generations": 2,
                    "language": "fa",
                }
            )
            self.assertTrue(attempted.wait(2))
            deadline = time.monotonic() + 2
            while controller.status()["phase"] != "backoff":
                self.assertLess(time.monotonic(), deadline)
                time.sleep(0.01)

            stopped = controller.stop()
            self.assertFalse(stopped["enabled"])
            self.assertEqual(stopped["phase"], "stopped")
            self.assertTrue(
                any(
                    entry["event_type"] == "autonomy.error"
                    for entry in controller.read_journal()
                )
            )
            controller.shutdown()

    def test_rejects_unbounded_or_invalid_configuration(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            controller = AutonomyController(
                evolve=lambda **kwargs: eligible_candidate(),
                state_path=root / "state.json",
                journal_path=root / "journal.jsonl",
            )
            with self.assertRaisesRegex(AutonomyError, "interval_seconds"):
                controller.start({"interval_seconds": 1})
            with self.assertRaisesRegex(AutonomyError, "max_generations"):
                controller.start({"max_generations": 0})
            with self.assertRaisesRegex(AutonomyError, "Language"):
                controller.start({"language": "de"})
            controller.shutdown()

    def test_population_organism_is_evaluated_and_ecology_is_journaled(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            evolved = Event()
            calls = []
            dish = PetriDish(
                state_path=root / "petri.json",
                initial_population=2,
                capacity=5,
            )

            def evolve(**kwargs):
                calls.append(kwargs)
                evolved.set()
                return eligible_candidate()

            controller = AutonomyController(
                evolve=evolve,
                state_path=root / "state.json",
                journal_path=root / "journal.jsonl",
                petri_dish=dish,
            )
            controller.start(
                {
                    "interval_seconds": 30,
                    "max_generations": 1,
                    "language": "en",
                }
            )
            self.assertTrue(evolved.wait(2))
            deadline = time.monotonic() + 2
            while controller.status()["phase"] != "completed":
                self.assertLess(time.monotonic(), deadline)
                time.sleep(0.01)

            self.assertEqual(calls[0]["organism_id"], "gnome-0002")
            self.assertIn("mutation_rate", calls[0]["traits"])
            self.assertIn("inherited_adaptations", calls[0]["traits"])
            self.assertIn("team_plan", calls[0]["traits"])
            self.assertEqual(dish.status()["summary"]["epoch"], 1)
            entry = next(
                item
                for item in controller.read_journal()
                if item["event_type"] == "autonomy.generation"
            )
            self.assertEqual(
                entry["payload"]["ecology"]["organism_id"],
                calls[0]["organism_id"],
            )
            self.assertEqual(
                entry["payload"]["evaluation_evidence"]["status"],
                "proposal_only",
            )
            controller.shutdown()
