"""Tests for csv_diff.differ."""

import pytest
from csv_diff.differ import diff_csv, DiffError, DiffResult


ROWS_A = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob",   "age": "25"},
    {"id": "3", "name": "Carol", "age": "40"},
]

ROWS_B = [
    {"id": "1", "name": "Alice", "age": "31"},  # modified
    {"id": "2", "name": "Bob",   "age": "25"},  # unchanged
    {"id": "4", "name": "Dave",  "age": "22"},  # added
    # id=3 removed
]


def test_added():
    r = diff_csv(ROWS_A, ROWS_B, key="id")
    assert len(r.added) == 1
    assert r.added[0]["id"] == "4"


def test_removed():
    r = diff_csv(ROWS_A, ROWS_B, key="id")
    assert len(r.removed) == 1
    assert r.removed[0]["id"] == "3"


def test_modified():
    r = diff_csv(ROWS_A, ROWS_B, key="id")
    assert len(r.modified) == 1
    mod = r.modified[0]
    assert mod["_key"] == "1"
    assert mod["age"] == ("30", "31")


def test_unchanged():
    r = diff_csv(ROWS_A, ROWS_B, key="id")
    assert len(r.unchanged) == 1
    assert r.unchanged[0]["id"] == "2"


def test_has_diff_true():
    assert diff_csv(ROWS_A, ROWS_B, key="id").has_diff


def test_has_diff_false():
    assert not diff_csv(ROWS_A, ROWS_A, key="id").has_diff


def test_both_empty():
    r = diff_csv([], [], key="id")
    assert isinstance(r, DiffResult)


def test_duplicate_key_raises():
    rows = [{"id": "1", "v": "a"}, {"id": "1", "v": "b"}]
    with pytest.raises(DiffError, match="duplicate"):
        diff_csv(rows, [], key="id")


def test_missing_key_raises():
    rows = [{"name": "Alice"}]
    with pytest.raises(DiffError):
        diff_csv(rows, [], key="id")
