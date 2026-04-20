"""Integration tests for --alias flag in the CLI."""
import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name,dept\n1,Alice,Eng\n2,Bob,HR\n")
    b.write_text("id,name,dept\n1,Alice,Eng\n2,Robert,HR\n")
    return str(a), str(b)


def test_cli_alias_text_output(two_csvs):
    """Aliased column names appear in text output."""
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--key", "id", "--alias", "name=Full Name"],
    )
    assert result.exit_code == 0, result.output
    assert "Full Name" in result.output


def test_cli_alias_json_output(two_csvs):
    """Aliased column names appear as keys in JSON output."""
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [a, b, "--key", "id", "--alias", "name=Full Name", "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    modified = data.get("modified", [])
    assert any("Full Name" in str(row) for row in modified)


def test_cli_no_alias_shows_original_names(two_csvs):
    """Without --alias the original column names are preserved."""
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id"])
    assert result.exit_code == 0
    assert "name" in result.output
    assert "Full Name" not in result.output
