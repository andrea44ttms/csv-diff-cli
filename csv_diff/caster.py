"""Type-casting utilities for CSV diff rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CastError(Exception):
    """Raised when a type-cast specification is invalid or fails."""


SUPPORTED_TYPES = {"int", "float", "str", "bool"}


@dataclass
class CastSpec:
    column: str
    type_name: str


@dataclass
class CastResult:
    rows: List[Dict[str, str]]
    casted_columns: List[str] = field(default_factory=list)


def parse_cast_spec(spec: Optional[str]) -> List[CastSpec]:
    """Parse a cast spec string like 'age:int,score:float' into CastSpec objects."""
    if not spec:
        return []
    result: List[CastSpec] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise CastError(f"Invalid cast spec {part!r}: expected 'column:type'")
        col, _, type_name = part.partition(":")
        col = col.strip()
        type_name = type_name.strip().lower()
        if not col:
            raise CastError(f"Empty column name in cast spec {part!r}")
        if type_name not in SUPPORTED_TYPES:
            raise CastError(
                f"Unsupported type {type_name!r} in cast spec {part!r}; "
                f"choose from {sorted(SUPPORTED_TYPES)}"
            )
        result.append(CastSpec(column=col, type_name=type_name))
    return result


def _cast_value(value: str, type_name: str) -> str:
    """Cast *value* to *type_name* and return its string representation."""
    try:
        if type_name == "int":
            return str(int(float(value)))
        if type_name == "float":
            return str(float(value))
        if type_name == "bool":
            return str(value.strip().lower() in {"true", "1", "yes"})
        return str(value)
    except (ValueError, TypeError) as exc:
        raise CastError(f"Cannot cast {value!r} to {type_name}: {exc}") from exc


def cast_row(row: Dict[str, str], specs: List[CastSpec]) -> Dict[str, str]:
    """Return a copy of *row* with specified columns cast to their target types."""
    result = dict(row)
    for spec in specs:
        if spec.column in result:
            result[spec.column] = _cast_value(result[spec.column], spec.type_name)
    return result


def cast_rows(rows: List[Dict[str, str]], specs: List[CastSpec]) -> CastResult:
    """Apply cast specs to every row and return a CastResult."""
    if not specs:
        return CastResult(rows=list(rows), casted_columns=[])
    casted = [cast_row(row, specs) for row in rows]
    return CastResult(
        rows=casted,
        casted_columns=[s.column for s in specs],
    )
