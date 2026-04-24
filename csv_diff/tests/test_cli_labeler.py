"""CLI integration tests for --severity-map / labeler feature."""
import json
import textwrap

import pytest

from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text(textwrap.dedent("""\
        id,dept,salary
        1,Engineering,90000
        2,Marketing,70000
    """))
    new.write_text(textwrap.dedent("""\
        id,dept,salary
        1,Engineering,95000
        3,Sales,60000
    """))
    return str(old), str(new)


def test_cli_severity_map_json_output(two_csvs, capsys):
    old, new = two_csvs
    with pytest.raises(SystemExit) as exc:
        main([old, new, "--format", "json", "--severity-map", "added=critical,removed=high"])
    assert exc.value.code == 1
    out = json.loads(capsys.readouterr().out)
    # JSON output should still contain diff sections
    assert "added" in out or "removed" in out or "modified" in out


def test_cli_severity_map_no_diff_exits_zero(tmp_path, capsys):
    f = tmp_path / "same.csv"
    f.write_text("id,name\n1,Alice\n")
    with pytest.raises(SystemExit) as exc:
        main([str(f), str(f), "--severity-map", "added=critical"])
    assert exc.value.code == 0


def test_cli_severity_map_invalid_exits_nonzero(two_csvs, capsys):
    old, new = two_csvs
    with pytest.raises(SystemExit) as exc:
        main([old, new, "--severity-map", "badkey=critical"])
    assert exc.value.code != 0
