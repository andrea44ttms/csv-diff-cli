"""Tests for csv_diff.stats module."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.stats import compute_stats, format_stats, DiffStats


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_compute_stats_empty():
    stats = compute_stats(_result())
    assert stats.total_added == 0
    assert stats.total_removed == 0
    assert stats.total_modified == 0
    assert stats.total_unchanged == 0
    assert stats.total_rows == 0
    assert stats.change_rate == 0.0


def test_compute_stats_added_removed():
    result = _result(
        added=[{"id": "1", "name": "Alice"}],
        removed=[{"id": "2", "name": "Bob"}],
        unchanged=[{"id": "3", "name": "Carol"}],
    )
    stats = compute_stats(result)
    assert stats.total_added == 1
    assert stats.total_removed == 1
    assert stats.total_unchanged == 1
    assert stats.total_rows == 3
    assert stats.change_rate == round(2 / 3, 4)


def test_compute_stats_modified_columns():
    result = _result(
        modified=[
            {"old": {"id": "1", "name": "Alice", "dept": "Eng"},
             "new": {"id": "1", "name": "Alicia", "dept": "Eng"}},
            {"old": {"id": "2", "name": "Bob", "dept": "HR"},
             "new": {"id": "2", "name": "Bobby", "dept": "Finance"}},
        ]
    )
    stats = compute_stats(result)
    assert stats.total_modified == 2
    assert stats.modified_columns["name"] == 2
    assert stats.modified_columns["dept"] == 1
    assert "id" not in stats.modified_columns


def test_change_rate_all_unchanged():
    result = _result(unchanged=[{"id": "1"}, {"id": "2"}])
    stats = compute_stats(result)
    assert stats.change_rate == 0.0


def test_format_stats_contains_sections():
    result = _result(
        added=[{"id": "1"}],
        modified=[
            {"old": {"id": "2", "val": "a"}, "new": {"id": "2", "val": "b"}}
        ],
        unchanged=[{"id": "3"}],
    )
    stats = compute_stats(result)
    output = format_stats(stats)
    assert "Added:" in output
    assert "Modified:" in output
    assert "Change rate:" in output
    assert "val" in output
