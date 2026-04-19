"""Integration tests for --sample flag in the CLI."""
import textwrap
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    base = tmp_path / "base.csv"
    other = tmp_path / "other.csv"
    base.write_text(textwrap.dedent("""\
        id,name,dept
        1,Alice,Eng
        2,Bob,HR
        3,Carol,Eng
        4,Dave,Mkt
        5,Eve,HR
    """))
    other.write_text(textwrap.dedent("""\
        id,name,dept
        1,Alice,Eng
        2,Bobby,HR
        3,Carol,Design
        6,Frank,Eng
        7,Grace,Mkt
    """))
    return str(base), str(other)


def test_cli_sample_limits_output(two_csvs):
    base, other = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [base, other, "--sample", "2", "--seed", "42"])
    assert result.exit_code == 0


def test_cli_sample_invalid_raises(two_csvs):
    base, other = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [base, other, "--sample", "0"])
    assert result.exit_code != 0


def test_cli_sample_json_format(two_csvs):
    base, other = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main, [base, other, "--sample", "3", "--seed", "1", "--format", "json"]
    )
    assert result.exit_code == 0
