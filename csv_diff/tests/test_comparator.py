"""Tests for csv_diff.comparator."""
import pytest
from csv_diff.comparator import (
    CompareError,
    CompareOptions,
    FieldComparison,
    parse_compare_options,
    compare_fields,
    _values_equal,
)


def test_parse_compare_options_defaults():
    opts = parse_compare_options(None)
    assert opts.numeric_tolerance == 0.0
    assert opts.ignore_case is False
    assert opts.ignore_whitespace is False


def test_parse_compare_options_from_dict():
    opts = parse_compare_options({"numeric_tolerance": "0.5", "ignore_case": True})
    assert opts.numeric_tolerance == 0.5
    assert opts.ignore_case is True


def test_parse_compare_options_invalid_tolerance():
    with pytest.raises(CompareError, match="Invalid numeric_tolerance"):
        parse_compare_options({"numeric_tolerance": "abc"})


def test_parse_compare_options_negative_tolerance():
    with pytest.raises(CompareError, match=">= 0"):
        parse_compare_options({"numeric_tolerance": "-1"})


def test_values_equal_exact():
    opts = CompareOptions()
    assert _values_equal("hello", "hello", opts) is True
    assert _values_equal("hello", "world", opts) is False


def test_values_equal_ignore_case():
    opts = CompareOptions(ignore_case=True)
    assert _values_equal("Hello", "hello", opts) is True


def test_values_equal_ignore_whitespace():
    opts = CompareOptions(ignore_whitespace=True)
    assert _values_equal("  foo  ", "foo", opts) is True


def test_values_equal_numeric_tolerance():
    opts = CompareOptions(numeric_tolerance=0.1)
    assert _values_equal("1.0", "1.05", opts) is True
    assert _values_equal("1.0", "1.2", opts) is False


def test_values_equal_numeric_tolerance_non_numeric_fallback():
    opts = CompareOptions(numeric_tolerance=0.5)
    assert _values_equal("abc", "abc", opts) is True
    assert _values_equal("abc", "def", opts) is False


def test_compare_fields_all_equal():
    opts = CompareOptions()
    old = {"name": "Alice", "dept": "Eng"}
    new = {"name": "Alice", "dept": "Eng"}
    result = compare_fields(["name", "dept"], old, new, opts)
    assert all(f.equal for f in result)


def test_compare_fields_some_changed():
    opts = CompareOptions()
    old = {"name": "Alice", "dept": "Eng"}
    new = {"name": "Alice", "dept": "HR"}
    result = compare_fields(["name", "dept"], old, new, opts)
    name_f = next(f for f in result if f.column == "name")
    dept_f = next(f for f in result if f.column == "dept")
    assert name_f.equal is True
    assert dept_f.equal is False
    assert dept_f.old_value == "Eng"
    assert dept_f.new_value == "HR"


def test_compare_fields_missing_key_defaults_empty():
    opts = CompareOptions()
    result = compare_fields(["score"], {}, {"score": "10"}, opts)
    assert result[0].old_value == ""
    assert result[0].equal is False
