"""Tests for csv_diff.caster."""
import pytest

from csv_diff.caster import (
    CastError,
    CastSpec,
    cast_row,
    cast_rows,
    parse_cast_spec,
)


# ---------------------------------------------------------------------------
# parse_cast_spec
# ---------------------------------------------------------------------------

def test_parse_cast_spec_single():
    specs = parse_cast_spec("age:int")
    assert specs == [CastSpec(column="age", type_name="int")]


def test_parse_cast_spec_multiple():
    specs = parse_cast_spec("age:int, score:float")
    assert len(specs) == 2
    assert specs[0] == CastSpec(column="age", type_name="int")
    assert specs[1] == CastSpec(column="score", type_name="float")


def test_parse_cast_spec_strips_spaces():
    specs = parse_cast_spec("  name : str  ")
    assert specs == [CastSpec(column="name", type_name="str")]


def test_parse_cast_spec_none_returns_empty():
    assert parse_cast_spec(None) == []


def test_parse_cast_spec_empty_string_returns_empty():
    assert parse_cast_spec("") == []


def test_parse_cast_spec_missing_colon_raises():
    with pytest.raises(CastError, match="expected 'column:type'"):
        parse_cast_spec("ageint")


def test_parse_cast_spec_unsupported_type_raises():
    with pytest.raises(CastError, match="Unsupported type"):
        parse_cast_spec("age:datetime")


def test_parse_cast_spec_empty_column_raises():
    with pytest.raises(CastError, match="Empty column name"):
        parse_cast_spec(":int")


# ---------------------------------------------------------------------------
# cast_row
# ---------------------------------------------------------------------------

def test_cast_row_int():
    row = {"name": "Alice", "age": "30"}
    specs = [CastSpec(column="age", type_name="int")]
    result = cast_row(row, specs)
    assert result["age"] == "30"
    assert result["name"] == "Alice"


def test_cast_row_float():
    row = {"score": "9.5"}
    specs = [CastSpec(column="score", type_name="float")]
    result = cast_row(row, specs)
    assert result["score"] == "9.5"


def test_cast_row_bool_true_values():
    specs = [CastSpec(column="active", type_name="bool")]
    for val in ("true", "True", "1", "yes"):
        assert cast_row({"active": val}, specs)["active"] == "True"


def test_cast_row_bool_false_values():
    specs = [CastSpec(column="active", type_name="bool")]
    for val in ("false", "0", "no", ""):
        assert cast_row({"active": val}, specs)["active"] == "False"


def test_cast_row_missing_column_is_ignored():
    row = {"name": "Bob"}
    specs = [CastSpec(column="age", type_name="int")]
    result = cast_row(row, specs)
    assert result == {"name": "Bob"}


def test_cast_row_invalid_int_raises():
    row = {"age": "notanumber"}
    specs = [CastSpec(column="age", type_name="int")]
    with pytest.raises(CastError, match="Cannot cast"):
        cast_row(row, specs)


# ---------------------------------------------------------------------------
# cast_rows
# ---------------------------------------------------------------------------

def test_cast_rows_returns_cast_result():
    rows = [{"age": "25"}, {"age": "30"}]
    specs = parse_cast_spec("age:int")
    result = cast_rows(rows, specs)
    assert result.casted_columns == ["age"]
    assert all(r["age"] in ("25", "30") for r in result.rows)


def test_cast_rows_no_specs_passthrough():
    rows = [{"x": "1"}]
    result = cast_rows(rows, [])
    assert result.rows == rows
    assert result.casted_columns == []
