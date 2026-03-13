"""document_catalog_query.api.deps — FastAPI dependency stubs."""
from __future__ import annotations

from typing import Any, Dict, List


def get_request_context() -> Dict[str, Any]:
    """Return an empty request context (overridden by platform at runtime)."""
    return {}


def get_catalog_records() -> List[Dict[str, Any]]:
    """Return an empty catalog records list.

    Overridden by the platform layer to provide records from the database.
    In standalone / CLI mode this default (empty list) is used and the caller
    provides a catalog_file path in the request body instead.
    """
    return []
