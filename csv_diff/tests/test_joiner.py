import pytest
from csv_diff.differ import DiffResult
from csv_diff.joiner import (
    JoinError,
    JoinResult,
    parse_join_key,
    join_diff_rows,
)


def _diff(added=None, removed=None, modified=None, unchanged=None):
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        unchanged=unchanged or [],
    )


def test_parse_join_key_valid():
    assert parse_join_key(" id ") == "id"


def test_parse_join_key_empty_raises():
    with pytest.raises(JoinError):
        parse_join_key("")


def test_parse_join_key_none_raises():
    with pytest.raises(JoinError):
        parse_join_key(None)


def test_join_basic():
    left = _diff(added=[{"id": "1", "score": "10"}, {"id": "2", "score": "20"}])
    right = _diff(added=[{"id": "1", "grade": "A"}, {"id": "3", "grade": "B"}])
    result = join_diff_rows(left, right, key="id")
    assert len(result.rows) == 1
    assert result.rows[0]["id"] == "1"
    assert result.rows[0]["score"] == "10"
    assert result.rows[0]["grade"] == "A"


def test_join_no_common_keys():
    left = _diff(added=[{"id": "1", "val": "x"}])
    right = _diff(added=[{"id": "2", "val": "y"}])
    result = join_diff_rows(left, right, key="id")
    assert result.rows == []
    assert result.headers == []


def test_join_suffix_collision():
    left = _diff(added=[{"id": "1", "name": "Alice"}])
    right = _diff(added=[{"id": "1", "name": "Bob"}])
    result = join_diff_rows(left, right, key="id")
    assert "name_left" in result.headers
    assert "name_right" in result.headers
    assert result.rows[0]["name_left"] == "Alice"
    assert result.rows[0]["name_right"] == "Bob"


def test_join_missing_key_raises():
    left = _diff(added=[{"id": "1", "val": "x"}])
    right = _diff(added=[{"nope": "1", "val": "y"}])
    with pytest.raises(JoinError):
        join_diff_rows(left, right, key="id")


def test_join_custom_suffixes():
    left = _diff(added=[{"id": "1", "v": "a"}])
    right = _diff(added=[{"id": "1", "v": "b"}])
    result = join_diff_rows(left, right, key="id", suffixes=("_L", "_R"))
    assert "v_L" in result.headers
    assert "v_R" in result.headers
