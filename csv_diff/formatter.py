"""Output formatters for DiffResult."""

import json
from typing import Any

from csv_diff.differ import DiffResult


def _row_str(row: dict[str, Any]) -> str:
    return ", ".join(f"{k}={v}" for k, v in row.items())


def format_text(result: DiffResult) -> str:
    lines = []
    for row in result.added:
        lines.append(f"+ {_row_str(row)}")
    for row in result.removed:
        lines.append(f"- {_row_str(row)}")
    for row in result.modified:
        key = row.get("_key", "?")
        changes = {k: v for k, v in row.items() if k != "_key"}
        parts = ", ".join(f"{k}: {v[0]!r} -> {v[1]!r}" for k, v in changes.items())
        lines.append(f"~ [{key}] {parts}")
    if not lines:
        lines.append("No differences found.")
    return "\n".join(lines)


def format_json(result: DiffResult) -> str:
    data = {
        "added": result.added,
        "removed": result.removed,
        "modified": result.modified,
        "unchanged_count": len(result.unchanged),
    }
    return json.dumps(data, indent=2)


def format_summary(result: DiffResult) -> str:
    return (
        f"Added:    {len(result.added)}\n"
        f"Removed:  {len(result.removed)}\n"
        f"Modified: {len(result.modified)}\n"
        f"Unchanged:{len(result.unchanged)}"
    )


FORMATS = {
    "text": format_text,
    "json": format_json,
    "summary": format_summary,
}


def render(result: DiffResult, fmt: str = "text") -> str:
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {list(FORMATS)}.")
    return FORMATS[fmt](result)
