# Testing and Debugging (V2)

## Environment
- Activate CLI env: `source claude_venv/bin/activate`
- Prefer `./cli.py ...` (or `python -m cli ...`).
- Services run in Docker; do not start/stop containers here.

## Agent Tests (Real Services, Fixtures)
- Generate fixture from an asset:
  `./cli.py agent fixture-template <agent_name> --from-asset <asset_id>`
- Run agent test:
  `./cli.py agent test <agent_name> --input test_input.json`

## Swarm Validation + Run (Recommended Flow)
1. Validate:
   `./cli.py swarm validate <swarm_name>`
2. Run sync:
   `./cli.py swarm-debug run-sync <swarm_name> --type <AssetType> --file test.json`
3. Inspect run:
   `./cli.py swarm-debug inspect <run_id>`

## Debugging Helpers
- Analyze structure: `./cli.py swarm-debug analyze <swarm_name>`
- Test triggers: `./cli.py swarm-debug triggers <swarm_name> "AssetType:name:{...}"`
- Field mapping: `./cli.py swarm-debug field-mapping <swarm_name> <agent_name>`
- Quick smoke: `./cli.py swarm-debug quick-test <swarm_name>`
- List V2 status: `./cli.py swarm-debug list`
- When investigating task failures, start with `./cli.py swarm-debug inspect <run_id>` and use the “Recent Errors” stack trace to locate missing imports/type mismatches.

## Validation After Python Changes
1. Imports: `python -c "from <module.path> import *"`
2. Syntax: `python -m py_compile <file_path>`
3. Integration: `python testing/integration/test_service_imports.py`
4. Daemon reload: `./cli.py daemon reload`

## Required Hygiene
- Follow Red -> Green -> Refactor (TDD).
- Update CHANGELOG.md for meaningful changes.

## See Also
- docs/troubleshooting/swarm-debug-guide.md
- docs/development-guides/agents/testing-guide.md
