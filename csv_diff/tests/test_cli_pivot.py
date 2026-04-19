import pytest
from click.testing import CliRunner
from csv_diff.cli import main
import os


@pytest.fixture
def pivot_csv(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    content = "name,metric,value\nAlice,score,90\nAlice,age,30\nBob,score,85\nBob,age,25\n"
    a.write_text(content)
    b.write_text(content)
    return str(a), str(b)


def test_pivot_spec_parsed(pivot_csv):
    """Ensure pivot spec is accepted without error via CLI arg."""
    from csv_diff.pivot import parse_pivot_spec
    row_key, col_key, val_key = parse_pivot_spec("name,metric,value")
    assert row_key == "name"
    assert col_key == "metric"
    assert val_key == "value"


def test_pivot_roundtrip():
    from csv_diff.pivot import pivot_rows, pivot_to_rows
    rows = [
        {"dept": "eng", "kpi": "headcount", "val": "10"},
        {"dept": "eng", "kpi": "budget", "val": "500"},
        {"dept": "hr", "kpi": "headcount", "val": "5"},
    ]
    result = pivot_rows(rows, "dept", "kpi", "val")
    flat = pivot_to_rows(result)
    eng = next(r for r in flat if r["dept"] == "eng")
    assert eng["headcount"] == "10"
    assert eng["budget"] == "500"
    hr = next(r for r in flat if r["dept"] == "hr")
    assert hr["headcount"] == "5"
    assert hr.get("budget", "") == ""
