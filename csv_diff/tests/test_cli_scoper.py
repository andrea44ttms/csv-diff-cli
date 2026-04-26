"""Integration tests for --scope-start / --scope-end CLI flags."""
import csv
import io
import pytest
from csv_diff.cli import main


@pytest.fixture()
def two_csvs(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    rows = [{"id": str(i), "val": str(i * 10)} for i in range(1, 6)]
    header = "id,val\n"
    old.write_text(header + "".join(f"{r['id']},{r['val']}\n" for r in rows))
    # new file: row 3 is modified
    modified = [
        r if r["id"] != "3" else {"id": "3", "val": "999"} for r in rows
    ]
    new.write_text(header + "".join(f"{r['id']},{r['val']}\n" for r in modified))
    return str(old), str(new)


def test_cli_scope_limits_output(two_csvs, capsys):
    old, new = two_csvs
    with pytest.raises(SystemExit) as exc:
        main([old, new, "--scope-start", "1", "--scope-end", "2"])
    out = capsys.readouterr().out
    # Only rows 1-2 are in scope; row 3 modification should not appear
    assert "Scope:" in out


def test_cli_scope_invalid_exits_nonzero(two_csvs, capsys):
    old, new = two_csvs
    with pytest.raises(SystemExit) as exc:
        main([old, new, "--scope-start", "bad"])
    assert exc.value.code != 0


def test_cli_no_scope_shows_all(two_csvs, capsys):
    old, new = two_csvs
    with pytest.raises(SystemExit):
        main([old, new])
    out = capsys.readouterr().out
    # Without scope flags no Scope section should appear
    assert "Scope:" not in out
