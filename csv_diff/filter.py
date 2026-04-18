"""Row filtering utilities for csv-diff-cli."""

from typing import List, Dict, Optional


class FilterError(ValueError):
    """Raised when a filter expression is invalid."""


def parse_filter(expr: str) -> tuple:
    """Parse a filter expression like 'column=value' or 'column!=value'.

    Returns (column, operator, value).
    """
    for op in ("!=", "="):
        if op in expr:
            parts = expr.split(op, 1)
            if len(parts) != 2 or not parts[0].strip():
                raise FilterError(f"Invalid filter expression: {expr!r}")
            return parts[0].strip(), op, parts[1].strip()
    raise FilterError(
        f"Filter expression must contain '=' or '!=': {expr!r}"
    )


def apply_filter(
    rows: List[Dict[str, str]],
    column: str,
    operator: str,
    value: str,
) -> List[Dict[str, str]]:
    """Return rows matching the filter condition."""
    if operator == "=":
        return [r for r in rows if r.get(column) == value]
    elif operator == "!=":
        return [r for r in rows if r.get(column) != value]
    raise FilterError(f"Unknown operator: {operator!r}")


def filter_rows(
    rows: List[Dict[str, str]],
    expr: Optional[str],
) -> List[Dict[str, str]]:
    """Filter rows by an optional expression string.

    If expr is None or empty, returns rows unchanged.
    """
    if not expr:
        return rows
    column, operator, value = parse_filter(expr)
    if not rows:
        return rows
    available = set(rows[0].keys())
    if column not in available:
        raise FilterError(
            f"Column {column!r} not found. Available: {sorted(available)}"
        )
    return apply_filter(rows, column, operator, value)
