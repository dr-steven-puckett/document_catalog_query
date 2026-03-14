# Prompt 07 — Final Gate

## Goal
Run all validation gates.

## Steps
```bash
# Template compliance validator
python tools/tool_template_validator/techvault-tool-validate <repo_path>

# Security harness validator
python tools/tool_security_harness/techvault-tool-security-scan <repo_path>

# Manifest validation check (dry-run) — validates manifest structure only;
# does NOT register the tool. TechVault discovers and activates tools
# automatically via auto-discovery; no manual registration step is required.
python tools/tool_registration_manager/techvault-tool-register <repo_path> \
  --techvault-root <root>

# Or validate all gates at once via sync manager (dry-run)
python tools/tool_sync_manager/techvault-tool-sync <repo_path> \
  --techvault-root <root>
```

## Checkpoint
- All gates exit 0.
- `pytest -q` all green.
- OpenAPI snapshot stable.
