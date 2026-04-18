"""Apply a diff result to a CSV to produce a patched output."""
from typing import List, Dict
from csv_diff.differ import DiffResult


class PatchError(Exception):
    pass


def patch_rows(
    original: List[Dict[str, str]],
    diff: DiffResult,
    key: str,
) -> List[Dict[str, str]]:
    """Return a new list of rows with diff applied to original.

    - removed rows are dropped
    - modified rows are updated with new values
    - added rows are appended
    """
    if key not in (original[0] if original else {}):
        if original:
            raise PatchError(f"Key column '{key}' not found in original rows")

    # index originals by key
    indexed: Dict[str, Dict[str, str]] = {}
    order: List[str] = []
    for row in original:
        k = row.get(key, "")
        indexed[k] = dict(row)
        order.append(k)

    removed_keys = {r.get(key, "") for r in diff.removed}
    modified_map: Dict[str, Dict[str, str]] = {
        entry["new"].get(key, ""): entry["new"]
        for entry in diff.modified
    }

    result: List[Dict[str, str]] = []
    for k in order:
        if k in removed_keys:
            continue
        if k in modified_map:
            result.append(modified_map[k])
        else:
            result.append(indexed[k])

    for row in diff.added:
        result.append(dict(row))

    return result


def patch_to_csv_lines(
    patched: List[Dict[str, str]],
    headers: List[str],
) -> List[str]:
    """Serialize patched rows back to CSV lines (no quoting for simplicity)."""
    lines = [",".join(headers)]
    for row in patched:
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    return lines
