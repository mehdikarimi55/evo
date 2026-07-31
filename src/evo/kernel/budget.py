"""Run-local resource accounting."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


class BudgetExceeded(RuntimeError):
    """Raised before an operation would exceed its declared resource ceiling."""


@dataclass(frozen=True, slots=True)
class BudgetSnapshot:
    calls_used: int
    input_tokens_used: int
    output_tokens_used: int


class RunBudget:
    def __init__(
        self,
        *,
        max_calls: int,
        max_input_tokens: int,
        max_output_tokens: int,
    ) -> None:
        self.max_calls = max_calls
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self._calls = 0
        self._input_tokens = 0
        self._output_tokens = 0
        self._lock = Lock()

    def reserve_call(self) -> None:
        with self._lock:
            if self._calls + 1 > self.max_calls:
                raise BudgetExceeded("سقف مجاز درخواست از مدل رد شده است")
            self._calls += 1

    def record_usage(self, input_tokens: int, output_tokens: int) -> None:
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("میزان مصرف توکن نمی‌تواند منفی باشد")
        with self._lock:
            next_input = self._input_tokens + input_tokens
            next_output = self._output_tokens + output_tokens
            if next_input > self.max_input_tokens:
                raise BudgetExceeded("سقف مجاز توکن ورودی رد شده است")
            if next_output > self.max_output_tokens:
                raise BudgetExceeded("سقف مجاز توکن خروجی رد شده است")
            self._input_tokens = next_input
            self._output_tokens = next_output

    def snapshot(self) -> BudgetSnapshot:
        with self._lock:
            return BudgetSnapshot(
                calls_used=self._calls,
                input_tokens_used=self._input_tokens,
                output_tokens_used=self._output_tokens,
            )
