"""Tests for csv_diff.timeline."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.timeline import (
    TimelineError,
    TimelineResult,
    add_snapshot,
    format_timeline,
    get_snapshot,
    parse_labels,
)


def _diff(added=0, removed=0, modified=0, unchanged=0):
    return DiffResult(
        added=[["r"] * added][0] if added else [],
        removed=[["r"] * removed][0] if removed else [],
        modified=[["r"] * modified][0] if modified else [],
        unchanged=[["r"] * unchanged][0] if unchanged else [],
    )


def _make_diff(added=0, removed=0, modified=0, unchanged=0):
    return DiffResult(
        added=[{"id": str(i)} for i in range(added)],
        removed=[{"id": str(i)} for i in range(removed)],
        modified=[{"id": str(i)} for i in range(modified)],
        unchanged=[{"id": str(i)} for i in range(unchanged)],
    )


def test_parse_labels_basic():
    assert parse_labels("v1,v2,v3") == ["v1", "v2", "v3"]


def test_parse_labels_strips_spaces():
    assert parse_labels(" v1 , v2 ") == ["v1", "v2"]


def test_parse_labels_none_returns_empty():
    assert parse_labels(None) == []


def test_parse_labels_empty_string_returns_empty():
    assert parse_labels("") == []


def test_parse_labels_empty_segment_raises():
    with pytest.raises(TimelineError):
        parse_labels("v1,,v2")


def test_add_snapshot_appends():
    tl = TimelineResult()
    result = _make_diff(added=1)
    add_snapshot(tl, "v1", result)
    assert len(tl.snapshots) == 1
    assert tl.snapshots[0].label == "v1"


def test_add_snapshot_empty_label_raises():
    tl = TimelineResult()
    with pytest.raises(TimelineError):
        add_snapshot(tl, "", _make_diff())


def test_get_snapshot_found():
    tl = TimelineResult()
    r = _make_diff(removed=2)
    add_snapshot(tl, "snap-a", r)
    snap = get_snapshot(tl, "snap-a")
    assert snap.label == "snap-a"
    assert snap.result is r


def test_get_snapshot_not_found_raises():
    tl = TimelineResult()
    with pytest.raises(TimelineError, match="not found"):
        get_snapshot(tl, "missing")


def test_format_timeline_empty():
    tl = TimelineResult()
    assert "empty" in format_timeline(tl)


def test_format_timeline_shows_labels():
    tl = TimelineResult()
    add_snapshot(tl, "week-1", _make_diff(added=3, removed=1))
    add_snapshot(tl, "week-2", _make_diff(modified=2))
    out = format_timeline(tl)
    assert "week-1" in out
    assert "week-2" in out
    assert "+3" in out
    assert "-1" in out
    assert "~2" in out
