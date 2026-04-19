import pytest
from csv_diff.pivot import (
    PivotError,
    PivotResult,
    parse_pivot_spec,
    pivot_rows,
    pivot_to_rows,
)


ROWS = [
    {"name": "Alice", "metric": "score", "value": "90"},
    {"name": "Alice", "metric": "age", "value": "30"},
    {"name": "Bob", "metric": "score", "value": "85"},
    {"name": "Bob", "metric": "age", "value": "25"},
]


def test_parse_pivot_spec_valid():
    r, c, v = parse_pivot_spec("name, metric, value")
    assert r == "name" and c == "metric" and v == "value"


def test_parse_pivot_spec_invalid():
    with pytest.raises(PivotError):
        parse_pivot_spec("only,two")


def test_pivot_rows_basic():
    result = pivot_rows(ROWS, "name", "metric", "value")
    assert result.table["Alice"]["score"] == "90"
    assert result.table["Bob"]["age"] == "25"


def test_pivot_rows_missing_column():
    with pytest.raises(PivotError):
        pivot_rows(ROWS, "name", "missing", "value")


def test_pivot_rows_empty():
    result = pivot_rows([], "name", "metric", "value")
    assert result.table == {}


def test_pivot_to_rows_columns():
    result = pivot_rows(ROWS, "name", "metric", "value")
    flat = pivot_to_rows(result)
    assert len(flat) == 2
    keys = set(flat[0].keys())
    assert "name" in keys
    assert "score" in keys
    assert "age" in keys


def test_pivot_to_rows_missing_value_is_empty_string():
    rows = [
        {"name": "Alice", "metric": "score", "value": "90"},
        {"name": "Bob", "metric": "age", "value": "25"},
    ]
    result = pivot_rows(rows, "name", "metric", "value")
    flat = pivot_to_rows(result)
    alice = next(r for r in flat if r["name"] == "Alice")
    assert alice.get("age", "") == ""
