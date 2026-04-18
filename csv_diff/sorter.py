"""Sorting utilities for CSV rows before diffing."""

from typing import List, Dict, Optional


class SortError(Exception):
    """Raised when sorting configuration is invalid."""


def parse_sort_keys(sort_expr: str) -> List[Dict]:
    """
    Parse a sort expression like "name:asc,age:desc" into a list of
    {"column": ..., "reverse": ...} dicts.
    """
    keys = []
    for part in sort_expr.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            col, direction = part.rsplit(":", 1)
            col = col.strip()
            direction = direction.strip().lower()
            if direction not in ("asc", "desc"):
                raise SortError(
                    f"Invalid sort direction '{direction}' for column '{col}'. Use 'asc' or 'desc'."
                )
            reverse = direction == "desc"
        else:
            col = part.strip()
            reverse = False
        if not col:
            raise SortError("Sort column name cannot be empty.")
        keys.append({"column": col, "reverse": reverse})
    if not keys:
        raise SortError("Sort expression produced no valid sort keys.")
    return keys


def sort_rows(
    rows: List[Dict[str, str]],
    sort_keys: List[Dict],
    headers: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    Sort rows by the given sort keys. Each key specifies a column and direction.
    Unknown columns raise SortError.
    """
    if not rows:
        return rows

    available = set(rows[0].keys())
    for key in sort_keys:
        col = key["column"]
        if col not in available:
            raise SortError(
                f"Sort column '{col}' not found in CSV headers: {sorted(available)}"
            )

    def sort_key_fn(row: Dict[str, str]):
        return tuple(row.get(k["column"], "") for k in sort_keys)

    # Apply stable multi-key sort by iterating keys in reverse order
    result = list(rows)
    for key in reversed(sort_keys):
        result = sorted(result, key=lambda r: r.get(key["column"], ""), reverse=key["reverse"])
    return result
