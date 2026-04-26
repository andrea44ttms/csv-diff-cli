"""Tests for csv_diff.scoper."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.scoper import (
    ScopeError,
    ScopeResult,
    format_scope,
    parse_scope,
    scope_diff,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


_ROWS = [{"id": str(i), "v": str(i)} for i in range(1, 6)]  # 5 rows


def test_parse_scope_defaults():
    s, e = parse_scope(None, None, 10)
    assert s == 1
    assert e == 10


def test_parse_scope_explicit():
    s, e = parse_scope("2", "4", 10)
    assert s == 2
    assert e == 4


def test_parse_scope_non_integer_raises():
    with pytest.raises(ScopeError):
        parse_scope("abc", None, 10)


def test_parse_scope_start_zero_raises():
    with pytest.raises(ScopeError, match=">= 1"):
        parse_scope("0", "5", 10)


def test_parse_scope_end_before_start_raises():
    with pytest.raises(ScopeError, match="scope-end"):
        parse_scope("5", "3", 10)


def test_scope_diff_full_range():
    r = _result(added=_ROWS)
    sr = scope_diff(r, 1, 5)
    assert len(sr.rows) == 5
    assert sr.total_before_scope == 5


def test_scope_diff_partial_range():
    r = _result(added=_ROWS)
    sr = scope_diff(r, 2, 4)
    assert len(sr.rows) == 3
    assert sr.rows[0]["id"] == "2"
    assert sr.rows[-1]["id"] == "4"


def test_scope_diff_clamps_end():
    r = _result(added=_ROWS)
    sr = scope_diff(r, 1, 999)
    assert sr.end == 5
    assert len(sr.rows) == 5


def test_scope_diff_empty_result():
    r = _result()
    sr = scope_diff(r, 1, 10)
    assert sr.rows == []
    assert sr.total_before_scope == 0


def test_format_scope_normal():
    sr = ScopeResult(rows=[{}, {}], start=2, end=3, total_before_scope=10)
    text = format_scope(sr)
    assert "2" in text and "3" in text and "10" in text


def test_format_scope_empty():
    sr = ScopeResult(rows=[], start=1, end=0, total_before_scope=0)
    text = format_scope(sr)
    assert "no rows" in text
