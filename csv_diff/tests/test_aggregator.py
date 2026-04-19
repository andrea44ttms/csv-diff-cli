import pytest
from csv_diff.differ import DiffResult
from csv_diff.aggregator import (
    AggregateError, GroupStats, AggregateResult,
    parse_group_by, aggregate_diff, format_aggregate,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_parse_group_by_strips():
    assert parse_group_by("  dept  ") == "dept"


def test_parse_group_by_empty_raises():
    with pytest.raises(AggregateError):
        parse_group_by("   ")


def test_aggregate_added():
    r = _result(added=[{"dept": "eng", "name": "alice"}, {"dept": "hr", "name": "bob"}])
    agg = aggregate_diff(r, "dept")
    assert agg.groups["eng"].added == 1
    assert agg.groups["hr"].added == 1


def test_aggregate_removed():
    r = _result(removed=[{"dept": "eng", "name": "alice"}])
    agg = aggregate_diff(r, "dept")
    assert agg.groups["eng"].removed == 1


def test_aggregate_modified():
    old = {"dept": "eng", "name": "alice"}
    new = {"dept": "eng", "name": "ALICE"}
    r = _result(modified=[(old, new)])
    agg = aggregate_diff(r, "dept")
    assert agg.groups["eng"].modified == 1


def test_aggregate_unchanged():
    r = _result(unchanged=[{"dept": "hr", "name": "bob"}])
    agg = aggregate_diff(r, "dept")
    assert agg.groups["hr"].unchanged == 1


def test_aggregate_missing_column_raises():
    r = _result(added=[{"name": "alice"}])
    with pytest.raises(AggregateError):
        aggregate_diff(r, "dept")


def test_aggregate_total():
    r = _result(
        added=[{"dept": "eng"}],
        removed=[{"dept": "eng"}],
        unchanged=[{"dept": "eng"}],
    )
    agg = aggregate_diff(r, "dept")
    assert agg.groups["eng"].total == 3


def test_format_aggregate_contains_group():
    r = _result(added=[{"dept": "eng"}])
    agg = aggregate_diff(r, "dept")
    out = format_aggregate(agg)
    assert "eng" in out
    assert "+1" in out
