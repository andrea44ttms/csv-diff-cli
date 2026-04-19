import pytest
from click.testing import CliRunner
from csv_diff.cli import main
import textwrap


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text(textwrap.dedent("""\
        name,email,dept
        Alice,alice@example.com,Eng
        Bob,bob@example.com,HR
    """))
    b.write_text(textwrap.dedent("""\
        name,email,dept
        Alice,alice@example.com,Eng
        Bob,bob2@example.com,HR
    """))
    return str(a), str(b)


def test_cli_redact_masks_column(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--redact", "email"])
    assert result.exit_code == 0
    assert "***" in result.output
    assert "bob@example.com" not in result.output
    assert "bob2@example.com" not in result.output


def test_cli_redact_json_format(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--redact", "email", "--format", "json"])
    assert result.exit_code == 0
    assert "***" in result.output


def test_cli_no_redact_shows_values(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b])
    assert result.exit_code == 0
    assert "bob2@example.com" in result.output
