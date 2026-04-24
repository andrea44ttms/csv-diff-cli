"""compressor.py — collapse repeated adjacent diff rows into a compact run-length form."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csv_diff.differ import DiffResult


class CompressError(Exception):
    """Raised when compression input is invalid."""


@dataclass
class Run:
    status: str
    count: int
    rows: list = field(default_factory=list)


@dataclass
class CompressResult:
    runs: List[Run]
    original_count: int
    run_count: int


def _status(row: dict) -> str:
    return row.get("_status", "unchanged")


def compress_diff(result: DiffResult) -> CompressResult:
    """Group consecutive rows with the same status into Run objects."""
    all_rows = (
        [{"_status": "added", **r} for r in result.added]
        + [{"_status": "removed", **r} for r in result.removed]
        + [{"_status": "modified", **r} for r in result.modified]
        + [{"_status": "unchanged", **r} for r in result.unchanged]
    )

    if not all_rows:
        return CompressResult(runs=[], original_count=0, run_count=0)

    runs: List[Run] = []
    current = Run(status=_status(all_rows[0]), count=0, rows=[])

    for row in all_rows:
        s = _status(row)
        if s == current.status:
            current.count += 1
            current.rows.append(row)
        else:
            runs.append(current)
            current = Run(status=s, count=1, rows=[row])
    runs.append(current)

    return CompressResult(
        runs=runs,
        original_count=len(all_rows),
        run_count=len(runs),
    )


def parse_compress_flag(value: str | None) -> bool:
    """Return True when the compress flag string is truthy."""
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes"}


def format_compressed(result: CompressResult) -> str:
    """Return a human-readable summary of the compressed runs."""
    if not result.runs:
        return "No rows."
    lines = [f"Compressed {result.original_count} rows into {result.run_count} run(s):"]
    for i, run in enumerate(result.runs, 1):
        lines.append(f"  [{i}] {run.status} x{run.count}")
    return "\n".join(lines)
