"""Command-line interface for csv-diff-cli."""
from __future__ import annotations
import argparse
import sys

from csv_diff.parser import load_csv, CSVParseError
from csv_diff.differ import diff_csv, DiffError
from csv_diff.formatter import render
from csv_diff.filter import parse_filter, apply_filter, FilterError
from csv_diff.stats import compute_stats, format_stats
from csv_diff.merger import merge_diffs
from csv_diff.sampler import parse_sample_size, sample_diff, SampleError
from csv_diff.pivot import parse_pivot_spec, pivot_to_rows, PivotError
from csv_diff.aggregator import parse_group_by, aggregate, AggregateError
from csv_diff.annotator import parse_label_map, annotate_rows
from csv_diff.scorer import compute_score, format_score


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csv-diff", description="Compare two CSV files.")
    p.add_argument("file_a", help="First CSV file")
    p.add_argument("file_b", help="Second CSV file")
    p.add_argument("--key", default="id", help="Column to use as row key")
    p.add_argument("--delimiter", default=",", help="CSV delimiter")
    p.add_argument("--format", dest="fmt", choices=["text", "json", "summary"], default="text")
    p.add_argument("--filter", dest="filter_expr", default=None, help="Filter expression col=val")
    p.add_argument("--stats", action="store_true", help="Show diff statistics")
    p.add_argument("--merge", default=None, help="Third CSV to merge with")
    p.add_argument("--sample", default=None, help="Limit diff output to N rows")
    p.add_argument("--pivot", default=None, help="Pivot spec: col=value_col")
    p.add_argument("--group-by", dest="group_by", default=None, help="Column to group aggregates by")
    p.add_argument("--annotate", default=None, help="Custom status labels added=X,removed=Y,modified=Z")
    p.add_argument("--score", action="store_true", help="Show similarity score")
    return p


def main(args=None):
    parser = build_parser()
    ns = parser.parse_args(args)

    try:
        rows_a = load_csv(ns.file_a, delimiter=ns.delimiter)
        rows_b = load_csv(ns.file_b, delimiter=ns.delimiter)
    except CSVParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if ns.filter_expr:
        try:
            f = parse_filter(ns.filter_expr)
            rows_a = apply_filter(rows_a, f)
            rows_b = apply_filter(rows_b, f)
        except FilterError as e:
            print(f"Filter error: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        result = diff_csv(rows_a, rows_b, key=ns.key)
    except DiffError as e:
        print(f"Diff error: {e}", file=sys.stderr)
        sys.exit(1)

    if ns.merge:
        try:
            rows_c = load_csv(ns.merge, delimiter=ns.delimiter)
            result2 = diff_csv(rows_a, rows_c, key=ns.key)
            result = merge_diffs(result, result2)
        except Exception as e:
            print(f"Merge error: {e}", file=sys.stderr)
            sys.exit(1)

    if ns.sample:
        try:
            n = parse_sample_size(ns.sample)
            result = sample_diff(result, n)
        except SampleError as e:
            print(f"Sample error: {e}", file=sys.stderr)
            sys.exit(1)

    if ns.annotate:
        label_map = parse_label_map(ns.annotate)
        annotated = annotate_rows(result)
        for row in annotated:
            row["_status"] = label_map.get(row["_status"], row["_status"])

    if ns.pivot:
        try:
            spec = parse_pivot_spec(ns.pivot)
            rows = pivot_to_rows(result, spec)
            for r in rows:
                print(r)
            return
        except PivotError as e:
            print(f"Pivot error: {e}", file=sys.stderr)
            sys.exit(1)

    if ns.group_by:
        try:
            key_col = parse_group_by(ns.group_by)
            agg = aggregate(result, key_col)
            for group, stats in agg.groups.items():
                print(f"{group}: +{stats.added} -{stats.removed} ~{stats.modified} ={stats.unchanged}")
            return
        except AggregateError as e:
            print(f"Aggregate error: {e}", file=sys.stderr)
            sys.exit(1)

    print(render(result, fmt=ns.fmt))

    if ns.stats:
        print(format_stats(compute_stats(result)))

    if ns.score:
        print(format_score(compute_score(result)))
