import pytest
from csv_diff.redactor import (
    parse_redact_columns,
    redact_row,
    redact_rows,
    RedactError,
    MASK,
)


def _rows():
    return [
        {"name": "Alice", "email": "alice@example.com", "dept": "Eng"},
        {"name": "Bob", "email": "bob@example.com", "dept": "HR"},
    ]


def test_parse_redact_columns_basic():
    assert parse_redact_columns("email") == ["email"]


def test_parse_redact_columns_multiple():
    assert parse_redact_columns("email, name") == ["email", "name"]


def test_parse_redact_columns_empty_raises():
    with pytest.raises(RedactError):
        parse_redact_columns("")


def test_parse_redact_columns_none_raises():
    with pytest.raises(RedactError):
        parse_redact_columns(None)


def test_parse_redact_columns_blank_entry_raises():
    with pytest.raises(RedactError):
        parse_redact_columns("email,,name")


def test_redact_row_masks_column():
    row = {"name": "Alice", "email": "alice@example.com"}
    result = redact_row(row, ["email"])
    assert result["email"] == MASK
    assert result["name"] == "Alice"


def test_redact_row_missing_column_raises():
    row = {"name": "Alice"}
    with pytest.raises(RedactError):
        redact_row(row, ["email"])


def test_redact_row_custom_mask():
    row = {"name": "Alice", "email": "a@b.com"}
    result = redact_row(row, ["email"], mask="REDACTED")
    assert result["email"] == "REDACTED"


def test_redact_row_does_not_mutate_original():
    """Ensure redact_row returns a new dict and does not modify the input row."""
    row = {"name": "Alice", "email": "alice@example.com"}
    original_email = row["email"]
    redact_row(row, ["email"])
    assert row["email"] == original_email


def test_redact_rows_all_rows():
    rows = _rows()
    result = redact_rows(rows, ["email"])
    assert all(r["email"] == MASK for r in result.rows)
    assert result.redacted_columns == ["email"]


def test_redact_rows_empty():
    result = redact_rows([], ["email"])
    assert result.rows == []
    assert result.redacted_columns == ["email"]


def test_redact_rows_multiple_columns():
    rows = _rows()
    result = redact_rows(rows, ["email", "name"])
    for r in result.rows:
        assert r["email"] == MASK
        assert r["name"] == MASK
        assert r["dept"] != MASK
