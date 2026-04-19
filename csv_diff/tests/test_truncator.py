import pytest
from csv_diff.differ import DiffResult
from csv_diff.truncator import (
    TruncateError,
    parse_max_rows,
    truncate_diff,
    format_truncation_notice,
)


def _result():
    return DiffResult(
        added=[("a", {}), ("b", {}), ("c", {})],
        removed=[("d", {})],
        modified=[("e", {}, {}), ("f", {}, {})],
        unchanged=[("g", {}), ("h", {}), ("i", {}), ("j", {})],
    )


def test_parse_max_rows_valid():
    assert parse_max_rows("5") == 5


def test_parse_max_rows_zero_raises():
    with pytest.raises(TruncateError, match="positive"):
        parse_max_rows("0")


def test_parse_max_rows_non_integer_raises():
    with pytest.raises(TruncateError, match="integer"):
        parse_max_rows("abc")


def test_truncate_added():
    tr = truncate_diff(_result(), max_rows=2)
    assert len(tr.result.added) == 2
    assert tr.added_truncated == 1


def test_truncate_removed_no_truncation():
    tr = truncate_diff(_result(), max_rows=2)
    assert len(tr.result.removed) == 1
    assert tr.removed_truncated == 0


def test_truncate_modified():
    tr = truncate_diff(_result(), max_rows=1)
    assert len(tr.result.modified) == 1
    assert tr.modified_truncated == 1


def test_truncate_unchanged():
    tr = truncate_diff(_result(), max_rows=2)
    assert len(tr.result.unchanged) == 2
    assert tr.unchanged_truncated == 2


def test_truncate_none_max_rows_no_truncation():
    tr = truncate_diff(_result(), max_rows=None)
    assert not tr.any_truncated
    assert len(tr.result.added) == 3


def test_any_truncated_false_when_all_fit():
    tr = truncate_diff(_result(), max_rows=100)
    assert not tr.any_truncated


def test_format_truncation_notice_empty_when_none():
    tr = truncate_diff(_result(), max_rows=None)
    assert format_truncation_notice(tr) == ""


def test_format_truncation_notice_shows_counts():
    tr = truncate_diff(_result(), max_rows=1)
    notice = format_truncation_notice(tr)
    assert "[truncated]" in notice
    assert "added: 2" in notice
    assert "modified: 1" in notice
    assert "unchanged: 3" in notice
