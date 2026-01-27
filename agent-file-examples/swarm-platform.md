# AGENTS.md

This file sets critical standards and quick references for working in the Agent Swarm Toolkit. For feature details and workflows, always consult the docs.

## Read This First
- Always read `docs/codex-docs-index.md` before starting any task.
- Follow linked docs from that index for details. This file only keeps rules and CLI helpers that apply to every request.

## Critical Warnings
- Files under `src/ep` are a Git submodule shared by multiple projects. Do not modify without explicit, special approval.
- Before finishing work, test. Do not say “this should work.” Say “I've tested this to be working.”

## Relevant Paths
- Agents: `src/agents/implementations_v2/`
- Swarms: `src/swarm_manager/swarms_v2/`
- Prompts: `src/prompt_providers/prompts`
- Models: `src/py_models`
- Observers: `src/observers`
- Transformers: `src/transformers`
- `docs/inventory.md` summarizes all agent/base locations that create swarm assets and how outputs are handled (typed vs JSON). Useful for auditing trigger pathways and ensuring agents follow V2 standards.

## V2 Only
- Use only V2 swarms and agents; V1 is deprecated.
 - Verify V2 status (local CLI): `./cli.py swarm-debug list`

## Development Standards
- Keep implementations abstract from specific LLM model names. Provider/model is always a parameter, never in filenames/classes.
- Context reduction:
  - Facades ≤ 100 lines; Services ≤ 200; Endpoints ≤ 500
  - Progressive disclosure: expose facades, hide implementation details
  - Explicit dependencies: use dependency injection, no hidden coupling

## Agent Implementation Standards
- Return raw data (dicts/Pydantic models). Let field mapping create assets.
- Avoid overriding `execute()` unless you need custom asset handling.
- Do not construct asset objects manually in agents.
- Flexible assets and field mapping details: see `docs/development-guides/agents/flexible-assets.md` (linked from `docs/codex-docs-index.md`).
- When extending MDS batch payload structure (e.g. attaching `signals` under `persons[].signals`), update both the payload model (`src/py_models/mds_models.py`) and the batch composer (`src/agents/implementations_v2/mds_saver/agent.py`) and add a deterministic unit test for the transformation.

## Models: Centralized and Auto‑Discovered
- All models live in `src/py_models`. Do not create `models.py` in agent directories.
- Import from `src.py_models` (organized by domain).
- Discovery/registration is automatic. List models: `python -m cli scaffold list models`.

## Testing Standards
IMPORTANT: you have all needed testing tools for swarms as cli-commands, so when asked to inspect a swarm run details, refer to these tools instead of searching the codebase. Service runs on docker and is always running, don't start/stop containers, ask user to do it. Cli tools are not using docker, but access database directly.

You don't need to ask permission to run the cli tools.

- Use the local CLI (activate `claude_venv`) for all commands.
- Full TDD required: follow Red → Green → Refactor.
  - Write/update a failing test or fixture first to capture the requirement or bug.
  - Implement the minimal code change to pass the test.
  - Refactor safely with tests green.
- Real-everything philosophy: no mocking; prefer integration over isolation.
- Use the V2 agent testing framework with fixtures. Do not create standalone test scripts.
- Commands:
  - `python -m cli agent test <agent_name> --input test_input.json`
  - Generate fixtures from assets: `python -m cli agent fixture-template <agent_name> --from-asset <asset_id>`
- Swarm testing: validate, run sync, inspect results.
  - `python -m cli swarm validate <swarm_name>`
  - `python -m cli swarm-debug run-sync <swarm_name> --help`
  - Inspect historical runs: `python -m cli swarm-debug inspect <run_id>` (see “CLI Helpers”).
- UI testing: use existing suites only.
  - Start: `ui/ui-tests/START_HERE_FOR_UI_TESTING.md`
  - Use: `ui/ui-tests/` (ignore `ui/tests/`)
  - Auth helper: `ui/ui-tests/core/utils/auth-helper.js`

### Success Reporting Policy
- Never declare success until tests have run and passed.
- At minimum, before saying work is complete:
  - Run relevant agent tests with fixtures and verify output.
  - Validate and run the swarm synchronously if affected.
  - Perform Validation After Python Changes (see section below).
- Phrase completion as: “I've tested this to be working,” and include what was tested (commands/files).

## Tooling and Environment
- CLI now runs locally. Services (API/daemon/DB) still run in Docker via `./manage.sh`.
- Activate the local environment: `source claude_venv/bin/activate`.
- Preferred CLI runner: `./cli.py ...` (equivalently: `python -m cli ...`).
- Never run pip on the host. Add packages to `setup/requirements.txt`; containers handle installs via entrypoints.
- Service management:
  - Start/stop/logs with `./manage.sh` (profiles: `-m dev|prod`; optional `--multi-daemon --workers N`).
  - Avoid ad-hoc container restarts; prefer `./manage.sh restart -m <mode>`.

