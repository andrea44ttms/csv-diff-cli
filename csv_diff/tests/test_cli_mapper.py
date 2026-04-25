"""Integration tests for --map-values CLI flag."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name,dept\n1,Alice,E\n2,Bob,S\n")
    b.write_text("id,name,dept\n1,Alice,E\n2,Bob,M\n")
    return str(a), str(b)


def test_cli_map_values_text_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--key", "id", "--map-values", "dept:E=Engineering,S=Sales,M=Marketing"],
    )
    assert result.exit_code == 0
    assert "Engineering" in result.output
    assert "Marketing" in result.output


def test_cli_map_values_json_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            a, b,
            "--key", "id",
            "--format", "json",
            "--map-values", "dept:E=Engineering,M=Marketing",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    modified = data.get("modified", [])
    assert any(
        "Marketing" in str(row) or "Engineering" in str(row)
        for row in modified
    )


def test_cli_no_map_shows_original_values(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id"])
    assert result.exit_code == 0
    assert "E" in result.output or "M" in result.output


def test_cli_map_invalid_spec_exits_nonzero(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--key", "id", "--map-values", "dept_no_colon"],
    )
    assert result.exit_code != 0
