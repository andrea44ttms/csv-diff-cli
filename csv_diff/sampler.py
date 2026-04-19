"""Row sampling utilities for large CSV diffs."""
from __future__ import annotations
import random
from typing import List, Dict, Optional


class SampleError(Exception):
    pass


def parse_sample_size(value: str) -> int:
    """Parse and validate a sample size string."""
    try:
        n = int(value)
    except ValueError:
        raise SampleError(f"Sample size must be an integer, got: {value!r}")
    if n <= 0:
        raise SampleError(f"Sample size must be positive, got: {n}")
    return n


def sample_rows(
    rows: List[Dict[str, str]],
    n: int,
    seed: Optional[int] = None,
) -> List[Dict[str, str]]:
    """Return up to *n* rows chosen without replacement."""
    if n <= 0:
        raise SampleError(f"Sample size must be positive, got: {n}")
    if n >= len(rows):
        return list(rows)
    rng = random.Random(seed)
    return rng.sample(rows, n)


def sample_diff(
    added: List[Dict[str, str]],
    removed: List[Dict[str, str]],
    modified: List[Dict[str, str]],
    n: int,
    seed: Optional[int] = None,
) -> dict:
    """Sample across all diff categories proportionally."""
    all_rows = [
        {"_status": "added", **r} for r in added
    ] + [
        {"_status": "removed", **r} for r in removed
    ] + [
        {"_status": "modified", **r} for r in modified
    ]
    sampled = sample_rows(all_rows, n, seed=seed)
    result: dict = {"added": [], "removed": [], "modified": []}
    for row in sampled:
        status = row.pop("_status")
        result[status].append(row)
    return result
