"""csv-diff: compare and highlight differences between CSV files."""
from .differ import diff_csv, DiffResult
from .aggregator import aggregate_diff, AggregateResult, format_aggregate
