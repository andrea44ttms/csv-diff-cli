"""Tests for csv_diff.thresholder."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.thresholder import (
    ThresholdError,
    ThresholdResult,
    apply_threshold,
    format_threshold,
    parse_min_rate,
)


def _result(
    added=None, removed=None, modified=None, unchanged=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        unchanged=unchanged or [],
    )


# ---------------------------------------------------------------------------
# parse_min_rate
# ---------------------------------------------------------------------------

def test_parse_min_rate_none_returns_zero():
    assert parse_min_rate(None) == 0.0


def test_parse_min_rate_integer_string():
    assert parse_min_rate("10") == pytest.approx(0.10)


def test_parse_min_rate_float_string():
    assert parse_min_rate("12.5") == pytest.approx(0.125)


def test_parse_min_rate_zero():
    assert parse_min_rate("0") == 0.0


def test_parse_min_rate_hundred():
    assert parse_min_rate("100") == pytest.approx(1.0)


def test_parse_min_rate_non_numeric_raises():
    with pytest.raises(ThresholdError, match="number"):
        parse_min_rate("abc")


def test_parse_min_rate_negative_raises():
    with pytest.raises(ThresholdError, match="between 0 and 100"):
        parse_min_rate("-1")


def test_parse_min_rate_over_100_raises():
    with pytest.raises(ThresholdError, match="between 0 and 100"):
        parse_min_rate("101")


# ---------------------------------------------------------------------------
# apply_threshold
# ---------------------------------------------------------------------------

def test_apply_threshold_passes_when_rate_above_min():
    r = _result(added=[{"id": "1"}], unchanged=[{"id": "2"}])
    tr = apply_threshold(r, min_rate=0.40)
    assert tr.passed is True
    assert tr.change_rate == pytest.approx(0.5)


def test_apply_threshold_fails_when_rate_below_min():
    r = _result(added=[{"id": "1"}], unchanged=[{"id": "2"}, {"id": "3"}, {"id": "4"}])
    tr = apply_threshold(r, min_rate=0.50)
    assert tr.passed is False
    assert tr.change_rate == pytest.approx(0.25)


def test_apply_threshold_zero_min_always_passes():
    r = _result(unchanged=[{"id": "1"}])
    tr = apply_threshold(r, min_rate=0.0)
    assert tr.passed is True


def test_apply_threshold_empty_result_passes_zero_min():
    r = _result()
    tr = apply_threshold(r, min_rate=0.0)
    assert tr.passed is True
    assert tr.change_rate == 0.0


def test_apply_threshold_preserves_original_result():
    r = _result(added=[{"id": "1"}])
    tr = apply_threshold(r, min_rate=0.0)
    assert tr.result is r


# ---------------------------------------------------------------------------
# format_threshold
# ---------------------------------------------------------------------------

def test_format_threshold_passed():
    tr = ThresholdResult(passed=True, change_rate=0.5, min_rate=0.25, result=_result())
    out = format_threshold(tr)
    assert "PASSED" in out
    assert "50.0%" in out
    assert "25.0%" in out


def test_format_threshold_failed():
    tr = ThresholdResult(passed=False, change_rate=0.1, min_rate=0.20, result=_result())
    out = format_threshold(tr)
    assert "BELOW THRESHOLD" in out
