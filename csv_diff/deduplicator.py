from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


class DeduplicateError(Exception):
    pass


@dataclass
class DeduplicateResult:
    unique: List[Dict[str, str]]
    duplicates: List[Dict[str, str]]
    duplicate_keys: List[Tuple[str, ...]]


def parse_key_columns(key_str: str) -> List[str]:
    cols = [c.strip() for c in key_str.split(",") if c.strip()]
    if not cols:
        raise DeduplicateError("Key columns must not be empty")
    return cols


def _row_key(row: Dict[str, str], keys: List[str]) -> Tuple[str, ...]:
    missing = [k for k in keys if k not in row]
    if missing:
        raise DeduplicateError(f"Key column(s) not found in row: {missing}")
    return tuple(row[k] for k in keys)


def deduplicate_rows(
    rows: List[Dict[str, str]],
    key_columns: List[str],
    keep: str = "first",
) -> DeduplicateResult:
    if keep not in ("first", "last"):
        raise DeduplicateError(f"keep must be 'first' or 'last', got '{keep}'")

    seen: Dict[Tuple[str, ...], int] = {}
    for i, row in enumerate(rows):
        key = _row_key(row, key_columns)
        if keep == "first":
            if key not in seen:
                seen[key] = i
        else:
            seen[key] = i

    kept_indices = set(seen.values())
    unique = [row for i, row in enumerate(rows) if i in kept_indices]
    duplicates = [row for i, row in enumerate(rows) if i not in kept_indices]
    dup_keys = list({
        _row_key(row, key_columns)
        for i, row in enumerate(rows)
        if i not in kept_indices
    })
    return DeduplicateResult(unique=unique, duplicates=duplicates, duplicate_keys=dup_keys)
