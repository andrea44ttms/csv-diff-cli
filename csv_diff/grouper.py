"""Group diff rows by a column value, producing named buckets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .differ import DiffResult


class GroupError(Exception):
    """Raised when grouping fails."""


@dataclass
class GroupResult:
    column: str
    groups: Dict[str, DiffResult] = field(default_factory=dict)


def parse_group_column(value: Optional[str]) -> Optional[str]:
    """Return stripped column name or None."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        raise GroupError("Group column name must not be empty.")
    return stripped


def group_diff(result: DiffResult, column: str) -> GroupResult:
    """Partition *result* rows into sub-DiffResults keyed by *column* value."""
    headers = result.headers
    if column not in headers:
        raise GroupError(f"Column '{column}' not found in headers: {headers}")

    buckets: Dict[str, Dict[str, List]] = {}

    def _bucket(key: str) -> Dict[str, List]:
        if key not in buckets:
            buckets[key] = {"added": [], "removed": [], "modified": [], "unchanged": []}
        return buckets[key]

    for row in result.added:
        _bucket(row.get(column, ""))["added"].append(row)
    for row in result.removed:
        _bucket(row.get(column, ""))["removed"].append(row)
    for old, new in result.modified:
        _bucket(new.get(column, ""))["modified"].append((old, new))
    for row in result.unchanged:
        _bucket(row.get(column, ""))["unchanged"].append(row)

    groups: Dict[str, DiffResult] = {}
    for key, data in sorted(buckets.items()):
        groups[key] = DiffResult(
            headers=headers,
            added=data["added"],
            removed=data["removed"],
            modified=data["modified"],
            unchanged=data["unchanged"],
        )

    return GroupResult(column=column, groups=groups)


def format_group_summary(gr: GroupResult) -> str:
    """Return a human-readable summary of groups."""
    lines = [f"Grouped by '{gr.column}':"]
    for key, dr in gr.groups.items():
        total = len(dr.added) + len(dr.removed) + len(dr.modified) + len(dr.unchanged)
        lines.append(
            f"  [{key}] total={total} added={len(dr.added)} "
            f"removed={len(dr.removed)} modified={len(dr.modified)} "
            f"unchanged={len(dr.unchanged)}"
        )
    return "\n".join(lines)
