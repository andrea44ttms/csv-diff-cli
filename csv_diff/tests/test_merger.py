import pytest
from csv_diff.differ import DiffResult
from csv_diff.merger import MergeError, MergeResult, merge_diffs

HEADERS = ["id", "name", "dept"]


def _r(id_, name, dept):
    return {"id": id_, "name": name, "dept": dept}


def _base_result(**kwargs):
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(headers=HEADERS, **defaults)


def test_merge_no_changes():
    base = _base_result(unchanged=[_r("1", "Alice", "Eng")])
    other = _base_result(unchanged=[_r("1", "Alice", "Eng")])
    result = merge_diffs(base, other, key="id")
    assert result.rows == [_r("1", "Alice", "Eng")]
    assert result.conflicts == []


def test_merge_other_addition_wins():
    base = _base_result(unchanged=[_r("1", "Alice", "Eng")])
    other = _base_result(
        unchanged=[_r("1", "Alice", "Eng")],
        added=[_r("2", "Bob", "HR")],
    )
    result = merge_diffs(base, other, key="id")
    ids = {r["id"] for r in result.rows}
    assert "2" in ids


def test_merge_other_modification_wins():
    old = _r("1", "Alice", "Eng")
    new_base = _r("1", "Alice", "HR")
    new_other = _r("1", "Alice", "Finance")
    base = _base_result(modified=[(old, new_base)])
    other = _base_result(modified=[(old, new_other)])
    result = merge_diffs(base, other, key="id")
    assert any(r["dept"] == "Finance" for r in result.rows)


def test_merge_conflict_detected():
    old = _r("1", "Alice", "Eng")
    new_base = _r("1", "Alice", "HR")
    new_other = _r("1", "Alice", "Finance")
    base = _base_result(modified=[(old, new_base)])
    other = _base_result(modified=[(old, new_other)])
    result = merge_diffs(base, other, key="id")
    assert len(result.conflicts) == 1


def test_merge_removed_in_other_excluded():
    base = _base_result(unchanged=[_r("1", "Alice", "Eng"), _r("2", "Bob", "HR")])
    other = _base_result(
        unchanged=[_r("1", "Alice", "Eng")],
        removed=[_r("2", "Bob", "HR")],
    )
    result = merge_diffs(base, other, key="id")
    ids = {r["id"] for r in result.rows}
    assert "2" not in ids


def test_merge_header_mismatch_raises():
    base = DiffResult(headers=["id", "name"], added=[], removed=[], modified=[], unchanged=[])
    other = DiffResult(headers=["id", "dept"], added=[], removed=[], modified=[], unchanged=[])
    with pytest.raises(MergeError, match="headers"):
        merge_diffs(base, other, key="id")


def test_merge_missing_key_raises():
    base = _base_result(added=[_r("1", "Alice", "Eng")])
    other = _base_result(added=[{"name": "Bob", "dept": "HR"}])
    with pytest.raises(MergeError):
        merge_diffs(base, other, key="id")
