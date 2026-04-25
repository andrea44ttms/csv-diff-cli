"""Timeline module: track and replay diff history across multiple CSV snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff.differ import DiffResult


class TimelineError(Exception):
    """Raised when timeline operations fail."""


@dataclass
class Snapshot:
    label: str
    result: DiffResult


@dataclass
class TimelineResult:
    snapshots: List[Snapshot] = field(default_factory=list)


def parse_labels(raw: Optional[str]) -> List[str]:
    """Parse a comma-separated label string into a list of stripped labels."""
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",")]
    if any(p == "" for p in parts):
        raise TimelineError("Labels must not be empty strings.")
    return parts


def add_snapshot(timeline: TimelineResult, label: str, result: DiffResult) -> TimelineResult:
    """Append a new snapshot to the timeline."""
    if not label:
        raise TimelineError("Snapshot label must not be empty.")
    timeline.snapshots.append(Snapshot(label=label, result=result))
    return timeline


def get_snapshot(timeline: TimelineResult, label: str) -> Snapshot:
    """Retrieve a snapshot by label; raises TimelineError if not found."""
    for snap in timeline.snapshots:
        if snap.label == label:
            return snap
    raise TimelineError(f"Snapshot '{label}' not found in timeline.")


def format_timeline(timeline: TimelineResult) -> str:
    """Render a human-readable summary of all snapshots."""
    if not timeline.snapshots:
        return "Timeline: (empty)"
    lines = ["Timeline:"]
    for i, snap in enumerate(timeline.snapshots, 1):
        r = snap.result
        lines.append(
            f"  [{i}] {snap.label}: "
            f"+{len(r.added)} -{len(r.removed)} ~{len(r.modified)} ={len(r.unchanged)}"
        )
    return "\n".join(lines)
