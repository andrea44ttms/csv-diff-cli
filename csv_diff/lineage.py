"""Track transformation lineage for diff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


class LineageError(Exception):
    pass


@dataclass
class LineageStep:
    operation: str
    description: str
    rows_in: int
    rows_out: int


@dataclass
class LineageResult:
    steps: List[LineageStep] = field(default_factory=list)

    def add(self, operation: str, description: str, rows_in: int, rows_out: int) -> None:
        self.steps.append(LineageStep(operation, description, rows_in, rows_out))

    def summary(self) -> List[str]:
        lines = ["Transformation Lineage:"]
        for i, s in enumerate(self.steps, 1):
            lines.append(
                f"  {i}. [{s.operation}] {s.description} "
                f"(rows: {s.rows_in} -> {s.rows_out})"
            )
        return lines


def parse_lineage_flag(value: Optional[str]) -> bool:
    """Return True if lineage tracking is enabled."""
    if value is None:
        return False
    if value.strip().lower() in ("1", "true", "yes"):
        return True
    if value.strip().lower() in ("0", "false", "no"):
        return False
    raise LineageError(f"Invalid lineage flag: {value!r}")


def record_step(
    lineage: LineageResult,
    operation: str,
    description: str,
    rows_before: List,
    rows_after: List,
) -> None:
    """Convenience wrapper to record a step given row lists."""
    lineage.add(operation, description, len(rows_before), len(rows_after))


def format_lineage(lineage: LineageResult) -> str:
    return "\n".join(lineage.summary())
