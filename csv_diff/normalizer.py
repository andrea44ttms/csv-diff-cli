"""Normalize CSV row values (strip whitespace, case folding, type coercion)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional


class NormalizeError(Exception):
    pass


@dataclass
class NormalizeOptions:
    strip: bool = True
    lowercase: bool = False
    uppercase: bool = False
    columns: Optional[List[str]] = None  # None means all columns


def parse_normalize_options(
    lowercase: bool = False,
    uppercase: bool = False,
    columns_expr: Optional[str] = None,
) -> NormalizeOptions:
    if lowercase and uppercase:
        raise NormalizeError("Cannot specify both --normalize-lower and --normalize-upper")
    columns: Optional[List[str]] = None
    if columns_expr:
        columns = [c.strip() for c in columns_expr.split(",") if c.strip()]
        if not columns:
            raise NormalizeError("--normalize-columns produced an empty column list")
    return NormalizeOptions(strip=True, lowercase=lowercase, uppercase=uppercase, columns=columns)


def _normalize_value(value: str, opts: NormalizeOptions) -> str:
    if opts.strip:
        value = value.strip()
    if opts.lowercase:
        value = value.lower()
    elif opts.uppercase:
        value = value.upper()
    return value


def normalize_row(row: Dict[str, str], opts: NormalizeOptions) -> Dict[str, str]:
    target_cols = set(opts.columns) if opts.columns is not None else None
    result: Dict[str, str] = {}
    for col, val in row.items():
        if target_cols is None or col in target_cols:
            result[col] = _normalize_value(val, opts)
        else:
            result[col] = val
    return result


def normalize_rows(
    rows: List[Dict[str, str]], opts: NormalizeOptions
) -> List[Dict[str, str]]:
    return [normalize_row(r, opts) for r in rows]
