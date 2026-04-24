"""Integration tests for --group-by CLI flag (grouper feature)."""
import json
import textwrap

import pytest
from click.testing import CliRunner

from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text(
        textwrap.dedent("""\
            dept,name,salary
            eng,Alice,80
            hr,Bob,70
            eng,Carol,90
        """)
    )
    b.write_text(
        textwrap.dedent("""\
            dept,name,salary
            eng,Alice,85
            hr,Bob,70
            eng,Dave,95
        """)
    )
    return str(a), str(b)


def test_cli_group_by_shows_groups(two_csvs):
    a, b = two_csvs
    result = CliRunner().invoke(main, [a, b, "--group-by", "dept"])
    assert result.exit_code == 0
    assert "eng" in result.output
    assert "hr" in result.output


def test_cli_group_by_summary_totals(two_csvs):
    a, b = two_csvs
    result = CliRunner().invoke(main, [a, b, "--group-by", "dept"])
    assert result.exit_code == 0
    assert "Grouped by" in result.output


def test_cli_no_group_by_no_group_section(two_csvs):
    a, b = two_csvs
    result = CliRunner().invoke(main, [a, b])
    assert "Grouped by" not in result.output
