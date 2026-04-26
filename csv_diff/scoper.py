"""scoper.py – restrict diff results to a sliding row-range window."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff.differ import DiffResult


class ScopeError(ValueError):
    """Raised when scope parameters are invalid."""


@dataclass
class ScopeResult:
    rows: List[dict] = field(default_factory=list)
    start: int = 0
    end: int = 0
    total_before_scope: int = 0


def parse_scope(
    start: Optional[str],
    end: Optional[str],
    total: int,
) -> tuple[int, int]:
    """Parse and validate start/end row indices (1-based, inclusive)."""
    try:
        s = int(start) if start is not None else 1
        e = int(end) if end is not None else total
    except (TypeError, ValueError) as exc:
        raise ScopeError(f"Scope values must be integers: {exc}") from exc

    if s < 1:
        raise ScopeError(f"--scope-start must be >= 1, got {s}")
    if e < s:
        raise ScopeError(
            f"--scope-end ({e}) must be >= --scope-start ({s})"
        )
    return s, e


def scope_diff(result: DiffResult, start: int, end: int) -> ScopeResult:
    """Return only the rows whose 1-based position falls within [start, end]."""
    all_rows: List[dict] = (
        result.added + result.removed + result.modified + result.unchanged
    )
    total = len(all_rows)

    # clamp end to actual length
    clamped_end = min(end, total)
    sliced = all_rows[start - 1 : clamped_end]

    return ScopeResult(
        rows=sliced,
        start=start,
        end=clamped_end,
        total_before_scope=total,
    )


def format_scope(sr: ScopeResult) -> str:
    """Return a human-readable summary of the scope window."""
    if sr.total_before_scope == 0:
        return "Scope: no rows available."
    return (
        f"Scope: rows {sr.start}–{sr.end} "
        f"of {sr.total_before_scope} total "
        f"({len(sr.rows)} shown)."
    )
