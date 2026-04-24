"""Tests for csv_diff.splitter."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.splitter import (
    SplitError,
    SplitResult,
    filter_split,
    parse_split_statuses,
    split_diff,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[{"id": "1", "name": "Alice!"}],
        unchanged=[{"id": "4", "name": "Dave"}],
    )


# ---------------------------------------------------------------------------
# parse_split_statuses
# ---------------------------------------------------------------------------

def test_parse_split_statuses_none_returns_all():
    statuses = parse_split_statuses(None)
    assert set(statuses) == {"added", "removed", "modified", "unchanged"}


def test_parse_split_statuses_empty_string_returns_all():
    statuses = parse_split_statuses("")
    assert set(statuses) == {"added", "removed", "modified", "unchanged"}


def test_parse_split_statuses_single():
    assert parse_split_statuses("added") == ["added"]


def test_parse_split_statuses_multiple():
    result = parse_split_statuses("added,removed")
    assert set(result) == {"added", "removed"}


def test_parse_split_statuses_strips_spaces():
    result = parse_split_statuses(" modified , unchanged ")
    assert set(result) == {"modified", "unchanged"}


def test_parse_split_statuses_invalid_raises():
    with pytest.raises(SplitError, match="Unknown status"):
        parse_split_statuses("added,bogus")


# ---------------------------------------------------------------------------
# split_diff
# ---------------------------------------------------------------------------

def test_split_diff_added():
    sr = split_diff(_result())
    assert sr.added == [{"id": "3", "name": "Carol"}]


def test_split_diff_removed():
    sr = split_diff(_result())
    assert sr.removed == [{"id": "2", "name": "Bob"}]


def test_split_diff_modified():
    sr = split_diff(_result())
    assert sr.modified == [{"id": "1", "name": "Alice!"}]


def test_split_diff_unchanged():
    sr = split_diff(_result())
    assert sr.unchanged == [{"id": "4", "name": "Dave"}]


def test_split_diff_empty_result():
    empty = DiffResult(added=[], removed=[], modified=[], unchanged=[])
    sr = split_diff(empty)
    assert sr.added == [] and sr.removed == [] and sr.modified == [] and sr.unchanged == []


# ---------------------------------------------------------------------------
# filter_split
# ---------------------------------------------------------------------------

def test_filter_split_keeps_only_requested():
    sr = split_diff(_result())
    filtered = filter_split(sr, ["added"])
    assert filtered.added == [{"id": "3", "name": "Carol"}]
    assert filtered.removed == []
    assert filtered.modified == []
    assert filtered.unchanged == []


def test_filter_split_multiple_statuses():
    sr = split_diff(_result())
    filtered = filter_split(sr, ["added", "removed"])
    assert len(filtered.added) == 1
    assert len(filtered.removed) == 1


def test_filter_split_unknown_status_raises():
    sr = SplitResult()
    with pytest.raises(SplitError, match="Unknown status"):
        filter_split(sr, ["invalid"])
