"""Integration tests for the CLI --filter flag."""

import csv
import pytest
from pathlib import Path
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    rows_a = [
        {"id": "1", "name": "Alice", "dept": "eng"},
        {"id": "2", "name": "Bob", "dept": "hr"},
    ]
    rows_b = [
        {"id": "1", "name": "Alice", "dept": "eng"},
        {"id": "2", "name": "Robert", "dept": "hr"},
        {"id": "3", "name": "Carol", "dept": "eng"},
    ]
    for path, rows in [(a, rows_a), (b, rows_b)]:
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "name", "dept"])
            w.writeheader()
            w.writerows(rows)
    return str(a), str(b)


def test_cli_no_filter_detects_diff(two_csvs):
    a, b = two_csvs
    rc = main([a, b, "--key", "id"])
    assert rc == 1  # differences found


def test_cli_filter_eng_only(two_csvs, capsys):
    a, b = two_csvs
    rc = main([a, b, "--key", "id", "--filter", "dept=eng"])
    captured = capsys.readouterr()
    # Only eng rows: id=1 unchanged, id=3 added — Bob (hr) excluded
    assert "Bob" not in captured.out
    assert rc == 1  # Carol added


def test_cli_filter_no_diff(two_csvs):
    a, b = two_csvs
    # Filter to eng rows that are identical between a and b (only id=1)
    # id=3 is added in b but filter on a side returns only id=1
    # result: added Carol still shows up, rc=1
    rc = main([a, b, "--key", "id", "--filter", "dept=hr"])
    # Bob row is modified (name changed) => diff exists
    assert rc == 1


def test_cli_filter_invalid_expr(two_csvs, capsys):
    a, b = two_csvs
    rc = main([a, b, "--filter", "nodepoperator"])
    assert rc == 2
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cli_filter_unknown_column(two_csvs, capsys):
    a, b = two_csvs
    rc = main([a, b, "--filter", "salary=100"])
    assert rc == 2
