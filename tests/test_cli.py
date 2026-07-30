from contextlib import redirect_stdout
from io import StringIO
import unittest

from evo.cli import build_parser


class CLITests(unittest.TestCase):
    def test_version_flag_reports_package_version(self):
        output = StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as exit_context:
                build_parser().parse_args(["--version"])
        self.assertEqual(exit_context.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), "evo 0.1.1")


if __name__ == "__main__":
    unittest.main()
