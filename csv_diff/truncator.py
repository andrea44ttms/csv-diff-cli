"""Truncate diff results to a maximum number of rows per category."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from csv_diff.differ import DiffResult


class TruncateError(Exception):
    pass


@dataclass
class TruncateResult:
    result: DiffResult
    added_truncated: int
    removed_truncated: int
    modified_truncated: int
    unchanged_truncated: int

    @property
    def any_truncated(self) -> bool:
        return any([
            self.added_truncated,
            self.removed_truncated,
            self.modified_truncated,
            self.unchanged_truncated,
        ])


def parse_max_rows(value: str) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise TruncateError(f"max-rows must be an integer, got: {value!r}")
    if n <= 0:
        raise TruncateError(f"max-rows must be a positive integer, got: {n}")
    return n


def _trunc(rows: list, n: Optional[int]) -> tuple[list, int]:
    if n is None or len(rows) <= n:
        return rows, 0
    return rows[:n], len(rows) - n


def truncate_diff(result: DiffResult, max_rows: Optional[int]) -> TruncateResult:
    added, at = _trunc(result.added, max_rows)
    removed, rt = _trunc(result.removed, max_rows)
    modified, mt = _trunc(result.modified, max_rows)
    unchanged, ut = _trunc(result.unchanged, max_rows)
    truncated = DiffResult(
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
    )
    return TruncateResult(
        result=truncated,
        added_truncated=at,
        removed_truncated=rt,
        modified_truncated=mt,
        unchanged_truncated=ut,
    )


def format_truncation_notice(tr: TruncateResult) -> str:
    if not tr.any_truncated:
        return ""
    parts = []
    if tr.added_truncated:
        parts.append(f"added: {tr.added_truncated}")
    if tr.removed_truncated:
        parts.append(f"removed: {tr.removed_truncated}")
    if tr.modified_truncated:
        parts.append(f"modified: {tr.modified_truncated}")
    if tr.unchanged_truncated:
        parts.append(f"unchanged: {tr.unchanged_truncated}")
    return "[truncated] " + ", ".join(parts)
