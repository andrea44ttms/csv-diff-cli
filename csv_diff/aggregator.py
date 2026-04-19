"""Aggregation of CSV diff results by column values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from .differ import DiffResult


class AggregateError(Exception):
    pass


@dataclass
class GroupStats:
    added: int = 0
    removed: int = 0
    modified: int = 0
    unchanged: int = 0

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified + self.unchanged


@dataclass
class AggregateResult:
    group_by: str
    groups: Dict[str, GroupStats] = field(default_factory=dict)


def parse_group_by(expr: str) -> str:
    col = expr.strip()
    if not col:
        raise AggregateError("group_by column must not be empty")
    return col


def aggregate_diff(result: DiffResult, group_by: str) -> AggregateResult:
    agg = AggregateResult(group_by=group_by)

    def _get_key(row: dict) -> str:
        if group_by not in row:
            raise AggregateError(f"Column '{group_by}' not found in row")
        return row[group_by]

    for row in result.added:
        k = _get_key(row)
        agg.groups.setdefault(k, GroupStats()).added += 1

    for row in result.removed:
        k = _get_key(row)
        agg.groups.setdefault(k, GroupStats()).removed += 1

    for old, _new in result.modified:
        k = _get_key(old)
        agg.groups.setdefault(k, GroupStats()).modified += 1

    for row in result.unchanged:
        k = _get_key(row)
        agg.groups.setdefault(k, GroupStats()).unchanged += 1

    return agg


def format_aggregate(agg: AggregateResult) -> str:
    lines = [f"Grouped by '{agg.group_by}':", ""]
    for group, stats in sorted(agg.groups.items()):
        lines.append(f"  {group}: +{stats.added} -{stats.removed} ~{stats.modified} ={stats.unchanged} (total {stats.total})")
    return "\n".join(lines)
