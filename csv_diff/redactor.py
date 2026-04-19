"""Redact (mask) specified columns in CSV rows."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

MASK = "***"


class RedactError(Exception):
    pass


@dataclass
class RedactResult:
    rows: List[Dict[str, str]]
    redacted_columns: List[str]


def parse_redact_columns(expr: str | None) -> List[str]:
    """Parse comma-separated column names to redact."""
    if not expr or not expr.strip():
        raise RedactError("Redact column list must not be empty.")
    cols = [c.strip() for c in expr.split(",")]
    if any(c == "" for c in cols):
        raise RedactError("Redact column list contains empty entry.")
    return cols


def redact_row(row: Dict[str, str], columns: List[str], mask: str = MASK) -> Dict[str, str]:
    """Return a copy of row with specified columns masked."""
    missing = [c for c in columns if c not in row]
    if missing:
        raise RedactError(f"Columns not found in row: {missing}")
    return {k: (mask if k in columns else v) for k, v in row.items()}


def redact_rows(
    rows: List[Dict[str, str]],
    columns: List[str],
    mask: str = MASK,
) -> RedactResult:
    """Redact columns across all rows."""
    if not rows:
        return RedactResult(rows=[], redacted_columns=columns)
    result = [redact_row(r, columns, mask) for r in rows]
    return RedactResult(rows=result, redacted_columns=columns)
