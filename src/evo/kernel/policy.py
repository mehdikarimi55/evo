"""Non-self-modifiable authorization policy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


PROTECTED_PREFIXES = (
    ".git/",
    ".github/",
    ".env",
    "src/evo/kernel/",
    "src/evo/providers/",
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
            return PolicyDecision(False, "Path must be a relative workspace path")
        normalized = PurePosixPath(target_path).as_posix().lstrip("/")
        if not normalized or normalized == "." or ".." in PurePosixPath(normalized).parts:
            return PolicyDecision(False, "Path is empty or escapes the workspace")
        if any(
            normalized == prefix.rstrip("/") or normalized.startswith(prefix)
            for prefix in PROTECTED_PREFIXES
        ):
            return PolicyDecision(False, "Target belongs to the immutable kernel")
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
            return PolicyDecision(False, "Target is outside genome mutable paths")
        return PolicyDecision(True, "Mutation target is inside the terrarium")

    def authorize_external_action(self, action: str) -> PolicyDecision:
        if action in DENIED_EXTERNAL_ACTIONS:
            return PolicyDecision(False, "Action requires an external approval gate")
        return PolicyDecision(False, "External actions are deny-by-default in v0.1")
