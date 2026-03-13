"""document_catalog_query.api.router — FastAPI router for document_catalog_query tool.

Prefix  : /v1/tools/document_catalog_query
Tags    : ["tools:document_catalog_query"]

Endpoints
---------
GET  /health   → HealthResponse
POST /query    → QueryResponse

Error mapping:
  PermissionError           → HTTP 403
  ValueError("not found")  → HTTP 404
  ValueError (other)       → HTTP 400
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from document_catalog_query.api.deps import get_catalog_records
from document_catalog_query.api.schemas import (
    DocumentRecord,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)
from document_catalog_query.core import service
from document_catalog_query.core.catalog_loader import load_catalog

router = APIRouter(
    prefix="/v1/tools/document_catalog_query",
    tags=["tools:document_catalog_query"],
)


def _handle_error(exc: Exception) -> JSONResponse:
    """Map service exceptions to HTTP error responses."""
    if isinstance(exc, PermissionError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    if isinstance(exc, ValueError):
        msg = str(exc)
        if "not found" in msg.lower():
            return JSONResponse(status_code=404, content={"detail": msg})
        return JSONResponse(status_code=400, content={"detail": msg})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def _load_records(catalog_file: str) -> list[dict]:
    """Load records from catalog_file if provided, otherwise return an empty list.

    In production the db session loader provides records; the catalog_file path
    is used only in standalone/test mode.
    """
    if catalog_file:
        return load_catalog(catalog_file)
    return []


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="document_catalog_query_health",
)
def document_catalog_query_health() -> HealthResponse:
    return HealthResponse(**service.health())


@router.post(
    "/query",
    response_model=QueryResponse,
    operation_id="document_catalog_query_query",
)
def document_catalog_query_query(
    request: QueryRequest,
    catalog_records: list[dict] = Depends(get_catalog_records),
) -> QueryResponse | JSONResponse:
    try:
        # Platform DB-loader provides records; fall back to file-based loader
        # (standalone / test mode) when no platform records are injected.
        records = catalog_records if catalog_records else _load_records(request.catalog_file)
        result = service.query_documents(
            records,
            document_id=request.document_id,
            title=request.title,
            author=request.author,
            library_id=request.library_id,
            group_id=request.group_id,
            security_level=request.security_level,
            doc_type=request.doc_type,
            language=request.language,
            status=request.status,
            ingest_date_from=request.ingest_date_from,
            ingest_date_to=request.ingest_date_to,
            sort_by=request.sort_by,
            sort_dir=request.sort_dir,
            limit=request.limit,
            offset=request.offset,
        )
        return QueryResponse(
            results=[DocumentRecord(**r) for r in result["results"]],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            sort_by=result["sort_by"],
            sort_dir=result["sort_dir"],
        )
    except (ValueError, PermissionError) as exc:
        return _handle_error(exc)
