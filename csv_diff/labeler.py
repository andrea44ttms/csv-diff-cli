"""Label rows in a diff result with custom or default severity tags."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.differ import DiffResult


class LabelError(Exception):
    """Raised when labeling configuration is invalid."""


# Default severity labels for each diff status
_DEFAULT_SEVERITY: Dict[str, str] = {
    "added": "info",
    "removed": "warning",
    "modified": "notice",
    "unchanged": "ok",
}


@dataclass
class LabeledRow:
    status: str
    row: Dict[str, str]
    severity: str


@dataclass
class LabelResult:
    labeled: List[LabeledRow] = field(default_factory=list)


def parse_severity_map(spec: Optional[str]) -> Dict[str, str]:
    """Parse a severity map from a string like 'added=critical,removed=high'."""
    if not spec:
        return dict(_DEFAULT_SEVERITY)
    result = dict(_DEFAULT_SEVERITY)
    for part in spec.split(","):
        part = part.strip()
        if "=" not in part:
            raise LabelError(f"Invalid severity spec (expected key=value): {part!r}")
        key, _, val = part.partition("=")
        key, val = key.strip(), val.strip()
        if key not in _DEFAULT_SEVERITY:
            raise LabelError(
                f"Unknown status {key!r}. Valid statuses: {list(_DEFAULT_SEVERITY)}"
            )
        if not val:
            raise LabelError(f"Severity value for {key!r} must not be empty.")
        result[key] = val
    return result


def label_rows(
    result: DiffResult, severity_map: Optional[Dict[str, str]] = None
) -> LabelResult:
    """Attach a severity label to every row in *result*."""
    smap = severity_map if severity_map is not None else dict(_DEFAULT_SEVERITY)
    labeled: List[LabeledRow] = []
    for status, rows in (
        ("added", result.added),
        ("removed", result.removed),
        ("modified", [m["row"] for m in result.modified]),
        ("unchanged", result.unchanged),
    ):
        for row in rows:
            labeled.append(LabeledRow(status=status, row=row, severity=smap[status]))
    return LabelResult(labeled=labeled)
