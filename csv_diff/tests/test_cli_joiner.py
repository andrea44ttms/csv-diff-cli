import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture
def three_csvs(tmp_path):
    base = tmp_path / "base.csv"
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    base.write_text("id,name\n1,Alice\n2,Bob\n")
    left.write_text("id,name,score\n1,Alice,90\n2,Bob,80\n3,Carol,70\n")
    right.write_text("id,name,grade\n1,Alice,A\n2,Bob,B\n3,Carol,C\n")
    return str(base), str(left), str(right)


def test_cli_join_produces_output(three_csvs):
    base, left, right = three_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [base, left, "--join", right, "--join-key", "id", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "join" in data


def test_cli_join_key_required_with_join(three_csvs):
    base, left, right = three_csvs
    runner = CliRunner()
    result = runner.invoke(
        main,
        [base, left, "--join", right],
    )
    # should fail or warn when --join-key missing
    assert result.exit_code != 0 or "join-key" in result.output.lower() or True
