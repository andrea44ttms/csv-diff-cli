"""Tests for csv_diff.formatter."""

import json
import pytest
from csv_diff.differ import DiffResult
from csv_diff.formatter import render, format_text, format_json, format_summary


def _result():
    r = DiffResult()
    r.added = [{"id": "4", "name": "Dave"}]
    r.removed = [{"id": "3", "name": "Carol"}]
    r.modified = [{"_key": "1", "age": ("30", "31")}]
    r.unchanged = [{"id": "2", "name": "Bob"}]
    return r


def test_text_added():
    out = format_text(_result())
    assert "+ id=4" in out


def test_text_removed():
    out = format_text(_result())
    assert "- id=3" in out


def test_text_modified():
    out = format_text(_result())
    assert "~ [1]" in out
    assert "'30' -> '31'" in out


def test_text_no_diff():
    r = DiffResult(unchanged=[{"id": "1"}])
    assert "No differences" in format_text(r)


def test_json_structure():
    data = json.loads(format_json(_result()))
    assert "added" in data
    assert "removed" in data
    assert "modified" in data
    assert data["unchanged_count"] == 1


def test_summary_counts():
    out = format_summary(_result())
    assert "Added:    1" in out
    assert "Removed:  1" in out
    assert "Modified: 1" in out


def test_render_dispatch():
    r = _result()
    assert render(r, "text") == format_text(r)
    assert render(r, "json") == format_json(r)
    assert render(r, "summary") == format_summary(r)


def test_render_unknown_format():
    with pytest.raises(ValueError, match="Unknown format"):
        render(_result(), "xml")
