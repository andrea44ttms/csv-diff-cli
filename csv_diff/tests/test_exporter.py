"""Tests for csv_diff.exporter."""
import json
import pytest
from csv_diff.differ import DiffResult
from csv_diff.exporter import export, export_to_csv, export_to_json, export_to_jsonl, ExportError


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


ROW_A = {"id": "1", "name": "Alice"}
ROW_B = {"id": "2", "name": "Bob"}


def test_export_csv_added():
    r = _result(added=[ROW_A])
    out = export_to_csv(r)
    assert "_status" in out
    assert "added" in out
    assert "Alice" in out


def test_export_csv_empty():
    r = _result()
    assert export_to_csv(r) == ""


def test_export_csv_all_statuses():
    mod = {"old": ROW_A, "new": {"id": "1", "name": "Alicia"}, "diff": {"name": ("Alice", "Alicia")}}
    r = _result(added=[ROW_B], removed=[ROW_A], modified=[mod], unchanged=[{"id": "3", "name": "Carol"}])
    out = export_to_csv(r)
    for status in ("added", "removed", "modified", "unchanged"):
        assert status in out


def test_export_json_structure():
    r = _result(added=[ROW_A], removed=[ROW_B])
    out = export_to_json(r)
    data = json.loads(out)
    assert "added" in data and "removed" in data
    assert data["added"][0]["name"] == "Alice"
    assert data["removed"][0]["name"] == "Bob"


def test_export_jsonl_lines():
    r = _result(added=[ROW_A], unchanged=[ROW_B])
    out = export_to_jsonl(r)
    lines = out.strip().split("\n")
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["_status"] == "added"


def test_export_dispatch_csv():
    r = _result(added=[ROW_A])
    out = export(r, "csv")
    assert "Alice" in out


def test_export_dispatch_json():
    r = _result(added=[ROW_A])
    out = export(r, "json")
    assert json.loads(out)["added"][0]["name"] == "Alice"


def test_export_dispatch_jsonl():
    r = _result(removed=[ROW_B])
    out = export(r, "jsonl")
    assert "Bob" in out


def test_export_invalid_format():
    r = _result()
    with pytest.raises(ExportError, match="Unsupported"):
        export(r, "xml")
