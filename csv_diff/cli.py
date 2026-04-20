"""Command-line interface for csv-diff-cli."""
from __future__ import annotations

import sys

import click

from csv_diff.aliaser import alias_rows, parse_alias_map
from csv_diff.annotator import annotate_rows, parse_label_map
from csv_diff.differ import diff_csv
from csv_diff.exporter import export
from csv_diff.filter import filter_rows, parse_filter
from csv_diff.formatter import render
from csv_diff.parser import load_csv
from csv_diff.redactor import parse_redact_columns, redact_rows
from csv_diff.sampler import parse_sample_size, sample_diff
from csv_diff.scorer import compute_score, format_score
from csv_diff.sorter import parse_sort_keys, sort_rows
from csv_diff.stats import compute_stats, format_stats
from csv_diff.transformer import apply_transforms, parse_columns, parse_rename
from csv_diff.truncator import parse_max_rows, truncate_diff
from csv_diff.aggregator import aggregate_diff, parse_group_by
from csv_diff.pivot import parse_pivot_spec, pivot_to_rows
from csv_diff.joiner import join_diff_rows, parse_join_key
from csv_diff.lineage import LineageResult, add, parse_lineage_flag, summary
from csv_diff.normalizer import normalize_row, parse_normalize_options


def build_parser():
    return main


@click.command()
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
@click.option("--key", default="id", show_default=True, help="Key column name.")
@click.option("--delimiter", default=",", show_default=True)
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json", "summary"]), show_default=True)
@click.option("--filter", "filter_expr", default=None)
@click.option("--sort", "sort_expr", default=None)
@click.option("--columns", default=None)
@click.option("--rename", "rename_expr", default=None)
@click.option("--stats", is_flag=True, default=False)
@click.option("--score", is_flag=True, default=False)
@click.option("--sample", "sample_size", default=None)
@click.option("--max-rows", default=None)
@click.option("--group-by", "group_by_expr", default=None)
@click.option("--redact", "redact_expr", default=None)
@click.option("--annotate", "annotate_expr", default=None)
@click.option("--pivot", "pivot_expr", default=None)
@click.option("--join", "join_file", default=None, type=click.Path(exists=True))
@click.option("--join-key", default=None)
@click.option("--lineage", "lineage_flag", default=None)
@click.option("--normalize", "normalize_expr", default=None)
@click.option("--alias", "alias_expr", default=None, help="Column alias map, e.g. 'name=Full Name,dept=Department'.")
@click.option("--export", "export_path", default=None)
@click.option("--export-format", default="csv", type=click.Choice(["csv", "json", "jsonl"]))
def main(
    file_a, file_b, key, delimiter, fmt, filter_expr, sort_expr, columns,
    rename_expr, stats, score, sample_size, max_rows, group_by_expr,
    redact_expr, annotate_expr, pivot_expr, join_file, join_key,
    lineage_flag, normalize_expr, alias_expr, export_path, export_format,
):
    """Compare FILE_A and FILE_B and report differences."""
    try:
        rows_a = load_csv(file_a, delimiter=delimiter)
        rows_b = load_csv(file_b, delimiter=delimiter)

        if normalize_expr:
            opts = parse_normalize_options(normalize_expr)
            rows_a = [normalize_row(r, opts) for r in rows_a]
            rows_b = [normalize_row(r, opts) for r in rows_b]

        if filter_expr:
            f = parse_filter(filter_expr)
            rows_a = filter_rows(rows_a, f)
            rows_b = filter_rows(rows_b, f)

        if sort_expr:
            keys = parse_sort_keys(sort_expr)
            rows_a = sort_rows(rows_a, keys)
            rows_b = sort_rows(rows_b, keys)

        result = diff_csv(rows_a, rows_b, key=key)

        if redact_expr:
            cols = parse_redact_columns(redact_expr)
            result = redact_rows(result, cols)

        if alias_expr:
            alias_map = parse_alias_map(alias_expr)
            all_rows = result.added + result.removed + result.modified + result.unchanged
            alias_result = alias_rows(all_rows, alias_map)
            _map = {id(old): new for old, new in zip(all_rows, alias_result.rows)}
            result = type(result)(
                added=[_map[id(r)] for r in result.added],
                removed=[_map[id(r)] for r in result.removed],
                modified=[_map[id(r)] for r in result.modified],
                unchanged=[_map[id(r)] for r in result.unchanged],
            )

        if columns or rename_expr:
            col_list = parse_columns(columns) if columns else None
            ren_map = parse_rename(rename_expr) if rename_expr else None
            result = apply_transforms(result, col_list, ren_map)

        if annotate_expr is not None:
            label_map = parse_label_map(annotate_expr)
            result = annotate_rows(result, label_map).result

        if sample_size:
            n = parse_sample_size(sample_size)
            result = sample_diff(result, n)

        if max_rows:
            n = parse_max_rows(max_rows)
            result = truncate_diff(result, n).result

        if pivot_expr:
            spec = parse_pivot_spec(pivot_expr)
            all_rows = result.added + result.removed + result.modified + result.unchanged
            pivoted = pivot_to_rows(all_rows, spec)
            click.echo(pivoted)
            return

        if join_file and join_key:
            extra_rows = load_csv(join_file, delimiter=delimiter)
            jk = parse_join_key(join_key)
            result = join_diff_rows(result, extra_rows, jk).result

        output = render(result, fmt)

        if group_by_expr:
            gb = parse_group_by(group_by_expr)
            agg = aggregate_diff(result, gb)
            output = output + "\n" + str(agg)

        if stats:
            s = compute_stats(result)
            output = output + "\n" + format_stats(s)

        if score:
            sc = compute_score(result)
            output = output + "\n" + format_score(sc)

        if lineage_flag and parse_lineage_flag(lineage_flag):
            lr = LineageResult(steps=[])
            lr = add(lr, "diff", {"key": key, "file_a": file_a, "file_b": file_b})
            output = output + "\n" + summary(lr)

        click.echo(output)

        if export_path:
            export(result, export_path, fmt=export_format)

    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
