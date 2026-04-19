"""Cell-level diff highlighting for modified rows."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


class HighlightError(Exception):
    pass


@dataclass
class CellDiff:
    column: str
    old_value: str
    new_value: str


@dataclass
class RowHighlight:
    key: str
    changes: List[CellDiff] = field(default_factory=list)

    @property
    def changed_columns(self) -> List[str]:
        return [c.column for c in self.changes]


def highlight_row(
    old_row: Dict[str, str],
    new_row: Dict[str, str],
) -> RowHighlight:
    """Return a RowHighlight describing cell-level differences between two rows."""
    if old_row.keys() != new_row.keys():
        raise HighlightError(
            f"Row keys do not match: {list(old_row.keys())} vs {list(new_row.keys())}"
        )
    key = next(iter(old_row.values()), "")
    changes = [
        CellDiff(column=col, old_value=old_row[col], new_value=new_row[col])
        for col in old_row
        if old_row[col] != new_row[col]
    ]
    return RowHighlight(key=key, changes=changes)


def highlight_diff(modified: List[Tuple[Dict, Dict]]) -> List[RowHighlight]:
    """Highlight all modified row pairs."""
    return [highlight_row(old, new) for old, new in modified]


def format_highlight(highlights: List[RowHighlight]) -> str:
    """Render highlights as a human-readable string."""
    if not highlights:
        return "No cell-level changes."
    lines = []
    for rh in highlights:
        lines.append(f"Row [{rh.key}]:")
        for cd in rh.changes:
            lines.append(f"  {cd.column}: {cd.old_value!r} -> {cd.new_value!r}")
    return "\n".join(lines)
