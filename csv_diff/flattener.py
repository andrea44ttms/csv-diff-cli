"""Flatten nested diff results into a list of plain dicts for tabular output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .differ import DiffResult


class FlattenError(Exception):
    """Raised when flattening fails."""


@dataclass
class FlatRow:
    status: str
    key: str
    column: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    extra: Dict[str, str] = field(default_factory=dict)


def _flat_row(
    status: str,
    key: str,
    column: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    extra: Optional[Dict[str, str]] = None,
) -> FlatRow:
    return FlatRow(
        status=status,
        key=key,
        column=column,
        old_value=old_value,
        new_value=new_value,
        extra=extra or {},
    )


def flatten_diff(result: DiffResult, key_column: str = "id") -> List[FlatRow]:
    """Convert a DiffResult into a flat list of FlatRow objects.

    Each modified row produces one FlatRow per changed column.
    Added and removed rows produce a single FlatRow with column=None.
    """
    if not isinstance(result, DiffResult):
        raise FlattenError("Expected a DiffResult instance.")

    rows: List[FlatRow] = []

    for row in result.added:
        key = row.get(key_column, "")
        rows.append(_flat_row("added", key, extra=dict(row)))

    for row in result.removed:
        key = row.get(key_column, "")
        rows.append(_flat_row("removed", key, extra=dict(row)))

    for old, new in result.modified:
        key = old.get(key_column, "")
        all_columns = set(old) | set(new)
        changed = [
            col for col in all_columns
            if old.get(col) != new.get(col) and col != key_column
        ]
        if not changed:
            rows.append(_flat_row("modified", key))
        for col in sorted(changed):
            rows.append(
                _flat_row(
                    "modified",
                    key,
                    column=col,
                    old_value=old.get(col),
                    new_value=new.get(col),
                )
            )

    return rows


def flatten_to_dicts(result: DiffResult, key_column: str = "id") -> List[Dict[str, str]]:
    """Return flat rows as plain dicts suitable for CSV/JSON export."""
    flat = flatten_diff(result, key_column=key_column)
    return [
        {
            "status": r.status,
            "key": r.key,
            "column": r.column or "",
            "old_value": r.old_value or "",
            "new_value": r.new_value or "",
        }
        for r in flat
    ]
