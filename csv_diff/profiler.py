"""Column profiling: value counts, nulls, and unique stats per column."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any


class ProfileError(Exception):
    pass


@dataclass
class ColumnProfile:
    name: str
    total: int = 0
    empty: int = 0
    unique_values: int = 0
    top_values: Dict[str, int] = field(default_factory=dict)

    @property
    def fill_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.total - self.empty) / self.total, 4)


@dataclass
class ProfileResult:
    headers: List[str]
    columns: Dict[str, ColumnProfile]


def profile_rows(headers: List[str], rows: List[Dict[str, Any]], top_n: int = 5) -> ProfileResult:
    if not headers:
        raise ProfileError("No headers provided for profiling.")

    counts: Dict[str, Dict[str, int]] = {h: {} for h in headers}
    totals: Dict[str, int] = {h: 0 for h in headers}
    empties: Dict[str, int] = {h: 0 for h in headers}

    for row in rows:
        for h in headers:
            val = row.get(h, "")
            totals[h] += 1
            if val == "" or val is None:
                empties[h] += 1
            counts[h][val] = counts[h].get(val, 0) + 1

    columns = {}
    for h in headers:
        top = dict(
            sorted(counts[h].items(), key=lambda x: x[1], reverse=True)[:top_n]
        )
        columns[h] = ColumnProfile(
            name=h,
            total=totals[h],
            empty=empties[h],
            unique_values=len(counts[h]),
            top_values=top,
        )

    return ProfileResult(headers=headers, columns=columns)


def format_profile(result: ProfileResult) -> str:
    lines = ["Column Profile:", "-" * 40]
    for h in result.headers:
        cp = result.columns[h]
        lines.append(f"  {cp.name}")
        lines.append(f"    total={cp.total}  empty={cp.empty}  unique={cp.unique_values}  fill_rate={cp.fill_rate}")
        top = ", ".join(f"{v!r}:{c}" for v, c in cp.top_values.items())
        lines.append(f"    top: {top}")
    return "\n".join(lines)
