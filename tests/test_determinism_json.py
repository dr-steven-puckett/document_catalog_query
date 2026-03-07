"""Tests for deterministic / canonical JSON output guarantees."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from document_catalog_query.core.catalog_loader import load_catalog
from document_catalog_query.core.determinism import canonical_json, canonical_json_bytes
from document_catalog_query.core.service import health, query_documents

# Relative to repo root (conftest autouse fixture ensures CWD = REPO_ROOT)
SMALL = "tests/fixtures/catalog_small.json"
SHUFFLED = "tests/fixtures/catalog_shuffled.json"


# ---------------------------------------------------------------------------
# canonical_json / canonical_json_bytes primitives
# ---------------------------------------------------------------------------


class TestCanonicalJson:
    def test_output_ends_with_newline(self):
        result = canonical_json({"a": 1})
        assert result.endswith("\n")

    def test_keys_are_sorted(self):
        result = canonical_json({"z": 1, "a": 2, "m": 3})
        parsed = json.loads(result)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_compact_separators(self):
        result = canonical_json({"a": 1, "b": 2})
        # Compact: no space after colon or comma
        assert ": " not in result
        assert ", " not in result

    def test_unicode_preserved(self):
        result = canonical_json({"name": "Díaz"})
        assert "Díaz" in result  # ensure_ascii=False

    def test_bytes_is_utf8_encoding(self):
        obj = {"name": "Díaz", "value": 42}
        text = canonical_json(obj)
        byt = canonical_json_bytes(obj)
        assert byt == text.encode("utf-8")

    def test_nested_objects_keys_sorted(self):
        result = canonical_json({"z": {"y": 1, "a": 2}, "a": 3})
        parsed = json.loads(result)
        assert list(parsed.keys()) == ["a", "z"]
        assert list(parsed["z"].keys()) == ["a", "y"]

    def test_none_serialized_as_null(self):
        result = canonical_json({"author": None})
        assert '"author":null' in result

    def test_list_preserved(self):
        result = canonical_json({"items": [3, 1, 2]})
        parsed = json.loads(result)
        assert parsed["items"] == [3, 1, 2]  # lists NOT sorted

    def test_identical_input_always_identical_output(self):
        obj = {"b": [1, 2], "a": {"x": True, "y": None}}
        assert canonical_json(obj) == canonical_json(obj)
        assert canonical_json(obj) == canonical_json({"a": {"x": True, "y": None}, "b": [1, 2]})


# ---------------------------------------------------------------------------
# health() determinism
# ---------------------------------------------------------------------------


class TestHealthDeterminism:
    def test_health_returns_expected_structure(self):
        result = health()
        assert result == {"status": "ok", "tool_id": "document_catalog_query"}

    def test_health_canonical_json_byte_identical(self):
        out1 = canonical_json_bytes(health())
        out2 = canonical_json_bytes(health())
        assert out1 == out2

    def test_health_canonical_json_exact_bytes(self):
        expected = b'{"status":"ok","tool_id":"document_catalog_query"}\n'
        assert canonical_json_bytes(health()) == expected


# ---------------------------------------------------------------------------
# query_documents() determinism
# ---------------------------------------------------------------------------


class TestQueryDeterminism:
    def test_repeated_calls_are_byte_identical(self):
        records = load_catalog(SMALL)
        r1 = canonical_json_bytes(query_documents(records))
        r2 = canonical_json_bytes(query_documents(records))
        assert r1 == r2

    def test_shuffled_catalog_same_output_as_small(self):
        small = load_catalog(SMALL)
        shuffled = load_catalog(SHUFFLED)
        r_small = canonical_json_bytes(query_documents(small))
        r_shuffled = canonical_json_bytes(query_documents(shuffled))
        assert r_small == r_shuffled

    def test_shuffled_same_with_filters(self):
        small = load_catalog(SMALL)
        shuffled = load_catalog(SHUFFLED)
        kwargs = {"status": "active", "sort_by": "title", "sort_dir": "desc"}
        r_small = canonical_json_bytes(query_documents(small, **kwargs))
        r_shuffled = canonical_json_bytes(query_documents(shuffled, **kwargs))
        assert r_small == r_shuffled

    def test_shuffled_same_with_pagination(self):
        small = load_catalog(SMALL)
        shuffled = load_catalog(SHUFFLED)
        kwargs = {"limit": 2, "offset": 1}
        r_small = canonical_json_bytes(query_documents(small, **kwargs))
        r_shuffled = canonical_json_bytes(query_documents(shuffled, **kwargs))
        assert r_small == r_shuffled

    def test_result_document_ids_are_deterministic(self):
        records = load_catalog(SMALL)
        r1 = query_documents(records)
        r2 = query_documents(records)
        ids1 = [x["document_id"] for x in r1["results"]]
        ids2 = [x["document_id"] for x in r2["results"]]
        assert ids1 == ids2

    def test_result_ids_ascending_by_default(self):
        records = load_catalog(SMALL)
        result = query_documents(records)
        ids = [r["document_id"] for r in result["results"]]
        assert ids == sorted(ids)
