"""splitter.py — split a DiffResult into named buckets by status."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from csv_diff.differ import DiffResult


class SplitError(Exception):
    """Raised when splitting fails."""


@dataclass
class SplitResult:
    added: List[Dict[str, str]] = field(default_factory=list)
    removed: List[Dict[str, str]] = field(default_factory=list)
    modified: List[Dict[str, str]] = field(default_factory=list)
    unchanged: List[Dict[str, str]] = field(default_factory=list)

    def bucket(self, status: str) -> List[Dict[str, str]]:
        """Return the bucket for *status*, raising SplitError if unknown."""
        try:
            return getattr(self, status)
        except AttributeError:
            raise SplitError(f"Unknown status: {status!r}")


VALID_STATUSES = {"added", "removed", "modified", "unchanged"}


def parse_split_statuses(raw: str | None) -> List[str]:
    """Parse a comma-separated list of statuses, e.g. 'added,modified'.

    Returns all four statuses when *raw* is None or empty.
    """
    if not raw:
        return list(VALID_STATUSES)
    statuses = [s.strip() for s in raw.split(",") if s.strip()]
    if not statuses:
        raise SplitError("Status list must not be empty.")
    unknown = set(statuses) - VALID_STATUSES
    if unknown:
        raise SplitError(
            f"Unknown status(es): {', '.join(sorted(unknown))}. "
            f"Valid choices: {', '.join(sorted(VALID_STATUSES))}."
        )
    return statuses


def split_diff(result: DiffResult) -> SplitResult:
    """Distribute rows from *result* into a :class:`SplitResult` by status."""
    out = SplitResult()
    for row in result.added:
        out.added.append(row)
    for row in result.removed:
        out.removed.append(row)
    for row in result.modified:
        out.modified.append(row)
    for row in result.unchanged:
        out.unchanged.append(row)
    return out


def filter_split(split: SplitResult, statuses: List[str]) -> SplitResult:
    """Return a new SplitResult containing only the requested *statuses*."""
    out = SplitResult()
    for status in statuses:
        bucket = split.bucket(status)  # validates status
        getattr(out, status).extend(bucket)
    return out
