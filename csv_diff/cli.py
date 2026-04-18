"""CLI entry point for csv-diff-cli."""

import argparse
import sys

from csv_diff.parser import load_csv, CSVParseError
from csv_diff.differ import diff_csv, DiffError
from csv_diff.formatter import render, FORMATS


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and highlight differences.",
    )
    p.add_argument("file_a", help="First (original) CSV file")
    p.add_argument("file_b", help="Second (modified) CSV file")
    p.add_argument("-k", "--key", required=True, help="Column to use as row key")
    p.add_argument(
        "-f",
        "--format",
        choices=list(FORMATS),
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument("-d", "--delimiter", default=",", help="CSV delimiter (default: ,)")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = load_csv(args.file_a, delimiter=args.delimiter)
        rows_b = load_csv(args.file_b, delimiter=args.delimiter)
    except CSVParseError as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        return 1

    try:
        result = diff_csv(rows_a, rows_b, key=args.key)
    except DiffError as exc:
        print(f"Diff error: {exc}", file=sys.stderr)
        return 1

    print(render(result, fmt=args.format))
    return 0 if not result.has_diff else 2


if __name__ == "__main__":
    sys.exit(main())
