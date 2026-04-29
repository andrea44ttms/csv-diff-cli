"""Assign numeric weights to diff rows based on their status and column changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .differ import DiffResult


class WeighError(Exception):
    """Raised when weight configuration is invalid."""


_DEFAULT_WEIGHTS: Dict[str, float] = {
    "added": 1.0,
    "removed": 1.0,
    "modified": 0.5,
    "unchanged": 0.0,
}


@dataclass
class WeighedRow:
    status: str
    row: Dict[str, str]
    weight: float


@dataclass
class WeighResult:
    rows: List[WeighedRow] = field(default_factory=list)
    total_weight: float = 0.0


def parse_weight_map(raw: Optional[str]) -> Dict[str, float]:
    """Parse a weight map string like 'added=2.0,removed=1.5' into a dict."""
    weights = dict(_DEFAULT_WEIGHTS)
    if not raw:
        return weights
    for part in raw.split(","):
        part = part.strip()
        if "=" not in part:
            raise WeighError(f"Invalid weight spec (missing '='): {part!r}")
        key, _, val = part.partition("=")
        key = key.strip()
        if key not in _DEFAULT_WEIGHTS:
            raise WeighError(f"Unknown status key: {key!r}")
        try:
            weights[key] = float(val.strip())
        except ValueError:
            raise WeighError(f"Non-numeric weight for {key!r}: {val!r}")
    return weights


def weigh_rows(result: DiffResult, weights: Dict[str, float]) -> WeighResult:
    """Assign weights to every row in a DiffResult."""
    out: List[WeighedRow] = []
    total = 0.0
    for status, rows in (
        ("added", result.added),
        ("removed", result.removed),
        ("modified", [r for r, _ in result.modified]),
        ("unchanged", result.unchanged),
    ):
        w = weights.get(status, 0.0)
        for row in rows:
            out.append(WeighedRow(status=status, row=row, weight=w))
            total += w
    return WeighResult(rows=out, total_weight=round(total, 6))


def format_weigh(wr: WeighResult) -> str:
    """Return a human-readable summary of total weight."""
    lines = [f"Total weight: {wr.total_weight}"]
    for r in wr.rows:
        if r.weight != 0.0:
            lines.append(f"  [{r.status}] weight={r.weight}  {r.row}")
    return "\n".join(lines)
