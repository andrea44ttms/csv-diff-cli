"""Tests for csv_diff.differ_context."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.differ_context import (
    ContextError,
    ContextRow,
    ContextResult,
    parse_context_lines,
    extract_context,
)


HEADERS = ["id", "name"]


def _result(added=None, removed=None, modified=None, unchanged=None):
    return DiffResult(
        headers=HEADERS,
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        unchanged=unchanged or [],
    )


# --- parse_context_lines ---

def test_parse_context_lines_valid():
    assert parse_context_lines(2) == 2


def test_parse_context_lines_zero():
    assert parse_context_lines(0) == 0


def test_parse_context_lines_string_int():
    assert parse_context_lines("3") == 3


def test_parse_context_lines_none_returns_zero():
    assert parse_context_lines(None) == 0


def test_parse_context_lines_negative_raises():
    with pytest.raises(ContextError, match=">= 0"):
        parse_context_lines(-1)


def test_parse_context_lines_non_integer_raises():
    with pytest.raises(ContextError, match="integer"):
        parse_context_lines("abc")


# --- extract_context ---

def test_extract_context_no_changes_returns_empty():
    r = _result(unchanged=[{"id": "1", "name": "Alice"}])
    cr = extract_context(r, 1)
    assert isinstance(cr, ContextResult)
    assert cr.rows == []


def test_extract_context_added_row_included():
    added = {"id": "2", "name": "Bob"}
    r = _result(added=[added])
    cr = extract_context(r, 0)
    assert len(cr.rows) == 1
    assert cr.rows[0].is_changed is True
    assert cr.rows[0].row == added


def test_extract_context_context_lines_includes_neighbours():
    unchanged1 = {"id": "1", "name": "Alice"}
    modified = {"id": "2", "name": "Bobby"}
    unchanged2 = {"id": "3", "name": "Carol"}
    r = _result(modified=[modified], unchanged=[unchanged1, unchanged2])
    cr = extract_context(r, 1)
    # All three rows should be present
    assert len(cr.rows) == 3


def test_extract_context_changed_row_flagged():
    unchanged = {"id": "1", "name": "Alice"}
    added = {"id": "2", "name": "Bob"}
    r = _result(added=[added], unchanged=[unchanged])
    cr = extract_context(r, 1)
    changed_flags = [row.is_changed for row in cr.rows]
    assert True in changed_flags


def test_extract_context_headers_preserved():
    r = _result(added=[{"id": "1", "name": "X"}])
    cr = extract_context(r, 0)
    assert cr.headers == HEADERS


def test_extract_context_negative_context_raises():
    r = _result()
    with pytest.raises(ContextError):
        extract_context(r, -1)
