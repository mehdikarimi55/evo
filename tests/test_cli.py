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
        self.assertEqual(output.getvalue().strip(), "evo 0.4.0")


if __name__ == "__main__":
    unittest.main()
