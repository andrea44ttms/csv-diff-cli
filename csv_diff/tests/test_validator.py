import pytest
from csv_diff.validator import (
    ColumnRule, ValidationResult, parse_rules, validate_row,
    validate_rows, ValidationError,
)


def test_parse_rules_basic():
    rules = parse_rules({"name": {"required": True}, "dept": {"allowed_values": ["eng"]}})
    assert len(rules) == 2
    assert rules[0].name == "name"
    assert rules[0].required is True
    assert rules[1].allowed_values == ["eng"]


def test_parse_rules_invalid_raises():
    with pytest.raises(ValidationError):
        parse_rules({"name": "bad"})


def test_validate_row_required_missing():
    rule = ColumnRule(name="name", required=True)
    errors = validate_row({"name": ""}, [rule])
    assert any("required" in e for e in errors)


def test_validate_row_required_present():
    rule = ColumnRule(name="name", required=True)
    errors = validate_row({"name": "Alice"}, [rule])
    assert errors == []


def test_validate_row_allowed_values_ok():
    rule = ColumnRule(name="dept", allowed_values=["eng", "hr"])
    errors = validate_row({"dept": "eng"}, [rule])
    assert errors == []


def test_validate_row_allowed_values_fail():
    rule = ColumnRule(name="dept", allowed_values=["eng", "hr"])
    errors = validate_row({"dept": "finance"}, [rule])
    assert any("not in" in e for e in errors)


def test_validate_row_max_length_ok():
    rule = ColumnRule(name="name", max_length=10)
    errors = validate_row({"name": "Alice"}, [rule])
    assert errors == []


def test_validate_row_max_length_fail():
    rule = ColumnRule(name="name", max_length=3)
    errors = validate_row({"name": "Alice"}, [rule])
    assert any("too long" in e for e in errors)


def test_validate_rows_aggregates():
    rules = [ColumnRule(name="dept", allowed_values=["eng"])]
    rows = [{"dept": "eng"}, {"dept": "hr"}, {"dept": "hr"}]
    result = validate_rows(rows, rules)
    assert not result.valid
    assert len(result.errors) == 2
    assert "Row 1" in result.errors[0]


def test_validate_rows_all_valid():
    rules = [ColumnRule(name="dept", required=True, allowed_values=["eng"])]
    rows = [{"dept": "eng"}, {"dept": "eng"}]
    result = validate_rows(rows, rules)
    assert result.valid
