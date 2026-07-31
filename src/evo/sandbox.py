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
            raise ValueError("مهلت اجرای محیط ایزوله باید بزرگ‌تر از صفر باشد")
        if self.memory_megabytes < 64:
            raise ValueError("حافظه محیط ایزوله باید حداقل ۶۴ مگابایت باشد")
        if self.cpu_count <= 0:
            raise ValueError("محدودیت پردازنده باید بزرگ‌تر از صفر باشد")
        if self.pids <= 0:
            raise ValueError("محدودیت پردازش‌ها باید بزرگ‌تر از صفر باشد")
        if self.max_output_bytes <= 0:
            raise ValueError("محدودیت خروجی باید بزرگ‌تر از صفر باشد")


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
            raise SandboxError("محیط کار ایزوله باید یک پوشه موجود باشد")
        if not self.image or any(character.isspace() for character in self.image):
            raise SandboxError("نام image محیط ایزوله نمی‌تواند خالی باشد")
        if self.engine not in {"docker", "podman"}:
            raise SandboxError("موتور محیط ایزوله باید docker یا podman باشد")
        if not self.allowed_commands:
            raise SandboxError("فهرست دستورهای مجاز محیط ایزوله نمی‌تواند خالی باشد")
        if any(
            "/" in command
            or "\\" in command
            or any(character.isspace() for character in command)
            for command in self.allowed_commands
        ):
            raise SandboxError("فهرست مجاز فقط باید شامل نام فایل‌های اجرایی باشد")

    def build_command(self, command: Sequence[str]) -> tuple[str, ...]:
        requested = tuple(str(part) for part in command)
        if not requested or not requested[0].strip():
            raise SandboxError("دستور محیط ایزوله نمی‌تواند خالی باشد")
        if any("\x00" in part for part in requested):
            raise SandboxError("دستور محیط ایزوله دارای null byte نامعتبر است")
        if requested[0] not in self.allowed_commands:
            raise SandboxError(
                f"اجرای این دستور در محیط ایزوله مجاز نیست: {requested[0]}"
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
                f"{self.engine} در دسترس نیست یا در حالت rootless اجرا نشده است"
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
            raise SandboxError("راه‌اندازی موتور محیط ایزوله ممکن نیست") from exc

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
                    "مهلت محیط ایزوله تمام شد و حذف کانتینر ممکن نشد: "
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
            return False, "دستور پاک‌سازی ناموفق بود"
        message = stderr.decode("utf-8", errors="replace").strip()
        removed = cleanup.returncode == 0 or "no such container" in message.lower()
        return removed, message


def _detect_engine() -> str:
    for name in ("podman", "docker"):
        if which(name):
            return name
    raise SandboxError(
        "موتور کانتینر پیدا نشد؛ Podman یا Docker را در حالت rootless نصب کنید"
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
    marker = "\n[خروجی EVO کوتاه شده است]\n".encode("utf-8")
    retained = max(0, limit - len(marker))
    return payload[:retained] + marker, True
