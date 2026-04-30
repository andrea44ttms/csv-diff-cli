"""Tests for csv_diff.bucketer."""

import pytest

from csv_diff.bucketer import (
    BucketError,
    BucketResult,
    bucket_diff,
    parse_bucket_spec,
)
from csv_diff.differ import DiffResult


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


# --- parse_bucket_spec ---

def test_parse_bucket_spec_basic():
    buckets = parse_bucket_spec("low:0:50,high:50:100")
    assert buckets == [("low", 0.0, 50.0), ("high", 50.0, 100.0)]


def test_parse_bucket_spec_single():
    buckets = parse_bucket_spec("all:0:9999")
    assert len(buckets) == 1
    assert buckets[0][0] == "all"


def test_parse_bucket_spec_strips_spaces():
    buckets = parse_bucket_spec(" low : 0 : 50 , high : 50 : 100 ")
    assert buckets[0] == ("low", 0.0, 50.0)


def test_parse_bucket_spec_empty_raises():
    with pytest.raises(BucketError, match="must not be empty"):
        parse_bucket_spec("")


def test_parse_bucket_spec_none_raises():
    with pytest.raises(BucketError, match="must not be empty"):
        parse_bucket_spec(None)


def test_parse_bucket_spec_missing_colon_raises():
    with pytest.raises(BucketError, match="expected 'label:min:max'"):
        parse_bucket_spec("low-0-50")


def test_parse_bucket_spec_non_numeric_bounds_raises():
    with pytest.raises(BucketError, match="must be numeric"):
        parse_bucket_spec("low:zero:fifty")


def test_parse_bucket_spec_min_gte_max_raises():
    with pytest.raises(BucketError, match="min must be less than max"):
        parse_bucket_spec("bad:100:50")


def test_parse_bucket_spec_empty_label_raises():
    with pytest.raises(BucketError, match="label must not be empty"):
        parse_bucket_spec(":0:50")


# --- bucket_diff ---

def test_bucket_diff_basic_grouping():
    rows = [
        {"score": "10"},
        {"score": "60"},
        {"score": "80"},
    ]
    result = _result(added=rows)
    spec = parse_bucket_spec("low:0:50,high:50:100")
    br = bucket_diff(result, "score", spec)
    assert isinstance(br, BucketResult)
    assert len(br.buckets["low"]) == 1
    assert len(br.buckets["high"]) == 2


def test_bucket_diff_non_numeric_goes_to_other():
    rows = [{"score": "N/A"}, {"score": "25"}]
    result = _result(added=rows)
    spec = parse_bucket_spec("low:0:50")
    br = bucket_diff(result, "score", spec)
    assert len(br.buckets["__other__"]) == 1
    assert len(br.buckets["low"]) == 1


def test_bucket_diff_out_of_range_goes_to_other():
    rows = [{"score": "200"}]
    result = _result(added=rows)
    spec = parse_bucket_spec("low:0:50,high:50:100")
    br = bucket_diff(result, "score", spec)
    assert br.buckets["__other__"] == [{"score": "200"}]


def test_bucket_diff_missing_column_raises():
    rows = [{"value": "10"}]
    result = _result(added=rows)
    spec = parse_bucket_spec("low:0:50")
    with pytest.raises(BucketError, match="not found in row"):
        bucket_diff(result, "score", spec)


def test_bucket_diff_empty_result():
    result = _result()
    spec = parse_bucket_spec("low:0:50")
    br = bucket_diff(result, "score", spec)
    assert br.buckets["low"] == []
    assert br.buckets["__other__"] == []
