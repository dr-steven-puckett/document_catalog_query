"""document_catalog_query.api.openapi_snapshot — deterministic OpenAPI schema generator."""
from __future__ import annotations

from fastapi import FastAPI

from document_catalog_query.api.router import router


def generate_openapi() -> dict:
    """Generate the OpenAPI schema dict deterministically.

    Creates a minimal FastAPI app, includes the router, and returns
    the resulting OpenAPI schema as a dict.
    """
    app = FastAPI(title="document_catalog_query", version="0.1.0")
    app.include_router(router)
    schema = app.openapi()
    return schema
