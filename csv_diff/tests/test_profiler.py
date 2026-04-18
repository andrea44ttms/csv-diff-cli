import pytest
from csv_diff.profiler import (
    profile_rows, format_profile, ProfileError, ColumnProfile, ProfileResult
)

HEADERS = ["name", "dept", "salary"]

ROWS = [
    {"name": "Alice", "dept": "Eng", "salary": "90000"},
    {"name": "Bob",   "dept": "Eng", "salary": ""},
    {"name": "Carol", "dept": "HR",  "salary": "70000"},
    {"name": "Dave",  "dept": "Eng", "salary": "80000"},
    {"name": "",      "dept": "HR",  "salary": "60000"},
]


def test_profile_basic_totals():
    result = profile_rows(HEADERS, ROWS)
    assert result.columns["name"].total == 5
    assert result.columns["salary"].total == 5


def test_profile_empty_count():
    result = profile_rows(HEADERS, ROWS)
    assert result.columns["name"].empty == 1
    assert result.columns["salary"].empty == 1
    assert result.columns["dept"].empty == 0


def test_profile_unique_values():
    result = profile_rows(HEADERS, ROWS)
    assert result.columns["dept"].unique_values == 2
    assert result.columns["name"].unique_values == 5  # includes ""


def test_profile_top_values():
    result = profile_rows(HEADERS, ROWS)
    top = result.columns["dept"].top_values
    assert top["Eng"] == 3
    assert top["HR"] == 2


def test_profile_fill_rate():
    result = profile_rows(HEADERS, ROWS)
    assert result.columns["salary"].fill_rate == 0.8
    assert result.columns["dept"].fill_rate == 1.0


def test_profile_fill_rate_zero_rows():
    cp = ColumnProfile(name="x", total=0)
    assert cp.fill_rate == 0.0


def test_profile_empty_rows():
    result = profile_rows(HEADERS, [])
    for h in HEADERS:
        assert result.columns[h].total == 0


def test_profile_no_headers_raises():
    with pytest.raises(ProfileError):
        profile_rows([], ROWS)


def test_profile_top_n_limit():
    rows = [{"v": str(i)} for i in range(20)]
    result = profile_rows(["v"], rows, top_n=3)
    assert len(result.columns["v"].top_values) == 3


def test_format_profile_contains_column_name():
    result = profile_rows(HEADERS, ROWS)
    output = format_profile(result)
    assert "dept" in output
    assert "fill_rate" in output
    assert "top:" in output
