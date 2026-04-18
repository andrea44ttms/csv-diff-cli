"""Integration tests: CLI --stats flag."""
import pytest
from click.testing import CliRunner
from csv_diff.cli import main
import os


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name,dept\n1,Alice,Eng\n2,Bob,HR\n3,Carol,Eng\n")
    b.write_text("id,name,dept\n1,Alicia,Eng\n2,Bob,HR\n4,Dave,Ops\n")
    return str(a), str(b)


def test_cli_stats_flag_present(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id", "--stats"])
    assert result.exit_code == 0
    assert "Diff Statistics" in result.output
    assert "Added:" in result.output
    assert "Removed:" in result.output
    assert "Modified:" in result.output


def test_cli_stats_shows_change_rate(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id", "--stats"])
    assert "Change rate:" in result.output


def test_cli_no_stats_flag_hides_section(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id"])
    assert "Diff Statistics" not in result.output
