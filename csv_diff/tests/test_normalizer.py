import pytest
from csv_diff.normalizer import (
    NormalizeError,
    NormalizeOptions,
    parse_normalize_options,
    normalize_row,
    normalize_rows,
)


def _row(**kwargs):
    return {k: v for k, v in kwargs.items()}


def test_parse_normalize_options_defaults():
    opts = parse_normalize_options()
    assert opts.strip is True
    assert opts.lowercase is False
    assert opts.uppercase is False
    assert opts.columns is None


def test_parse_normalize_options_lowercase():
    opts = parse_normalize_options(lowercase=True)
    assert opts.lowercase is True


def test_parse_normalize_options_uppercase():
    opts = parse_normalize_options(uppercase=True)
    assert opts.uppercase is True


def test_parse_normalize_options_both_raises():
    with pytest.raises(NormalizeError):
        parse_normalize_options(lowercase=True, uppercase=True)


def test_parse_normalize_options_columns():
    opts = parse_normalize_options(columns_expr="name, city")
    assert opts.columns == ["name", "city"]


def test_parse_normalize_options_empty_columns_raises():
    with pytest.raises(NormalizeError):
        parse_normalize_options(columns_expr="  ,  ")


def test_normalize_row_strips_whitespace():
    opts = NormalizeOptions(strip=True)
    row = _row(name="  Alice ", age=" 30")
    result = normalize_row(row, opts)
    assert result["name"] == "Alice"
    assert result["age"] == "30"


def test_normalize_row_lowercase():
    opts = NormalizeOptions(strip=True, lowercase=True)
    row = _row(name="ALICE", city="New York")
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["city"] == "new york"


def test_normalize_row_uppercase():
    opts = NormalizeOptions(strip=True, uppercase=True)
    row = _row(name="alice")
    result = normalize_row(row, opts)
    assert result["name"] == "ALICE"


def test_normalize_row_column_filter():
    opts = NormalizeOptions(strip=True, lowercase=True, columns=["name"])
    row = _row(name="  ALICE ", dept="Engineering")
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["dept"] == "Engineering"  # untouched


def test_normalize_rows_applies_to_all():
    opts = NormalizeOptions(strip=True, uppercase=True)
    rows = [_row(name=" alice"), _row(name=" bob ")]
    results = normalize_rows(rows, opts)
    assert results[0]["name"] == "ALICE"
    assert results[1]["name"] == "BOB"


def test_normalize_rows_empty_list():
    opts = NormalizeOptions()
    assert normalize_rows([], opts) == []
