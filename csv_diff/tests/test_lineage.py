"""Tests for csv_diff.lineage."""
import pytest
from csv_diff.lineage import (
    LineageError,
    LineageResult,
    LineageStep,
    parse_lineage_flag,
    record_step,
    format_lineage,
)


def test_add_step_appends():
    lr = LineageResult()
    lr.add("filter", "keep eng", 10, 5)
    assert len(lr.steps) == 1
    s = lr.steps[0]
    assert s.operation == "filter"
    assert s.rows_in == 10
    assert s.rows_out == 5


def test_summary_contains_operation():
    lr = LineageResult()
    lr.add("sort", "by name asc", 4, 4)
    lines = lr.summary()
    assert any("sort" in l for l in lines)
    assert any("by name asc" in l for l in lines)


def test_summary_numbers_steps():
    lr = LineageResult()
    lr.add("filter", "a", 3, 2)
    lr.add("sort", "b", 2, 2)
    lines = lr.summary()
    assert any("1." in l for l in lines)
    assert any("2." in l for l in lines)


def test_parse_lineage_flag_true_values():
    for v in ("1", "true", "True", "yes", "YES"):
        assert parse_lineage_flag(v) is True


def test_parse_lineage_flag_false_values():
    for v in ("0", "false", "False", "no"):
        assert parse_lineage_flag(v) is False


def test_parse_lineage_flag_none_returns_false():
    assert parse_lineage_flag(None) is False


def test_parse_lineage_flag_invalid_raises():
    with pytest.raises(LineageError):
        parse_lineage_flag("maybe")


def test_record_step_uses_lengths():
    lr = LineageResult()
    before = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
    after = [{"a": "1"}]
    record_step(lr, "truncate", "max 1", before, after)
    assert lr.steps[0].rows_in == 3
    assert lr.steps[0].rows_out == 1


def test_format_lineage_returns_string():
    lr = LineageResult()
    lr.add("diff", "compare files", 5, 5)
    out = format_lineage(lr)
    assert isinstance(out, str)
    assert "diff" in out


def test_empty_lineage_summary():
    lr = LineageResult()
    lines = lr.summary()
    assert lines[0] == "Transformation Lineage:"
    assert len(lines) == 1
