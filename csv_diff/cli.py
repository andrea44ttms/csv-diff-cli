"""CLI entry point for csv-diff."""
from __future__ import annotations
import argparse
import sys

from .parser import load_csv, CSVParseError
from .differ import diff_csv, DiffError
from .formatter import render
from .filter import parse_filter, apply_filter, FilterError
from .stats import compute_stats, format_stats
from .transformer import parse_columns, parse_rename, apply_transforms, TransformError
from .patcher import patch_rows, patch_to_csv_lines, PatchError
from .exporter import export, ExportError
from .merger import merge_diffs, MergeError
from .sampler import parse_sample_size, sample_diff, SampleError
from .pivot import parse_pivot_spec, pivot_rows, pivot_to_rows, PivotError
from .aggregator import parse_group_by, aggregate_diff, format_aggregate, AggregateError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csv-diff", description="Compare two CSV files")
    p.add_argument("file_a")
    p.add_argument("file_b")
    p.add_argument("--key", default="id")
    p.add_argument("--delimiter", default=",")
    p.add_argument("--format", choices=["text", "json", "summary"], default="text")
    p.add_argument("--filter", dest="filter_expr", default=None)
    p.add_argument("--stats", action="store_true")
    p.add_argument("--select", default=None)
    p.add_argument("--rename", default=None)
    p.add_argument("--patch", action="store_true")
    p.add_argument("--export", dest="export_path", default=None)
    p.add_argument("--merge", dest="file_c", default=None)
    p.add_argument("--sample", default=None)
    p.add_argument("--pivot", default=None)
    p.add_argument("--group-by", dest="group_by", default=None)
    return p


def main(args=None):
    parser = build_parser()
    ns = parser.parse_args(args)

    try:
        rows_a = load_csv(ns.file_a, delimiter=ns.delimiter)
        rows_b = load_csv(ns.file_b, delimiter=ns.delimiter)

        if ns.filter_expr:
            f = parse_filter(ns.filter_expr)
            rows_a = apply_filter(rows_a, f)
            rows_b = apply_filter(rows_b, f)

        if ns.select:
            cols = parse_columns(ns.select)
            renames = parse_rename(ns.rename) if ns.rename else {}
            rows_a = apply_transforms(rows_a, cols, renames)
            rows_b = apply_transforms(rows_b, cols, renames)

        if ns.pivot:
            spec = parse_pivot_spec(ns.pivot)
            rows_a = pivot_to_rows(pivot_rows(rows_a, spec))
            rows_b = pivot_to_rows(pivot_rows(rows_b, spec))

        result = diff_csv(rows_a, rows_b, key=ns.key)

        if ns.file_c:
            rows_c = load_csv(ns.file_c, delimiter=ns.delimiter)
            result2 = diff_csv(rows_a, rows_c, key=ns.key)
            result = merge_diffs(result, result2)

        if ns.sample:
            n = parse_sample_size(ns.sample)
            result = sample_diff(result, n)

        if ns.patch:
            lines = patch_to_csv_lines(patch_rows(rows_a, result))
            print("\n".join(lines))
            return

        if ns.export_path:
            export(result, ns.export_path)

        print(render(result, fmt=ns.format))

        if ns.stats:
            print(format_stats(compute_stats(result)))

        if ns.group_by:
            col = parse_group_by(ns.group_by)
            agg = aggregate_diff(result, col)
            print(format_aggregate(agg))

    except (CSVParseError, DiffError, FilterError, TransformError,
            PatchError, ExportError, MergeError, SampleError,
            PivotError, AggregateError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
