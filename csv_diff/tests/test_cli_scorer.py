import pytest
from click.testing import CliRunner
from csv_diff.cli import main
import os


@pytest.fixture
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    b.write_text("id,name\n1,Alice\n2,Robert\n4,Dave\n")
    return str(a), str(b)


def test_cli_score_flag_present(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--score"])
    assert result.exit_code == 0
    assert "Similarity Score" in result.output


def test_cli_score_shows_percentage(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--score"])
    assert "%" in result.output


def test_cli_no_score_flag_hides_section(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b])
    assert "Similarity Score" not in result.output
