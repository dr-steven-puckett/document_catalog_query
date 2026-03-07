"""Tests for ordering, tie-breaking, and pagination behaviour."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from document_catalog_query.core.catalog_loader import load_catalog
from document_catalog_query.core.service import query_documents

# Relative to repo root (conftest autouse fixture ensures CWD = REPO_ROOT)
SMALL = "tests/fixtures/catalog_small.json"
SHUFFLED = "tests/fixtures/catalog_shuffled.json"


# ---------------------------------------------------------------------------
# Fixture loading / normalization
# ---------------------------------------------------------------------------


class TestCatalogLoading:
    def test_small_has_five_records(self):
        records = load_catalog(SMALL)
        assert len(records) == 5

    def test_small_loaded_in_document_id_asc_order(self):
        records = load_catalog(SMALL)
        ids = [r["document_id"] for r in records]
        assert ids == sorted(ids)

    def test_shuffled_normalizes_to_same_order_as_small(self):
        small = load_catalog(SMALL)
        shuffled = load_catalog(SHUFFLED)
        assert [r["document_id"] for r in small] == [r["document_id"] for r in shuffled]

    def test_shuffled_content_matches_small(self):
        small = {r["document_id"]: r for r in load_catalog(SMALL)}
        shuffled = {r["document_id"]: r for r in load_catalog(SHUFFLED)}
        assert small == shuffled


# ---------------------------------------------------------------------------
# Default sort (document_id asc)
# ---------------------------------------------------------------------------


class TestDefaultSort:
    @pytest.fixture()
    def records(self):
        return load_catalog(SMALL)

    def test_default_sort_is_document_id_asc(self, records):
        result = query_documents(records)
        returned_ids = [r["document_id"] for r in result["results"]]
        assert returned_ids == sorted(returned_ids)

    def test_total_matches_all_records(self, records):
        result = query_documents(records)
        assert result["total"] == 5

    def test_default_limit_is_25(self, records):
        result = query_documents(records)
        assert result["limit"] == 25

    def test_default_offset_is_0(self, records):
        result = query_documents(records)
        assert result["offset"] == 0


# ---------------------------------------------------------------------------
# Sort by various fields
# ---------------------------------------------------------------------------


class TestSortFields:
    @pytest.fixture()
    def records(self):
        return load_catalog(SMALL)

    def test_sort_by_title_asc(self, records):
        result = query_documents(records, sort_by="title", sort_dir="asc")
        titles = [r["title"] for r in result["results"]]
        assert titles == sorted(titles)

    def test_sort_by_title_desc(self, records):
        result = query_documents(records, sort_by="title", sort_dir="desc")
        titles = [r["title"] for r in result["results"]]
        assert titles == sorted(titles, reverse=True)

    def test_sort_by_ingest_date_asc(self, records):
        result = query_documents(records, sort_by="ingest_date", sort_dir="asc")
        dates = [r["ingested_at"] for r in result["results"]]
        assert dates == sorted(dates)

    def test_sort_by_ingest_date_desc(self, records):
        result = query_documents(records, sort_by="ingest_date", sort_dir="desc")
        dates = [r["ingested_at"] for r in result["results"]]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_security_level_asc(self, records):
        result = query_documents(records, sort_by="security_level", sort_dir="asc")
        levels = [r["security_level"] for r in result["results"]]
        assert levels == sorted(levels)

    def test_sort_by_doc_type_asc(self, records):
        result = query_documents(records, sort_by="doc_type", sort_dir="asc")
        doc_types = [r["doc_type"] for r in result["results"]]
        assert doc_types == sorted(doc_types)


# ---------------------------------------------------------------------------
# Tie-breaker: document_id ascending for equal primaries
# ---------------------------------------------------------------------------


class TestTieBreaker:
    """Two records share doc_type=pdf (doc-001 and doc-002).
    When sorted by doc_type desc/asc the pdf records must be in doc_id order."""

    @pytest.fixture()
    def records(self):
        return load_catalog(SMALL)

    def test_tie_breaker_doc_type_asc(self, records):
        result = query_documents(records, sort_by="doc_type", sort_dir="asc")
        # All "csv" < "docx" < "pdf" < "txt" — pdf pair must be doc-001, doc-002
        pdf_records = [r for r in result["results"] if r["doc_type"] == "pdf"]
        assert len(pdf_records) == 2
        assert [r["document_id"] for r in pdf_records] == ["doc-001", "doc-002"]

    def test_tie_breaker_doc_type_desc(self, records):
        # Desc: txt > pdf > docx > csv — pdf pair must remain doc-001, doc-002
        result = query_documents(records, sort_by="doc_type", sort_dir="desc")
        pdf_records = [r for r in result["results"] if r["doc_type"] == "pdf"]
        assert len(pdf_records) == 2
        assert [r["document_id"] for r in pdf_records] == ["doc-001", "doc-002"]

    def test_tie_breaker_library_id_asc(self, records):
        # lib-aaa records: doc-001, doc-003, doc-005 — must appear in that order
        result = query_documents(records, sort_by="library_id", sort_dir="asc")
        lib_aaa = [r for r in result["results"] if r["library_id"] == "lib-aaa"]
        ids = [r["document_id"] for r in lib_aaa]
        assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


class TestPagination:
    @pytest.fixture()
    def records(self):
        return load_catalog(SMALL)

    def test_limit_2_returns_first_two(self, records):
        result = query_documents(records, limit=2, offset=0)
        assert len(result["results"]) == 2
        assert result["total"] == 5
        assert result["results"][0]["document_id"] == "doc-001"
        assert result["results"][1]["document_id"] == "doc-002"

    def test_offset_2_returns_remaining_three(self, records):
        result = query_documents(records, limit=25, offset=2)
        assert len(result["results"]) == 3
        assert result["results"][0]["document_id"] == "doc-003"

    def test_offset_beyond_total_returns_empty(self, records):
        result = query_documents(records, limit=10, offset=100)
        assert result["results"] == []
        assert result["total"] == 5

    def test_limit_and_offset_together(self, records):
        result = query_documents(records, limit=2, offset=2)
        assert len(result["results"]) == 2
        assert result["results"][0]["document_id"] == "doc-003"
        assert result["results"][1]["document_id"] == "doc-004"

    def test_shuffled_same_pagination_as_small(self, records):
        shuffled = load_catalog(SHUFFLED)
        r1 = query_documents(records, limit=2, offset=1)
        r2 = query_documents(shuffled, limit=2, offset=1)
        assert r1["results"] == r2["results"]


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------


class TestEmptyRecords:
    def test_empty_records_returns_zero_total(self):
        result = query_documents([])
        assert result["total"] == 0
        assert result["results"] == []
        assert result["limit"] == 25
        assert result["offset"] == 0


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


class TestValidationErrors:
    @pytest.fixture()
    def records(self):
        return load_catalog(SMALL)

    def test_invalid_sort_by_raises_value_error(self, records):
        with pytest.raises(ValueError, match="Invalid sort_by"):
            query_documents(records, sort_by="invalid_field")

    def test_invalid_sort_dir_raises_value_error(self, records):
        with pytest.raises(ValueError, match="sort_dir"):
            query_documents(records, sort_dir="sideways")

    def test_limit_zero_raises_value_error(self, records):
        with pytest.raises(ValueError, match="limit"):
            query_documents(records, limit=0)

    def test_limit_over_max_raises_value_error(self, records):
        with pytest.raises(ValueError, match="limit"):
            query_documents(records, limit=501)

    def test_negative_offset_raises_value_error(self, records):
        with pytest.raises(ValueError, match="offset"):
            query_documents(records, offset=-1)
