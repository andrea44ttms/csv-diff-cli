"""Integration tests for --bucket-column / --bucket-spec CLI flags."""

import json
import pytest
from click.testing import CliRunner

from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("name,score\nAlice,30\nBob,70\nCarol,90\n")
    new.write_text("name,score\nAlice,45\nBob,70\nCarol,95\n")
    return str(old), str(new)


def test_cli_bucket_shows_section(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            old, new,
            "--bucket-column", "score",
            "--bucket-spec", "low:0:50,high:50:100",
        ],
    )
    assert result.exit_code == 0
    assert "low" in result.output or "high" in result.output


def test_cli_bucket_json_format(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            old, new,
            "--format", "json",
            "--bucket-column", "score",
            "--bucket-spec", "low:0:50,high:50:100",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "buckets" in data


def test_cli_bucket_invalid_spec_exits_nonzero(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            old, new,
            "--bucket-column", "score",
            "--bucket-spec", "bad-spec",
        ],
    )
    assert result.exit_code != 0


def test_cli_no_bucket_flag_hides_section(two_csvs):
    old, new = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [old, new])
    assert result.exit_code == 0
    assert "buckets" not in result.output.lower()
