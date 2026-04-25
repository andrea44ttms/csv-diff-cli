"""Enricher: join extra columns from a lookup CSV into diff rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .differ import DiffResult


class EnrichError(Exception):
    """Raised when enrichment configuration or data is invalid."""


@dataclass
class EnrichResult:
    headers: List[str]
    added: List[Dict[str, str]] = field(default_factory=list)
    removed: List[Dict[str, str]] = field(default_factory=list)
    modified: List[Dict[str, str]] = field(default_factory=list)
    unchanged: List[Dict[str, str]] = field(default_factory=list)


def parse_enrich_key(key: Optional[str]) -> str:
    """Validate and return the join key column name."""
    if not key or not key.strip():
        raise EnrichError("Enrich key column must be a non-empty string.")
    return key.strip()


def _index_lookup(
    lookup_rows: List[Dict[str, str]], key_col: str
) -> Dict[str, Dict[str, str]]:
    """Build a dict keyed by *key_col* value for O(1) lookup."""
    index: Dict[str, Dict[str, str]] = {}
    for row in lookup_rows:
        if key_col not in row:
            raise EnrichError(
                f"Lookup row missing key column '{key_col}': {row}"
            )
        index[row[key_col]] = row
    return index


def _enrich_row(
    row: Dict[str, str],
    index: Dict[str, Dict[str, str]],
    key_col: str,
    extra_cols: List[str],
) -> Dict[str, str]:
    """Return *row* with extra columns appended from the lookup index."""
    key_val = row.get(key_col, "")
    lookup_row = index.get(key_val, {})
    enriched = dict(row)
    for col in extra_cols:
        enriched[col] = lookup_row.get(col, "")
    return enriched


def enrich_diff(
    result: DiffResult,
    lookup_rows: List[Dict[str, str]],
    key_col: str,
    extra_cols: List[str],
) -> EnrichResult:
    """Attach *extra_cols* from *lookup_rows* to every row in *result*."""
    if not extra_cols:
        raise EnrichError("At least one extra column must be specified for enrichment.")
    index = _index_lookup(lookup_rows, key_col)
    new_headers = result.headers + [
        c for c in extra_cols if c not in result.headers
    ]

    def enrich_list(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return [_enrich_row(r, index, key_col, extra_cols) for r in rows]

    return EnrichResult(
        headers=new_headers,
        added=enrich_list(result.added),
        removed=enrich_list(result.removed),
        modified=enrich_list(result.modified),
        unchanged=enrich_list(result.unchanged),
    )
