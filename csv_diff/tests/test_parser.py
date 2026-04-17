"""Tests for csv_diff.parser module."""

import pytest
from pathlib import Path

from csv_diff.parser import load_csv, get_headers, CSVParseError


@pytest.fixture
def tmp_csv(tmp_path):
    """Factory fixture that writes a CSV file and returns its path."""
    def _make(content: str, name: str = "test.csv") -> str:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _make


def test_load_csv_basic(tmp_csv):
    path = tmp_csv("id,name,age\n1,Alice,30\n2,Bob,25\n")
    rows = load_csv(path)
    assert len(rows) == 2
    assert rows[0] == {"id": "1", "name": "Alice", "age": "30"}
    assert rows[1] == {"id": "2", "name": "Bob", "age": "25"}


def test_load_csv_custom_delimiter(tmp_csv):
    path = tmp_csv("id;name\n1;Alice\n", name="semi.csv")
    rows = load_csv(path, delimiter=";")
    assert rows[0]["name"] == "Alice"


def test_load_csv_empty_rows(tmp_csv):
    path = tmp_csv("id,name\n")
    rows = load_csv(path)
    assert rows == []


def test_load_csv_file_not_found():
    with pytest.raises(CSVParseError, match="File not found"):
        load_csv("/nonexistent/path/file.csv")


def test_load_csv_not_a_file(tmp_path):
    with pytest.raises(CSVParseError, match="Not a file"):
        load_csv(str(tmp_path))


def test_load_csv_encoding_error(tmp_path):
    p = tmp_path / "latin.csv"
    p.write_bytes(b"id,name\n1,Caf\xe9\n")  # latin-1 byte in utf-8 context
    with pytest.raises(CSVParseError, match="Encoding error"):
        load_csv(str(p), encoding="utf-8")


def test_get_headers(tmp_csv):
    path = tmp_csv("id,name,score\n1,Alice,99\n")
    headers = get_headers(path)
    assert headers == ["id", "name", "score"]


def test_get_headers_empty_file(tmp_csv):
    path = tmp_csv("")
    headers = get_headers(path)
    assert headers is None
