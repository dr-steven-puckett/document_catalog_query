# Prompt 07 — Final Gate

## Goal
Run all validation gates.

## Steps
```bash
# Template compliance
python tools/tool_template_validator/techvault-tool-validate <repo_path>

# Security harness
python tools/tool_security_harness/techvault-tool-security-scan <repo_path>

# Registration (dry-run then apply)
python tools/tool_registration_manager/techvault-tool-register <repo_path> \
  --techvault-root <root>
python tools/tool_registration_manager/techvault-tool-register <repo_path> \
  --techvault-root <root> --apply

# Or all at once via sync manager
python tools/tool_sync_manager/techvault-tool-sync <repo_path> \
  --techvault-root <root> --apply
```

## Checkpoint
- All gates exit 0.
- `pytest -q` all green.
- OpenAPI snapshot stable.
