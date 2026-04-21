"""cli.py – command-line entry point for csv-diff-cli."""
from __future__ import annotations

import sys
import argparse
from typing import Optional

from csv_diff.parser import load_csv, get_headers, CSVParseError
from csv_diff.differ import diff_csv, DiffError
from csv_diff.formatter import render
from csv_diff.filter import parse_filter, apply_filter, FilterError
from csv_diff.sorter import parse_sort_keys, sort_rows, SortError
from csv_diff.stats import compute_stats, format_stats
from csv_diff.transformer import parse_columns, parse_rename, apply_transforms, TransformError
from csv_diff.patcher import patch_rows, patch_to_csv_lines, PatchError
from csv_diff.exporter import export, ExportError
from csv_diff.merger import merge_diffs, MergeError
from csv_diff.validator import parse_rules, validate_rows, ValidationError
from csv_diff.profiler import profile_rows, ProfileError
from csv_diff.sampler import parse_sample_size, sample_diff, SampleError
from csv_diff.highlighter import highlight_rows, HighlightError
from csv_diff.pivot import parse_pivot_spec, pivot_to_rows, PivotError
from csv_diff.aggregator import parse_group_by, aggregate, AggregateError
from csv_diff.deduplicator import parse_key_columns, deduplicate_rows, DeduplicateError
from csv_diff.annotator import parse_label_map, annotate_rows, AnnotateError
from csv_diff.truncator import parse_max_rows, truncate_diff, TruncateError
from csv_diff.normalizer import parse_normalize_options, normalize_rows, NormalizeError
from csv_diff.scorer import compute_score, format_score
from csv_diff.joiner import parse_join_key, join_diff_rows, JoinError
from csv_diff.lineage import build as build_lineage, parse_lineage_flag, LineageError
from csv_diff.redactor import parse_redact_columns, redact_rows, RedactError
from csv_diff.chunker import parse_chunk_size, chunk_diff, ChunkError
from csv_diff.aliaser import parse_alias_map, alias_rows, AliasError
from csv_diff.masker import parse_mask_spec, mask_rows, MaskError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and highlight differences.",
    )
    p.add_argument("file_a", help="First (base) CSV file")
    p.add_argument("file_b", help="Second (new) CSV file")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    p.add_argument("--key", default=None, help="Column to use as row key")
    p.add_argument(
        "--format", dest="fmt", choices=["text", "json", "summary"], default="text"
    )
    p.add_argument("--filter", dest="filter_expr", default=None)
    p.add_argument("--sort", dest="sort_keys", default=None)
    p.add_argument("--stats", action="store_true")
    p.add_argument("--select", dest="select_cols", default=None)
    p.add_argument("--rename", dest="rename_cols", default=None)
    p.add_argument("--patch", dest="patch_out", default=None)
    p.add_argument("--export", dest="export_out", default=None)
    p.add_argument("--export-format", dest="export_fmt", choices=["csv", "json", "jsonl"], default="csv")
    p.add_argument("--merge", dest="merge_file", default=None)
    p.add_argument("--validate", dest="validate_rules", default=None)
    p.add_argument("--profile", action="store_true")
    p.add_argument("--sample", dest="sample_size", default=None)
    p.add_argument("--highlight", action="store_true")
    p.add_argument("--pivot", dest="pivot_spec", default=None)
    p.add_argument("--group-by", dest="group_by", default=None)
    p.add_argument("--dedup", dest="dedup_keys", default=None)
    p.add_argument("--annotate", dest="label_map", default=None)
    p.add_argument("--max-rows", dest="max_rows", default=None)
    p.add_argument("--normalize", dest="normalize_opts", default=None)
    p.add_argument("--score", action="store_true")
    p.add_argument("--join", dest="join_file", default=None)
    p.add_argument("--join-key", dest="join_key", default=None)
    p.add_argument("--lineage", dest="lineage_flag", default=None)
    p.add_argument("--redact", dest="redact_cols", default=None)
    p.add_argument("--chunk-size", dest="chunk_size", default=None)
    p.add_argument("--alias", dest="alias_map", default=None)
    p.add_argument("--mask", dest="mask_spec", default=None)
    return p


