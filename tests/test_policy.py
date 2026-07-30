import unittest

from evo.kernel.policy import KernelPolicy


class KernelPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = KernelPolicy()

    def test_mutable_organism_path_is_allowed(self):
        decision = self.policy.authorize_mutation(
            "organisms/cell/prompt.md", ("organisms/",)
        )
        self.assertTrue(decision.allowed)

    def test_kernel_path_is_denied(self):
        decision = self.policy.authorize_mutation(
            "src/evo/kernel/policy.py", ("src/",)
        )
        self.assertFalse(decision.allowed)

    def test_parent_path_is_denied(self):
        decision = self.policy.authorize_mutation(
            "organisms/../../.env.local", ("organisms/",)
        )
        self.assertFalse(decision.allowed)

    def test_absolute_and_similar_prefix_paths_are_denied(self):
        absolute = self.policy.authorize_mutation(
            "/organisms/cell/prompt.md", ("organisms/",)
        )
        similar = self.policy.authorize_mutation(
            "organisms-escape/prompt.md", ("organisms",)
        )
        self.assertFalse(absolute.allowed)
        self.assertFalse(similar.allowed)

    def test_external_action_is_denied(self):
        decision = self.policy.authorize_external_action("account.create")
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
