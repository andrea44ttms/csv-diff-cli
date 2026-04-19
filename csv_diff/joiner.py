"""Join two DiffResults on a shared key column."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from .differ import DiffResult


class JoinError(Exception):
    pass


@dataclass
class JoinResult:
    headers: List[str]
    rows: List[Dict[str, str]]


def parse_join_key(key: Optional[str]) -> str:
    if not key or not key.strip():
        raise JoinError("Join key column must not be empty")
    return key.strip()


def _index_rows(rows: List[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    index: Dict[str, Dict[str, str]] = {}
    for row in rows:
        if key not in row:
            raise JoinError(f"Key column '{key}' not found in row: {row}")
        index[row[key]] = row
    return index


def join_diff_rows(
    left: DiffResult,
    right: DiffResult,
    key: str,
    suffixes: tuple[str, str] = ("_left", "_right"),
) -> JoinResult:
    """Inner-join the *added* rows of two DiffResults on a shared key."""
    left_idx = _index_rows(left.added, key)
    right_idx = _index_rows(right.added, key)

    common_keys = set(left_idx) & set(right_idx)

    if not common_keys:
        return JoinResult(headers=[], rows=[])

    left_sample = next(iter(left_idx.values()))
    right_sample = next(iter(right_idx.values()))

    left_cols = [c for c in left_sample if c != key]
    right_cols = [c for c in right_sample if c != key]

    headers = [key]
    for c in left_cols:
        headers.append(c + suffixes[0] if c in right_cols else c)
    for c in right_cols:
        headers.append(c + suffixes[1] if c in left_cols else c)

    rows: List[Dict[str, str]] = []
    for k in sorted(common_keys):
        lr = left_idx[k]
        rr = right_idx[k]
        merged: Dict[str, str] = {key: k}
        for c in left_cols:
            merged[c + suffixes[0] if c in right_cols else c] = lr[c]
        for c in right_cols:
            merged[c + suffixes[1] if c in left_cols else c] = rr[c]
        rows.append(merged)

    return JoinResult(headers=headers, rows=rows)