## Validation After Python Changes
Run locally (with `claude_venv` activated):
1. Imports: `python -c "from <module.path> import *"`
2. Syntax: `python -m py_compile <file_path>`
3. Integration: `python testing/integration/test_service_imports.py`
4. Daemon reload: `./cli.py daemon reload`
- If reload fails, check container logs and `logs/unified_daemon.log` mounted in the workspace.

## CLI Helpers (Keep Handy)
Run locally (activate `claude_venv`; prefer `./cli.py`):
- Swarm scope paths: `./cli.py swarm_scope <swarm_name>` (this will show you all files that are related to particular swarm)
- Validate swarm: `./cli.py swarm validate <swarm_name>`
- Run sync (dev): `./cli.py swarm-debug run-sync <swarm_name> --type <AssetType> --file test.json`
- Inspect runs: `./cli.py swarm-debug inspect <run_id>`
- Visualize swarm: `./cli.py swarm-debug graph <swarm_name> --format json`
- Quick test: `./cli.py swarm-debug quick-test <swarm_name>`
  - Useful flags: `--verbose`, `--full-asset-info`, `--usage`, `--usage-report-responses`, `--errors`, `--no-tasks`, `--no-assets`
- Analyze swarm: `./cli.py swarm-debug analyze <swarm_name>`
- Field mapping: `./cli.py swarm-debug field-mapping <swarm_name> <agent_name>`
- Direct runner: `./cli.py swarm-debug run-direct <swarm_name> --input-file test.json`
- Monitor runs: `./cli.py swarm-debug monitor --follow`
- Export config: `./cli.py swarm-debug export <swarm_name> --format yaml`
- Prompt validation: `./cli.py prompt validate --help` and `--fix`
- Scaffolding: `./cli.py scaffold --help`
- Config management: `./cli.py config --help`, `python src/cli/config_params.py --help`
- Inspect database: `./cli.py debug db --help`
- Health check: `./cli.py doctor`
- IDE scope: `./cli.py jetbrains scope <swarm_name>`
- Swarm assets: `./cli.py swarm assets <swarm_name>`
- Create trigger: `./cli.py swarm create-asset <swarm_name> --type <AssetType> --file <path>|--json '{...}'`
- Investigate errors: `./cli.py debug errors --help`

## Architecture Principles (Condensed)
- Domain-driven structure in progress under `src/domains/` (execution, management, infrastructure).
- SOLID principles:
  - Single Responsibility: one reason to change per class
  - Open/Closed: extend via abstractions, avoid modifying core behavior
  - Liskov Substitution: preserve behavior contracts and return types
  - Interface Segregation: keep interfaces focused and role-based
  - Dependency Inversion: depend on abstractions; inject real dependencies

## Documentation
- Primary index: `docs/codex-docs-index.md` (required reading).
- Full and curated indexes plus guides are linked from there; prefer links over duplicating details here.
- If adding new documentation, update the index.

## Common Issues
- Use the troubleshooting guide: `docs/troubleshooting/` (linked from the docs index) for swarm triggers, field mapping, service connections.

## Workflow Reminders
- Core system changes: run `testing/e2e/contact_process.sh` and verify the full flow completes with final output.
- Before finishing a session: update `CHANGELOG.md` with your changes.

## Deployment
- Docker remains the runtime for services (local and prod). Use local CLI for dev/debug.
- Use `./manage.sh` for orchestration:
  - Start: `./manage.sh start -m dev` (local) or `./manage.sh start -m prod` (prod)
  - Multi-daemon: add `--multi-daemon --workers N`
  - Logs: `./manage.sh logs` or `./manage.sh logs api`
  - Restart: `./manage.sh restart -m <mode>`
- Compose files:
  - Base: `deployment/docker-compose.yml` (profiles: dev/prod)
  - Overlay: `deployment/docker-compose.multi.yml` (adds orchestrator + workers)
- Entrypoints: `deployment/scripts/start-api.sh`, `deployment/scripts/start-daemon.sh` (idempotent installs inside containers).
- Daemon config: `daemon_config.yaml` (mounted at `/app/daemon_config.yaml`). Override via `DAEMON_CONFIG_FILE`. Roles via `DAEMON_ROLE`/`DAEMON_ENABLE_TRIGGERS`.
- UI: `/daemons` shows instance role, triggers, worker metrics; use to verify orchestrator and workers are healthy.

### Before finishing session
- **Update CHANGELOG.md**: Update CHANGELOG.md file with your changes
- **Documentation updates**: Check if any of the changes should be reflected also in the documentation, update. 

### When you have questions
- provide your suggestion
- give always numbered lists
