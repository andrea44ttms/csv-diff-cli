"""Summary statistics for CSV diff results."""
from dataclasses import dataclass
from typing import List, Dict, Any
from csv_diff.differ import DiffResult


@dataclass
class DiffStats:
    total_added: int
    total_removed: int
    total_modified: int
    total_unchanged: int
    modified_columns: Dict[str, int]  # column -> number of times it changed

    @property
    def total_rows(self) -> int:
        return self.total_added + self.total_removed + self.total_modified + self.total_unchanged

    @property
    def change_rate(self) -> float:
        if self.total_rows == 0:
            return 0.0
        changed = self.total_added + self.total_removed + self.total_modified
        return round(changed / self.total_rows, 4)


def compute_stats(result: DiffResult) -> DiffStats:
    """Compute statistics from a DiffResult."""
    modified_columns: Dict[str, int] = {}

    for entry in result.modified:
        old_row = entry.get("old", {})
        new_row = entry.get("new", {})
        all_keys = set(old_row) | set(new_row)
        for col in all_keys:
            if old_row.get(col) != new_row.get(col):
                modified_columns[col] = modified_columns.get(col, 0) + 1

    return DiffStats(
        total_added=len(result.added),
        total_removed=len(result.removed),
        total_modified=len(result.modified),
        total_unchanged=len(result.unchanged),
        modified_columns=modified_columns,
    )


def format_stats(stats: DiffStats) -> str:
    """Render stats as a human-readable string."""
    lines = [
        "=== Diff Statistics ===",
        f"  Added:     {stats.total_added}",
        f"  Removed:   {stats.total_removed}",
        f"  Modified:  {stats.total_modified}",
        f"  Unchanged: {stats.total_unchanged}",
        f"  Total:     {stats.total_rows}",
        f"  Change rate: {stats.change_rate * 100:.2f}%",
    ]
    if stats.modified_columns:
        lines.append("  Most changed columns:")
        for col, count in sorted(stats.modified_columns.items(), key=lambda x: -x[1]):
            lines.append(f"    {col}: {count} change(s)")
    return "\n".join(lines)
