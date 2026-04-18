"""Column selection and renaming transformations for CSV rows."""

from typing import List, Dict, Optional


class TransformError(Exception):
    pass


def parse_columns(columns_expr: str) -> List[str]:
    """Parse a comma-separated list of column names."""
    if not columns_expr or not columns_expr.strip():
        raise TransformError("Columns expression must not be empty")
    return [c.strip() for c in columns_expr.split(",") if c.strip()]


def parse_rename(rename_expr: str) -> Dict[str, str]:
    """Parse rename mappings like 'old:new,old2:new2'."""
    mapping: Dict[str, str] = {}
    if not rename_expr or not rename_expr.strip():
        return mapping
    for part in rename_expr.split(","):
        part = part.strip()
        if ":" not in part:
            raise TransformError(f"Invalid rename expression '{part}': expected 'old:new'")
        old, new = part.split(":", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise TransformError(f"Invalid rename expression '{part}': names must not be empty")
        mapping[old] = new
    return mapping


def select_columns(
    rows: List[Dict[str, str]],
    headers: List[str],
    columns: List[str],
) -> tuple:
    """Return rows and headers restricted to the given columns."""
    missing = [c for c in columns if c not in headers]
    if missing:
        raise TransformError(f"Columns not found in CSV: {missing}")
    new_rows = [{c: row.get(c, "") for c in columns} for row in rows]
    return new_rows, columns


def rename_columns(
    rows: List[Dict[str, str]],
    headers: List[str],
    mapping: Dict[str, str],
) -> tuple:
    """Rename columns in rows and headers according to mapping."""
    missing = [k for k in mapping if k not in headers]
    if missing:
        raise TransformError(f"Columns to rename not found: {missing}")
    new_headers = [mapping.get(h, h) for h in headers]
    new_rows = [{mapping.get(k, k): v for k, v in row.items()} for row in rows]
    return new_rows, new_headers


def apply_transforms(
    rows: List[Dict[str, str]],
    headers: List[str],
    columns_expr: Optional[str] = None,
    rename_expr: Optional[str] = None,
) -> tuple:
    """Apply column selection then renaming to rows."""
    if columns_expr:
        columns = parse_columns(columns_expr)
        rows, headers = select_columns(rows, headers, columns)
    if rename_expr:
        mapping = parse_rename(rename_expr)
        rows, headers = rename_columns(rows, headers, mapping)
    return rows, headers
