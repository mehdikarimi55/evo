"""Non-self-modifiable authorization policy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


PROTECTED_PREFIXES = (
    ".git/",
    ".github/",
    ".gitattributes",
    ".gitignore",
    ".gitmodules",
    ".codex/",
    ".env",
    "AGENTS.md",
    "pyproject.toml",
    "requirements.txt",
    "requirements.lock",
    "tests/",
    "benchmarks/",
    "src/evo/kernel/",
    "src/evo/providers/",
    "src/evo/evolution/",
    "src/evo/ui/",
    "src/evo/cli.py",
    "src/evo/config.py",
    "src/evo/runtime.py",
    "src/evo/sandbox.py",
    "src/evo/worktree.py",
    "src/evo/mutation.py",
)

DENIED_EXTERNAL_ACTIONS = frozenset(
    {
        "account.create",
        "identity.verify",
        "terms.accept",
        "credential.obtain",
        "payment.create",
        "purchase.execute",
        "production.deploy",
    }
)


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    reason: str


class KernelPolicy:
    def authorize_mutation(
        self, target_path: str, mutable_paths: tuple[str, ...]
    ) -> PolicyDecision:
        if "\x00" in target_path or target_path.startswith("/"):
            return PolicyDecision(False, "مسیر باید نسبت به محیط کار تعریف شود")
        normalized = PurePosixPath(target_path).as_posix().lstrip("/")
        if not normalized or normalized == "." or ".." in PurePosixPath(normalized).parts:
            return PolicyDecision(
                False, "مسیر خالی است یا از محیط کار خارج می‌شود"
            )
        if any(
            normalized == prefix.rstrip("/") or normalized.startswith(prefix)
            for prefix in PROTECTED_PREFIXES
        ):
            return PolicyDecision(
                False, "مسیر مقصد متعلق به هسته تغییرناپذیر است"
            )
        safe_prefixes = tuple(
            normalized_prefix
            for prefix in mutable_paths
            if (
                (normalized_prefix := PurePosixPath(prefix).as_posix().strip("/"))
                and normalized_prefix != "."
                and ".." not in PurePosixPath(normalized_prefix).parts
            )
        )
        if not any(
            normalized == prefix or normalized.startswith(prefix + "/")
            for prefix in safe_prefixes
        ):
            return PolicyDecision(
                False, "مسیر مقصد خارج از مسیرهای قابل‌تغییر ژنوم است"
            )
        return PolicyDecision(True, "مسیر تغییر در محدوده زیست‌بوم قرار دارد")

    def authorize_external_action(self, action: str) -> PolicyDecision:
        if action in DENIED_EXTERNAL_ACTIONS:
            return PolicyDecision(
                False, "این عملیات به تأیید یک سامانه خارجی نیاز دارد"
            )
        return PolicyDecision(
            False, "عملیات خارجی در نسخه ۰٫۱ به‌صورت پیش‌فرض ممنوع است"
        )
