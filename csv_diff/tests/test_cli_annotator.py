import json
import pytest
from click.testing import CliRunner
from csv_diff.cli import main


@pytest.fixture
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n2,Bob\n")
    b.write_text("id,name\n1,Alice\n2,Robert\n3,Carol\n")
    return str(a), str(b)


def test_cli_annotate_text_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id", "--annotate"])
    assert result.exit_code == 0
    assert "ADDED" in result.output or "MODIFIED" in result.output


def test_cli_annotate_json_output(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(main, [a, b, "--key", "id", "--annotate", "--format", "json"])
    assert result.exit_code == 0


def test_cli_annotate_custom_labels(two_csvs):
    a, b = two_csvs
    runner = CliRunner()
    result = runner.invoke(
        main, [a, b, "--key", "id", "--annotate", "--annotation-labels", "added=NEW,removed=DEL"]
    )
    assert result.exit_code == 0
