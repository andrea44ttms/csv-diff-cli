"""Rename values within a specific column based on a mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class RenameError(Exception):
    """Raised when a rename specification is invalid."""


@dataclass
class RenameResult:
    rows: List[Dict[str, str]]
    column: str
    mapping: Dict[str, str]
    renamed_count: int = 0


def parse_rename_spec(spec: str | None) -> Dict[str, str]:
    """Parse a rename spec string like 'old1=new1,old2=new2' into a dict.

    Args:
        spec: Comma-separated key=value pairs, or None.

    Returns:
        A dict mapping old values to new values.

    Raises:
        RenameError: If the spec is empty or malformed.
    """
    if not spec:
        return {}
    mapping: Dict[str, str] = {}
    for part in spec.split(","):
        part = part.strip()
        if "=" not in part:
            raise RenameError(
                f"Invalid rename spec fragment {part!r}: expected 'old=new'."
            )
        old, new = part.split("=", 1)
        old, new = old.strip(), new.strip()
        if not old:
            raise RenameError("Rename spec has an empty source value.")
        mapping[old] = new
    if not mapping:
        raise RenameError("Rename spec produced no mappings.")
    return mapping


def rename_values(
    rows: List[Dict[str, str]],
    column: str,
    mapping: Dict[str, str],
) -> RenameResult:
    """Apply value renaming to *column* in each row.

    Rows that do not contain *column* are left untouched.
    Values not present in *mapping* are left untouched.
    """
    out: List[Dict[str, str]] = []
    renamed = 0
    for row in rows:
        if column in row and row[column] in mapping:
            row = {**row, column: mapping[row[column]]}
            renamed += 1
        out.append(row)
    return RenameResult(rows=out, column=column, mapping=mapping, renamed_count=renamed)
