"""Tests for csv_diff.grouper."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.grouper import (
    GroupError,
    GroupResult,
    format_group_summary,
    group_diff,
    parse_group_column,
)


def _result() -> DiffResult:
    headers = ["dept", "name", "salary"]
    return DiffResult(
        headers=headers,
        added=[{"dept": "eng", "name": "Alice", "salary": "90"}],
        removed=[{"dept": "hr", "name": "Bob", "salary": "70"}],
        modified=[
            (
                {"dept": "eng", "name": "Carol", "salary": "80"},
                {"dept": "eng", "name": "Carol", "salary": "85"},
            )
        ],
        unchanged=[{"dept": "hr", "name": "Dave", "salary": "60"}],
    )


def test_parse_group_column_strips():
    assert parse_group_column("  dept  ") == "dept"


def test_parse_group_column_none_returns_none():
    assert parse_group_column(None) is None


def test_parse_group_column_empty_raises():
    with pytest.raises(GroupError, match="empty"):
        parse_group_column("   ")


def test_group_diff_creates_correct_keys():
    gr = group_diff(_result(), "dept")
    assert set(gr.groups.keys()) == {"eng", "hr"}


def test_group_diff_eng_bucket():
    gr = group_diff(_result(), "dept")
    eng = gr.groups["eng"]
    assert len(eng.added) == 1
    assert len(eng.modified) == 1
    assert len(eng.removed) == 0
    assert len(eng.unchanged) == 0


def test_group_diff_hr_bucket():
    gr = group_diff(_result(), "dept")
    hr = gr.groups["hr"]
    assert len(hr.removed) == 1
    assert len(hr.unchanged) == 1
    assert len(hr.added) == 0


def test_group_diff_missing_column_raises():
    with pytest.raises(GroupError, match="not found"):
        group_diff(_result(), "nonexistent")


def test_group_diff_headers_preserved():
    gr = group_diff(_result(), "dept")
    for dr in gr.groups.values():
        assert dr.headers == ["dept", "name", "salary"]


def test_format_group_summary_contains_column():
    gr = group_diff(_result(), "dept")
    summary = format_group_summary(gr)
    assert "dept" in summary


def test_format_group_summary_contains_keys():
    gr = group_diff(_result(), "dept")
    summary = format_group_summary(gr)
    assert "eng" in summary
    assert "hr" in summary


def test_format_group_summary_counts():
    gr = group_diff(_result(), "dept")
    summary = format_group_summary(gr)
    assert "added=1" in summary
