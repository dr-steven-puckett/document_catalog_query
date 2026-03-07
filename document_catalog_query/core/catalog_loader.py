"""document_catalog_query.core.catalog_loader — safe catalog loading and normalization.

Path safety rules:
- reject absolute paths
- reject path traversal (any component is "..")
- reject non-UTF-8 filenames or content
- reject null bytes in path

Catalog format:
- UTF-8 JSON array of document record objects
- Each item must have: document_id (str), status (str)
- Optional: title (str|null), author (str|null), library_id (str|null),
  group_id (str|null), security_level (str|null), doc_type (str|null),
  language (str|null), ingested_at (str|null, ISO datetime)

Normalization:
- Primary sort: document_id ascending
- Tie-breaker: (none — document_id is unique PK; kept for template compliance)
"""
from __future__ import annotations

import json
import os
from pathlib import PurePosixPath


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------


def _check_path_safety(raw_path: str) -> None:
    """Raise ValueError if *raw_path* is unsafe.

    Checks:
    - Null bytes: rejected.
    - Non-UTF-8 / surrogate chars: encode("utf-8", errors="strict") must succeed.
    - Absolute path: os.path.isabs(raw_path) must be False.
    - Path traversal: any component equal to ".." is rejected.
    """
    if "\x00" in raw_path:
        raise ValueError(f"Catalog path contains null bytes: {raw_path!r}")

    try:
        raw_path.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"Catalog path is not valid UTF-8 (contains surrogates): {raw_path!r}"
        ) from exc

    if os.path.isabs(raw_path):
        raise ValueError(f"Catalog path must not be absolute: {raw_path!r}")

    for part in PurePosixPath(raw_path.replace("\\", "/")).parts:
        if part == "..":
            raise ValueError(
                f"Catalog path contains path traversal component: {raw_path!r}"
            )


# ---------------------------------------------------------------------------
# Catalog item validation
# ---------------------------------------------------------------------------


def _validate_item(item: object, index: int) -> dict:
    """Validate one catalog item. Returns the item dict on success."""
    if not isinstance(item, dict):
        raise ValueError(
            f"Catalog item at index {index} must be a JSON object, "
            f"got {type(item).__name__}"
        )

    for required_field in ("document_id", "status"):
        if required_field not in item:
            raise ValueError(
                f"Catalog item at index {index} missing required field: "
                f"{required_field!r}"
            )
        if not isinstance(item[required_field], str):
            raise ValueError(
                f"Catalog item at index {index} field {required_field!r} "
                f"must be a string"
            )

    # Validate optional string fields
    for optional_str in (
        "title",
        "author",
        "library_id",
        "group_id",
        "security_level",
        "doc_type",
        "language",
        "ingested_at",
    ):
        if optional_str in item and item[optional_str] is not None:
            if not isinstance(item[optional_str], str):
                raise ValueError(
                    f"Catalog item at index {index} field {optional_str!r} "
                    f"must be a string or null"
                )

    return item  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def _normalize_items(items: list[dict]) -> list[dict]:
    """Sort items deterministically by document_id ascending.

    document_id is a primary key so ties should not occur, but the sort
    is unconditional to satisfy the template invariant.
    """
    return sorted(items, key=lambda d: (d.get("document_id") or ""))


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------


def load_catalog(catalog_file: str) -> list[dict]:
    """Load and validate a document catalog from *catalog_file*.

    Parameters
    ----------
    catalog_file:
        Relative path to a UTF-8 JSON file containing an array of document
        record objects.

    Returns
    -------
    list[dict]
        Validated and normalized (document_id-sorted) list of document records.

    Raises
    ------
    ValueError
        On any path safety violation, parse error, or validation failure.
    """
    _check_path_safety(catalog_file)

    try:
        with open(catalog_file, encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        raise ValueError(f"Catalog file not found: {catalog_file!r}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Catalog file is not valid JSON: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Catalog file is not valid UTF-8: {exc}"
        ) from exc

    if not isinstance(raw, list):
        raise ValueError(
            f"Catalog file must contain a JSON array, "
            f"got {type(raw).__name__}"
        )

    validated = [_validate_item(item, i) for i, item in enumerate(raw)]
    return _normalize_items(validated)
