"""Bucketer: assign numeric column values into named ranges (buckets)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csv_diff.differ import DiffResult


class BucketError(Exception):
    """Raised when bucketing configuration or data is invalid."""


@dataclass
class BucketResult:
    column: str
    buckets: Dict[str, List[dict]]  # bucket_label -> list of rows


def parse_bucket_spec(spec: Optional[str]) -> List[Tuple[str, float, float]]:
    """Parse a bucket spec string like 'low:0:50,mid:50:100,high:100:200'.

    Each segment is  label:min:max  where min is inclusive, max is exclusive.
    """
    if not spec:
        raise BucketError("Bucket spec must not be empty.")
    buckets: List[Tuple[str, float, float]] = []
    for part in spec.split(","):
        part = part.strip()
        segments = part.split(":")
        if len(segments) != 3:
            raise BucketError(
                f"Invalid bucket segment {part!r}: expected 'label:min:max'."
            )
        label, raw_min, raw_max = segments
        label = label.strip()
        if not label:
            raise BucketError("Bucket label must not be empty.")
        try:
            lo = float(raw_min.strip())
            hi = float(raw_max.strip())
        except ValueError:
            raise BucketError(
                f"Bucket bounds must be numeric in segment {part!r}."
            )
        if lo >= hi:
            raise BucketError(
                f"Bucket min must be less than max in segment {part!r}."
            )
        buckets.append((label, lo, hi))
    return buckets


def _assign_bucket(
    value: str,
    buckets: List[Tuple[str, float, float]],
) -> Optional[str]:
    """Return the first matching bucket label or None if no match."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return None
    for label, lo, hi in buckets:
        if lo <= num < hi:
            return label
    return None


def bucket_diff(
    result: DiffResult,
    column: str,
    buckets: List[Tuple[str, float, float]],
) -> BucketResult:
    """Group all changed rows by which bucket their *column* value falls into."""
    all_rows = (
        result.added + result.removed + result.modified + result.unchanged
    )
    grouped: Dict[str, List[dict]] = {label: [] for label, _, _ in buckets}
    grouped["__other__"] = []
    for row in all_rows:
        if column not in row:
            raise BucketError(
                f"Column {column!r} not found in row: {list(row.keys())}"
            )
        label = _assign_bucket(row[column], buckets)
        grouped[label if label is not None else "__other__"].append(row)
    return BucketResult(column=column, buckets=grouped)
