import pytest
from csv_diff.differ import DiffResult
from csv_diff.patcher import PatchError, patch_rows, patch_to_csv_lines


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


ORIGINAL = [
    {"id": "1", "name": "Alice", "dept": "Eng"},
    {"id": "2", "name": "Bob",   "dept": "HR"},
    {"id": "3", "name": "Carol", "dept": "Eng"},
]


def test_patch_no_changes():
    diff = _result(unchanged=list(ORIGINAL))
    result = patch_rows(ORIGINAL, diff, key="id")
    assert result == ORIGINAL


def test_patch_removes_row():
    removed = [{"id": "2", "name": "Bob", "dept": "HR"}]
    diff = _result(removed=removed)
    result = patch_rows(ORIGINAL, diff, key="id")
    ids = [r["id"] for r in result]
    assert "2" not in ids
    assert len(result) == 2


def test_patch_adds_row():
    added = [{"id": "4", "name": "Dave", "dept": "Fin"}]
    diff = _result(added=added)
    result = patch_rows(ORIGINAL, diff, key="id")
    assert len(result) == 4
    assert result[-1]["id"] == "4"


def test_patch_modifies_row():
    modified = [{"old": {"id": "1", "name": "Alice", "dept": "Eng"},
                 "new": {"id": "1", "name": "Alice", "dept": "Finance"}}]
    diff = _result(modified=modified)
    result = patch_rows(ORIGINAL, diff, key="id")
    row1 = next(r for r in result if r["id"] == "1")
    assert row1["dept"] == "Finance"


def test_patch_invalid_key_raises():
    diff = _result()
    with pytest.raises(PatchError):
        patch_rows(ORIGINAL, diff, key="nonexistent")


def test_patch_to_csv_lines():
    rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    headers = ["id", "name"]
    lines = patch_to_csv_lines(rows, headers)
    assert lines[0] == "id,name"
    assert lines[1] == "1,Alice"
    assert lines[2] == "2,Bob"


def test_patch_combined():
    added = [{"id": "5", "name": "Eve", "dept": "Ops"}]
    removed = [{"id": "3", "name": "Carol", "dept": "Eng"}]
    modified = [{"old": {"id": "2", "name": "Bob", "dept": "HR"},
                 "new": {"id": "2", "name": "Bob", "dept": "Legal"}}]
    diff = _result(added=added, removed=removed, modified=modified)
    result = patch_rows(ORIGINAL, diff, key="id")
    ids = [r["id"] for r in result]
    assert "3" not in ids
    assert "5" in ids
    assert next(r for r in result if r["id"] == "2")["dept"] == "Legal"
