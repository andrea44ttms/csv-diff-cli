"""Threshold filtering: suppress diff output when change rate is below a minimum."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csv_diff.differ import DiffResult
from csv_diff.stats import compute_stats


class ThresholdError(Exception):
    """Raised when threshold configuration is invalid."""


@dataclass(frozen=True)
class ThresholdResult:
    passed: bool          # True when change rate >= min_rate
    change_rate: float    # Actual change rate (0.0 – 1.0)
    min_rate: float       # Configured minimum
    result: DiffResult    # Original diff (always preserved)


def parse_min_rate(value: Optional[str]) -> float:
    """Parse a threshold percentage string such as '5' or '12.5' into a fraction.

    Accepts values in the range [0, 100].  Returns 0.0 when *value* is None.
    """
    if value is None:
        return 0.0
    try:
        pct = float(value)
    except ValueError:
        raise ThresholdError(
            f"Threshold must be a number, got {value!r}"
        )
    if not (0.0 <= pct <= 100.0):
        raise ThresholdError(
            f"Threshold must be between 0 and 100, got {pct}"
        )
    return pct / 100.0


def apply_threshold(result: DiffResult, min_rate: float) -> ThresholdResult:
    """Evaluate whether *result* meets the minimum change-rate *min_rate*.

    The diff itself is never modified; callers decide what to do when
    ``ThresholdResult.passed`` is *False*.
    """
    stats = compute_stats(result)
    total = stats.added + stats.removed + stats.modified + stats.unchanged
    changed = stats.added + stats.removed + stats.modified
    rate = changed / total if total > 0 else 0.0
    return ThresholdResult(
        passed=rate >= min_rate,
        change_rate=rate,
        min_rate=min_rate,
        result=result,
    )


def format_threshold(tr: ThresholdResult) -> str:
    """Return a human-readable summary line for the threshold evaluation."""
    status = "PASSED" if tr.passed else "BELOW THRESHOLD"
    return (
        f"Threshold: {status} "
        f"(change rate {tr.change_rate * 100:.1f}% "
        f"vs minimum {tr.min_rate * 100:.1f}%)"
    )
