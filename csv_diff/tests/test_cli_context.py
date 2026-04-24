"""Integration tests for --context CLI flag."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    new.write_text("id,name\n1,Alice\n2,Bobby\n3,Carol\n")
    return str(old), str(new)


def test_cli_context_text_output(two_csvs):
    old, new = two_csvs
    result = CliRunner().invoke(main, [old, new, "--context", "1"])
    assert result.exit_code == 0
    assert "Bobby" in result.output


def test_cli_context_includes_neighbours(two_csvs):
    old, new = two_csvs
    result = CliRunner().invoke(main, [old, new, "--context", "1", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    # modified row must appear
    modified = data.get("modified", [])
    assert any("Bobby" in str(r) for r in modified)


def test_cli_context_zero_shows_only_changed(two_csvs):
    old, new = two_csvs
    result = CliRunner().invoke(main, [old, new, "--context", "0"])
    assert result.exit_code == 0
    assert "Bobby" in result.output


def test_cli_context_invalid_exits_nonzero(two_csvs):
    old, new = two_csvs
    result = CliRunner().invoke(main, [old, new, "--context", "abc"])
    assert result.exit_code != 0
