"""masker.py – selectively mask cell values matching a pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MaskError(Exception):
    """Raised when masking configuration or execution fails."""


@dataclass
class MaskResult:
    rows: List[Dict[str, str]] = field(default_factory=list)
    masked_count: int = 0


def parse_mask_spec(spec: Optional[str]) -> Dict[str, re.Pattern]:
    """Parse 'col:pattern,col2:pattern2' into {column: compiled_regex}.

    Raises MaskError on empty spec or malformed entries.
    """
    if not spec:
        raise MaskError("mask spec must not be empty")
    result: Dict[str, re.Pattern] = {}
    for part in spec.split(","):
        part = part.strip()
        if ":" not in part:
            raise MaskError(
                f"invalid mask spec entry {part!r}: expected 'column:pattern'"
            )
        col, pattern = part.split(":", 1)
        col = col.strip()
        pattern = pattern.strip()
        if not col:
            raise MaskError("column name must not be empty in mask spec")
        try:
            result[col] = re.compile(pattern)
        except re.error as exc:
            raise MaskError(f"invalid regex {pattern!r}: {exc}") from exc
    return result


MASK_PLACEHOLDER = "***"


def mask_row(
    row: Dict[str, str],
    spec: Dict[str, re.Pattern],
    placeholder: str = MASK_PLACEHOLDER,
) -> tuple[Dict[str, str], int]:
    """Return (new_row, count_of_cells_masked) for a single row."""
    new_row = dict(row)
    count = 0
    for col, pattern in spec.items():
        if col in new_row and pattern.search(new_row[col]):
            new_row[col] = placeholder
            count += 1
    return new_row, count


def mask_rows(
    rows: List[Dict[str, str]],
    spec: Dict[str, re.Pattern],
    placeholder: str = MASK_PLACEHOLDER,
) -> MaskResult:
    """Apply pattern-based masking to every row."""
    out: List[Dict[str, str]] = []
    total_masked = 0
    for row in rows:
        new_row, count = mask_row(row, spec, placeholder)
        out.append(new_row)
        total_masked += count
    return MaskResult(rows=out, masked_count=total_masked)
