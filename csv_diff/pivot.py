from dataclasses import dataclass, field
from typing import Dict, List, Optional


class PivotError(Exception):
    pass


@dataclass
class PivotResult:
    row_keys: List[str]
    col_key: str
    value_key: str
    table: Dict[str, Dict[str, str]] = field(default_factory=dict)


def parse_pivot_spec(spec: str):
    """Parse 'row_key,col_key,value_key' string."""
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) != 3:
        raise PivotError(f"Pivot spec must be 'row_key,col_key,value_key', got: {spec!r}")
    return parts[0], parts[1], parts[2]


def pivot_rows(
    rows: List[Dict[str, str]],
    row_key: str,
    col_key: str,
    value_key: str,
) -> PivotResult:
    for required in (row_key, col_key, value_key):
        if rows and required not in rows[0]:
            raise PivotError(f"Column {required!r} not found in rows")

    result = PivotResult(row_keys=[row_key], col_key=col_key, value_key=value_key)
    for row in rows:
        rk = row[row_key]
        ck = row[col_key]
        vk = row[value_key]
        if rk not in result.table:
            result.table[rk] = {}
        result.table[rk][ck] = vk
    return result


def pivot_to_rows(pivot: PivotResult) -> List[Dict[str, str]]:
    """Flatten pivot table back to list of dicts."""
    all_cols: List[str] = []
    for col_map in pivot.table.values():
        for c in col_map:
            if c not in all_cols:
                all_cols.append(c)

    out = []
    for rk, col_map in pivot.table.items():
        row = {pivot.row_keys[0]: rk}
        for c in all_cols:
            row[c] = col_map.get(c, "")
        out.append(row)
    return out
