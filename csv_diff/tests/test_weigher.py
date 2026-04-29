"""Tests for csv_diff.weigher."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.weigher import (
    WeighError,
    WeighResult,
    WeighedRow,
    parse_weight_map,
    weigh_rows,
    format_weigh,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_parse_weight_map_defaults():
    wm = parse_weight_map(None)
    assert wm["added"] == 1.0
    assert wm["unchanged"] == 0.0


def test_parse_weight_map_custom():
    wm = parse_weight_map("added=3.0, removed=2.0")
    assert wm["added"] == 3.0
    assert wm["removed"] == 2.0
    assert wm["modified"] == 0.5  # unchanged default


def test_parse_weight_map_invalid_format():
    with pytest.raises(WeighError, match="missing '='"):
        parse_weight_map("added")


def test_parse_weight_map_unknown_key():
    with pytest.raises(WeighError, match="Unknown status key"):
        parse_weight_map("deleted=1.0")


def test_parse_weight_map_non_numeric():
    with pytest.raises(WeighError, match="Non-numeric weight"):
        parse_weight_map("added=high")


def test_weigh_rows_added():
    r = _result(added=[{"id": "1", "name": "Alice"}])
    wm = parse_weight_map(None)
    wr = weigh_rows(r, wm)
    assert len(wr.rows) == 1
    assert wr.rows[0].status == "added"
    assert wr.rows[0].weight == 1.0
    assert wr.total_weight == 1.0


def test_weigh_rows_unchanged_zero_weight():
    r = _result(unchanged=[{"id": "2", "name": "Bob"}])
    wm = parse_weight_map(None)
    wr = weigh_rows(r, wm)
    assert wr.rows[0].weight == 0.0
    assert wr.total_weight == 0.0


def test_weigh_rows_modified():
    r = _result(modified=[({"id": "3", "val": "new"}, {"id": "3", "val": "old"})])
    wm = parse_weight_map(None)
    wr = weigh_rows(r, wm)
    assert wr.rows[0].status == "modified"
    assert wr.rows[0].weight == 0.5


def test_weigh_rows_mixed_total():
    r = _result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}],
        modified=[({"id": "3", "v": "a"}, {"id": "3", "v": "b"})],
    )
    wm = parse_weight_map(None)
    wr = weigh_rows(r, wm)
    assert wr.total_weight == pytest.approx(2.5)


def test_format_weigh_contains_total():
    r = _result(added=[{"id": "1"}])
    wm = parse_weight_map(None)
    wr = weigh_rows(r, wm)
    out = format_weigh(wr)
    assert "Total weight:" in out
    assert "added" in out
