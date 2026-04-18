"""Export diff results to various file formats."""
from __future__ import annotations
import csv
import io
import json
from typing import List, Dict
from csv_diff.differ import DiffResult


class ExportError(Exception):
    pass


SUPPORTED_FORMATS = ("csv", "json", "jsonl")


def export_to_csv(result: DiffResult) -> str:
    """Serialize diff result rows to CSV string with a 'status' column."""
    buf = io.StringIO()
    all_rows: List[Dict] = []
    for row in result.added:
        all_rows.append({"_status": "added", **row})
    for row in result.removed:
        all_rows.append({"_status": "removed", **row})
    for entry in result.modified:
        all_rows.append({"_status": "modified", **entry["new"]})
    for row in result.unchanged:
        all_rows.append({"_status": "unchanged", **row})

    if not all_rows:
        return ""

    fieldnames = list(all_rows[0].keys())
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(all_rows)
    return buf.getvalue()


def export_to_json(result: DiffResult) -> str:
    """Serialize diff result to a JSON string."""
    data = {
        "added": result.added,
        "removed": result.removed,
        "modified": result.modified,
        "unchanged": result.unchanged,
    }
    return json.dumps(data, indent=2)


def export_to_jsonl(result: DiffResult) -> str:
    """Serialize diff result rows to newline-delimited JSON."""
    lines = []
    for row in result.added:
        lines.append(json.dumps({"_status": "added", **row}))
    for row in result.removed:
        lines.append(json.dumps({"_status": "removed", **row}))
    for entry in result.modified:
        lines.append(json.dumps({"_status": "modified", **entry["new"]}))
    for row in result.unchanged:
        lines.append(json.dumps({"_status": "unchanged", **row}))
    return "\n".join(lines)


def export(result: DiffResult, fmt: str) -> str:
    """Dispatch export by format name."""
    if fmt == "csv":
        return export_to_csv(result)
    if fmt == "json":
        return export_to_json(result)
    if fmt == "jsonl":
        return export_to_jsonl(result)
    raise ExportError(f"Unsupported export format: {fmt!r}. Choose from {SUPPORTED_FORMATS}")
