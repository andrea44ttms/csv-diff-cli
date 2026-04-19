"""Similarity scoring between two CSV diff results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from csv_diff.differ import DiffResult


class ScoreError(Exception):
    pass


@dataclass
class SimilarityScore:
    total_rows: int
    unchanged: int
    added: int
    removed: int
    modified: int
    score: float  # 0.0 – 1.0


def _safe_div(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def compute_score(result: DiffResult) -> SimilarityScore:
    """Return a similarity score where 1.0 means identical files."""
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)
    unchanged = len(result.unchanged)
    total = added + removed + modified + unchanged
    score = round(_safe_div(unchanged, total), 4)
    return SimilarityScore(
        total_rows=total,
        unchanged=unchanged,
        added=added,
        removed=removed,
        modified=modified,
        score=score,
    )


def format_score(s: SimilarityScore) -> str:
    lines = [
        "=== Similarity Score ===",
        f"Score      : {s.score:.2%}",
        f"Total rows : {s.total_rows}",
        f"Unchanged  : {s.unchanged}",
        f"Added      : {s.added}",
        f"Removed    : {s.removed}",
        f"Modified   : {s.modified}",
    ]
    return "\n".join(lines)
