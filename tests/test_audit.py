import unittest

from evo.kernel.audit import redact


class AuditTests(unittest.TestCase):
    def test_groq_keys_are_redacted_recursively(self):
        secret = "gsk_" + "a" * 32
        redacted = redact({"nested": [f"token={secret}"]})
        self.assertNotIn(secret, redacted["nested"][0])
        self.assertIn("[REDACTED]", redacted["nested"][0])

    def test_nvidia_keys_are_redacted_recursively(self):
        secret = "nvapi-" + "a" * 48
        redacted = redact({"nested": [f"token={secret}"]})
        self.assertNotIn(secret, redacted["nested"][0])
        self.assertIn("[REDACTED]", redacted["nested"][0])


if __name__ == "__main__":
    unittest.main()
