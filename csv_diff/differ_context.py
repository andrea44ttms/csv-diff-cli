"""Context-window module: extract N rows of surrounding context around changed rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csv_diff.differ import DiffResult


class ContextError(ValueError):
    """Raised when context configuration is invalid."""


@dataclass
class ContextRow:
    index: int
    row: dict
    is_changed: bool


@dataclass
class ContextResult:
    headers: List[str]
    rows: List[ContextRow] = field(default_factory=list)


def parse_context_lines(value: object) -> int:
    """Parse and validate the number of context lines."""
    if value is None:
        return 0
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ContextError(f"context lines must be an integer, got {value!r}")
    if n < 0:
        raise ContextError(f"context lines must be >= 0, got {n}")
    return n


def _changed_indices(result: DiffResult) -> set:
    """Return the set of row indices (0-based) that are changed in the 'new' file."""
    indices: set = set()
    all_rows = result.added + result.removed + result.modified + result.unchanged
    # Build index from row identity by matching dicts
    new_rows = result.added + result.modified + result.unchanged
    for i, row in enumerate(new_rows):
        status_rows = result.added + result.modified
        if any(row is s or row == s for s in status_rows):
            indices.add(i)
    return indices


def extract_context(result: DiffResult, context_lines: int) -> ContextResult:
    """Return rows with context_lines of surrounding unchanged rows for each change."""
    if context_lines < 0:
        raise ContextError("context_lines must be >= 0")

    new_rows = result.added + result.modified + result.unchanged
    changed_set = set()
    for i, row in enumerate(new_rows):
        if any(row is r or row == r for r in result.added + result.modified):
            changed_set.add(i)

    if not changed_set:
        return ContextResult(headers=result.headers)

    visible: set = set()
    for idx in changed_set:
        for offset in range(-context_lines, context_lines + 1):
            neighbour = idx + offset
            if 0 <= neighbour < len(new_rows):
                visible.add(neighbour)

    rows = [
        ContextRow(index=i, row=new_rows[i], is_changed=(i in changed_set))
        for i in sorted(visible)
    ]
    return ContextResult(headers=result.headers, rows=rows)
