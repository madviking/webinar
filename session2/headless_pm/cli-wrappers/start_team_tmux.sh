#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
session="${HEADLESS_PM_TMUX_SESSION:-headlesspm}"

# Default to the project Codex profile that runs with maximum autonomy:
# - approval_policy = "never" (auto-approve tools)
# - sandbox_mode = "danger-full-access" (full filesystem access)
# See: .codex/config.toml ([profiles.headlesspm]).
cmd_string="${CODEX_CMD:-codex --profile headlesspm}"
IFS=' ' read -r -a cmd_parts <<<"$cmd_string"

if [[ "${#cmd_parts[@]}" -eq 0 ]]; then
  echo "Error: CODEX_CMD is empty" >&2
  exit 2
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "Error: tmux is not installed." >&2
  echo "Run these manually instead:" >&2
  #echo "  ${cmd_string} < headless/client/team_roles/pm.md" >&2
  echo "  ${cmd_string} < headless/client/team_roles/backend_dev.md" >&2
  echo "  ${cmd_string} < headless/client/team_roles/frontend_dev.md" >&2
  echo "  ${cmd_string} < headless/client/team_roles/qa.md" >&2
  echo "  ${cmd_string} < headless/client/team_roles/architect.md" >&2
  exit 1
fi

if ! command -v "${cmd_parts[0]}" >/dev/null 2>&1; then
  echo "Error: Codex command not found: ${cmd_parts[0]}" >&2
  echo "Fix: set CODEX_CMD to your Codex CLI command (e.g. 'codex'), then retry." >&2
  exit 1
fi

cd "$ROOT_DIR"

if tmux has-session -t "$session" 2>/dev/null; then
  echo "tmux session '$session' already exists. Attaching..." >&2
  exec tmux attach -t "$session"
fi

# Create the session (and server) first, then add windows.
# tmux new-session -d -s "$session" -n pm "CODEX_CMD=$(printf %q "$cmd_string") scripts/headless_pm/start_codex_role.sh pm"
tmux new-session -d -s "$session" -n backend "CODEX_CMD=$(printf %q "$cmd_string") scripts/headless_pm/start_codex_role.sh backend_dev"
tmux new-window -t "$session" -n frontend "CODEX_CMD=$(printf %q "$cmd_string") scripts/headless_pm/start_codex_role.sh frontend_dev"
tmux new-window -t "$session" -n qa "CODEX_CMD=$(printf %q "$cmd_string") scripts/headless_pm/start_codex_role.sh qa"
tmux new-window -t "$session" -n architect "CODEX_CMD=$(printf %q "$cmd_string") scripts/headless_pm/start_codex_role.sh architect"

exec tmux attach -t "$session"
