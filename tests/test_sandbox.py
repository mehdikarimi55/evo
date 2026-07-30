from pathlib import Path
from subprocess import TimeoutExpired
from tempfile import TemporaryDirectory
import unittest

from evo.sandbox import RootlessSandbox, SandboxError, SandboxLimits


class FakeProcess:
    def __init__(
        self,
        *,
        stdout: bytes = b"",
        stderr: bytes = b"",
        returncode: int = 0,
        timeout: bool = False,
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.timeout = timeout
        self.killed = False

    def communicate(self, *, input=None, timeout=None):
        if self.timeout and not self.killed:
            raise TimeoutExpired(cmd="container", timeout=timeout)
        return self.stdout, self.stderr

    def kill(self):
        self.killed = True
        self.returncode = -9


class SandboxTests(unittest.TestCase):
    def _sandbox(self, directory: str, **kwargs) -> RootlessSandbox:
        return RootlessSandbox(
            workspace=Path(directory),
            image="python:3.13-alpine",
            engine="podman",
            rootless_check=lambda engine: True,
            **kwargs,
        )

    def test_command_is_fail_closed_and_read_only(self):
        with TemporaryDirectory() as directory:
            command = self._sandbox(directory).build_command(
                ("python", "-m", "unittest")
            )

        self.assertEqual(command[:3], ("podman", "run", "--rm"))
        self.assertIn("--network", command)
        self.assertEqual(command[command.index("--network") + 1], "none")
        self.assertIn("--read-only", command)
        self.assertIn("ALL", command)
        self.assertIn("no-new-privileges", command)
        mount = command[command.index("--mount") + 1]
        self.assertTrue(mount.endswith(",dst=/workspace,readonly"))
        self.assertEqual(command[-3:], ("python", "-m", "unittest"))

    def test_environment_is_not_forwarded_to_candidate(self):
        captured = {}

        def factory(command, **kwargs):
            captured.update(kwargs)
            return FakeProcess()

        with TemporaryDirectory() as directory:
            self._sandbox(directory, process_factory=factory).run(
                ("python", "--version")
            )

        environment = captured["env"]
        self.assertNotIn("GROQ_API_KEY", environment)
        self.assertNotIn("NVIDIA_API_KEY", environment)

    def test_timeout_kills_container_client_and_returns_124(self):
        processes = [FakeProcess(timeout=True), FakeProcess()]
        commands = []

        def factory(command, **kwargs):
            commands.append(command)
            return processes.pop(0)

        with TemporaryDirectory() as directory:
            result = self._sandbox(
                directory,
                limits=SandboxLimits(timeout_seconds=1),
                process_factory=factory,
            ).run(("python", "-c", "while True: pass"))

        self.assertTrue(result.timed_out)
        self.assertEqual(result.exit_code, 124)
        self.assertEqual(commands[1][1:3], ("rm", "--force"))

    def test_refuses_rootful_engine(self):
        with TemporaryDirectory() as directory:
            sandbox = RootlessSandbox(
                workspace=Path(directory),
                image="python:3.13-alpine",
                engine="docker",
                rootless_check=lambda engine: False,
            )
            with self.assertRaisesRegex(SandboxError, "rootless"):
                sandbox.run(("python", "--version"))

    def test_rejects_command_outside_allowlist(self):
        with TemporaryDirectory() as directory:
            sandbox = self._sandbox(directory)
            with self.assertRaisesRegex(SandboxError, "not allowed"):
                sandbox.build_command(("sh", "-c", "python -m unittest"))

    def test_custom_command_allowlist_is_exact(self):
        with TemporaryDirectory() as directory:
            sandbox = self._sandbox(
                directory,
                allowed_commands=("ruff",),
            )
            command = sandbox.build_command(("ruff", "check", "."))
            self.assertEqual(command[-3:], ("ruff", "check", "."))
            with self.assertRaises(SandboxError):
                sandbox.build_command(("/usr/bin/ruff", "check", "."))

    def test_output_is_bounded(self):
        process = FakeProcess(stdout=b"x" * 100)
        with TemporaryDirectory() as directory:
            result = self._sandbox(
                directory,
                limits=SandboxLimits(max_output_bytes=64),
                process_factory=lambda *args, **kwargs: process,
            ).run(("python", "-c", "print('x')"))

        self.assertTrue(result.output_truncated)
        self.assertLessEqual(len(result.stdout.encode()), 64)
        self.assertIn("output truncated", result.stdout)

    def test_rejects_missing_workspace_and_empty_command(self):
        with self.assertRaises(SandboxError):
            RootlessSandbox(
                workspace=Path("/definitely/missing"),
                image="python:3.13-alpine",
                engine="podman",
                rootless_check=lambda engine: True,
            )
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SandboxError, "allowlist"):
                self._sandbox(directory, allowed_commands=())
        with TemporaryDirectory() as directory:
            with self.assertRaises(SandboxError):
                self._sandbox(directory).build_command(())


if __name__ == "__main__":
    unittest.main()
