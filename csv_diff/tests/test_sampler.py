"""Tests for csv_diff.sampler."""
import pytest
from csv_diff.sampler import (
    SampleError,
    parse_sample_size,
    sample_rows,
    sample_diff,
)


ROWS = [{"id": str(i), "val": str(i * 2)} for i in range(20)]


def test_parse_sample_size_valid():
    assert parse_sample_size("10") == 10


def test_parse_sample_size_non_integer():
    with pytest.raises(SampleError, match="integer"):
        parse_sample_size("abc")


def test_parse_sample_size_zero():
    with pytest.raises(SampleError, match="positive"):
        parse_sample_size("0")


def test_sample_rows_returns_correct_count():
    result = sample_rows(ROWS, 5, seed=42)
    assert len(result) == 5


def test_sample_rows_no_duplicates():
    result = sample_rows(ROWS, 10, seed=0)
    ids = [r["id"] for r in result]
    assert len(ids) == len(set(ids))


def test_sample_rows_larger_than_population():
    result = sample_rows(ROWS, 100, seed=1)
    assert len(result) == len(ROWS)


def test_sample_rows_deterministic():
    a = sample_rows(ROWS, 7, seed=99)
    b = sample_rows(ROWS, 7, seed=99)
    assert a == b


def test_sample_rows_zero_raises():
    with pytest.raises(SampleError):
        sample_rows(ROWS, 0)


def test_sample_diff_distributes_statuses():
    added = [{"id": "a1"}, {"id": "a2"}, {"id": "a3"}]
    removed = [{"id": "r1"}, {"id": "r2"}]
    modified = [{"id": "m1"}, {"id": "m2"}, {"id": "m3"}, {"id": "m4"}]
    result = sample_diff(added, removed, modified, n=5, seed=7)
    total = len(result["added"]) + len(result["removed"]) + len(result["modified"])
    assert total == 5


def test_sample_diff_all_when_n_large():
    added = [{"id": "a"}]
    removed = [{"id": "r"}]
    modified = [{"id": "m"}]
    result = sample_diff(added, removed, modified, n=100, seed=0)
    assert len(result["added"]) == 1
    assert len(result["removed"]) == 1
    assert len(result["modified"]) == 1
