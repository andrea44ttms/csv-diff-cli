"""Tests for csv_diff.renamer."""
import pytest
from csv_diff.renamer import (
    RenameError,
    RenameResult,
    parse_rename_spec,
    rename_values,
)


def test_parse_rename_spec_basic():
    mapping = parse_rename_spec("eng=Engineering,hr=Human Resources")
    assert mapping == {"eng": "Engineering", "hr": "Human Resources"}


def test_parse_rename_spec_single():
    assert parse_rename_spec("old=new") == {"old": "new"}


def test_parse_rename_spec_strips_spaces():
    assert parse_rename_spec(" a = b , c = d ") == {"a": "b", "c": "d"}


def test_parse_rename_spec_none_returns_empty():
    assert parse_rename_spec(None) == {}


def test_parse_rename_spec_empty_string_returns_empty():
    assert parse_rename_spec("") == {}


def test_parse_rename_spec_missing_equals_raises():
    with pytest.raises(RenameError, match="expected 'old=new'"):
        parse_rename_spec("badvalue")


def test_parse_rename_spec_empty_source_raises():
    with pytest.raises(RenameError, match="empty source"):
        parse_rename_spec("=new")


def test_rename_values_basic():
    rows = [{"dept": "eng", "name": "Alice"}, {"dept": "hr", "name": "Bob"}]
    result = rename_values(rows, "dept", {"eng": "Engineering", "hr": "Human Resources"})
    assert isinstance(result, RenameResult)
    assert result.rows[0]["dept"] == "Engineering"
    assert result.rows[1]["dept"] == "Human Resources"
    assert result.renamed_count == 2


def test_rename_values_unmatched_left_unchanged():
    rows = [{"dept": "finance", "name": "Carol"}]
    result = rename_values(rows, "dept", {"eng": "Engineering"})
    assert result.rows[0]["dept"] == "finance"
    assert result.renamed_count == 0


def test_rename_values_missing_column_left_untouched():
    rows = [{"name": "Dave"}]
    result = rename_values(rows, "dept", {"eng": "Engineering"})
    assert result.rows == [{"name": "Dave"}]
    assert result.renamed_count == 0


def test_rename_values_does_not_mutate_original():
    rows = [{"dept": "eng"}]
    rename_values(rows, "dept", {"eng": "Engineering"})
    assert rows[0]["dept"] == "eng"


def test_rename_values_partial_match():
    rows = [
        {"dept": "eng"},
        {"dept": "hr"},
        {"dept": "finance"},
    ]
    result = rename_values(rows, "dept", {"eng": "Engineering"})
    assert result.renamed_count == 1
    assert result.rows[1]["dept"] == "hr"
    assert result.rows[2]["dept"] == "finance"
