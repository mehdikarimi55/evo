from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from evo.petri import PetriDish, PetriDishError


def candidate(
    *,
    candidate_id: str = "candidate-1",
    status: str = "eligible",
    summary: str = "Develop a novel adaptive memory strategy.",
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "status": status,
        "score": {
            "schema_validity": 1.0,
            "policy_compliance": 1.0,
            "rationale_quality": 1.0,
        },
        "proposal": {
            "target_path": "organisms/memory.json",
            "summary": summary,
            "rationale": "Verified outcomes should guide inherited behavior.",
            "expected_benefit": "Improved adaptation.",
            "risk": "Additional bounded state.",
        },
        "rejection_reason": None if status == "eligible" else "policy rejected",
    }


class PetriDishTests(unittest.TestCase):
    def test_initializes_bounded_diverse_founder_population(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=4,
                capacity=8,
            )
            status = dish.status()
            self.assertEqual(status["summary"]["living"], 4)
            self.assertEqual(status["summary"]["births"], 0)
            self.assertEqual(status["summary"]["epoch"], 0)
            self.assertEqual(
                len(
                    {
                        organism["traits"]["exploration"]
                        for organism in status["organisms"]
                    }
                ),
                4,
            )

    def test_eligible_outcome_spends_energy_rewards_and_reproduces(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=2,
                capacity=6,
            )
            selected = dish.select_for_evaluation()
            event = dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(),
            )
            status = dish.status()
            self.assertEqual(status["summary"]["epoch"], 1)
            self.assertEqual(status["summary"]["births"], 1)
            self.assertIsNotNone(event["offspring_id"])
            child = next(
                organism
                for organism in status["organisms"]
                if organism["organism_id"] == event["offspring_id"]
            )
            self.assertEqual(child["parent_ids"], [selected["organism_id"]])
            self.assertEqual(child["generation"], 1)
            self.assertTrue(child["selected_adaptations"][0]["inherited"])
            self.assertNotEqual(child["traits"], selected["traits"])
            self.assertEqual(status["lineage"][0]["child_id"], child["organism_id"])

    def test_rejected_outcome_reduces_energy_without_reproduction(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=2,
                capacity=4,
            )
            selected = dish.select_for_evaluation()
            event = dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(status="rejected"),
            )
            status = dish.status()
            updated = next(
                organism
                for organism in status["organisms"]
                if organism["organism_id"] == selected["organism_id"]
            )
            self.assertEqual(updated["energy"], 90.0)
            self.assertEqual(updated["rejections"], 1)
            self.assertIsNone(event["offspring_id"])
            self.assertEqual(status["summary"]["births"], 0)

    def test_state_survives_restart_and_selection_prefers_underexplored(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "petri.json"
            dish = PetriDish(
                state_path=path,
                initial_population=2,
                capacity=4,
            )
            first = dish.select_for_evaluation()
            dish.record_outcome(
                organism_id=first["organism_id"],
                candidate=candidate(status="rejected"),
            )
            restarted = PetriDish(
                state_path=path,
                initial_population=2,
                capacity=4,
            )
            second = restarted.select_for_evaluation()
            self.assertNotEqual(second["organism_id"], first["organism_id"])
            self.assertEqual(restarted.status()["summary"]["epoch"], 1)

    def test_rejects_invalid_population_configuration(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(PetriDishError):
                PetriDish(
                    state_path=Path(directory) / "petri.json",
                    initial_population=1,
                    capacity=4,
                )

    def test_environment_cycles_through_measurable_selection_phases(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=4,
                capacity=8,
            )
            for index in range(4):
                selected = dish.select_for_evaluation()
                dish.record_outcome(
                    organism_id=selected["organism_id"],
                    candidate=candidate(
                        candidate_id=f"rejected-{index}",
                        status="rejected",
                    ),
                )
            status = dish.status()
            self.assertEqual(status["summary"]["epoch"], 4)
            self.assertEqual(status["environment"]["phase"], "scarcity")
            # Balanced epochs net +2 compute; the scarcity step then nets -3.
            self.assertAlmostEqual(
                status["environment"]["resources"]["compute"],
                103.0,
                places=2,
            )

    def test_drained_compute_recovers_during_balanced_phase(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=4,
                capacity=8,
            )
            state = dish._read_state()
            state["epoch"] = 0  # next evaluation enters balanced (epochs 1-3)
            state["environment"]["phase"] = "balanced"
            state["environment"]["resources"]["compute"] = 0.0
            dish._write_state(state)

            selected = dish.select_for_evaluation()
            dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(candidate_id="recover-1", status="rejected"),
            )
            status = dish.status()
            self.assertEqual(status["environment"]["phase"], "balanced")
            # Regen 6.0 minus evaluation spend 4.0 leaves a net recovery.
            self.assertGreater(status["environment"]["resources"]["compute"], 0.0)
            self.assertAlmostEqual(
                status["environment"]["resources"]["compute"],
                2.0,
                places=2,
            )

    def test_cooperation_is_bounded_observable_and_rewards_partner(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=3,
                capacity=8,
            )
            selected = dish.select_for_evaluation()
            context = selected["cooperation_context"]
            self.assertIsNotNone(context)
            collaborator_id = context["collaborator_id"]
            event = dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(),
            )
            status = dish.status()
            collaborator = next(
                organism
                for organism in status["organisms"]
                if organism["organism_id"] == collaborator_id
            )
            self.assertEqual(event["collaborator_id"], collaborator_id)
            self.assertEqual(
                status["summary"]["cooperation_links"],
                len(event["team"]) - 1,
            )
            self.assertEqual(collaborator["collaborations"], 1)
            self.assertEqual(collaborator["successful_collaborations"], 1)
            self.assertGreater(collaborator["energy"], 100.0)

    def test_team_plan_is_bounded_and_assigns_explicit_responsibilities(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=6,
                capacity=8,
            )
            selected = dish.select_for_evaluation()
            plan = selected["team_plan"]
            self.assertTrue(plan["bounded"])
            self.assertLessEqual(len(plan["members"]), 3)
            self.assertTrue(plan["members"][0]["lead"])
            self.assertTrue(
                all(member["responsibility"] for member in plan["members"])
            )

    def test_metrics_and_proposal_only_evidence_are_recorded_honestly(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=4,
                capacity=8,
            )
            selected = dish.select_for_evaluation()
            event = dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(),
            )
            status = dish.status()
            self.assertEqual(event["evaluation_evidence"]["status"], "proposal_only")
            self.assertFalse(event["evaluation_evidence"]["verified"])
            self.assertEqual(len(status["metric_history"]), 1)
            for metric in (
                "ecological_stability",
                "population_diversity",
                "open_endedness_proxy",
            ):
                self.assertGreaterEqual(status["metrics"][metric], 0.0)
                self.assertLessEqual(status["metrics"][metric], 1.0)
            self.assertIn("not proof", status["metrics"]["interpretation"])

    def test_unsubstantiated_verified_claim_is_rejected(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=2,
                capacity=4,
            )
            selected = dish.select_for_evaluation()
            proposed = candidate()
            proposed["evaluation_evidence"] = {
                "status": "sandbox_verified",
                "promotion_eligible": True,
            }
            event = dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=proposed,
            )
            self.assertEqual(event["evaluation_evidence"]["status"], "invalid")
            self.assertFalse(event["evaluation_evidence"]["verified"])
            self.assertFalse(
                event["evaluation_evidence"]["promotion_eligible"]
            )
            self.assertFalse(event["lifecycle_eligible"])
            self.assertIsNone(event["offspring_id"])

    def test_observed_behavior_produces_niche_role_and_distribution(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=3,
                capacity=8,
            )
            selected = dish.select_for_evaluation()
            dish.record_outcome(
                organism_id=selected["organism_id"],
                candidate=candidate(),
            )
            status = dish.status()
            evolved = next(
                organism
                for organism in status["organisms"]
                if organism["organism_id"] == selected["organism_id"]
            )
            self.assertNotEqual(evolved["emergent_role"], "undifferentiated")
            self.assertEqual(evolved["behavioral_observations"], 1)
            self.assertIn(
                evolved["emergent_role"],
                status["summary"]["niche_distribution"],
            )

    def test_long_run_ecology_preserves_bounds_and_lineage_integrity(self):
        with TemporaryDirectory() as directory:
            dish = PetriDish(
                state_path=Path(directory) / "petri.json",
                initial_population=6,
                capacity=12,
            )
            for index in range(80):
                selected = dish.select_for_evaluation()
                dish.record_outcome(
                    organism_id=selected["organism_id"],
                    candidate=candidate(
                        candidate_id=f"candidate-{index}",
                        status="eligible" if index % 3 else "rejected",
                        summary=f"Adaptation family {index % 11} variant {index}.",
                    ),
                )
            status = dish.status()
            living = [
                organism
                for organism in status["organisms"]
                if organism["status"] == "alive"
            ]
            organism_ids = {
                organism["organism_id"] for organism in status["organisms"]
            }
            self.assertLessEqual(len(living), 12)
            self.assertTrue(living)
            self.assertTrue(
                all(0.0 <= organism["energy"] <= 160.0 for organism in living)
            )
            self.assertTrue(
                all(
                    0.0 <= value <= 120.0
                    for value in status["environment"]["resources"].values()
                )
            )
            self.assertLessEqual(len(status["cooperation"]), 300)
            self.assertLessEqual(len(status["metric_history"]), 500)
            self.assertTrue(
                all(
                    edge["parent_id"] in organism_ids
                    and edge["child_id"] in organism_ids
                    for edge in status["lineage"]
                )
            )


if __name__ == "__main__":
    unittest.main()
