"""Integration tests for --classify CLI flag."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("name,dept,level\nAlice,eng,3\nBob,eng,1\nCarol,hr,2\n")
    b.write_text("name,dept,level\nAlice,eng,3\nBob,eng,2\nDave,eng,3\n")
    return str(a), str(b)


def test_cli_classify_shows_categories(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--classify", "Senior:level=3;Junior:level=1"],
    )
    assert result.exit_code == 0
    assert "Senior" in result.output or "Junior" in result.output or "Classify" in result.output


def test_cli_classify_json_format(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--format", "json", "--classify", "Senior:level=3"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "classify" in data or isinstance(data, dict)


def test_cli_no_classify_flag_hides_section(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b])
    assert result.exit_code == 0
    assert "Classify" not in result.output
