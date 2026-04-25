"""Tests for csv_diff.tagger."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.tagger import (
    TagError,
    TagResult,
    parse_tag_spec,
    tag_row,
    tag_rows,
)


# ---------------------------------------------------------------------------
# parse_tag_spec
# ---------------------------------------------------------------------------

def test_parse_tag_spec_basic():
    result = parse_tag_spec("dept=eng:engineering")
    assert result == {"dept": {"eng": "engineering"}}


def test_parse_tag_spec_multiple_columns():
    result = parse_tag_spec("dept=eng:engineering,role=admin:privileged")
    assert result["dept"] == {"eng": "engineering"}
    assert result["role"] == {"admin": "privileged"}


def test_parse_tag_spec_same_column_multiple_values():
    result = parse_tag_spec("dept=eng:engineering,dept=hr:human-resources")
    assert result["dept"] == {"eng": "engineering", "hr": "human-resources"}


def test_parse_tag_spec_strips_spaces():
    result = parse_tag_spec(" dept = eng : engineering ")
    assert result == {"dept": {"eng": "engineering"}}


def test_parse_tag_spec_none_returns_empty():
    assert parse_tag_spec(None) == {}


def test_parse_tag_spec_empty_string_returns_empty():
    assert parse_tag_spec("") == {}


def test_parse_tag_spec_missing_colon_raises():
    with pytest.raises(TagError):
        parse_tag_spec("dept=eng")


def test_parse_tag_spec_missing_equals_raises():
    with pytest.raises(TagError):
        parse_tag_spec("dept:engineering")


# ---------------------------------------------------------------------------
# tag_row
# ---------------------------------------------------------------------------

def test_tag_row_matches_single():
    row = {"dept": "eng", "name": "Alice"}
    tag_map = {"dept": {"eng": "engineering"}}
    assert tag_row(row, tag_map) == ["engineering"]


def test_tag_row_no_match_returns_empty():
    row = {"dept": "finance", "name": "Bob"}
    tag_map = {"dept": {"eng": "engineering"}}
    assert tag_row(row, tag_map) == []


def test_tag_row_multiple_matches():
    row = {"dept": "eng", "role": "admin"}
    tag_map = {"dept": {"eng": "engineering"}, "role": {"admin": "privileged"}}
    tags = tag_row(row, tag_map)
    assert "engineering" in tags
    assert "privileged" in tags


# ---------------------------------------------------------------------------
# tag_rows
# ---------------------------------------------------------------------------

def _result() -> DiffResult:
    return DiffResult(
        headers=["id", "dept"],
        added=[{"id": "1", "dept": "eng"}],
        removed=[{"id": "2", "dept": "hr"}],
        modified=[],
        unchanged=[{"id": "3", "dept": "finance"}],
    )


def test_tag_rows_adds_tags_column():
    tr = tag_rows(_result(), {"dept": {"eng": "engineering"}})
    assert "_tags" in tr.headers


def test_tag_rows_correct_tag_value():
    tr = tag_rows(_result(), {"dept": {"eng": "engineering"}})
    tagged_eng = next(r for r in tr.rows if r["id"] == "1")
    assert tagged_eng["_tags"] == "engineering"


def test_tag_rows_empty_tag_for_no_match():
    tr = tag_rows(_result(), {"dept": {"eng": "engineering"}})
    unmatched = next(r for r in tr.rows if r["id"] == "3")
    assert unmatched["_tags"] == ""


def test_tag_rows_empty_map_all_empty_tags():
    tr = tag_rows(_result(), {})
    assert all(r["_tags"] == "" for r in tr.rows)
