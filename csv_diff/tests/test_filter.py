"""Tests for csv_diff.filter module."""

import pytest
from csv_diff.filter import (
    parse_filter,
    apply_filter,
    filter_rows,
    FilterError,
)

ROWS = [
    {"name": "Alice", "dept": "eng", "age": "30"},
    {"name": "Bob", "dept": "hr", "age": "25"},
    {"name": "Carol", "dept": "eng", "age": "28"},
]


def test_parse_filter_eq():
    assert parse_filter("dept=eng") == ("dept", "=", "eng")


def test_parse_filter_neq():
    assert parse_filter("dept!=hr") == ("dept", "!=", "hr")


def test_parse_filter_strips_spaces():
    assert parse_filter(" name = Alice ") == ("name", "=", "Alice")


def test_parse_filter_invalid():
    with pytest.raises(FilterError):
        parse_filter("nodepoperator")


def test_parse_filter_missing_column():
    with pytest.raises(FilterError):
        parse_filter("=value")


def test_apply_filter_eq():
    result = apply_filter(ROWS, "dept", "=", "eng")
    assert len(result) == 2
    assert all(r["dept"] == "eng" for r in result)


def test_apply_filter_neq():
    result = apply_filter(ROWS, "dept", "!=", "eng")
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_filter_rows_none_expr():
    assert filter_rows(ROWS, None) == ROWS


def test_filter_rows_empty_expr():
    assert filter_rows(ROWS, "") == ROWS


def test_filter_rows_valid():
    result = filter_rows(ROWS, "dept=eng")
    assert len(result) == 2


def test_filter_rows_unknown_column():
    with pytest.raises(FilterError, match="Column"):
        filter_rows(ROWS, "salary=100")


def test_filter_rows_empty_list():
    assert filter_rows([], "dept=eng") == []
