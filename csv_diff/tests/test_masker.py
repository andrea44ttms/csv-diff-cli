"""Tests for csv_diff.masker."""
import pytest
from csv_diff.masker import (
    MaskError,
    MaskResult,
    parse_mask_spec,
    mask_row,
    mask_rows,
    MASK_PLACEHOLDER,
)


# ---------------------------------------------------------------------------
# parse_mask_spec
# ---------------------------------------------------------------------------

def test_parse_mask_spec_single():
    spec = parse_mask_spec("email:@")
    assert "email" in spec
    assert spec["email"].search("user@example.com")


def test_parse_mask_spec_multiple():
    spec = parse_mask_spec("email:@, phone:^\\d+$")
    assert set(spec.keys()) == {"email", "phone"}


def test_parse_mask_spec_strips_spaces():
    spec = parse_mask_spec("  name : Alice ")
    assert "name" in spec


def test_parse_mask_spec_empty_raises():
    with pytest.raises(MaskError, match="must not be empty"):
        parse_mask_spec(None)


def test_parse_mask_spec_missing_colon_raises():
    with pytest.raises(MaskError, match="expected 'column:pattern'"):
        parse_mask_spec("emailATsign")


def test_parse_mask_spec_invalid_regex_raises():
    with pytest.raises(MaskError, match="invalid regex"):
        parse_mask_spec("col:[invalid")


def test_parse_mask_spec_empty_column_raises():
    with pytest.raises(MaskError, match="column name must not be empty"):
        parse_mask_spec(":pattern")


# ---------------------------------------------------------------------------
# mask_row
# ---------------------------------------------------------------------------

def test_mask_row_matches():
    spec = parse_mask_spec("email:@")
    row = {"name": "Alice", "email": "alice@example.com"}
    new_row, count = mask_row(row, spec)
    assert new_row["email"] == MASK_PLACEHOLDER
    assert new_row["name"] == "Alice"
    assert count == 1


def test_mask_row_no_match():
    spec = parse_mask_spec("email:@")
    row = {"name": "Bob", "email": "not-an-email"}
    new_row, count = mask_row(row, spec)
    assert new_row["email"] == "not-an-email"
    assert count == 0


def test_mask_row_missing_column_is_skipped():
    spec = parse_mask_spec("email:@")
    row = {"name": "Carol"}
    new_row, count = mask_row(row, spec)
    assert count == 0
    assert new_row == {"name": "Carol"}


def test_mask_row_custom_placeholder():
    spec = parse_mask_spec("ssn:\\d")
    row = {"ssn": "123-45-6789"}
    new_row, _ = mask_row(row, spec, placeholder="[REDACTED]")
    assert new_row["ssn"] == "[REDACTED]"


# ---------------------------------------------------------------------------
# mask_rows
# ---------------------------------------------------------------------------

def test_mask_rows_returns_mask_result():
    spec = parse_mask_spec("email:@")
    rows = [
        {"id": "1", "email": "a@b.com"},
        {"id": "2", "email": "no-match"},
    ]
    result = mask_rows(rows, spec)
    assert isinstance(result, MaskResult)
    assert result.masked_count == 1
    assert result.rows[0]["email"] == MASK_PLACEHOLDER
    assert result.rows[1]["email"] == "no-match"


def test_mask_rows_empty_input():
    spec = parse_mask_spec("col:x")
    result = mask_rows([], spec)
    assert result.rows == []
    assert result.masked_count == 0
