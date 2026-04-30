"""Tests for csv_diff.segmenter."""
import pytest
from csv_diff.differ import DiffResult
from csv_diff.segmenter import (
    SegmentError,
    SegmentResult,
    parse_segment_spec,
    segment_diff,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


# --- parse_segment_spec ---

def test_parse_segment_spec_basic():
    result = parse_segment_spec("head:1-3,body:4-10")
    assert result == [("head", 1, 3), ("body", 4, 10)]


def test_parse_segment_spec_single():
    assert parse_segment_spec("all:1-100") == [("all", 1, 100)]


def test_parse_segment_spec_strips_spaces():
    result = parse_segment_spec(" head : 1 - 5 , body : 6 - 10 ")
    assert result[0] == ("head", 1, 5)
    assert result[1] == ("body", 6, 10)


def test_parse_segment_spec_none_returns_empty():
    assert parse_segment_spec(None) == []


def test_parse_segment_spec_empty_string_returns_empty():
    assert parse_segment_spec("") == []


def test_parse_segment_spec_missing_colon_raises():
    with pytest.raises(SegmentError, match="Invalid segment spec"):
        parse_segment_spec("nocoion")


def test_parse_segment_spec_missing_dash_raises():
    with pytest.raises(SegmentError, match="Invalid segment spec"):
        parse_segment_spec("label:110")


def test_parse_segment_spec_non_integer_range_raises():
    with pytest.raises(SegmentError, match="must be integers"):
        parse_segment_spec("label:a-b")


def test_parse_segment_spec_invalid_range_raises():
    with pytest.raises(SegmentError, match="is invalid"):
        parse_segment_spec("label:5-2")


def test_parse_segment_spec_zero_start_raises():
    with pytest.raises(SegmentError, match="is invalid"):
        parse_segment_spec("label:0-5")


# --- segment_diff ---

def test_segment_diff_assigns_to_correct_bucket():
    r = _result(
        added=[{"id": "1"}, {"id": "2"}, {"id": "3"}],
    )
    segs = parse_segment_spec("first:1-2,last:3-3")
    out = segment_diff(r, segs)
    assert len(out.segments["first"].added) == 2
    assert len(out.segments["last"].added) == 1


def test_segment_diff_unmatched_rows():
    r = _result(removed=[{"id": "x"}, {"id": "y"}])
    segs = parse_segment_spec("only:1-1")
    out = segment_diff(r, segs)
    assert len(out.segments["only"].removed) == 1
    assert len(out.unmatched.removed) == 1


def test_segment_diff_empty_result():
    r = _result()
    segs = parse_segment_spec("a:1-5")
    out = segment_diff(r, segs)
    assert out.segments["a"].added == []
    assert out.unmatched.added == []


def test_segment_diff_no_segments_all_unmatched():
    r = _result(unchanged=[{"id": "1"}, {"id": "2"}])
    out = segment_diff(r, [])
    assert len(out.unmatched.unchanged) == 2
    assert out.segments == {}
