import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture
def three_csvs(tmp_path):
    base = tmp_path / "base.csv"
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    base.write_text("id,name,dept\n1,Alice,Eng\n2,Bob,HR\n")
    left.write_text("id,name,dept\n1,Alice,Finance\n2,Bob,HR\n")
    right.write_text("id,name,dept\n1,Alice,Eng\n2,Bob,Marketing\n3,Carol,Eng\n")
    return str(base), str(left), str(right)


def test_cli_merge_produces_output(three_csvs):
    base, left, right = three_csvs
    runner = CliRunner()
    result = runner.invoke(main, [left, right])
    assert result.exit_code == 0


def test_cli_json_format(three_csvs):
    base, left, right = three_csvs
    runner = CliRunner()
    result = runner.invoke(main, [left, right, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "added" in data
    assert "modified" in data
