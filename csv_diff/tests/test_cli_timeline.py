"""Integration tests for the --timeline CLI feature."""
import json
import pytest
from click.testing import CliRunner

from csv_diff.cli import main


@pytest.fixture()
def three_csvs(tmp_path):
    base = tmp_path / "base.csv"
    v1 = tmp_path / "v1.csv"
    v2 = tmp_path / "v2.csv"
    base.write_text("id,name\n1,Alice\n2,Bob\n")
    v1.write_text("id,name\n1,Alice\n2,Bobby\n")
    v2.write_text("id,name\n1,Alice\n2,Bobby\n3,Carol\n")
    return str(base), str(v1), str(v2)


def test_cli_timeline_text_output(three_csvs):
    base, v1, _ = three_csvs
    runner = CliRunner()
    result = runner.invoke(main, [base, v1, "--timeline"])
    assert result.exit_code == 0
    assert "Timeline" in result.output


def test_cli_timeline_shows_snapshot_label(three_csvs):
    base, v1, _ = three_csvs
    runner = CliRunner()
    result = runner.invoke(main, [base, v1, "--timeline", "--timeline-label", "release-1"])
    assert result.exit_code == 0
    assert "release-1" in result.output


def test_cli_no_timeline_flag_hides_section(three_csvs):
    base, v1, _ = three_csvs
    runner = CliRunner()
    result = runner.invoke(main, [base, v1])
    assert result.exit_code == 0
    assert "Timeline" not in result.output
