"""Column aliasing: map column names to user-friendly aliases before output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class AliasError(Exception):
    """Raised when alias configuration is invalid."""


@dataclass
class AliasResult:
    rows: List[Dict[str, str]]
    alias_map: Dict[str, str]  # original -> alias
    renamed: int = 0


def parse_alias_map(alias_expr: str | None) -> Dict[str, str]:
    """Parse 'col1=Alias One,col2=Alias Two' into a dict.

    Raises AliasError on malformed input.
    """
    if not alias_expr:
        return {}
    result: Dict[str, str] = {}
    for part in alias_expr.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise AliasError(
                f"Invalid alias expression {part!r}: expected 'column=Alias'."
            )
        original, _, alias = part.partition("=")
        original = original.strip()
        alias = alias.strip()
        if not original or not alias:
            raise AliasError(
                f"Invalid alias expression {part!r}: both column and alias must be non-empty."
            )
        result[original] = alias
    return result


def alias_row(
    row: Dict[str, str], alias_map: Dict[str, str]
) -> Dict[str, str]:
    """Return a new row dict with keys renamed according to alias_map."""
    return {alias_map.get(k, k): v for k, v in row.items()}


def alias_rows(
    rows: List[Dict[str, str]], alias_map: Dict[str, str]
) -> AliasResult:
    """Apply alias_map to every row, counting how many columns were renamed."""
    if not alias_map:
        return AliasResult(rows=list(rows), alias_map={}, renamed=0)

    aliased = [alias_row(r, alias_map) for r in rows]
    # Count distinct original columns that actually appeared in the data.
    seen_originals = {k for row in rows for k in row} & alias_map.keys()
    return AliasResult(rows=aliased, alias_map=alias_map, renamed=len(seen_originals))
