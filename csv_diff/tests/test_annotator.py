import pytest
from csv_diff.annotator import (
    AnnotateError,
    AnnotateResult,
    parse_label_map,
    annotate_rows,
    DEFAULT_LABELS,
)


def _rows():
    return [
        {"id": "1", "name": "Alice", "_status": "added"},
        {"id": "2", "name": "Bob", "_status": "removed"},
        {"id": "3", "name": "Carol", "_status": "modified"},
        {"id": "4", "name": "Dave", "_status": "unchanged"},
    ]


def test_parse_label_map_none_returns_defaults():
    assert parse_label_map(None) == DEFAULT_LABELS


def test_parse_label_map_custom():
    m = parse_label_map("added=NEW,removed=DEL")
    assert m["added"] == "NEW"
    assert m["removed"] == "DEL"
    assert m["modified"] == "MODIFIED"


def test_parse_label_map_invalid_format():
    with pytest.raises(AnnotateError, match="Invalid label mapping"):
        parse_label_map("addedNEW")


def test_parse_label_map_unknown_key():
    with pytest.raises(AnnotateError, match="Unknown status key"):
        parse_label_map("unknown=X")


def test_annotate_rows_default_labels():
    result = annotate_rows(_rows())
    assert isinstance(result, AnnotateResult)
    assert result.label_column == "_annotation"
    labels = [r["_annotation"] for r in result.rows]
    assert labels == ["ADDED", "REMOVED", "MODIFIED", "UNCHANGED"]


def test_annotate_rows_custom_label_column():
    result = annotate_rows(_rows(), label_column="diff_label")
    assert "diff_label" in result.rows[0]


def test_annotate_rows_custom_label_map():
    lm = {**DEFAULT_LABELS, "added": "NEW"}
    result = annotate_rows(_rows(), label_map=lm)
    assert result.rows[0]["_annotation"] == "NEW"


def test_annotate_rows_missing_status_uses_empty():
    rows = [{"id": "1", "name": "X"}]
    result = annotate_rows(rows)
    assert result.rows[0]["_annotation"] == ""


def test_annotate_rows_preserves_original_columns():
    result = annotate_rows(_rows())
    for row in result.rows:
        assert "id" in row and "name" in row and "_status" in row
