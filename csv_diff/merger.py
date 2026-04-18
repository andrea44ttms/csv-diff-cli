"""Merge two DiffResults or apply a patch strategy to produce a merged CSV."""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from .differ import DiffResult


class MergeError(Exception):
    pass


@dataclass
class MergeResult:
    headers: List[str]
    rows: List[Dict[str, str]] = field(default_factory=list)
    conflicts: List[Tuple[Dict, Dict]] = field(default_factory=list)


def _row_key(row: Dict[str, str], key: str) -> str:
    if key not in row:
        raise MergeError(f"Key column '{key}' not found in row: {row}")
    return row[key]


def merge_diffs(base: DiffResult, other: DiffResult, key: str) -> MergeResult:
    """Merge two diffs against the same base. 'other' changes take priority
    unless both modify the same row differently (conflict)."""
    if base.headers != other.headers:
        raise MergeError("Cannot merge diffs with different headers")

    headers = base.headers
    base_modified = {_row_key(a, key): (a, b) for a, b in base.modified}
    other_modified = {_row_key(a, key): (a, b) for a, b in other.modified}

    base_added = {_row_key(r, key): r for r in base.added}
    other_added = {_row_key(r, key): r for r in other.added}
    base_removed = {_row_key(r, key): r for r in base.removed}
    other_removed = {_row_key(r, key): r for r in other.removed}

    rows: List[Dict[str, str]] = []
    conflicts: List[Tuple[Dict, Dict]] = []

    all_keys = set(
        list(base_modified) + list(other_modified) +
        list(base_added) + list(other_added)
    ) - set(base_removed) - set(other_removed)

    for k in all_keys:
        if k in other_modified:
            _, new = other_modified[k]
            if k in base_modified and base_modified[k][1] != new:
                conflicts.append((base_modified[k][1], new))
            rows.append(new)
        elif k in base_modified:
            _, new = base_modified[k]
            rows.append(new)
        elif k in other_added:
            rows.append(other_added[k])
        elif k in base_added:
            rows.append(base_added[k])

    for r in base.unchanged:
        k = _row_key(r, key)
        if k not in other_removed and k not in base_removed and k not in other_modified and k not in base_modified:
            rows.append(r)

    return MergeResult(headers=headers, rows=rows, conflicts=conflicts)
