import pytest
from csv_diff.differ import DiffResult
from csv_diff.chunker import (
    ChunkError, ChunkResult, parse_chunk_size, chunk_diff
)


def _result(**kwargs):
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_parse_chunk_size_valid():
    assert parse_chunk_size("5") == 5


def test_parse_chunk_size_non_integer():
    with pytest.raises(ChunkError, match="integer"):
        parse_chunk_size("abc")


def test_parse_chunk_size_zero_raises():
    with pytest.raises(ChunkError, match=">= 1"):
        parse_chunk_size("0")


def test_chunk_diff_empty_returns_single_chunk():
    result = _result()
    chunks = chunk_diff(result, 10)
    assert len(chunks) == 1
    assert chunks[0].is_empty()
    assert chunks[0].total == 1


def test_chunk_diff_single_chunk():
    rows = [{"id": str(i)} for i in range(3)]
    result = _result(added=rows)
    chunks = chunk_diff(result, 10)
    assert len(chunks) == 1
    assert chunks[0].added == rows
    assert chunks[0].total == 1


def test_chunk_diff_multiple_chunks():
    rows = [{"id": str(i)} for i in range(5)]
    result = _result(added=rows)
    chunks = chunk_diff(result, 2)
    assert len(chunks) == 3
    assert chunks[0].total == 3
    assert len(chunks[0].added) == 2
    assert len(chunks[1].added) == 2
    assert len(chunks[2].added) == 1


def test_chunk_diff_mixed_statuses():
    result = _result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}],
        modified=[{"id": "3"}],
        unchanged=[{"id": "4"}],
    )
    chunks = chunk_diff(result, 2)
    assert len(chunks) == 2
    total_rows = sum(
        len(c.added) + len(c.removed) + len(c.modified) + len(c.unchanged)
        for c in chunks
    )
    assert total_rows == 4


def test_chunk_diff_invalid_size_raises():
    result = _result(added=[{"id": "1"}])
    with pytest.raises(ChunkError):
        chunk_diff(result, 0)


def test_chunk_result_is_empty_false_when_has_rows():
    c = ChunkResult(index=0, total=1, added=[{"id": "1"}])
    assert not c.is_empty()
