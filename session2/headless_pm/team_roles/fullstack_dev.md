# Fullstack Developer (Codex + Headless PM Client)

Use the Headless PM **Python client** for tasks and communication:
- `python headless/client/headless_pm_client.py ...`

Codex skill (task workflow + status hygiene):
- Read and follow `.codex/skills/headless-pm-ops/SKILL.md`.

Headless PM config is read from the repo root `.env.local` (preferred) or `.env`:
- `API_KEY_HEADLESS_PM` (required)
- `HEADLESS_PM_URL` (optional; defaults to `http://localhost:6969`)

Follow `AGENTS.md` rules.

## Startup (do immediately)

1) Verify connection:
   - `python headless/client/headless_pm_client.py context`
2) Register:
   - If your PM server supports a `fullstack_dev` role, use it. Otherwise, register as `backend_dev`.
   - `python headless/client/headless_pm_client.py register --agent-id "<agent_id>" --role backend_dev --level senior`
3) Work loop:
   - `python headless/client/headless_pm_client.py tasks next --role backend_dev --level senior`
   - Lock + set `under_work` when a task arrives.

## Done checklist (minimum)

- Run required backend/frontend checks per the task (and `AGENTS.md`).
- Set status: `python headless/client/headless_pm_client.py tasks status <task_id> --status dev_done --agent-id "<agent_id>" --notes "Done + tests"`

## Task completion marker (required)

When you have fully completed a Headless PM task (status updated appropriately + progress documented), end your final message with this exact marker on its own line:

HEADLESS_PM_TASK_COMPLETE
