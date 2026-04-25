"""Tests for csv_diff.mapper."""
import pytest
from csv_diff.mapper import (
    MapError,
    MapResult,
    parse_map_spec,
    map_row,
    map_rows,
)


def test_parse_map_spec_basic():
    result = parse_map_spec("status:A=Active,I=Inactive")
    assert result == {"status": {"A": "Active", "I": "Inactive"}}


def test_parse_map_spec_multiple_columns():
    result = parse_map_spec("dept:E=Engineering,S=Sales;level:1=Junior,2=Senior")
    assert result["dept"] == {"E": "Engineering", "S": "Sales"}
    assert result["level"] == {"1": "Junior", "2": "Senior"}


def test_parse_map_spec_strips_spaces():
    result = parse_map_spec(" status : A = Active , I = Inactive ")
    assert result == {"status": {"A": "Active", "I": "Inactive"}}


def test_parse_map_spec_none_returns_empty():
    assert parse_map_spec(None) == {}


def test_parse_map_spec_empty_string_returns_empty():
    assert parse_map_spec("") == {}


def test_parse_map_spec_missing_colon_raises():
    with pytest.raises(MapError, match="missing ':'")
        parse_map_spec("statusA=Active")


def test_parse_map_spec_missing_equals_raises():
    with pytest.raises(MapError, match="missing '='")
        parse_map_spec("status:AActive")


def test_parse_map_spec_empty_column_raises():
    with pytest.raises(MapError, match="Empty column"):
        parse_map_spec(":A=Active")


def test_map_row_replaces_matching_value():
    row = {"id": "1", "status": "A"}
    spec = {"status": {"A": "Active"}}
    new_row, count = map_row(row, spec)
    assert new_row["status"] == "Active"
    assert count == 1


def test_map_row_leaves_unmatched_value():
    row = {"id": "1", "status": "X"}
    spec = {"status": {"A": "Active"}}
    new_row, count = map_row(row, spec)
    assert new_row["status"] == "X"
    assert count == 0


def test_map_row_ignores_missing_column():
    row = {"id": "1"}
    spec = {"status": {"A": "Active"}}
    new_row, count = map_row(row, spec)
    assert new_row == {"id": "1"}
    assert count == 0


def test_map_rows_returns_map_result():
    rows = [{"id": "1", "dept": "E"}, {"id": "2", "dept": "S"}]
    spec = parse_map_spec("dept:E=Engineering,S=Sales")
    result = map_rows(rows, spec)
    assert isinstance(result, MapResult)
    assert result.rows[0]["dept"] == "Engineering"
    assert result.rows[1]["dept"] == "Sales"
    assert result.total_mapped == 2
    assert "dept" in result.mapped_columns


def test_map_rows_empty_spec_returns_unchanged():
    rows = [{"id": "1", "dept": "E"}]
    result = map_rows(rows, {})
    assert result.rows == rows
    assert result.total_mapped == 0
    assert result.mapped_columns == []
