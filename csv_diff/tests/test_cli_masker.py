"""Integration tests for --mask CLI flag."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,email,dept\n1,alice@example.com,Eng\n2,bob@example.com,HR\n")
    b.write_text("id,email,dept\n1,alice@example.com,Eng\n2,bob@new.org,HR\n")
    return str(a), str(b)


def test_cli_mask_hides_email(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--mask", "email:@"])
    assert result.exit_code == 0
    assert "***" in result.output
    assert "alice@example.com" not in result.output


def test_cli_mask_json_format(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--mask", "email:@", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    for section in ("added", "removed", "modified", "unchanged"):
        for row in data.get(section, []):
            assert "alice@example.com" not in str(row)
            assert "bob@example.com" not in str(row)


def test_cli_no_mask_shows_values(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b])
    assert result.exit_code == 0
    assert "alice@example.com" in result.output


def test_cli_mask_invalid_spec_exits(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--mask", "no-colon-here"])
    assert result.exit_code != 0
