"""CLI integration tests for the --enrich-* flags."""
import json
import textwrap
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture()
def three_csvs(tmp_path):
    base = tmp_path / "base.csv"
    other = tmp_path / "other.csv"
    lookup = tmp_path / "lookup.csv"

    base.write_text(textwrap.dedent("""\
        id,name
        1,Alice
        2,Bob
    """))
    other.write_text(textwrap.dedent("""\
        id,name
        1,Alice
        3,Carol
    """))
    lookup.write_text(textwrap.dedent("""\
        id,dept,level
        1,Eng,L3
        2,HR,L2
        3,Eng,L5
    """))
    return str(base), str(other), str(lookup)


def test_cli_enrich_adds_column(three_csvs):
    base, other, lookup = three_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [base, other, "--enrich-file", lookup, "--enrich-key", "id",
         "--enrich-cols", "dept", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    all_rows = data.get("added", []) + data.get("removed", [])
    assert any("dept" in r for r in all_rows)


def test_cli_enrich_correct_value(three_csvs):
    base, other, lookup = three_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [base, other, "--enrich-file", lookup, "--enrich-key", "id",
         "--enrich-cols", "dept", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    removed = {r["id"]: r for r in data.get("removed", [])}
    assert removed["2"]["dept"] == "HR"


def test_cli_enrich_missing_key_exits_nonzero(three_csvs):
    base, other, lookup = three_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [base, other, "--enrich-file", lookup, "--enrich-cols", "dept",
         "--format", "json"],
    )
    # missing --enrich-key when --enrich-file provided should fail
    assert result.exit_code != 0
