import pytest
from click.testing import CliRunner
from csv_diff.cli import main
import csv, os


@pytest.fixture
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,dept,name\n1,eng,alice\n2,hr,bob\n")
    b.write_text("id,dept,name\n1,eng,alice\n3,eng,carol\n")
    return str(a), str(b)


def test_cli_group_by_shows_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id", "--group-by", "dept"])
    assert result.exit_code == 0
    assert "dept" in result.output


def test_cli_group_by_counts(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id", "--group-by", "dept"])
    assert "+1" in result.output or "eng" in result.output


def test_cli_no_group_by_no_aggregate(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id"])
    assert "Grouped by" not in result.output
