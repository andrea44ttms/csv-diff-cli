"""CLI integration tests for the --segment feature."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    new.write_text("id,name\n1,Alice\n2,Bobby\n4,Dave\n")
    return str(old), str(new)


def test_cli_segment_text_output(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [old, new, "--key", "id", "--segment", "top:1-2,bottom:3-4"],
    )
    assert result.exit_code == 0
    assert "top" in result.output or "bottom" in result.output or "Segment" in result.output


def test_cli_segment_json_format(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [old, new, "--key", "id", "--format", "json", "--segment", "all:1-10"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, dict)


def test_cli_no_segment_flag_hides_section(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new, "--key", "id"])
    assert result.exit_code == 0
    assert "Segment" not in result.output


def test_cli_segment_invalid_spec_exits_nonzero(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [old, new, "--key", "id", "--segment", "bad_spec"],
    )
    assert result.exit_code != 0
