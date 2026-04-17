"""CSV file parsing utilities for csv-diff-cli."""

import csv
from pathlib import Path
from typing import List, Dict, Optional


class CSVParseError(Exception):
    """Raised when a CSV file cannot be parsed."""
    pass


def load_csv(filepath: str, delimiter: str = ",", encoding: str = "utf-8") -> List[Dict[str, str]]:
    """
    Load a CSV file and return a list of row dictionaries.

    Args:
        filepath: Path to the CSV file.
        delimiter: Field delimiter character.
        encoding: File encoding.

    Returns:
        List of dicts mapping column names to values.

    Raises:
        CSVParseError: If the file cannot be read or parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise CSVParseError(f"File not found: {filepath}")
    if not path.is_file():
        raise CSVParseError(f"Not a file: {filepath}")

    try:
        with open(path, newline="", encoding=encoding) as fh:
            reader = csv.DictReader(fh, delimiter=delimiter)
            if reader.fieldnames is None:
                raise CSVParseError(f"Empty or header-less CSV: {filepath}")
            rows = [dict(row) for row in reader]
    except UnicodeDecodeError as exc:
        raise CSVParseError(f"Encoding error reading {filepath}: {exc}") from exc
    except csv.Error as exc:
        raise CSVParseError(f"CSV parse error in {filepath}: {exc}") from exc

    return rows


def get_headers(filepath: str, delimiter: str = ",", encoding: str = "utf-8") -> Optional[List[str]]:
    """
    Return the header row of a CSV file without loading all rows.

    Args:
        filepath: Path to the CSV file.
        delimiter: Field delimiter character.
        encoding: File encoding.

    Returns:
        List of column names, or None if the file is empty.
    """
    path = Path(filepath)
    with open(path, newline="", encoding=encoding) as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        return list(reader.fieldnames) if reader.fieldnames else None
