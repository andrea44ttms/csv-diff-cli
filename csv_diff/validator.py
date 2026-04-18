"""Schema validation for CSV diff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class ValidationError(Exception):
    pass


@dataclass
class ColumnRule:
    name: str
    required: bool = False
    allowed_values: Optional[List[str]] = None
    max_length: Optional[int] = None


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


def parse_rules(spec: Dict) -> List[ColumnRule]:
    """Parse a dict spec into ColumnRule list.

    spec example:
        {"name": {"required": true, "max_length": 50},
         "dept": {"allowed_values": ["eng", "hr"]}}
    """
    rules = []
    for col, cfg in spec.items():
        if not isinstance(cfg, dict):
            raise ValidationError(f"Rule for '{col}' must be a dict")
        rules.append(ColumnRule(
            name=col,
            required=cfg.get("required", False),
            allowed_values=cfg.get("allowed_values"),
            max_length=cfg.get("max_length"),
        ))
    return rules


def validate_row(row: Dict[str, str], rules: List[ColumnRule]) -> List[str]:
    errors = []
    for rule in rules:
        value = row.get(rule.name, "")
        if rule.required and not value:
            errors.append(f"Column '{rule.name}' is required but empty")
        if rule.allowed_values is not None and value and value not in rule.allowed_values:
            errors.append(
                f"Column '{rule.name}' value '{value}' not in {rule.allowed_values}"
            )
        if rule.max_length is not None and len(value) > rule.max_length:
            errors.append(
                f"Column '{rule.name}' value too long ({len(value)} > {rule.max_length})"
            )
    return errors


def validate_rows(rows: List[Dict[str, str]], rules: List[ColumnRule]) -> ValidationResult:
    result = ValidationResult()
    for i, row in enumerate(rows):
        for err in validate_row(row, rules):
            result.errors.append(f"Row {i}: {err}")
    return result
