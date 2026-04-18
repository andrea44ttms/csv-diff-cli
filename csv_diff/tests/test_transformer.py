import pytest
from csv_diff.transformer import (
    TransformError,
    parse_columns,
    parse_rename,
    select_columns,
    rename_columns,
    apply_transforms,
)

ROWS = [
    {"name": "Alice", "dept": "Eng", "salary": "100"},
    {"name": "Bob", "dept": "HR", "salary": "90"},
]
HEADERS = ["name", "dept", "salary"]


def test_parse_columns_basic():
    assert parse_columns("name,dept") == ["name", "dept"]


def test_parse_columns_strips_spaces():
    assert parse_columns(" name , salary ") == ["name", "salary"]


def test_parse_columns_empty_raises():
    with pytest.raises(TransformError):
        parse_columns("")


def test_parse_rename_basic():
    assert parse_rename("name:full_name") == {"name": "full_name"}


def test_parse_rename_multiple():
    result = parse_rename("name:full_name,dept:department")
    assert result == {"name": "full_name", "dept": "department"}


def test_parse_rename_empty_returns_empty():
    assert parse_rename("") == {}


def test_parse_rename_invalid_raises():
    with pytest.raises(TransformError):
        parse_rename("nodot")


def test_select_columns_basic():
    rows, headers = select_columns(ROWS, HEADERS, ["name", "salary"])
    assert headers == ["name", "salary"]
    assert rows[0] == {"name": "Alice", "salary": "100"}
    assert "dept" not in rows[0]


def test_select_columns_missing_raises():
    with pytest.raises(TransformError, match="not found"):
        select_columns(ROWS, HEADERS, ["name", "missing"])


def test_rename_columns_basic():
    rows, headers = rename_columns(ROWS, HEADERS, {"name": "full_name"})
    assert "full_name" in headers
    assert "name" not in headers
    assert rows[0]["full_name"] == "Alice"


def test_rename_columns_missing_raises():
    with pytest.raises(TransformError, match="not found"):
        rename_columns(ROWS, HEADERS, {"ghost": "x"})


def test_apply_transforms_select_and_rename():
    rows, headers = apply_transforms(
        ROWS, HEADERS, columns_expr="name,dept", rename_expr="dept:department"
    )
    assert headers == ["name", "department"]
    assert rows[0] == {"name": "Alice", "department": "Eng"}


def test_apply_transforms_no_ops():
    rows, headers = apply_transforms(ROWS, HEADERS)
    assert headers == HEADERS
    assert rows == ROWS
