"""Fail-closed rootless container execution for candidate evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import which
from subprocess import PIPE, Popen, TimeoutExpired
from time import monotonic
from typing import Callable, Sequence
from uuid import uuid4
import os


DEFAULT_ALLOWED_COMMANDS = ("python", "python3", "pytest")


class SandboxError(RuntimeError):
    """A sanitized sandbox failure safe to expose at host boundaries."""


@dataclass(frozen=True, slots=True)
class SandboxLimits:
    timeout_seconds: int = 30
    memory_megabytes: int = 512
    cpu_count: float = 1.0
    pids: int = 128
    max_output_bytes: int = 256_000

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("Sandbox timeout must be positive")
        if self.memory_megabytes < 64:
            raise ValueError("Sandbox memory limit must be at least 64 MiB")
        if self.cpu_count <= 0:
            raise ValueError("Sandbox CPU limit must be positive")
        if self.pids <= 0:
            raise ValueError("Sandbox PID limit must be positive")
        if self.max_output_bytes <= 0:
            raise ValueError("Sandbox output limit must be positive")


@dataclass(frozen=True, slots=True)
class SandboxResult:
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    output_truncated: bool = False

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


ProcessFactory = Callable[..., Popen[bytes]]
RootlessCheck = Callable[[str], bool]


class RootlessSandbox:
    """Run a command in a restricted Docker or Podman container.

    The runner deliberately has no host-process fallback. The configured
    container engine is responsible for rootless user-namespace isolation.
    """

    def __init__(
        self,
        *,
        workspace: Path,
        image: str,
        engine: str | None = None,
        limits: SandboxLimits | None = None,
        process_factory: ProcessFactory = Popen,
        rootless_check: RootlessCheck | None = None,
        allowed_commands: Sequence[str] = DEFAULT_ALLOWED_COMMANDS,
    ) -> None:
        self.workspace = workspace.resolve()
        self.image = image.strip()
        self.engine = engine or _detect_engine()
        self.limits = limits or SandboxLimits()
        self.process_factory = process_factory
        self.rootless_check = rootless_check or _is_rootless_engine
        self.container_name = f"evo-sandbox-{uuid4().hex}"
        self.allowed_commands = frozenset(
            command.strip() for command in allowed_commands if command.strip()
        )
        if not self.workspace.is_dir():
            raise SandboxError("Sandbox workspace must be an existing directory")
        if not self.image or any(character.isspace() for character in self.image):
            raise SandboxError("Sandbox image must be a non-empty image reference")
        if self.engine not in {"docker", "podman"}:
            raise SandboxError("Sandbox engine must be docker or podman")
        if not self.allowed_commands:
            raise SandboxError("Sandbox command allowlist cannot be empty")
        if any(
            "/" in command
            or "\\" in command
            or any(character.isspace() for character in command)
            for command in self.allowed_commands
        ):
            raise SandboxError("Sandbox allowlist entries must be executable names")

    def build_command(self, command: Sequence[str]) -> tuple[str, ...]:
        requested = tuple(str(part) for part in command)
        if not requested or not requested[0].strip():
            raise SandboxError("Sandbox command cannot be empty")
        if any("\x00" in part for part in requested):
            raise SandboxError("Sandbox command contains an invalid null byte")
        if requested[0] not in self.allowed_commands:
            raise SandboxError(
                f"Sandbox command is not allowed: {requested[0]}"
            )

        limits = self.limits
        invocation = [
            self.engine,
            "run",
            "--rm",
            "--name",
            self.container_name,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            str(limits.pids),
            "--memory",
            f"{limits.memory_megabytes}m",
            "--cpus",
            str(limits.cpu_count),
            "--user",
            "65534:65534",
            "--workdir",
            "/workspace",
            "--mount",
            f"type=bind,src={self.workspace},dst=/workspace,readonly",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,nodev,size=64m",
            "--env",
            "HOME=/tmp",
            "--env",
            "TMPDIR=/tmp",
            self.image,
            *requested,
        ]
        return tuple(invocation)

    def run(self, command: Sequence[str]) -> SandboxResult:
        invocation = self.build_command(command)
        if not self.rootless_check(self.engine):
            raise SandboxError(
                f"{self.engine} is unavailable or is not running in rootless mode"
            )
        started = monotonic()
        try:
            process = self.process_factory(
                invocation,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                env=_engine_environment(),
            )
        except OSError as exc:
            raise SandboxError("Unable to start the sandbox engine") from exc

        timed_out = False
        try:
            stdout, stderr = process.communicate(
                input=b"", timeout=self.limits.timeout_seconds
            )
        except TimeoutExpired:
            timed_out = True
            process.kill()
            client_stdout, client_stderr = process.communicate()
            removed, cleanup_stderr = self._force_remove()
            if not removed:
                raise SandboxError(
                    "Sandbox timed out and its container could not be removed: "
                    + cleanup_stderr
                )
            stdout, stderr = client_stdout, client_stderr

        stdout, stdout_truncated = _bounded(stdout, self.limits.max_output_bytes)
        stderr, stderr_truncated = _bounded(stderr, self.limits.max_output_bytes)
        return SandboxResult(
            command=tuple(str(part) for part in command),
            exit_code=124 if timed_out else int(process.returncode),
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            duration_seconds=round(monotonic() - started, 4),
            timed_out=timed_out,
            output_truncated=stdout_truncated or stderr_truncated,
        )

    def _force_remove(self) -> tuple[bool, str]:
        try:
            cleanup = self.process_factory(
                (self.engine, "rm", "--force", self.container_name),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                env=_engine_environment(),
            )
            _, stderr = cleanup.communicate(input=b"", timeout=10)
        except (OSError, TimeoutExpired):
            return False, "cleanup command failed"
        message = stderr.decode("utf-8", errors="replace").strip()
        removed = cleanup.returncode == 0 or "no such container" in message.lower()
        return removed, message


def _detect_engine() -> str:
    for name in ("podman", "docker"):
        if which(name):
            return name
    raise SandboxError(
        "No container sandbox engine found; install rootless Podman or Docker"
    )


def _engine_environment() -> dict[str, str]:
    allowed = ("PATH", "HOME", "DOCKER_HOST", "DOCKER_CONFIG", "XDG_RUNTIME_DIR")
    return {name: os.environ[name] for name in allowed if name in os.environ}


def _is_rootless_engine(engine: str) -> bool:
    command = (
        (engine, "info", "--format", "{{.Host.Security.Rootless}}")
        if engine == "podman"
        else (engine, "info", "--format", "{{json .SecurityOptions}}")
    )
    try:
        process = Popen(
            command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            env=_engine_environment(),
        )
        stdout, _ = process.communicate(input=b"", timeout=10)
    except (OSError, TimeoutExpired):
        return False
    value = stdout.decode("utf-8", errors="replace").strip().lower()
    return process.returncode == 0 and (
        value == "true" if engine == "podman" else "rootless" in value
    )


def _bounded(payload: bytes, limit: int) -> tuple[bytes, bool]:
    if len(payload) <= limit:
        return payload, False
    marker = b"\n[EVO output truncated]\n"
    retained = max(0, limit - len(marker))
    return payload[:retained] + marker, True
