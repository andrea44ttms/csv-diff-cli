import pytest
from csv_diff.deduplicator import (
    DeduplicateError,
    parse_key_columns,
    deduplicate_rows,
)


ROWS = [
    {"id": "1", "name": "Alice", "dept": "Eng"},
    {"id": "2", "name": "Bob",   "dept": "HR"},
    {"id": "1", "name": "Alice2", "dept": "Eng"},
    {"id": "3", "name": "Carol", "dept": "Eng"},
    {"id": "2", "name": "Bob2",  "dept": "HR"},
]


def test_parse_key_columns_basic():
    assert parse_key_columns("id") == ["id"]


def test_parse_key_columns_multiple():
    assert parse_key_columns("id, name") == ["id", "name"]


def test_parse_key_columns_empty_raises():
    with pytest.raises(DeduplicateError):
        parse_key_columns("  ")


def test_deduplicate_keep_first():
    result = deduplicate_rows(ROWS, ["id"], keep="first")
    assert len(result.unique) == 3
    assert result.unique[0]["name"] == "Alice"
    assert result.unique[1]["name"] == "Bob"


def test_deduplicate_keep_last():
    result = deduplicate_rows(ROWS, ["id"], keep="last")
    assert len(result.unique) == 3
    names = {r["name"] for r in result.unique}
    assert "Alice2" in names
    assert "Bob2" in names


def test_deduplicate_reports_duplicates():
    result = deduplicate_rows(ROWS, ["id"], keep="first")
    assert len(result.duplicates) == 2


def test_deduplicate_duplicate_keys():
    result = deduplicate_rows(ROWS, ["id"], keep="first")
    dup_keys_flat = [k[0] for k in result.duplicate_keys]
    assert set(dup_keys_flat) == {"1", "2"}


def test_deduplicate_no_duplicates():
    rows = [{"id": "1"}, {"id": "2"}]
    result = deduplicate_rows(rows, ["id"])
    assert result.unique == rows
    assert result.duplicates == []


def test_deduplicate_missing_key_column_raises():
    with pytest.raises(DeduplicateError):
        deduplicate_rows([{"name": "Alice"}], ["id"])


def test_deduplicate_invalid_keep_raises():
    with pytest.raises(DeduplicateError):
        deduplicate_rows(ROWS, ["id"], keep="middle")
