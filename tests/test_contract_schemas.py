"""Tests for Pydantic request/response schema contracts."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from document_catalog_query.api.schemas import (
    DocumentRecord,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)


# ---------------------------------------------------------------------------
# HealthResponse
# ---------------------------------------------------------------------------


class TestHealthResponse:
    def test_required_fields(self):
        h = HealthResponse(status="ok", tool_id="document_catalog_query")
        assert h.status == "ok"
        assert h.tool_id == "document_catalog_query"

    def test_model_dump_keys(self):
        h = HealthResponse(status="ok", tool_id="document_catalog_query")
        keys = set(h.model_dump().keys())
        assert keys == {"status", "tool_id"}

    def test_missing_status_raises(self):
        with pytest.raises(ValidationError):
            HealthResponse(tool_id="document_catalog_query")  # type: ignore[call-arg]

    def test_missing_tool_id_raises(self):
        with pytest.raises(ValidationError):
            HealthResponse(status="ok")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# QueryRequest defaults
# ---------------------------------------------------------------------------


class TestQueryRequest:
    def test_defaults(self):
        q = QueryRequest()
        assert q.catalog_file == ""
        assert q.sort_by == "document_id"
        assert q.sort_dir == "asc"
        assert q.limit == 25
        assert q.offset == 0

    def test_all_filter_fields_default_to_none(self):
        q = QueryRequest()
        for field in (
            "document_id",
            "title",
            "author",
            "library_id",
            "group_id",
            "security_level",
            "doc_type",
            "language",
            "status",
            "ingest_date_from",
            "ingest_date_to",
        ):
            assert getattr(q, field) is None, f"{field} should default to None"

    def test_limit_lower_bound(self):
        with pytest.raises(ValidationError):
            QueryRequest(limit=0)

    def test_limit_upper_bound(self):
        with pytest.raises(ValidationError):
            QueryRequest(limit=501)

    def test_offset_negative_raises(self):
        with pytest.raises(ValidationError):
            QueryRequest(offset=-1)

    def test_custom_values(self):
        q = QueryRequest(
            catalog_file="tests/fixtures/catalog_small.json",
            title="alpha",
            sort_by="title",
            sort_dir="desc",
            limit=10,
            offset=5,
        )
        assert q.catalog_file == "tests/fixtures/catalog_small.json"
        assert q.title == "alpha"
        assert q.sort_by == "title"
        assert q.sort_dir == "desc"
        assert q.limit == 10
        assert q.offset == 5


# ---------------------------------------------------------------------------
# DocumentRecord
# ---------------------------------------------------------------------------


class TestDocumentRecord:
    def test_all_fields_optional(self):
        # Empty construction should succeed
        rec = DocumentRecord()
        for field in (
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
        ):
            assert getattr(rec, field) is None, f"{field} should default to None"

    def test_model_dump_keys(self):
        rec = DocumentRecord(document_id="doc-001", title="Test Doc")
        keys = set(rec.model_dump().keys())
        assert keys == {
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
        }

    def test_full_record(self):
        rec = DocumentRecord(
            document_id="doc-001",
            title="Alpha Architecture Guide",
            author="Alice Smith",
            library_id="lib-aaa",
            group_id="grp-001",
            security_level="public",
            doc_type="pdf",
            language="en",
            status="active",
            ingested_at="2026-01-10T08:00:00Z",
        )
        assert rec.document_id == "doc-001"
        assert rec.ingested_at == "2026-01-10T08:00:00Z"


# ---------------------------------------------------------------------------
# QueryResponse
# ---------------------------------------------------------------------------


class TestQueryResponse:
    def test_empty_response(self):
        r = QueryResponse(
            results=[],
            total=0,
            limit=25,
            offset=0,
            sort_by="document_id",
            sort_dir="asc",
        )
        assert r.results == []
        assert r.total == 0

    def test_model_dump_keys(self):
        r = QueryResponse(
            results=[],
            total=0,
            limit=25,
            offset=0,
            sort_by="document_id",
            sort_dir="asc",
        )
        keys = set(r.model_dump().keys())
        assert keys == {"results", "total", "limit", "offset", "sort_by", "sort_dir"}

    def test_required_total_raises(self):
        with pytest.raises(ValidationError):
            QueryResponse(results=[], limit=25, offset=0, sort_by="document_id", sort_dir="asc")  # type: ignore[call-arg]
