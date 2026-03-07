"""test_cli_smoke — subprocess CLI smoke tests asserting byte-identical stdout."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PYTHON = sys.executable
# Relative to repo root; subprocess uses cwd=REPO_ROOT so this resolves correctly
SMALL = "tests/fixtures/catalog_small.json"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", "document_catalog_query.cli.main"] + args,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


def test_cli_health_exits_zero():
    result = _run(["health"])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_cli_health_stdout_is_valid_json():
    result = _run(["health"])
    data = json.loads(result.stdout)
    assert data["status"] == "ok"
    assert data["tool_id"] == "document_catalog_query"


def test_cli_health_byte_identical_on_repeat():
    r1 = _run(["health"])
    r2 = _run(["health"])
    assert r1.stdout == r2.stdout, "CLI health output must be byte-identical on repeat"


def test_cli_health_no_stderr():
    result = _run(["health"])
    assert result.stderr == ""


# ---------------------------------------------------------------------------
# query — basic
# ---------------------------------------------------------------------------


def test_cli_query_exits_zero():
    result = _run(["query", "--catalog-file", SMALL])
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_cli_query_stdout_is_valid_json():
    result = _run(["query", "--catalog-file", SMALL])
    data = json.loads(result.stdout)
    assert "results" in data
    assert "total" in data
    assert data["total"] == 5


def test_cli_query_no_stderr_on_success():
    result = _run(["query", "--catalog-file", SMALL])
    assert result.stderr == ""


def test_cli_query_byte_identical_on_repeat():
    r1 = _run(["query", "--catalog-file", SMALL])
    r2 = _run(["query", "--catalog-file", SMALL])
    assert r1.stdout == r2.stdout, "CLI query output must be byte-identical on repeat"


# ---------------------------------------------------------------------------
# query — filter --status
# ---------------------------------------------------------------------------


def test_cli_query_filter_status_active():
    result = _run(["query", "--catalog-file", SMALL, "--status", "active"])
    data = json.loads(result.stdout)
    assert data["total"] == 4
    for rec in data["results"]:
        assert rec["status"] == "active"


def test_cli_query_filter_status_archived():
    result = _run(["query", "--catalog-file", SMALL, "--status", "archived"])
    data = json.loads(result.stdout)
    assert data["total"] == 1
    assert data["results"][0]["document_id"] == "doc-004"


# ---------------------------------------------------------------------------
# query — filter --doc-type
# ---------------------------------------------------------------------------


def test_cli_query_filter_doc_type_pdf():
    result = _run(["query", "--catalog-file", SMALL, "--doc-type", "pdf"])
    data = json.loads(result.stdout)
    assert data["total"] == 2
    ids = [r["document_id"] for r in data["results"]]
    assert "doc-001" in ids
    assert "doc-002" in ids


# ---------------------------------------------------------------------------
# query — filter --title substring
# ---------------------------------------------------------------------------


def test_cli_query_filter_title_alpha():
    result = _run(["query", "--catalog-file", SMALL, "--title", "alpha"])
    data = json.loads(result.stdout)
    assert data["total"] == 1
    assert data["results"][0]["document_id"] == "doc-001"


# ---------------------------------------------------------------------------
# query — sort and pagination
# ---------------------------------------------------------------------------


def test_cli_query_sort_by_title():
    result = _run(["query", "--catalog-file", SMALL, "--sort-by", "title", "--sort-dir", "asc"])
    data = json.loads(result.stdout)
    titles = [r["title"] for r in data["results"]]
    assert titles == sorted(titles)


def test_cli_query_sort_byte_identical_on_repeat():
    args = ["query", "--catalog-file", SMALL, "--sort-by", "title", "--sort-dir", "asc"]
    r1 = _run(args)
    r2 = _run(args)
    assert r1.stdout == r2.stdout


def test_cli_query_pagination_limit_2():
    result = _run(["query", "--catalog-file", SMALL, "--limit", "2", "--offset", "0"])
    data = json.loads(result.stdout)
    assert len(data["results"]) == 2
    assert data["total"] == 5


def test_cli_query_pagination_offset_2():
    result = _run(["query", "--catalog-file", SMALL, "--limit", "10", "--offset", "2"])
    data = json.loads(result.stdout)
    assert len(data["results"]) == 3


# ---------------------------------------------------------------------------
# query — date range filter
# ---------------------------------------------------------------------------


def test_cli_query_ingest_date_from():
    result = _run([
        "query", "--catalog-file", SMALL,
        "--ingest-date-from", "2026-02-01",
    ])
    data = json.loads(result.stdout)
    # doc-003 (2026-02-01), doc-004 (2026-02-10), doc-005 (2026-03-01) = 3
    assert data["total"] == 3


def test_cli_query_ingest_date_to():
    result = _run([
        "query", "--catalog-file", SMALL,
        "--ingest-date-to", "2026-01-31",
    ])
    data = json.loads(result.stdout)
    # doc-001 (2026-01-10), doc-002 (2026-01-15) = 2
    assert data["total"] == 2


# ---------------------------------------------------------------------------
# query — invalid inputs exit non-zero
# ---------------------------------------------------------------------------


def test_cli_query_invalid_sort_by_exits_nonzero():
    result = _run(["query", "--catalog-file", SMALL, "--sort-by", "invalid_field"])
    assert result.returncode != 0


def test_cli_query_invalid_sort_by_error_on_stderr():
    result = _run(["query", "--catalog-file", SMALL, "--sort-by", "invalid_field"])
    assert result.stderr != ""
    assert result.stdout == ""
