"""document_catalog_query.core.service — deterministic business logic.

All public functions follow the service exception boundary:
  - Only ValueError and PermissionError may escape.
  - Unexpected exceptions are wrapped as ValueError("Unexpected error: <ClassName>: <msg>").

This module operates exclusively on in-memory record lists.  Record lists are
provided by either:
  - catalog_loader.load_catalog() (CLI standalone / tests)
  - a db loader that fetches rows from Postgres (API production path)

Either way the filtering, sorting, and pagination logic is identical.
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Public sort-field name → record dict key
_SORT_FIELD_MAP: dict[str, str] = {
    "document_id":   "document_id",
    "title":         "title",
    "author":        "author",
    "library_id":    "library_id",
    "group_id":      "group_id",
    "security_level": "security_level",
    "doc_type":      "doc_type",
    "language":      "language",
    "status":        "status",
    "ingest_date":   "ingested_at",
}

VALID_SORT_FIELDS: frozenset[str] = frozenset(_SORT_FIELD_MAP.keys())
VALID_SORT_DIRS: frozenset[str] = frozenset({"asc", "desc"})

_DEFAULT_SORT_BY = "document_id"
_DEFAULT_SORT_DIR = "asc"
_DEFAULT_LIMIT = 25
_MAX_LIMIT = 500


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sort_key_for(record: dict, field_key: str) -> str:
    """Return a comparable sort key for *field_key* in *record*.

    None values sort as empty string (smallest) to ensure stable ordering.
    """
    val = record.get(field_key)
    if val is None:
        return ""
    return str(val)


def _apply_filters(
    records: list[dict],
    *,
    document_id: str | None = None,
    title: str | None = None,
    author: str | None = None,
    library_id: str | None = None,
    group_id: str | None = None,
    security_level: str | None = None,
    doc_type: str | None = None,
    language: str | None = None,
    status: str | None = None,
    ingest_date_from: str | None = None,
    ingest_date_to: str | None = None,
) -> list[dict]:
    """Return only those records matching ALL provided (non-None) filters.

    Rules:
    - document_id: exact match (case-sensitive)
    - title: case-insensitive substring contains
    - author: case-insensitive substring contains
    - library_id: exact match (case-sensitive)
    - group_id: exact match (case-sensitive)
    - security_level: exact match (case-sensitive)
    - doc_type: exact match (case-sensitive)
    - language: case-insensitive exact match
    - status: exact match (case-sensitive)
    - ingest_date_from: record ingested_at >= date (ISO prefix comparison)
    - ingest_date_to: record ingested_at <= date (ISO prefix comparison)
    """
    result: list[dict] = []
    for rec in records:
        if document_id is not None and rec.get("document_id") != document_id:
            continue
        if title is not None:
            rec_title = (rec.get("title") or "").lower()
            if title.lower() not in rec_title:
                continue
        if author is not None:
            rec_author = (rec.get("author") or "").lower()
            if author.lower() not in rec_author:
                continue
        if library_id is not None and rec.get("library_id") != library_id:
            continue
        if group_id is not None and rec.get("group_id") != group_id:
            continue
        if security_level is not None and rec.get("security_level") != security_level:
            continue
        if doc_type is not None and rec.get("doc_type") != doc_type:
            continue
        if language is not None:
            rec_lang = (rec.get("language") or "").lower()
            if rec_lang != language.lower():
                continue
        if status is not None and rec.get("status") != status:
            continue
        # Date range: compare ISO prefix (lexicographic, safe for ISO-8601)
        ingested = rec.get("ingested_at") or ""
        if ingest_date_from is not None:
            if ingested < ingest_date_from:
                continue
        if ingest_date_to is not None:
            # ingest_date_to is a date (YYYY-MM-DD); a datetime on that day begins
            # with that prefix, so we accept anything that starts with or is before
            # the date boundary (exclusive next day).
            next_day = _next_day(ingest_date_to)
            if ingested >= next_day:
                continue
        result.append(rec)
    return result


def _next_day(date_str: str) -> str:
    """Return the ISO date string for the day after *date_str* (YYYY-MM-DD).

    Used for inclusive upper-bound date filtering.
    If *date_str* is not a valid YYYY-MM-DD string, returns *date_str* + 'T'
    as a safe lexicographic upper bound for any datetime on that date.
    """
    try:
        from datetime import date, timedelta
        d = date.fromisoformat(date_str)
        return (d + timedelta(days=1)).isoformat()
    except (ValueError, OverflowError):
        # Fallback: append 'T' so any datetime on that date is <= (date + 'T')
        return date_str + "T"


def _sort_records(
    records: list[dict],
    sort_by: str,
    sort_dir: str,
) -> list[dict]:
    """Sort *records* by *sort_by* ascending/descending with document_id tie-breaker.

    The sort is always stable: identical primary-key values break on document_id
    ascending (document_id is the unique PK, so ties are only possible if the
    caller constructed artificial duplicate records in tests).
    """
    field_key = _SORT_FIELD_MAP[sort_by]
    reverse = sort_dir == "desc"

    def sort_key(rec: dict) -> tuple[str, str]:
        primary = _sort_key_for(rec, field_key)
        tiebreak = _sort_key_for(rec, "document_id")
        return (primary, tiebreak)

    sorted_records = sorted(records, key=sort_key, reverse=False)
    if reverse:
        # Reverse primary sort but keep tie-breaker stable ascending.
        # Two-pass: sort ascending then stable-reverse the primary while keeping
        # document_id tie-breaker ascending for equal primaries.
        sorted_records = _stable_desc_sort_correct(records, field_key)

    return sorted_records


def _stable_desc_sort_correct(records: list[dict], field_key: str) -> list[dict]:
    """Sort descending on *field_key*, ascending on document_id for equal primaries."""
    # Decorate with index to make sort stable for tie-breaker
    decorated: list[tuple[str, str, int, dict]] = [
        (_sort_key_for(r, field_key), _sort_key_for(r, "document_id"), i, r)
        for i, r in enumerate(records)
    ]
    # Sort: primary DESCENDING (negate not possible for strings; use two-pass)
    # Pass 1: sort by tiebreak (document_id) ascending
    decorated.sort(key=lambda t: t[1])
    # Pass 2: stable sort by primary DESCENDING
    decorated.sort(key=lambda t: t[0], reverse=True)
    return [t[3] for t in decorated]


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------


def health() -> dict:
    """Return a deterministic health response.

    Returns
    -------
    dict
        {"status": "ok", "tool_id": "document_catalog_query"}
    """
    try:
        return {"status": "ok", "tool_id": "document_catalog_query"}
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"Unexpected error: {type(exc).__name__}: {exc}") from None


def query_documents(
    records: list[dict],
    *,
    document_id: str | None = None,
    title: str | None = None,
    author: str | None = None,
    library_id: str | None = None,
    group_id: str | None = None,
    security_level: str | None = None,
    doc_type: str | None = None,
    language: str | None = None,
    status: str | None = None,
    ingest_date_from: str | None = None,
    ingest_date_to: str | None = None,
    sort_by: str = _DEFAULT_SORT_BY,
    sort_dir: str = _DEFAULT_SORT_DIR,
    limit: int = _DEFAULT_LIMIT,
    offset: int = 0,
) -> dict:
    """Filter, sort, and paginate *records* deterministically.

    Parameters
    ----------
    records:
        Pre-loaded list of document record dicts (from catalog_loader or db loader).
    document_id, title, author, library_id, group_id, security_level,
    doc_type, language, status, ingest_date_from, ingest_date_to:
        Optional filter values (None = no filter applied for that field).
    sort_by:
        One of VALID_SORT_FIELDS. Default: "document_id".
    sort_dir:
        "asc" or "desc". Default: "asc".
    limit:
        Maximum number of results to return (1–MAX_LIMIT). Default: 25.
    offset:
        Zero-based pagination offset. Default: 0.

    Returns
    -------
    dict
        {
          "results": list[dict],
          "total": int,          # total matching (before pagination)
          "limit": int,
          "offset": int,
          "sort_by": str,
          "sort_dir": str,
        }

    Raises
    ------
    ValueError
        On invalid sort_by, sort_dir, limit < 1 or > MAX_LIMIT, or offset < 0.
    """
    try:
        # --- Input validation ---
        if sort_by not in VALID_SORT_FIELDS:
            raise ValueError(
                f"Invalid sort_by {sort_by!r}. "
                f"Valid fields: {sorted(VALID_SORT_FIELDS)}"
            )
        if sort_dir not in VALID_SORT_DIRS:
            raise ValueError(
                f"Invalid sort_dir {sort_dir!r}. Must be 'asc' or 'desc'."
            )
        if not isinstance(limit, int) or limit < 1 or limit > _MAX_LIMIT:
            raise ValueError(
                f"limit must be an integer between 1 and {_MAX_LIMIT}, got {limit!r}."
            )
        if not isinstance(offset, int) or offset < 0:
            raise ValueError(f"offset must be a non-negative integer, got {offset!r}.")

        # --- Filter ---
        filtered = _apply_filters(
            records,
            document_id=document_id,
            title=title,
            author=author,
            library_id=library_id,
            group_id=group_id,
            security_level=security_level,
            doc_type=doc_type,
            language=language,
            status=status,
            ingest_date_from=ingest_date_from,
            ingest_date_to=ingest_date_to,
        )

        total = len(filtered)

        # --- Sort ---
        if sort_dir == "desc":
            sorted_records = _stable_desc_sort_correct(filtered, _SORT_FIELD_MAP[sort_by])
        else:
            sorted_records = sorted(
                filtered,
                key=lambda r: (
                    _sort_key_for(r, _SORT_FIELD_MAP[sort_by]),
                    _sort_key_for(r, "document_id"),
                ),
            )

        # --- Paginate ---
        page = sorted_records[offset: offset + limit]

        # --- Serialize result rows (only expose defined fields) ---
        results = [_serialize_record(r) for r in page]

        return {
            "results": results,
            "total": total,
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        }
    except (ValueError, PermissionError):
        raise
    except Exception as exc:
        raise ValueError(
            f"Unexpected error: {type(exc).__name__}: {exc}"
        ) from None


# ---------------------------------------------------------------------------
# Record serialization
# ---------------------------------------------------------------------------

_OUTPUT_FIELDS: tuple[str, ...] = (
    "document_id",
    "title",
    "author",
    "library_id",
    "group_id",
    "security_level",
    "doc_type",
    "language",
    "status",
    "ingested_at",
)


def _serialize_record(rec: dict) -> dict[str, Any]:
    """Extract and return only the defined output fields from *rec*.

    Missing fields default to None.  Preserves None for nullable fields.
    """
    return {field: rec.get(field) for field in _OUTPUT_FIELDS}
