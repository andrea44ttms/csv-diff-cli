"""Segment diff rows into named bands based on row-index ranges."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csv_diff.differ import DiffResult


class SegmentError(Exception):
    """Raised when segment specification is invalid."""


@dataclass
class SegmentResult:
    segments: Dict[str, DiffResult]
    unmatched: DiffResult


def parse_segment_spec(spec: Optional[str]) -> List[Tuple[str, int, int]]:
    """Parse 'label:start-end,...' into list of (label, start, end) tuples.

    Indices are 1-based and inclusive.
    Example: 'header:1-5,body:6-20,footer:21-25'
    """
    if not spec:
        return []
    segments: List[Tuple[str, int, int]] = []
    for part in spec.split(","):
        part = part.strip()
        if ":" not in part or "-" not in part:
            raise SegmentError(
                f"Invalid segment spec {part!r}. Expected 'label:start-end'."
            )
        label, range_part = part.split(":", 1)
        label = label.strip()
        if not label:
            raise SegmentError("Segment label must not be empty.")
        try:
            start_s, end_s = range_part.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
        except ValueError:
            raise SegmentError(
                f"Range in segment {label!r} must be integers, got {range_part!r}."
            )
        if start < 1 or end < start:
            raise SegmentError(
                f"Segment {label!r} range {start}-{end} is invalid."
            )
        segments.append((label, start, end))
    return segments


def segment_diff(
    result: DiffResult,
    segments: List[Tuple[str, int, int]],
) -> SegmentResult:
    """Assign each row to the first matching named segment by 1-based row index."""
    all_rows = result.added + result.removed + result.modified + result.unchanged
    buckets: Dict[str, DiffResult] = {
        label: DiffResult(added=[], removed=[], modified=[], unchanged=[])
        for label, _, _ in segments
    }
    unmatched = DiffResult(added=[], removed=[], modified=[], unchanged=[])

    def _place(row: dict, status: str, idx: int) -> None:
        for label, start, end in segments:
            if start <= idx <= end:
                target = buckets[label]
                getattr(target, status).append(row)
                return
        getattr(unmatched, status).append(row)

    for status in ("added", "removed", "modified", "unchanged"):
        for i, row in enumerate(getattr(result, status), start=1):
            _place(row, status, i)

    return SegmentResult(segments=buckets, unmatched=unmatched)
