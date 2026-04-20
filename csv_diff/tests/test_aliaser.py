"""Tests for csv_diff.aliaser."""
import pytest
from csv_diff.aliaser import (
    AliasError,
    AliasResult,
    alias_row,
    alias_rows,
    parse_alias_map,
)


# ---------------------------------------------------------------------------
# parse_alias_map
# ---------------------------------------------------------------------------

def test_parse_alias_map_basic():
    result = parse_alias_map("name=Full Name,dept=Department")
    assert result == {"name": "Full Name", "dept": "Department"}


def test_parse_alias_map_single():
    result = parse_alias_map("id=Identifier")
    assert result == {"id": "Identifier"}


def test_parse_alias_map_strips_spaces():
    result = parse_alias_map(" name = Full Name , dept = Department ")
    assert result == {"name": "Full Name", "dept": "Department"}


def test_parse_alias_map_none_returns_empty():
    assert parse_alias_map(None) == {}


def test_parse_alias_map_empty_string_returns_empty():
    assert parse_alias_map("") == {}


def test_parse_alias_map_missing_equals_raises():
    with pytest.raises(AliasError, match="expected 'column=Alias'"):
        parse_alias_map("nodivider")


def test_parse_alias_map_empty_alias_raises():
    with pytest.raises(AliasError, match="non-empty"):
        parse_alias_map("name=")


def test_parse_alias_map_empty_column_raises():
    with pytest.raises(AliasError, match="non-empty"):
        parse_alias_map("=Alias")


# ---------------------------------------------------------------------------
# alias_row
# ---------------------------------------------------------------------------

def test_alias_row_renames_keys():
    row = {"name": "Alice", "dept": "Eng"}
    result = alias_row(row, {"name": "Full Name", "dept": "Department"})
    assert result == {"Full Name": "Alice", "Department": "Eng"}


def test_alias_row_leaves_unmapped_keys():
    row = {"name": "Alice", "salary": "100"}
    result = alias_row(row, {"name": "Full Name"})
    assert result == {"Full Name": "Alice", "salary": "100"}


def test_alias_row_empty_map_unchanged():
    row = {"name": "Alice"}
    assert alias_row(row, {}) == row


# ---------------------------------------------------------------------------
# alias_rows
# ---------------------------------------------------------------------------

def test_alias_rows_counts_renamed():
    rows = [{"name": "Alice", "dept": "Eng"}, {"name": "Bob", "dept": "HR"}]
    result = alias_rows(rows, {"name": "Full Name", "dept": "Department"})
    assert isinstance(result, AliasResult)
    assert result.renamed == 2
    assert result.rows[0] == {"Full Name": "Alice", "Department": "Eng"}


def test_alias_rows_empty_map_returns_original():
    rows = [{"name": "Alice"}]
    result = alias_rows(rows, {})
    assert result.renamed == 0
    assert result.rows == rows


def test_alias_rows_partial_match_counts_only_present():
    rows = [{"name": "Alice"}]
    result = alias_rows(rows, {"name": "Full Name", "missing_col": "X"})
    assert result.renamed == 1
