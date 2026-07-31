"""Command-line boundary for EVO Terrarium."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import argparse
import json
import sys

from evo import __version__
from evo.config import ConfigurationError
from evo.evaluation import EvidenceRecorder
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


class PersianArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self._positionals.title = "آرگومان‌ها"
        self._optionals.title = "گزینه‌ها"
        self.add_argument(
            "-h",
            "--help",
            action="help",
            help="نمایش راهنما و خروج",
        )

    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "نحوه استفاده:", 1)

    def format_help(self) -> str:
        return super().format_help().replace("usage:", "نحوه استفاده:", 1)

    def error(self, message: str) -> None:
        translations = (
            (
                "the following arguments are required:",
                "آرگومان‌های زیر الزامی هستند:",
            ),
            ("unrecognized arguments:", "آرگومان‌های ناشناخته:"),
            ("invalid choice:", "انتخاب نامعتبر:"),
            ("expected one argument", "به یک مقدار نیاز دارد"),
        )
        for source, target in translations:
            message = message.replace(source, target)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: خطا: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = PersianArgumentParser(
        prog="evo",
        description="محیط کنترل‌شده EVO برای آزمایش تکامل کد",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="نمایش نسخه برنامه و خروج",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="دستورها",
        metavar="دستور",
    )
    doctor = subparsers.add_parser(
        "doctor", help="اعتبارسنجی پیکربندی میزبان"
    )
    doctor.add_argument("--env-file", help="مسیر فایل محیطی")
    probe = subparsers.add_parser(
        "probe", help="آزمون اتصال به ارائه‌دهنده مدل"
    )
    probe.add_argument("--env-file", help="مسیر فایل محیطی")
    evolve = subparsers.add_parser("evolve", help="اجرای یک نسل تکاملی")
    evolve.add_argument("--env-file", help="مسیر فایل محیطی")
    evolve.add_argument("--task", required=True, help="هدف نسل تکاملی")
    evolve.add_argument(
        "--mutable-path",
        action="append",
        default=["organisms/"],
        help="مسیر قابل‌تغییر؛ امکان تکرار این گزینه وجود دارد",
    )
    sandbox = subparsers.add_parser(
        "sandbox", help="اجرای دستور در محیط کانتینری ایزوله"
    )
    sandbox.add_argument("--workspace", default=".", help="مسیر محیط کار")
    sandbox.add_argument("--image", required=True, help="نام image کانتینر")
    sandbox.add_argument(
        "--engine",
        choices=("podman", "docker"),
        help="موتور کانتینر",
    )
    sandbox.add_argument(
        "--timeout", type=int, default=30, help="مهلت اجرا برحسب ثانیه"
    )
    sandbox.add_argument(
        "--allow-command",
        action="append",
        dest="allowed_commands",
        help=(
            "نام فایل اجرایی مجاز؛ امکان تکرار دارد "
            f"(پیش‌فرض: {', '.join(DEFAULT_ALLOWED_COMMANDS)})"
        ),
    )
    sandbox.add_argument(
        "sandbox_command",
        nargs=argparse.REMAINDER,
        help="دستور موردنظر برای اجرا",
    )
    evaluate = subparsers.add_parser(
        "evaluate",
        help="اجرای ارزیابی قابل‌ردیابی در محیط ایزوله",
    )
    evaluate.add_argument("--workspace", default=".", help="مسیر محیط کار")
    evaluate.add_argument("--image", required=True, help="نام image کانتینر")
    evaluate.add_argument(
        "--engine",
        choices=("podman", "docker"),
        help="موتور کانتینر",
    )
    evaluate.add_argument(
        "--timeout", type=int, default=30, help="مهلت اجرا برحسب ثانیه"
    )
    evaluate.add_argument("--candidate-id", required=True, help="شناسه نامزد")
    evaluate.add_argument(
        "--team-id",
        action="append",
        required=True,
        help="شناسه عضو تیم؛ حداکثر سه بار",
    )
    evaluate.add_argument(
        "--evidence-path",
        default=".evo/evaluation-evidence.jsonl",
        help="مسیر دفتر شواهد",
    )
    evaluate.add_argument(
        "--allow-command",
        action="append",
        dest="allowed_commands",
        help="نام فایل اجرایی مجاز؛ امکان تکرار دارد",
    )
    evaluate.add_argument(
        "evaluation_command",
        nargs=argparse.REMAINDER,
        help="دستور ارزیابی",
    )
    ui = subparsers.add_parser("ui", help="اجرای رابط کاربری محلی")
    ui.add_argument("--env-file", help="مسیر فایل محیطی")
    ui.add_argument("--host", default="127.0.0.1", help="نشانی میزبان")
    ui.add_argument("--port", type=int, default=8787, help="شماره درگاه")
    ui.add_argument(
        "--no-browser",
        action="store_true",
        help="مرورگر را به‌صورت خودکار باز نکن",
    )
    evidence = subparsers.add_parser(
        "evidence", help="بازپخش، امضا و بررسی انسانی شواهد"
    )
    evidence.add_argument(
        "action",
        choices=("status", "bundle", "approve", "reject"),
        help="عملیات شواهد",
    )
    evidence.add_argument("--env-file", help="مسیر فایل محیطی")
    evidence.add_argument("--approver", help="نام بازبین محلی")
    evidence.add_argument("--note", default="", help="یادداشت بازبینی")
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
            result = runtime.doctor()
            print(
                json.dumps(
                    {
                        "وضعیت پیکربندی": result["configuration"],
                        "ارائه‌دهنده": result["provider"],
                        "مدل": result["model"],
                        "کلید API": result["api_key"],
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        if args.command == "evidence":
            control = runtime.evidence_control()
            if args.action == "status":
                payload = control.status()
            elif args.action == "bundle":
                payload = control.create_bundle()
            else:
                payload = control.approve_latest(
                    approver=args.approver or "",
                    decision=args.action,
                    note=args.note,
                )
            print(json.dumps(payload, indent=2, ensure_ascii=False))
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
        if args.command == "evaluate":
            command = list(args.evaluation_command)
            if command[:1] == ["--"]:
                command = command[1:]
            workspace = Path(args.workspace).resolve()
            evidence_path = Path(args.evidence_path)
            if not evidence_path.is_absolute():
                evidence_path = workspace / evidence_path
            recorder = EvidenceRecorder(
                sandbox=RootlessSandbox(
                    workspace=workspace,
                    image=args.image,
                    engine=args.engine,
                    limits=SandboxLimits(timeout_seconds=args.timeout),
                    allowed_commands=(
                        args.allowed_commands or DEFAULT_ALLOWED_COMMANDS
                    ),
                ),
                evidence_path=evidence_path,
            )
            evidence = recorder.evaluate(
                candidate_id=args.candidate_id,
                team_ids=args.team_id,
                command=command,
            )
            print(
                json.dumps(
                    {**asdict(evidence), "verified": evidence.verified},
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0 if evidence.verified else 2

        candidate = runtime.evolve(
            task=args.task,
            mutable_paths=list(args.mutable_path),
        )
        print(
            json.dumps(
                _localize_candidate(candidate),
                indent=2,
                default=str,
                ensure_ascii=False,
            )
        )
        evidence = candidate.get("evaluation_evidence")
        evidence_status = (
            evidence.get("status") if isinstance(evidence, dict) else "proposal_only"
        )
        return (
            0
            if candidate.get("rejection_reason") is None
            and evidence_status not in {"invalid", "sandbox_failed"}
            else 2
        )
    except (
        ConfigurationError,
        ProviderError,
        BudgetExceeded,
        SandboxError,
        ValueError,
    ) as exc:
        print(f"خطای EVO: {exc}")
        return 1


def _localize_candidate(candidate: dict[str, object]) -> dict[str, object]:
    proposal = candidate.get("proposal")
    score = candidate.get("score")
    status_labels = {
        "proposed": "پیشنهادشده",
        "eligible": "واجد شرایط",
        "rejected": "ردشده",
    }
    localized_proposal = (
        {
            "مسیر هدف": proposal.get("target_path"),
            "خلاصه": proposal.get("summary"),
            "منطق پیشنهاد": proposal.get("rationale"),
            "فایده مورد انتظار": proposal.get("expected_benefit"),
            "ریسک": proposal.get("risk"),
        }
        if isinstance(proposal, dict)
        else None
    )
    localized_score = (
        {
            "اعتبار ساختار": score.get("schema_validity"),
            "انطباق با سیاست": score.get("policy_compliance"),
            "کیفیت استدلال": score.get("rationale_quality"),
        }
        if isinstance(score, dict)
        else None
    )
    status = str(candidate.get("status", ""))
    return {
        "شناسه نامزد": candidate.get("candidate_id"),
        "اثر انگشت ژنوم": candidate.get("genome_fingerprint"),
        "پیشنهاد": localized_proposal,
        "امتیاز": localized_score,
        "وضعیت": status_labels.get(status, status),
        "دلیل رد": candidate.get("rejection_reason"),
        "شواهد ارزیابی": candidate.get("evaluation_evidence"),
        "واجد شرایط ارتقا": candidate.get("promotion_eligible", False),
    }


if __name__ == "__main__":
    raise SystemExit(main())
