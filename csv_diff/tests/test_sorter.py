"""Tests for csv_diff.sorter module."""

import pytest
from csv_diff.sorter import SortError, parse_sort_keys, sort_rows


ROWS = [
    {"name": "Charlie", "age": "30", "dept": "HR"},
    {"name": "Alice", "age": "25", "dept": "Eng"},
    {"name": "Bob", "age": "25", "dept": "HR"},
]


def test_parse_sort_keys_single_asc():
    keys = parse_sort_keys("name:asc")
    assert keys == [{"column": "name", "reverse": False}]


def test_parse_sort_keys_single_desc():
    keys = parse_sort_keys("age:desc")
    assert keys == [{"column": "age", "reverse": True}]


def test_parse_sort_keys_default_asc():
    keys = parse_sort_keys("name")
    assert keys == [{"column": "name", "reverse": False}]


def test_parse_sort_keys_multiple():
    keys = parse_sort_keys("age:asc, name:desc")
    assert keys == [
        {"column": "age", "reverse": False},
        {"column": "name", "reverse": True},
    ]


def test_parse_sort_keys_invalid_direction():
    with pytest.raises(SortError, match="Invalid sort direction"):
        parse_sort_keys("name:random")


def test_parse_sort_keys_empty_column():
    with pytest.raises(SortError, match="cannot be empty"):
        parse_sort_keys(":asc")


def test_parse_sort_keys_empty_expr():
    with pytest.raises(SortError, match="no valid sort keys"):
        parse_sort_keys("   ")


def test_sort_rows_by_name_asc():
    keys = parse_sort_keys("name:asc")
    result = sort_rows(ROWS, keys)
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie"]


def test_sort_rows_by_name_desc():
    keys = parse_sort_keys("name:desc")
    result = sort_rows(ROWS, keys)
    assert [r["name"] for r in result] == ["Charlie", "Bob", "Alice"]


def test_sort_rows_by_age_then_name():
    keys = parse_sort_keys("age:asc,name:asc")
    result = sort_rows(ROWS, keys)
    names = [r["name"] for r in result]
    assert names.index("Alice") < names.index("Bob")
    assert names.index("Bob") < names.index("Charlie")


def test_sort_rows_empty():
    assert sort_rows([], parse_sort_keys("name")) == []


def test_sort_rows_unknown_column():
    with pytest.raises(SortError, match="not found in CSV headers"):
        sort_rows(ROWS, parse_sort_keys("salary:asc"))
