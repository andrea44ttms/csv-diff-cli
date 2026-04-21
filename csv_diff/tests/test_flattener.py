"""Tests for csv_diff.flattener."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.flattener import (
    FlattenError,
    flatten_diff,
    flatten_to_dicts,
)


def _result(
    added=None,
    removed=None,
    modified=None,
    unchanged=None,
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        unchanged=unchanged or [],
    )


def test_flatten_added():
    r = _result(added=[{"id": "1", "name": "Alice"}])
    rows = flatten_diff(r, key_column="id")
    assert len(rows) == 1
    assert rows[0].status == "added"
    assert rows[0].key == "1"
    assert rows[0].column is None


def test_flatten_removed():
    r = _result(removed=[{"id": "2", "name": "Bob"}])
    rows = flatten_diff(r, key_column="id")
    assert len(rows) == 1
    assert rows[0].status == "removed"
    assert rows[0].key == "2"


def test_flatten_modified_single_column():
    old = {"id": "3", "name": "Carol", "dept": "HR"}
    new = {"id": "3", "name": "Caroline", "dept": "HR"}
    r = _result(modified=[(old, new)])
    rows = flatten_diff(r, key_column="id")
    assert len(rows) == 1
    assert rows[0].status == "modified"
    assert rows[0].key == "3"
    assert rows[0].column == "name"
    assert rows[0].old_value == "Carol"
    assert rows[0].new_value == "Caroline"


def test_flatten_modified_multiple_columns():
    old = {"id": "4", "name": "Dave", "dept": "IT"}
    new = {"id": "4", "name": "David", "dept": "Eng"}
    r = _result(modified=[(old, new)])
    rows = flatten_diff(r, key_column="id")
    assert len(rows) == 2
    columns = {row.column for row in rows}
    assert columns == {"name", "dept"}


def test_flatten_unchanged_produces_no_rows():
    r = _result(unchanged=[{"id": "5", "name": "Eve"}])
    rows = flatten_diff(r, key_column="id")
    assert rows == []


def test_flatten_invalid_input_raises():
    with pytest.raises(FlattenError):
        flatten_diff({"not": "a DiffResult"})  # type: ignore


def test_flatten_to_dicts_keys():
    r = _result(added=[{"id": "6", "name": "Frank"}])
    dicts = flatten_to_dicts(r, key_column="id")
    assert len(dicts) == 1
    assert set(dicts[0].keys()) == {"status", "key", "column", "old_value", "new_value"}


def test_flatten_to_dicts_empty_strings_for_none():
    r = _result(added=[{"id": "7", "name": "Grace"}])
    dicts = flatten_to_dicts(r, key_column="id")
    assert dicts[0]["column"] == ""
    assert dicts[0]["old_value"] == ""
    assert dicts[0]["new_value"] == ""


def test_flatten_mixed_result():
    r = _result(
        added=[{"id": "1", "val": "a"}],
        removed=[{"id": "2", "val": "b"}],
        modified=[({"id": "3", "val": "c"}, {"id": "3", "val": "d"})],
    )
    rows = flatten_diff(r, key_column="id")
    statuses = [row.status for row in rows]
    assert "added" in statuses
    assert "removed" in statuses
    assert "modified" in statuses
