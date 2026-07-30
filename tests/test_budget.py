import unittest

from evo.kernel.budget import BudgetExceeded, RunBudget


class RunBudgetTests(unittest.TestCase):
    def test_call_ceiling_is_enforced_before_call(self):
        budget = RunBudget(
            max_calls=1, max_input_tokens=100, max_output_tokens=100
        )
        budget.reserve_call()
        with self.assertRaises(BudgetExceeded):
            budget.reserve_call()

    def test_token_usage_is_recorded(self):
        budget = RunBudget(
            max_calls=1, max_input_tokens=100, max_output_tokens=100
        )
        budget.record_usage(12, 5)
        snapshot = budget.snapshot()
        self.assertEqual(snapshot.input_tokens_used, 12)
        self.assertEqual(snapshot.output_tokens_used, 5)


if __name__ == "__main__":
    unittest.main()

