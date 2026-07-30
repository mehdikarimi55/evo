"""Command-line boundary for EVO Terrarium."""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

from evo.config import ConfigurationError
from evo.kernel.budget import BudgetExceeded
from evo.providers.groq import ProviderError
from evo.runtime import TerrariumRuntime
from evo.sandbox import (
    DEFAULT_ALLOWED_COMMANDS,
    RootlessSandbox,
    SandboxError,
    SandboxLimits,
)
from evo.ui import serve_ui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evo")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "probe"):
        command = subparsers.add_parser(name)
        command.add_argument("--env-file")
    evolve = subparsers.add_parser("evolve")
    evolve.add_argument("--env-file")
    evolve.add_argument("--task", required=True)
    evolve.add_argument("--mutable-path", action="append", default=["organisms/"])
    sandbox = subparsers.add_parser("sandbox")
    sandbox.add_argument("--workspace", default=".")
    sandbox.add_argument("--image", required=True)
    sandbox.add_argument("--engine", choices=("podman", "docker"))
    sandbox.add_argument("--timeout", type=int, default=30)
    sandbox.add_argument(
        "--allow-command",
        action="append",
        dest="allowed_commands",
        help=(
            "allowed executable name; may be repeated "
            f"(default: {', '.join(DEFAULT_ALLOWED_COMMANDS)})"
        ),
    )
    sandbox.add_argument("sandbox_command", nargs=argparse.REMAINDER)
    ui = subparsers.add_parser("ui")
    ui.add_argument("--env-file")
    ui.add_argument("--host", default="127.0.0.1")
    ui.add_argument("--port", type=int, default=8787)
    ui.add_argument("--no-browser", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime = TerrariumRuntime(
        env_file=Path(args.env_file) if getattr(args, "env_file", None) else None
    )
    try:
        if args.command == "ui":
            serve_ui(
                runtime=runtime,
                host=args.host,
                port=args.port,
                open_browser=not args.no_browser,
            )
            return 0
        if args.command == "doctor":
            print(json.dumps(runtime.doctor()))
            return 0
        if args.command == "probe":
            print(runtime.probe())
            return 0
        if args.command == "sandbox":
            command = list(args.sandbox_command)
            if command[:1] == ["--"]:
                command = command[1:]
            result = RootlessSandbox(
                workspace=Path(args.workspace),
                image=args.image,
                engine=args.engine,
                limits=SandboxLimits(timeout_seconds=args.timeout),
                allowed_commands=args.allowed_commands or DEFAULT_ALLOWED_COMMANDS,
            ).run(command)
            if result.stdout:
                print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
            if result.stderr:
                print(
                    result.stderr,
                    file=sys.stderr,
                    end="" if result.stderr.endswith("\n") else "\n",
                )
            return result.exit_code

        candidate = runtime.evolve(
            task=args.task,
            mutable_paths=list(args.mutable_path),
        )
        print(json.dumps(candidate, indent=2, default=str))
        return 0 if candidate.get("rejection_reason") is None else 2
    except (
        ConfigurationError,
        ProviderError,
        BudgetExceeded,
        SandboxError,
        ValueError,
    ) as exc:
        print(f"EVO error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
