"""Tests for csv_diff.classifier."""
import pytest
from csv_diff.classifier import (
    ClassifyError,
    ClassifyResult,
    parse_classify_spec,
    classify_rows,
    classify_diff,
)
from csv_diff.differ import DiffResult


# ---------------------------------------------------------------------------
# parse_classify_spec
# ---------------------------------------------------------------------------

def test_parse_classify_spec_basic():
    spec = parse_classify_spec("Senior:level=3")
    assert spec == {"Senior": {"level": "3"}}


def test_parse_classify_spec_multiple_categories():
    spec = parse_classify_spec("A:col=1;B:col=2")
    assert spec == {"A": {"col": "1"}, "B": {"col": "2"}}


def test_parse_classify_spec_multiple_conditions():
    spec = parse_classify_spec("X:dept=eng,level=3")
    assert spec == {"X": {"dept": "eng", "level": "3"}}


def test_parse_classify_spec_strips_spaces():
    spec = parse_classify_spec(" Alpha : col = val ")
    assert "Alpha" in spec
    assert spec["Alpha"] == {"col": "val"}


def test_parse_classify_spec_none_returns_empty():
    assert parse_classify_spec(None) == {}


def test_parse_classify_spec_empty_string_returns_empty():
    assert parse_classify_spec("") == {}


def test_parse_classify_spec_missing_colon_raises():
    with pytest.raises(ClassifyError, match="missing ':'" ):
        parse_classify_spec("NoCategoryColon")


def test_parse_classify_spec_missing_equals_raises():
    with pytest.raises(ClassifyError, match="missing '='" ):
        parse_classify_spec("Cat:noequalssign")


# ---------------------------------------------------------------------------
# classify_rows
# ---------------------------------------------------------------------------

ROWS = [
    {"name": "Alice", "dept": "eng", "level": "3"},
    {"name": "Bob",   "dept": "eng", "level": "1"},
    {"name": "Carol", "dept": "hr",  "level": "2"},
]


def test_classify_rows_basic():
    spec = parse_classify_spec("Senior:level=3;Junior:level=1")
    buckets = classify_rows(ROWS, spec)
    assert len(buckets["Senior"]) == 1
    assert buckets["Senior"][0]["name"] == "Alice"
    assert len(buckets["Junior"]) == 1
    assert buckets["Junior"][0]["name"] == "Bob"
    assert len(buckets["_unclassified"]) == 1


def test_classify_rows_unclassified_bucket_always_present():
    spec = parse_classify_spec("Eng:dept=eng")
    buckets = classify_rows([], spec)
    assert "_unclassified" in buckets


def test_classify_rows_empty_rows():
    spec = parse_classify_spec("A:col=1")
    buckets = classify_rows([], spec)
    assert buckets["A"] == []
    assert buckets["_unclassified"] == []


# ---------------------------------------------------------------------------
# classify_diff
# ---------------------------------------------------------------------------

def _make_result():
    headers = ["name", "dept", "level"]
    return DiffResult(
        added=[{"name": "Dave", "dept": "eng", "level": "3"}],
        removed=[{"name": "Eve",  "dept": "hr",  "level": "2"}],
        modified=[],
        unchanged=[{"name": "Frank", "dept": "eng", "level": "1"}],
        headers=headers,
    )


def test_classify_diff_returns_classify_result():
    result = classify_diff(_make_result(), parse_classify_spec("Senior:level=3"))
    assert isinstance(result, ClassifyResult)


def test_classify_diff_counts_across_all_buckets():
    spec = parse_classify_spec("Senior:level=3;Junior:level=1")
    result = classify_diff(_make_result(), spec)
    all_rows = sum(len(v) for v in result.categories.values())
    assert all_rows == 3  # added + removed + unchanged
