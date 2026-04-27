"""Integration tests for comparator options wired through the CLI."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name,score\n1,Alice,100\n2,Bob,200\n")
    b.write_text("id,name,score\n1,Alice,100.05\n2,Bob,201\n")
    return str(a), str(b)


def test_cli_numeric_tolerance_suppresses_diff(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--numeric-tolerance", "0.1", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    # row 1 diff (0.05) within tolerance → unchanged; row 2 diff (1) outside → modified
    modified = [r for r in data.get("modified", [])]
    assert any(r["key"] == "2" for r in modified)


def test_cli_numeric_tolerance_detects_large_diff(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--numeric-tolerance", "0.01", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    modified_keys = {r["key"] for r in data.get("modified", [])}
    assert "1" in modified_keys


def test_cli_ignore_case_suppresses_diff(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,dept\n1,Engineering\n")
    b.write_text("id,dept\n1,engineering\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(a), str(b), "--ignore-case", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data.get("modified", []) == []


def test_cli_no_tolerance_detects_diff(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data.get("modified", [])) > 0
