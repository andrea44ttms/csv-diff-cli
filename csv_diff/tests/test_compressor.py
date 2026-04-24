"""Tests for csv_diff/compressor.py."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.compressor import (
    compress_diff,
    format_compressed,
    parse_compress_flag,
    CompressResult,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


# ---------------------------------------------------------------------------
# compress_diff
# ---------------------------------------------------------------------------

def test_compress_empty_result():
    cr = compress_diff(_result())
    assert cr.original_count == 0
    assert cr.run_count == 0
    assert cr.runs == []


def test_compress_single_status():
    rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    cr = compress_diff(_result(added=rows))
    assert cr.original_count == 2
    assert cr.run_count == 1
    assert cr.runs[0].status == "added"
    assert cr.runs[0].count == 2


def test_compress_multiple_statuses():
    cr = compress_diff(
        _result(
            added=[{"id": "1"}],
            removed=[{"id": "2"}],
            modified=[{"id": "3"}],
            unchanged=[{"id": "4"}],
        )
    )
    assert cr.original_count == 4
    # Each bucket is separate so we get 4 runs (all different statuses)
    assert cr.run_count == 4


def test_compress_rows_preserved():
    rows = [{"id": "1", "v": "a"}, {"id": "2", "v": "b"}]
    cr = compress_diff(_result(removed=rows))
    assert len(cr.runs[0].rows) == 2
    assert cr.runs[0].rows[0]["_status"] == "removed"


def test_compress_run_count_matches_runs_list():
    cr = compress_diff(_result(added=[{"id": "1"}], unchanged=[{"id": "2"}]))
    assert cr.run_count == len(cr.runs)


# ---------------------------------------------------------------------------
# parse_compress_flag
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val", ["1", "true", "True", "TRUE", "yes", "YES"])
def test_parse_compress_flag_truthy(val):
    assert parse_compress_flag(val) is True


@pytest.mark.parametrize("val", ["0", "false", "no", "", "random"])
def test_parse_compress_flag_falsy(val):
    assert parse_compress_flag(val) is False


def test_parse_compress_flag_none():
    assert parse_compress_flag(None) is False


# ---------------------------------------------------------------------------
# format_compressed
# ---------------------------------------------------------------------------

def test_format_compressed_empty():
    cr = CompressResult(runs=[], original_count=0, run_count=0)
    assert format_compressed(cr) == "No rows."


def test_format_compressed_shows_counts():
    cr = compress_diff(_result(added=[{"id": "1"}, {"id": "2"}]))
    out = format_compressed(cr)
    assert "2 rows" in out
    assert "1 run" in out
    assert "added x2" in out
