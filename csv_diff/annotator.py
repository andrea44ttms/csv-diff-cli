"""Annotate diff rows with a custom label column."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional


class AnnotateError(Exception):
    pass


@dataclass
class AnnotateResult:
    rows: List[Dict[str, str]]
    label_column: str


DEFAULT_LABELS = {
    "added": "ADDED",
    "removed": "REMOVED",
    "modified": "MODIFIED",
    "unchanged": "UNCHANGED",
}


def parse_label_map(raw: Optional[str]) -> Dict[str, str]:
    """Parse 'added=A,removed=R' style string into a label map."""
    labels = dict(DEFAULT_LABELS)
    if not raw:
        return labels
    for part in raw.split(","):
        part = part.strip()
        if "=" not in part:
            raise AnnotateError(f"Invalid label mapping: {part!r}. Expected key=value.")
        k, v = part.split("=", 1)
        k = k.strip()
        if k not in DEFAULT_LABELS:
            raise AnnotateError(f"Unknown status key: {k!r}. Valid keys: {list(DEFAULT_LABELS)}.")
        labels[k] = v.strip()
    return labels


def annotate_rows(
    rows: List[Dict[str, str]],
    status_column: str = "_status",
    label_column: str = "_annotation",
    label_map: Optional[Dict[str, str]] = None,
) -> AnnotateResult:
    """Add a label column based on the status column value."""
    if label_map is None:
        label_map = DEFAULT_LABELS
    annotated = []
    for row in rows:
        status = row.get(status_column, "")
        label = label_map.get(status, status)
        annotated.append({**row, label_column: label})
    return AnnotateResult(rows=annotated, label_column=label_column)
