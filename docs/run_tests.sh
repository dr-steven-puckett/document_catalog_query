#!/usr/bin/env bash
set -Eeuo pipefail

TOOL_PATH="backend/tools/document_catalog_query"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

echo "==> Running document_catalog_query validation gates"
echo "==> Python: ${PYTHON_BIN}"
echo "==> Tool path: ${TOOL_PATH}"
echo

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: Python executable not found at ${PYTHON_BIN}"
  echo "Set PYTHON_BIN explicitly, for example:"
  echo '  PYTHON_BIN=python3 ./run_document_catalog_query_gates.sh'
  exit 1
fi

if [[ ! -d "${TOOL_PATH}" ]]; then
  echo "ERROR: Tool directory not found: ${TOOL_PATH}"
  exit 1
fi

run_step() {
  local name="$1"
  shift
  echo "----------------------------------------------------------------------"
  echo "STEP: ${name}"
  echo "CMD : $*"
  echo "----------------------------------------------------------------------"
  "$@"
  echo
}

run_if_exists() {
  local name="$1"
  local file_path="$2"
  shift 2
  if [[ -e "${file_path}" ]]; then
    run_step "${name}" "$@"
  else
    echo "----------------------------------------------------------------------"
    echo "SKIP: ${name}"
    echo "Reason: missing ${file_path}"
    echo "----------------------------------------------------------------------"
    echo
  fi
}

# Core required checks
run_if_exists \
  "Template validator" \
  "tools/tool_template_validator/techvault-tool-validate" \
  "${PYTHON_BIN}" tools/tool_template_validator/techvault-tool-validate "${TOOL_PATH}"

run_if_exists \
  "Template strict check" \
  "tools/tool_template_check/techvault-tool-template-check" \
  "${PYTHON_BIN}" tools/tool_template_check/techvault-tool-template-check "${TOOL_PATH}" --strict

run_step \
  "Pytest full tool test suite" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests"

# Focused pytest gates
run_if_exists \
  "Contract schemas test" \
  "${TOOL_PATH}/tests/test_contract_schemas.py" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests/test_contract_schemas.py"

run_if_exists \
  "Ordering and pagination test" \
  "${TOOL_PATH}/tests/test_ordering_pagination.py" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests/test_ordering_pagination.py"

run_if_exists \
  "Determinism JSON test" \
  "${TOOL_PATH}/tests/test_determinism_json.py" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests/test_determinism_json.py"

run_if_exists \
  "CLI smoke test" \
  "${TOOL_PATH}/tests/test_cli_smoke.py" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests/test_cli_smoke.py"

run_if_exists \
  "API smoke test" \
  "${TOOL_PATH}/tests/test_api_smoke.py" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests/test_api_smoke.py"

run_if_exists \
  "OpenAPI snapshot test" \
  "${TOOL_PATH}/tests/test_openapi_snapshot.py" \
  "${PYTHON_BIN}" -m pytest -q "${TOOL_PATH}/tests/test_openapi_snapshot.py"

# Optional registration checks
run_if_exists \
  "Tool registration dry run" \
  "tools/tool_registration_manager/techvault-tool-register" \
  "${PYTHON_BIN}" tools/tool_registration_manager/techvault-tool-register "${TOOL_PATH}" --techvault-root . --verbose

# Optional workspace/catalog checks
if [[ -f "tools/tools.catalog.json" ]]; then
  if command -v make >/dev/null 2>&1; then
    run_step "Catalog sync" make catalog-sync
    run_step "Catalog check" make catalog-check
  else
    echo "----------------------------------------------------------------------"
    echo "SKIP: catalog-sync / catalog-check"
    echo "Reason: 'make' not found"
    echo "----------------------------------------------------------------------"
    echo
  fi
else
  echo "----------------------------------------------------------------------"
  echo "SKIP: catalog-sync / catalog-check"
  echo "Reason: tools/tools.catalog.json not found"
  echo "----------------------------------------------------------------------"
  echo
fi

run_if_exists \
  "Fleet manager validation pass" \
  "tools/tool_fleet_manager/techvault-tool-fleet" \
  "${PYTHON_BIN}" tools/tool_fleet_manager/techvault-tool-fleet --catalog tools/tools.catalog.json --steps validate,security_scan,template-check

echo "==> All requested gates completed."