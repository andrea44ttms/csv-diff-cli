"""ranker.py – rank diff rows by a numeric column value."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .differ import DiffResult


class RankError(ValueError):
    pass


@dataclass
class RankedRow:
    status: str
    row: Dict[str, str]
    rank: int
    score: float


@dataclass
class RankResult:
    column: str
    ascending: bool
    rows: List[RankedRow] = field(default_factory=list)


def parse_rank_column(value: Optional[str]) -> Optional[str]:
    """Return stripped column name or None."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        raise RankError("Rank column must not be empty.")
    return stripped


def parse_rank_order(value: Optional[str]) -> bool:
    """Return True for ascending, False for descending."""
    if value is None:
        return False  # default: descending (highest first)
    v = value.strip().lower()
    if v in ("asc", "ascending"):
        return True
    if v in ("desc", "descending"):
        return False
    raise RankError(f"Unknown rank order {value!r}; use 'asc' or 'desc'.")


def _score(row: Dict[str, str], column: str) -> float:
    val = row.get(column, "")
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def rank_diff(result: DiffResult, column: str, ascending: bool = False) -> RankResult:
    """Collect all changed rows, sort by *column*, and assign 1-based ranks."""
    all_rows: List[Dict[str, str]] = []
    statuses: Dict[int, str] = {}

    for row in result.added:
        statuses[len(all_rows)] = "added"
        all_rows.append(row)
    for row in result.removed:
        statuses[len(all_rows)] = "removed"
        all_rows.append(row)
    for old, new in result.modified:
        statuses[len(all_rows)] = "modified"
        all_rows.append(new)

    if not all_rows:
        return RankResult(column=column, ascending=ascending, rows=[])

    scored = [(i, _score(r, column), r) for i, r in enumerate(all_rows)]
    scored.sort(key=lambda t: t[1], reverse=not ascending)

    ranked_rows = [
        RankedRow(status=statuses[i], row=r, rank=pos + 1, score=s)
        for pos, (i, s, r) in enumerate(scored)
    ]
    return RankResult(column=column, ascending=ascending, rows=ranked_rows)
