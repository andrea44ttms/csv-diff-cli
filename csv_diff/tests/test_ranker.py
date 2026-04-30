"""Tests for csv_diff.ranker."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.ranker import (
    RankError,
    RankResult,
    RankedRow,
    parse_rank_column,
    parse_rank_order,
    rank_diff,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


# --- parse_rank_column ---

def test_parse_rank_column_strips():
    assert parse_rank_column("  score  ") == "score"


def test_parse_rank_column_none_returns_none():
    assert parse_rank_column(None) is None


def test_parse_rank_column_empty_raises():
    with pytest.raises(RankError):
        parse_rank_column("   ")


# --- parse_rank_order ---

def test_parse_rank_order_none_returns_desc():
    assert parse_rank_order(None) is False


def test_parse_rank_order_asc():
    assert parse_rank_order("asc") is True


def test_parse_rank_order_desc():
    assert parse_rank_order("desc") is False


def test_parse_rank_order_case_insensitive():
    assert parse_rank_order("ASC") is True
    assert parse_rank_order("Descending") is False


def test_parse_rank_order_invalid_raises():
    with pytest.raises(RankError):
        parse_rank_order("random")


# --- rank_diff ---

def test_rank_diff_empty_returns_empty():
    r = rank_diff(_result(), column="score")
    assert r.rows == []
    assert r.column == "score"


def test_rank_diff_orders_descending_by_default():
    rows = [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "30"},
        {"name": "c", "score": "20"},
    ]
    result = _result(added=rows)
    ranked = rank_diff(result, column="score", ascending=False)
    scores = [rr.score for rr in ranked.rows]
    assert scores == [30.0, 20.0, 10.0]
    assert ranked.rows[0].rank == 1


def test_rank_diff_ascending():
    rows = [{"v": "5"}, {"v": "1"}, {"v": "3"}]
    result = _result(removed=rows)
    ranked = rank_diff(result, column="v", ascending=True)
    scores = [rr.score for rr in ranked.rows]
    assert scores == [1.0, 3.0, 5.0]


def test_rank_diff_non_numeric_scores_zero():
    rows = [{"name": "x", "score": "n/a"}, {"name": "y", "score": "42"}]
    result = _result(added=rows)
    ranked = rank_diff(result, column="score", ascending=False)
    assert ranked.rows[0].score == 42.0
    assert ranked.rows[1].score == 0.0


def test_rank_diff_modified_uses_new_row():
    old = {"id": "1", "val": "5"}
    new = {"id": "1", "val": "99"}
    result = _result(modified=[(old, new)])
    ranked = rank_diff(result, column="val")
    assert ranked.rows[0].score == 99.0
    assert ranked.rows[0].status == "modified"
