"""Split diff results into chunks of a given size."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from csv_diff.differ import DiffResult


class ChunkError(Exception):
    pass


def parse_chunk_size(value: str) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ChunkError(f"Chunk size must be an integer, got: {value!r}")
    if n < 1:
        raise ChunkError(f"Chunk size must be >= 1, got: {n}")
    return n


@dataclass
class ChunkResult:
    index: int
    total: int
    added: List[dict] = field(default_factory=list)
    removed: List[dict] = field(default_factory=list)
    modified: List[dict] = field(default_factory=list)
    unchanged: List[dict] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.modified or self.unchanged)


def chunk_diff(result: DiffResult, size: int) -> List[ChunkResult]:
    """Partition all rows from a DiffResult into ChunkResult pages."""
    if size < 1:
        raise ChunkError(f"Chunk size must be >= 1, got: {size}")

    all_rows: List[tuple] = []
    for row in result.added:
        all_rows.append(("added", row))
    for row in result.removed:
        all_rows.append(("removed", row))
    for row in result.modified:
        all_rows.append(("modified", row))
    for row in result.unchanged:
        all_rows.append(("unchanged", row))

    if not all_rows:
        return [ChunkResult(index=0, total=1)]

    pages = [all_rows[i:i + size] for i in range(0, len(all_rows), size)]
    total = len(pages)
    chunks: List[ChunkResult] = []
    for idx, page in enumerate(pages):
        c = ChunkResult(index=idx, total=total)
        for status, row in page:
            getattr(c, status).append(row)
        chunks.append(c)
    return chunks
