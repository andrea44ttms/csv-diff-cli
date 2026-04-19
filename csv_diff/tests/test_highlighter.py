import pytest
from csv_diff.highlighter import (
    CellDiff,
    RowHighlight,
    HighlightError,
    highlight_row,
    highlight_diff,
    format_highlight,
)


OLD = {"id": "1", "name": "Alice", "dept": "Eng"}
NEW = {"id": "1", "name": "Alicia", "dept": "Eng"}


def test_highlight_row_detects_change():
    rh = highlight_row(OLD, NEW)
    assert len(rh.changes) == 1
    assert rh.changes[0].column == "name"
    assert rh.changes[0].old_value == "Alice"
    assert rh.changes[0].new_value == "Alicia"


def test_highlight_row_no_change():
    rh = highlight_row(OLD, OLD)
    assert rh.changes == []


def test_highlight_row_multiple_changes():
    new = {"id": "1", "name": "Bob", "dept": "HR"}
    rh = highlight_row(OLD, new)
    assert set(rh.changed_columns) == {"name", "dept"}


def test_highlight_row_key_is_first_value():
    rh = highlight_row(OLD, NEW)
    assert rh.key == "1"


def test_highlight_row_mismatched_keys_raises():
    with pytest.raises(HighlightError):
        highlight_row(OLD, {"id": "1", "name": "Alice", "extra": "x"})


def test_highlight_diff_returns_list():
    pairs = [(OLD, NEW), (OLD, OLD)]
    results = highlight_diff(pairs)
    assert len(results) == 2
    assert len(results[0].changes) == 1
    assert len(results[1].changes) == 0


def test_format_highlight_empty():
    assert format_highlight([]) == "No cell-level changes."


def test_format_highlight_shows_changes():
    rh = highlight_row(OLD, NEW)
    output = format_highlight([rh])
    assert "Row [1]" in output
    assert "name" in output
    assert "Alice" in output
    assert "Alicia" in output


def test_format_highlight_multiple_rows():
    new2 = {"id": "2", "name": "Bob", "dept": "HR"}
    old2 = {"id": "2", "name": "Bobby", "dept": "HR"}
    highlights = highlight_diff([(OLD, NEW), (old2, new2)])
    output = format_highlight(highlights)
    assert "Row [1]" in output
    assert "Row [2]" in output
