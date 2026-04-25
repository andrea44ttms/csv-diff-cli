"""Classify diff rows into named categories based on column value patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.differ import DiffResult


class ClassifyError(Exception):
    pass


@dataclass
class ClassifyResult:
    categories: Dict[str, List[dict]]
    headers: List[str]


def parse_classify_spec(spec: Optional[str]) -> Dict[str, Dict[str, str]]:
    """Parse 'CategoryName:column=value,...' pairs separated by ';'.

    Example: 'Senior:level=3;Junior:level=1'
    Returns: {'Senior': {'level': '3'}, 'Junior': {'level': '1'}}
    """
    if not spec:
        return {}
    result: Dict[str, Dict[str, str]] = {}
    for part in spec.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ClassifyError(f"Invalid classify spec (missing ':'): {part!r}")
        name, conditions_str = part.split(":", 1)
        name = name.strip()
        if not name:
            raise ClassifyError(f"Empty category name in spec: {part!r}")
        conditions: Dict[str, str] = {}
        for cond in conditions_str.split(","):
            cond = cond.strip()
            if "=" not in cond:
                raise ClassifyError(f"Invalid condition (missing '='): {cond!r}")
            col, val = cond.split("=", 1)
            conditions[col.strip()] = val.strip()
        result[name] = conditions
    return result


def _matches(row: dict, conditions: Dict[str, str]) -> bool:
    return all(row.get(col) == val for col, val in conditions.items())


def classify_rows(
    rows: List[dict],
    spec: Dict[str, Dict[str, str]],
) -> Dict[str, List[dict]]:
    """Return mapping of category name -> matching rows."""
    buckets: Dict[str, List[dict]] = {name: [] for name in spec}
    buckets["_unclassified"] = []
    for row in rows:
        matched = False
        for name, conditions in spec.items():
            if _matches(row, conditions):
                buckets[name].append(row)
                matched = True
                break
        if not matched:
            buckets["_unclassified"].append(row)
    return buckets


def classify_diff(
    result: DiffResult,
    spec: Dict[str, Dict[str, str]],
) -> ClassifyResult:
    all_rows = result.added + result.removed + result.modified + result.unchanged
    categories = classify_rows(all_rows, spec)
    return ClassifyResult(categories=categories, headers=result.headers)
