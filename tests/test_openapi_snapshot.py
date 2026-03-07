"""test_openapi_snapshot — verify openapi.snapshot.json is stable.

Run with UPDATE_OPENAPI_SNAPSHOT=1 to regenerate the snapshot:
    UPDATE_OPENAPI_SNAPSHOT=1 pytest tests/test_openapi_snapshot.py -q

Run normally to assert no drift:
    pytest tests/test_openapi_snapshot.py -q
"""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SNAPSHOT_PATH = REPO_ROOT / "openapi.snapshot.json"


def _canonical(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def _generate() -> dict:
    from document_catalog_query.api.openapi_snapshot import generate_openapi

    return generate_openapi()


def test_openapi_snapshot_stable():
    """Generated OpenAPI schema must match the committed snapshot.

    Set UPDATE_OPENAPI_SNAPSHOT=1 to regenerate.
    """
    update = os.environ.get("UPDATE_OPENAPI_SNAPSHOT", "0") == "1"
    generated = _generate()
    canonical_generated = _canonical(generated)

    if update:
        SNAPSHOT_PATH.write_text(canonical_generated, encoding="utf-8")
        # After writing, the test passes trivially
        return

    assert SNAPSHOT_PATH.exists(), (
        f"openapi.snapshot.json not found at {SNAPSHOT_PATH}. "
        "Run with UPDATE_OPENAPI_SNAPSHOT=1 to generate it."
    )

    snapshot_text = SNAPSHOT_PATH.read_text(encoding="utf-8")
    snapshot = json.loads(snapshot_text)
    canonical_snapshot = _canonical(snapshot)

    assert canonical_generated == canonical_snapshot, (
        "OpenAPI schema has drifted from openapi.snapshot.json.\n"
        "Run with UPDATE_OPENAPI_SNAPSHOT=1 to update the snapshot.\n\n"
        f"Generated:\n{canonical_generated[:500]}\n\n"
        f"Snapshot:\n{canonical_snapshot[:500]}"
    )
