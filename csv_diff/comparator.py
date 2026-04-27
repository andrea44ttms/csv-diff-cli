"""Field-level comparison with configurable tolerance for numeric and string values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CompareError(Exception):
    """Raised when comparator configuration is invalid."""


@dataclass
class CompareOptions:
    numeric_tolerance: float = 0.0
    ignore_case: bool = False
    ignore_whitespace: bool = False


@dataclass
class FieldComparison:
    column: str
    old_value: str
    new_value: str
    equal: bool


@dataclass
class RowComparison:
    key: str
    fields: List[FieldComparison] = field(default_factory=list)

    @property
    def has_diff(self) -> bool:
        return any(not f.equal for f in self.fields)


def parse_compare_options(args: object) -> CompareOptions:
    """Build CompareOptions from CLI namespace or dict-like object."""
    if args is None:
        return CompareOptions()
    get = args.get if isinstance(args, dict) else lambda k, d=None: getattr(args, k, d)
    tol_raw = get("numeric_tolerance", None)
    try:
        tol = float(tol_raw) if tol_raw is not None else 0.0
    except (TypeError, ValueError):
        raise CompareError(f"Invalid numeric_tolerance: {tol_raw!r}")
    if tol < 0:
        raise CompareError("numeric_tolerance must be >= 0")
    return CompareOptions(
        numeric_tolerance=tol,
        ignore_case=bool(get("ignore_case", False)),
        ignore_whitespace=bool(get("ignore_whitespace", False)),
    )


def _normalize(value: str, opts: CompareOptions) -> str:
    if opts.ignore_whitespace:
        value = value.strip()
    if opts.ignore_case:
        value = value.lower()
    return value


def compare_fields(
    columns: List[str],
    old_row: Dict[str, str],
    new_row: Dict[str, str],
    opts: CompareOptions,
) -> List[FieldComparison]:
    results: List[FieldComparison] = []
    for col in columns:
        ov = old_row.get(col, "")
        nv = new_row.get(col, "")
        equal = _values_equal(ov, nv, opts)
        results.append(FieldComparison(column=col, old_value=ov, new_value=nv, equal=equal))
    return results


def _values_equal(ov: str, nv: str, opts: CompareOptions) -> bool:
    if opts.numeric_tolerance > 0:
        try:
            return abs(float(ov) - float(nv)) <= opts.numeric_tolerance
        except (ValueError, TypeError):
            pass
    return _normalize(ov, opts) == _normalize(nv, opts)
