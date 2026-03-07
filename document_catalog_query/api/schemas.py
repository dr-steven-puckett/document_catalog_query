"""document_catalog_query.api.schemas — Pydantic request/response models."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    tool_id: str


# ---------------------------------------------------------------------------
# Query request
# ---------------------------------------------------------------------------


class QueryRequest(BaseModel):
    # Standalone catalog-file path (CLI / test mode)
    catalog_file: str = ""

    # Filters — all optional; None means "no filter"
    document_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    library_id: Optional[str] = None
    group_id: Optional[str] = None
    security_level: Optional[str] = None
    doc_type: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    ingest_date_from: Optional[str] = Field(
        default=None,
        description="ISO date lower bound (YYYY-MM-DD), inclusive",
    )
    ingest_date_to: Optional[str] = Field(
        default=None,
        description="ISO date upper bound (YYYY-MM-DD), inclusive",
    )

    # Sorting
    sort_by: str = "document_id"
    sort_dir: str = "asc"

    # Pagination
    limit: int = Field(default=25, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Document record (one result row)
# ---------------------------------------------------------------------------


class DocumentRecord(BaseModel):
    document_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    library_id: Optional[str] = None
    group_id: Optional[str] = None
    security_level: Optional[str] = None
    doc_type: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    ingested_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Query response
# ---------------------------------------------------------------------------


class QueryResponse(BaseModel):
    results: list[DocumentRecord]
    total: int
    limit: int
    offset: int
    sort_by: str
    sort_dir: str
