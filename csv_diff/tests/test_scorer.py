import pytest
from csv_diff.differ import DiffResult
from csv_diff.scorer import (
    SimilarityScore,
    compute_score,
    format_score,
)


def _result(**kwargs):
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_score_identical():
    r = _result(unchanged=[{"id": "1"}] * 5)
    s = compute_score(r)
    assert s.score == 1.0
    assert s.total_rows == 5


def test_score_all_added():
    r = _result(added=[{"id": "1"}] * 4)
    s = compute_score(r)
    assert s.score == 0.0
    assert s.added == 4


def test_score_mixed():
    r = _result(
        unchanged=[{"id": "1"}, {"id": "2"}],
        modified=[{"id": "3"}],
        added=[{"id": "4"}],
    )
    s = compute_score(r)
    assert s.total_rows == 4
    assert s.score == pytest.approx(0.5)


def test_score_empty():
    r = _result()
    s = compute_score(r)
    assert s.score == 0.0
    assert s.total_rows == 0


def test_format_score_contains_percentage():
    r = _result(unchanged=[{"id": "1"}] * 3, modified=[{"id": "2"}])
    s = compute_score(r)
    out = format_score(s)
    assert "75.00%" in out
    assert "Similarity Score" in out
    assert "Total rows" in out
