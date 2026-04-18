"""Command-line interface for csv-diff-cli."""

import sys
import argparse

from csv_diff.parser import load_csv, CSVParseError
from csv_diff.differ import diff_csv, DiffError
from csv_diff.formatter import render
from csv_diff.filter import filter_rows, FilterError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and highlight differences.",
    )
    p.add_argument("file_a", help="First (original) CSV file")
    p.add_argument("file_b", help="Second (modified) CSV file")
    p.add_argument(
        "--key",
        default=None,
        help="Column name to use as unique row key",
    )
    p.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter character (default: ',')",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--filter",
        dest="filter_expr",
        default=None,
        metavar="EXPR",
        help="Filter rows before diffing, e.g. 'status=active' or 'dept!=hr'",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = load_csv(args.file_a, delimiter=args.delimiter)
        rows_b = load_csv(args.file_b, delimiter=args.delimiter)

        rows_a = filter_rows(rows_a, args.filter_expr)
        rows_b = filter_rows(rows_b, args.filter_expr)

        result = diff_csv(rows_a, rows_b, key=args.key)
        print(render(result, fmt=args.fmt))
        return 0 if not result.has_diff else 1

    except (CSVParseError, DiffError, FilterError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
