"""Tests for csv_diff.labeler."""
import pytest

from csv_diff.differ import DiffResult
from csv_diff.labeler import (
    LabelError,
    LabelResult,
    LabeledRow,
    label_rows,
    parse_severity_map,
)


def _result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[], headers=["id", "name"])
    defaults.update(kwargs)
    return DiffResult(**defaults)


# --- parse_severity_map ---

def test_parse_severity_map_defaults():
    m = parse_severity_map(None)
    assert m["added"] == "info"
    assert m["removed"] == "warning"


def test_parse_severity_map_custom():
    m = parse_severity_map("added=critical,removed=high")
    assert m["added"] == "critical"
    assert m["removed"] == "high"
    # unchanged keys keep defaults
    assert m["modified"] == "notice"


def test_parse_severity_map_invalid_format():
    with pytest.raises(LabelError, match="Invalid severity spec"):
        parse_severity_map("addedcritical")


def test_parse_severity_map_unknown_key():
    with pytest.raises(LabelError, match="Unknown status"):
        parse_severity_map("deleted=critical")


def test_parse_severity_map_empty_value_raises():
    with pytest.raises(LabelError, match="must not be empty"):
        parse_severity_map("added=")


# --- label_rows ---

def test_label_rows_added():
    r = _result(added=[{"id": "1", "name": "Alice"}])
    lr = label_rows(r)
    assert len(lr.labeled) == 1
    assert lr.labeled[0].status == "added"
    assert lr.labeled[0].severity == "info"


def test_label_rows_removed():
    r = _result(removed=[{"id": "2", "name": "Bob"}])
    lr = label_rows(r)
    assert lr.labeled[0].status == "removed"
    assert lr.labeled[0].severity == "warning"


def test_label_rows_modified():
    r = _result(modified=[{"row": {"id": "3", "name": "Carol"}, "diff": {}}])
    lr = label_rows(r)
    assert lr.labeled[0].status == "modified"
    assert lr.labeled[0].severity == "notice"


def test_label_rows_unchanged():
    r = _result(unchanged=[{"id": "4", "name": "Dave"}])
    lr = label_rows(r)
    assert lr.labeled[0].status == "unchanged"
    assert lr.labeled[0].severity == "ok"


def test_label_rows_custom_severity_map():
    r = _result(added=[{"id": "5", "name": "Eve"}])
    smap = parse_severity_map("added=critical")
    lr = label_rows(r, severity_map=smap)
    assert lr.labeled[0].severity == "critical"


def test_label_rows_empty_result():
    r = _result()
    lr = label_rows(r)
    assert lr.labeled == []
