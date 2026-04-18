"""Core diffing logic for comparing two CSV files."""

from dataclasses import dataclass, field
from typing import Any


class DiffError(Exception):
    pass


@dataclass
class DiffResult:
    added: list[dict[str, Any]] = field(default_factory=list)
    removed: list[dict[str, Any]] = field(default_factory=list)
    modified: list[dict[str, tuple[Any, Any]]] = field(default_factory=list)
    unchanged: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.modified)


def diff_csv(
    rows_a: list[dict[str, Any]],
    rows_b: list[dict[str, Any]],
    key: str,
) -> DiffResult:
    """Compare two lists of CSV rows by a key column."""
    if not rows_a and not rows_b:
        return DiffResult()

    map_a = {row[key]: row for row in rows_a if key in row}
    map_b = {row[key]: row for row in rows_b if key in row}

    if len(map_a) != len(rows_a) or len(map_b) != len(rows_b):
        raise DiffError(f"Key column '{key}' contains duplicate or missing values.")

    keys_a = set(map_a)
    keys_b = set(map_b)

    result = DiffResult()
    result.removed = [map_a[k] for k in keys_a - keys_b]
    result.added = [map_b[k] for k in keys_b - keys_a]

    for k in keys_a & keys_b:
        row_a, row_b = map_a[k], map_b[k]
        changes = {
            col: (row_a.get(col), row_b.get(col))
            for col in set(row_a) | set(row_b)
            if row_a.get(col) != row_b.get(col)
        }
        if changes:
            result.modified.append({"_key": k, **changes})
        else:
            result.unchanged.append(row_a)

    return result
