"""Map values in specified columns using a lookup table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MapError(Exception):
    """Raised when mapping configuration is invalid."""


@dataclass
class MapResult:
    rows: List[Dict[str, str]]
    mapped_columns: List[str]
    total_mapped: int


def parse_map_spec(spec: Optional[str]) -> Dict[str, Dict[str, str]]:
    """Parse a mapping spec string into a nested dict.

    Format: ``col:old=new,old2=new2;col2:x=y``
    Returns ``{column: {old_value: new_value}}``.
    """
    if not spec:
        return {}
    result: Dict[str, Dict[str, str]] = {}
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise MapError(f"Invalid map spec segment (missing ':'): {part!r}")
        col, mappings_str = part.split(":", 1)
        col = col.strip()
        if not col:
            raise MapError(f"Empty column name in map spec: {part!r}")
        mapping: Dict[str, str] = {}
        for pair in mappings_str.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if "=" not in pair:
                raise MapError(f"Invalid mapping pair (missing '='): {pair!r}")
            old, new = pair.split("=", 1)
            mapping[old.strip()] = new.strip()
        result[col] = mapping
    return result


def map_row(
    row: Dict[str, str],
    map_spec: Dict[str, Dict[str, str]],
) -> tuple[Dict[str, str], int]:
    """Apply value mappings to a single row. Returns (new_row, count_of_replacements)."""
    new_row = dict(row)
    count = 0
    for col, mapping in map_spec.items():
        if col in new_row and new_row[col] in mapping:
            new_row[col] = mapping[new_row[col]]
            count += 1
    return new_row, count


def map_rows(
    rows: List[Dict[str, str]],
    map_spec: Dict[str, Dict[str, str]],
) -> MapResult:
    """Apply value mappings to all rows."""
    if not map_spec:
        return MapResult(rows=list(rows), mapped_columns=[], total_mapped=0)
    out: List[Dict[str, str]] = []
    total = 0
    for row in rows:
        new_row, count = map_row(row, map_spec)
        out.append(new_row)
        total += count
    return MapResult(
        rows=out,
        mapped_columns=list(map_spec.keys()),
        total_mapped=total,
    )
