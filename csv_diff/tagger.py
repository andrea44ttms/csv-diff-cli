"""Tag diff rows with custom string labels based on column value patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .differ import DiffResult


class TagError(Exception):
    """Raised when tagging configuration or execution fails."""


@dataclass
class TagResult:
    headers: List[str]
    rows: List[Dict[str, str]]  # each row gains a "_tags" key


def parse_tag_spec(spec: Optional[str]) -> Dict[str, Dict[str, str]]:
    """Parse a tag spec string into a mapping of {column: {value: tag}}.

    Format: ``col1=val1:tag1,col1=val2:tag2,col2=val3:tag3``
    """
    if not spec:
        return {}
    mapping: Dict[str, Dict[str, str]] = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part or ":" not in part:
            raise TagError(
                f"Invalid tag spec segment {part!r}. Expected 'column=value:tag'."
            )
        col_val, tag = part.rsplit(":", 1)
        if "=" not in col_val:
            raise TagError(
                f"Invalid tag spec segment {part!r}. Expected 'column=value:tag'."
            )
        col, val = col_val.split("=", 1)
        col, val, tag = col.strip(), val.strip(), tag.strip()
        if not col or not tag:
            raise TagError(f"Column and tag must be non-empty in segment {part!r}.")
        mapping.setdefault(col, {})[val] = tag
    return mapping


def tag_row(
    row: Dict[str, str],
    tag_map: Dict[str, Dict[str, str]],
) -> List[str]:
    """Return a list of tags that apply to *row* given *tag_map*."""
    tags: List[str] = []
    for col, val_map in tag_map.items():
        cell = row.get(col, "")
        if cell in val_map:
            tags.append(val_map[cell])
    return tags


def tag_rows(
    result: DiffResult,
    tag_map: Dict[str, Dict[str, str]],
) -> TagResult:
    """Attach a ``_tags`` field to every row in *result*."""
    tagged: List[Dict[str, str]] = []
    for row in result.added + result.removed + result.modified + result.unchanged:
        tags = tag_row(row, tag_map)
        enriched = dict(row)
        enriched["_tags"] = "|".join(tags) if tags else ""
        tagged.append(enriched)
    headers = list(result.headers) + ["_tags"]
    return TagResult(headers=headers, rows=tagged)
