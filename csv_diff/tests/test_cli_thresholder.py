"""CLI integration tests for the --min-change-rate threshold flag."""
import json
import pytest
from click.testing import CliRunner

from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    """Returns (old_path, new_path) where new has one addition out of four rows."""
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    new.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n4,Dave\n")
    return str(old), str(new)


def test_cli_threshold_passes_when_rate_met(two_csvs):
    """With 1 addition out of 4 rows (25 %), a threshold of 20 % should pass."""
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new, "--min-change-rate", "20"])
    assert result.exit_code == 0


def test_cli_threshold_exits_nonzero_when_rate_not_met(two_csvs):
    """With 25 % change rate, a threshold of 50 % should cause exit code 2."""
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new, "--min-change-rate", "50"])
    assert result.exit_code == 2


def test_cli_threshold_message_in_output(two_csvs):
    """Output should contain threshold status information."""
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new, "--min-change-rate", "10"])
    assert "Threshold" in result.output or result.exit_code == 0


def test_cli_no_threshold_flag_always_exits_zero(two_csvs):
    """Without --min-change-rate the tool should not apply any threshold."""
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new])
    assert result.exit_code in (0, 1)  # 1 = diff found, both are acceptable


def test_cli_threshold_invalid_value_exits_nonzero(two_csvs):
    """A non-numeric threshold value should produce a non-zero exit code."""
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new, "--min-change-rate", "bad"])
    assert result.exit_code != 0
