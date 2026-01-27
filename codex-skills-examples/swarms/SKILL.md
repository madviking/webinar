---
name: swarms
description: V2 swarm development and debugging for the Agent Swarm Toolkit. Use when creating or editing swarm.yaml files, agent config.yaml files, or agent.py implementations; defining assets in src/py_models; configuring triggers, field mapping, completion, and task wiring; validating and running swarms via the CLI (swarm-debug, run-sync, analyze, run); or troubleshooting swarm execution and V2 migrations.
---

# Swarms

## Overview
Build and debug V2 swarms and agents in this repo using the official docs and CLI. Focus on asset-driven flows, field mapping, model-agnostic naming, and real integration tests.

## Core Rules (Non-Negotiable)
- Use V2 swarms and agents only; verify with `./cli.py swarm-debug list`.
- Keep model names out of filenames/classes; pass provider/model via config.
- Do not modify `src/ep` (shared submodule) without explicit approval.
- Define all models in `src/py_models`; do not create agent-local `models.py`.
- Return raw dicts or Pydantic models; let field mapping create assets.
- Keep prompts in config/prompt providers, not in code.

## Workflow: Create or Update a Swarm
1. Read `docs/codex-docs-index.md` and open `references/doc-map.md`.
2. Scope existing files with `./cli.py swarm_scope <swarm_name>`.
3. Reuse existing agents/models before creating new ones.
4. Edit assets in `src/py_models`, agent config in `src/agents/implementations_v2/<agent>/config.yaml`, and agent logic in `agent.py`.
5. Update `src/swarm_manager/swarms_v2/<swarm_name>/swarm.yaml` with triggers, input_assets, output_assets, field_mapping, and completion.
6. Validate and run tests (see `references/testing-debugging.md`).
7. Update `CHANGELOG.md`.

## Pattern: MDS Batch Payload Shape Changes
When you need MDS to attach data differently (e.g. moving company `signals[]` under `persons[].signals[]`):
1. Inspect the current composer in `src/agents/implementations_v2/mds_saver/agent.py` (look for `_build_batch_payload` and helpers).
2. Update the payload model in `src/py_models/mds_models.py` to reflect the new structure.
3. Keep structure-changing logic deterministic (no LLM-driven reshaping).
4. Add a focused unit test that exercises the transformation without network calls.

## Workflow: Debug a Swarm Run
1. Analyze: `./cli.py swarm-debug analyze <swarm_name>`.
2. Validate: `./cli.py swarm validate <swarm_name>`.
3. Run sync: `./cli.py swarm-debug run-sync <swarm_name> --type <AssetType> --file test.json`.
4. Inspect: `./cli.py swarm-debug inspect <run_id>`.
5. Drill into triggers/field mapping as needed.

## References (Open Only When Needed)
- references/doc-map.md
- references/swarm-yaml.md
- references/agent-yaml.md
- references/agent-code.md
- references/asset-models.md
- references/testing-debugging.md