def main(args=None):
    """Entry point; returns exit code."""
    parser = build_parser()
    ns = parser.parse_args(args)

    try:
        rows_a = load_csv(ns.file_a, delimiter=ns.delimiter)
        rows_b = load_csv(ns.file_b, delimiter=ns.delimiter)
        headers = get_headers(ns.file_a, delimiter=ns.delimiter)

        # --normalize
        if ns.normalize_opts:
            opts = parse_normalize_options(ns.normalize_opts)
            rows_a = normalize_rows(rows_a, opts)
            rows_b = normalize_rows(rows_b, opts)

        # --select / --rename
        if ns.select_cols:
            cols = parse_columns(ns.select_cols)
            rows_a = apply_transforms(rows_a, cols, {})
            rows_b = apply_transforms(rows_b, cols, {})
            headers = cols
        if ns.rename_cols:
            rmap = parse_rename(ns.rename_cols)
            rows_a = apply_transforms(rows_a, list(headers), rmap)
            rows_b = apply_transforms(rows_b, list(headers), rmap)

        # --filter
        if ns.filter_expr:
            col, val = parse_filter(ns.filter_expr)
            rows_a = apply_filter(rows_a, col, val)
            rows_b = apply_filter(rows_b, col, val)

        # --sort
        if ns.sort_keys:
            keys = parse_sort_keys(ns.sort_keys)
            rows_a = sort_rows(rows_a, keys)
            rows_b = sort_rows(rows_b, keys)

        # --dedup
        if ns.dedup_keys:
            key_cols = parse_key_columns(ns.dedup_keys)
            rows_a = deduplicate_rows(rows_a, key_cols).rows
            rows_b = deduplicate_rows(rows_b, key_cols).rows

        # --mask
        if ns.mask_spec:
            mask_spec = parse_mask_spec(ns.mask_spec)
            rows_a = mask_rows(rows_a, mask_spec).rows
            rows_b = mask_rows(rows_b, mask_spec).rows

        # --redact
        if ns.redact_cols:
            rcols = parse_redact_columns(ns.redact_cols)
            rows_a = redact_rows(rows_a, rcols).rows
            rows_b = redact_rows(rows_b, rcols).rows

        result = diff_csv(rows_a, rows_b, key=ns.key)

        # --merge
        if ns.merge_file:
            rows_c = load_csv(ns.merge_file, delimiter=ns.delimiter)
            result2 = diff_csv(rows_a, rows_c, key=ns.key)
            result = merge_diffs(result, result2)

        # --join
        if ns.join_file and ns.join_key:
            join_rows = load_csv(ns.join_file, delimiter=ns.delimiter)
            jkey = parse_join_key(ns.join_key)
            result = join_diff_rows(result, join_rows, jkey)

        # --sample
        if ns.sample_size:
            n = parse_sample_size(ns.sample_size)
            result = sample_diff(result, n)

        # --max-rows
        if ns.max_rows:
            n = parse_max_rows(ns.max_rows)
            result = truncate_diff(result, n).result

        # --annotate
        if ns.label_map is not None:
            lmap = parse_label_map(ns.label_map)
            result = annotate_rows(result, lmap).result

        # --alias
        if ns.alias_map:
            amap = parse_alias_map(ns.alias_map)
            result = alias_rows(result, amap).result

        # --pivot
        if ns.pivot_spec:
            pspec = parse_pivot_spec(ns.pivot_spec)
            rows_out = pivot_to_rows(result, pspec)
            print("\n".join(str(r) for r in rows_out))
            return 0

        # --group-by
        if ns.group_by:
            gcol = parse_group_by(ns.group_by)
            agg = aggregate(result, gcol)
            for grp, stats in agg.groups.items():
                print(f"{grp}: +{stats.added} -{stats.removed} ~{stats.modified} ={stats.unchanged}")
            return 0

        # --validate
        if ns.validate_rules:
            rules = parse_rules(ns.validate_rules)
            vresult = validate_rows(rows_b, rules)
            for err in vresult.errors:
                print(f"VALIDATION ERROR: {err}", file=sys.stderr)
            if not vresult.valid:
                return 2

        # --chunk-size
        if ns.chunk_size:
            csz = parse_chunk_size(ns.chunk_size)
            chunks = chunk_diff(result, csz)
            for i, chunk in enumerate(chunks.chunks, 1):
                print(f"--- chunk {i} ---")
                print(render(chunk, ns.fmt))
            # stats / score still printed below if requested
            if ns.stats:
                stats = compute_stats(result)
                print(format_stats(stats))
            if ns.score:
                score = compute_score(result)
                print(format_score(score))
            return 0

        output = render(result, ns.fmt)
        print(output)

        if ns.stats:
            stats = compute_stats(result)
            print(format_stats(stats))

        if ns.score:
            score = compute_score(result)
            print(format_score(score))

        if ns.profile:
            pr = profile_rows(rows_b)
            for col, cp in pr.columns.items():
                print(f"[profile] {col}: fill={cp.fill_rate:.0%} unique={cp.unique_count}")

        if ns.patch_out:
            lines = patch_to_csv_lines(result, headers)
            with open(ns.patch_out, "w", newline="") as fh:
                fh.write("\n".join(lines))

        if ns.export_out:
            export(result, ns.export_out, fmt=ns.export_fmt)

        if ns.lineage_flag and parse_lineage_flag(ns.lineage_flag):
            lin = build_lineage(ns.file_a, ns.file_b, result)
            print(lin.summary())

        return 0

    except (
        CSVParseError, DiffError, FilterError, SortError, TransformError,
        PatchError, ExportError, MergeError, ValidationError, ProfileError,
        SampleError, HighlightError, PivotError, AggregateError,
        DeduplicateError, AnnotateError, TruncateError, NormalizeError,
        JoinError, LineageError, RedactError, ChunkError, AliasError,
        MaskError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
