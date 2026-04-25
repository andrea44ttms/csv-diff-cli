"""Tests for csv_diff.enricher."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.enricher import (
    EnrichError,
    EnrichResult,
    parse_enrich_key,
    enrich_diff,
)


def _result() -> DiffResult:
    return DiffResult(
        headers=["id", "name"],
        added=[{"id": "1", "name": "Alice"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[{"id": "3", "name": "Carol"}],
        unchanged=[{"id": "4", "name": "Dave"}],
    )


LOOKUP = [
    {"id": "1", "dept": "Eng", "level": "L3"},
    {"id": "2", "dept": "HR", "level": "L2"},
    {"id": "3", "dept": "Eng", "level": "L5"},
    {"id": "4", "dept": "Finance", "level": "L4"},
]


def test_parse_enrich_key_valid():
    assert parse_enrich_key("id") == "id"


def test_parse_enrich_key_strips_spaces():
    assert parse_enrich_key("  id  ") == "id"


def test_parse_enrich_key_empty_raises():
    with pytest.raises(EnrichError):
        parse_enrich_key("")


def test_parse_enrich_key_none_raises():
    with pytest.raises(EnrichError):
        parse_enrich_key(None)


def test_enrich_diff_adds_headers():
    er = enrich_diff(_result(), LOOKUP, "id", ["dept"])
    assert "dept" in er.headers


def test_enrich_diff_added_rows():
    er = enrich_diff(_result(), LOOKUP, "id", ["dept"])
    assert er.added[0]["dept"] == "Eng"


def test_enrich_diff_removed_rows():
    er = enrich_diff(_result(), LOOKUP, "id", ["dept"])
    assert er.removed[0]["dept"] == "HR"


def test_enrich_diff_modified_rows():
    er = enrich_diff(_result(), LOOKUP, "id", ["level"])
    assert er.modified[0]["level"] == "L5"


def test_enrich_diff_unchanged_rows():
    er = enrich_diff(_result(), LOOKUP, "id", ["dept", "level"])
    assert er.unchanged[0]["dept"] == "Finance"
    assert er.unchanged[0]["level"] == "L4"


def test_enrich_diff_missing_lookup_key_blank():
    lookup = [{"id": "99", "dept": "X"}]
    er = enrich_diff(_result(), lookup, "id", ["dept"])
    # rows whose key isn't in lookup get empty string
    assert er.added[0]["dept"] == ""


def test_enrich_diff_no_extra_cols_raises():
    with pytest.raises(EnrichError):
        enrich_diff(_result(), LOOKUP, "id", [])


def test_enrich_diff_lookup_missing_key_col_raises():
    bad_lookup = [{"name": "Alice"}]  # no 'id' column
    with pytest.raises(EnrichError):
        enrich_diff(_result(), bad_lookup, "id", ["name"])


def test_enrich_result_type():
    er = enrich_diff(_result(), LOOKUP, "id", ["dept"])
    assert isinstance(er, EnrichResult)
