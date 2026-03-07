"""test_api_smoke — FastAPI TestClient smoke tests."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from document_catalog_query.api.router import router

SMALL = "tests/fixtures/catalog_small.json"


@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /v1/tools/document_catalog_query/health
# ---------------------------------------------------------------------------


def test_health_status_ok(client):
    resp = client.get("/v1/tools/document_catalog_query/health")
    assert resp.status_code == 200


def test_health_response_shape(client):
    resp = client.get("/v1/tools/document_catalog_query/health")
    data = resp.json()
    assert data["status"] == "ok"
    assert data["tool_id"] == "document_catalog_query"


def test_health_only_expected_keys(client):
    resp = client.get("/v1/tools/document_catalog_query/health")
    assert set(resp.json().keys()) == {"status", "tool_id"}


# ---------------------------------------------------------------------------
# POST /v1/tools/document_catalog_query/query — no catalog (empty results)
# ---------------------------------------------------------------------------


def test_query_empty_body_returns_200(client):
    resp = client.post("/v1/tools/document_catalog_query/query", json={})
    assert resp.status_code == 200


def test_query_empty_body_response_shape(client):
    resp = client.post("/v1/tools/document_catalog_query/query", json={})
    data = resp.json()
    assert "results" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert "sort_by" in data
    assert "sort_dir" in data


def test_query_empty_body_no_catalog_total_zero(client):
    resp = client.post("/v1/tools/document_catalog_query/query", json={})
    data = resp.json()
    assert data["total"] == 0
    assert data["results"] == []


def test_query_defaults(client):
    resp = client.post("/v1/tools/document_catalog_query/query", json={})
    data = resp.json()
    assert data["limit"] == 25
    assert data["offset"] == 0
    assert data["sort_by"] == "document_id"
    assert data["sort_dir"] == "asc"


# ---------------------------------------------------------------------------
# POST /query — with catalog_file
# ---------------------------------------------------------------------------


def test_query_with_catalog_file_returns_all(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["results"]) == 5


def test_query_results_sorted_by_document_id(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL},
    )
    ids = [r["document_id"] for r in resp.json()["results"]]
    assert ids == sorted(ids)


def test_query_filter_status_active(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "status": "active"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 4
    for rec in data["results"]:
        assert rec["status"] == "active"


def test_query_filter_status_archived(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "status": "archived"},
    )
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["document_id"] == "doc-004"


def test_query_filter_doc_type_pdf(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "doc_type": "pdf"},
    )
    data = resp.json()
    assert data["total"] == 2


def test_query_filter_title_substring(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "title": "Alpha"},
    )
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["document_id"] == "doc-001"


def test_query_filter_title_case_insensitive(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "title": "alpha"},
    )
    data = resp.json()
    assert data["total"] == 1


def test_query_sort_by_title_desc(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "sort_by": "title", "sort_dir": "desc"},
    )
    data = resp.json()
    titles = [r["title"] for r in data["results"]]
    assert titles == sorted(titles, reverse=True)


def test_query_pagination_limit(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "limit": 2},
    )
    data = resp.json()
    assert len(data["results"]) == 2
    assert data["total"] == 5
    assert data["limit"] == 2


def test_query_pagination_offset(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "limit": 2, "offset": 2},
    )
    data = resp.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["document_id"] == "doc-003"


def test_query_ingest_date_from(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "ingest_date_from": "2026-02-01"},
    )
    data = resp.json()
    assert data["total"] == 3


def test_query_ingest_date_to(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "ingest_date_to": "2026-01-31"},
    )
    data = resp.json()
    assert data["total"] == 2


# ---------------------------------------------------------------------------
# POST /query — error cases
# ---------------------------------------------------------------------------


def test_query_invalid_sort_by_returns_400(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "sort_by": "invalid_field"},
    )
    assert resp.status_code == 400


def test_query_invalid_sort_dir_returns_400(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"catalog_file": SMALL, "sort_dir": "sideways"},
    )
    assert resp.status_code == 400


def test_query_limit_zero_returns_422(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"limit": 0},
    )
    assert resp.status_code == 422


def test_query_limit_over_max_returns_422(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"limit": 501},
    )
    assert resp.status_code == 422


def test_query_negative_offset_returns_422(client):
    resp = client.post(
        "/v1/tools/document_catalog_query/query",
        json={"offset": -1},
    )
    assert resp.status_code == 422
