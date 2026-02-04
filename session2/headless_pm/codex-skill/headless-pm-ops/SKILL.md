---
name: headless-pm-ops
description: Use when coordinating work via Headless PM (triage task statuses, maintain ready queues, create/promote tasks, and keep workflow consistent without touching the PM database).
---

# Headless PM Ops (Task Triage + Ready Queue Discipline)

This skill keeps Headless PM usage consistent and prevents stalled work due to stale statuses, missing ready queues, or shell/quoting mistakes when creating tasks.

## When to use

- You are acting as PM, architect, or lead and need to:
  - triage `under_work` vs `created` vs `pending`
  - promote a ready queue for agents to pick up
  - bulk-promote `qa_done` → `committed` after merges
  - create new tasks with complete, developer-ready prompts
- You notice agents are idle because there are no `created` tasks for their role.

## Non-negotiables

- Use the Headless PM Python client only: `python headless/client/headless_pm_client.py ...`
- Do not touch the PM database directly.
- Tasks default to `pending`. Promote to `created` only when ready.
- Keep the ready queue small (suggested 2–4 tasks per role).
- Avoid vendor/API mocks for E2E proof. If creds are missing, tests must skip with a clear reason.

## Startup (must do)

1) Verify connection
- `source claude_venv/bin/activate && python headless/client/headless_pm_client.py context`

2) Register (role-specific)
- PM: `... register --agent-id "<id>" --role pm --level principal`
- Backend: `... register --agent-id "<id>" --role backend_dev --level senior`
- Frontend: `... register --agent-id "<id>" --role frontend_dev --level senior`
- QA: `... register --agent-id "<id>" --role qa --level senior`
- Architect: `... register --agent-id "<id>" --role architect --level principal`

3) Check mentions
- `... mentions --agent-id "<id>"`

## Connectivity / sandbox note

The client talks to a local server (default `http://localhost:6969`). If `context` fails due to local-network restrictions, request permission/escalation for:
- `python headless/client/headless_pm_client.py context`
- `python headless/client/headless_pm_client.py tasks list`
- `python headless/client/headless_pm_client.py tasks status`

## Daily PM hygiene loop (recommended)

Prefer the wrapper scripts in `scripts/headless_pm/` (they call the Python client and avoid shell quoting issues):

- Board snapshot: `source claude_venv/bin/activate && python scripts/headless_pm/pm_board.py`
- Find stale `under_work` tasks (no-lock): `source claude_venv/bin/activate && python scripts/headless_pm/triage_under_work.py`
- Apply triage (example): `source claude_venv/bin/activate && python scripts/headless_pm/triage_under_work.py --apply --to created --agent-id "<id>"`
- Bulk `qa_done` → `committed` (dry-run): `source claude_venv/bin/activate && python scripts/headless_pm/promote_qa_done.py`
- Bulk `qa_done` → `committed` (apply): `source claude_venv/bin/activate && python scripts/headless_pm/promote_qa_done.py --apply --agent-id "<id>"`

1) Snapshot the board
- `... tasks list --status created`
- `... tasks list --status under_work`
- `... tasks list --status qa_done`
- `... tasks list --status pending`

2) Triage stale `under_work`

Rule of thumb: if `status=under_work` but no lock, treat it as stale.

- If the task is ready and was just abandoned: move back to `created` with a short note.
- If blocked on prereqs (keys, migrations, upstream decision): move to `pending` with a concrete blocker note.

3) Keep the ready queue filled (but small)

Promote the next best `pending` items to `created` in dependency order until each role has 2–4 items.

4) After merges: bulk-promote `qa_done` → `committed`

Once code is merged/committed, move tasks to `committed` with a short note like “Promoted from qa_done to committed (code merged).”

## Task creation quality gate (developer prompt)

Every task description must include:
- Context
- Goal
- Non-goals
- Key decisions / invariants
- Implementation notes (paths, module boundaries)
- Acceptance criteria
- Testing / validation commands

## Shell/quoting safety when creating tasks

When passing `--description` in zsh, avoid characters that trigger globbing or shell expansion:
- Avoid: `*`, `{}`, `[]`, backticks
- Prefer plain text.
- If you must include special characters, use a safe quoting strategy (e.g. `$'...'`) or keep the task description plain text and link to an in-repo doc.
