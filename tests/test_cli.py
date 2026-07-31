from contextlib import redirect_stdout
from io import StringIO
import unittest

from evo.cli import build_parser


class CLITests(unittest.TestCase):
    def test_help_is_fully_localized_in_persian(self):
        help_text = build_parser().format_help()

        self.assertIn("نحوه استفاده:", help_text)
        self.assertIn("نمایش راهنما و خروج", help_text)
        self.assertIn("اجرای یک نسل تکاملی", help_text)
        self.assertNotIn("show this help message", help_text)

    def test_evolve_help_is_localized_in_persian(self):
        parser = build_parser()
        subparsers_action = next(
            action
            for action in parser._actions
            if action.__class__.__name__ == "_SubParsersAction"
        )
        help_text = subparsers_action.choices["evolve"].format_help()

        self.assertIn("هدف نسل تکاملی", help_text)
        self.assertIn("مسیر قابل‌تغییر", help_text)
        self.assertNotIn("show this help message", help_text)

    def test_version_flag_reports_package_version(self):
        output = StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as exit_context:
                build_parser().parse_args(["--version"])
        self.assertEqual(exit_context.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), "evo 1.0.0")

    def test_evidence_command_exposes_explicit_human_decisions(self):
        args = build_parser().parse_args(
            ["evidence", "approve", "--approver", "Local reviewer"]
        )
        self.assertEqual(args.command, "evidence")
        self.assertEqual(args.action, "approve")
        self.assertEqual(args.approver, "Local reviewer")

    def test_trust_command_requires_explicit_reviewer_key_paths(self):
        args = build_parser().parse_args(
            [
                "trust",
                "approve",
                "--reviewer-id",
                "reviewer-1",
                "--private-key",
                "/external/reviewer.key",
            ]
        )
        self.assertEqual(args.command, "trust")
        self.assertEqual(args.action, "approve")
        self.assertEqual(args.reviewer_id, "reviewer-1")
        self.assertEqual(args.private_key, "/external/reviewer.key")

    def test_promotion_command_requires_exact_confirmation_input(self):
        args = build_parser().parse_args(
            [
                "promotion",
                "apply",
                "--artifact-id",
                "artifact-123",
                "--confirm",
                "APPLY-artifact-123",
            ]
        )
        self.assertEqual(args.command, "promotion")
        self.assertEqual(args.action, "apply")
        self.assertEqual(args.artifact_id, "artifact-123")
        self.assertEqual(args.confirm, "APPLY-artifact-123")

    def test_deployment_command_exposes_signed_handoff_inputs(self):
        args = build_parser().parse_args(
            [
                "deployment",
                "request-stage",
                "--release-id",
                "release-123",
                "--confirm",
                "STAGE-release-123",
            ]
        )
        self.assertEqual(args.command, "deployment")
        self.assertEqual(args.action, "request-stage")
        self.assertEqual(args.release_id, "release-123")
        self.assertEqual(args.confirm, "STAGE-release-123")


if __name__ == "__main__":
    unittest.main()
