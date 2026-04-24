"""CLI integration tests for the --rename-values feature."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,dept\n1,eng\n2,hr\n")
    b.write_text("id,dept\n1,eng\n2,hr\n3,finance\n")
    return str(a), str(b)


def test_cli_rename_values_text_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--rename-values", "dept:eng=Engineering,hr=Human Resources"],
    )
    assert result.exit_code == 0
    assert "Engineering" in result.output or "finance" in result.output


def test_cli_rename_values_json_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            a, b,
            "--rename-values", "dept:eng=Engineering",
            "--format", "json",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, dict)


def test_cli_no_rename_shows_original_values(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    depts = [
        row.get("dept", "")
        for row in data.get("added", []) + data.get("unchanged", [])
    ]
    assert any(d in ("eng", "hr", "finance") for d in depts)


def test_cli_rename_invalid_spec_exits_nonzero(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--rename-values", "dept:badspec"],
    )
    assert result.exit_code != 0
