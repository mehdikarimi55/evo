"""Unit tests for the host-owned achievement catalog."""

import unittest

from evo.achievements import (
    ACHIEVEMENT_MILESTONES,
    catalog,
    public_catalog_payload,
    total_milestones,
    unlock_for_generation,
)


class AchievementsCatalogTests(unittest.TestCase):
    def test_catalog_has_stable_eight_milestones(self):
        milestones = catalog()
        self.assertEqual(total_milestones(), 8)
        self.assertEqual(len(milestones), 8)
        self.assertEqual(
            [item["id"] for item in milestones],
            [milestone.id for milestone in ACHIEVEMENT_MILESTONES],
        )
        self.assertEqual(
            [item["threshold"] for item in milestones],
            [1, 5, 10, 25, 50, 100, 500, 1000],
        )

    def test_unlock_is_idempotent_and_threshold_based(self):
        first = unlock_for_generation(1, [], unlocked_at="t1")
        self.assertEqual([item["id"] for item in first], ["first_spark"])

        again = unlock_for_generation(1, first, unlocked_at="t2")
        self.assertEqual(again, [])

        mid = unlock_for_generation(10, first, unlocked_at="t3")
        self.assertEqual(
            [item["id"] for item in mid],
            ["stable_lineage", "adaptive_colony"],
        )

    def test_public_payload_includes_unlocked_count(self):
        unlocked = [{"id": "first_spark", "generation": 1}]
        payload = public_catalog_payload(unlocked=unlocked)
        self.assertEqual(payload["total"], 8)
        self.assertEqual(payload["unlocked_count"], 1)
        self.assertEqual(payload["unlocked"][0]["id"], "first_spark")
        self.assertEqual(len(payload["milestones"]), 8)


if __name__ == "__main__":
    unittest.main()
