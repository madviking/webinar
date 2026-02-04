#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

role="${1:-}"
if [[ -z "$role" || "$role" == "-h" || "$role" == "--help" ]]; then
  echo "Usage: scripts/headless_pm/start_codex_role.sh <backend_dev|frontend_dev|qa|architect|pm|fullstack_dev>" >&2
  echo "Env: CODEX_CMD (default: codex)" >&2
  exit 2
fi

prompt="$ROOT_DIR/headless/client/team_roles/${role}.md"
if [[ ! -f "$prompt" ]]; then
  echo "Error: prompt not found: $prompt" >&2
  exit 1
fi

cmd_string="${CODEX_CMD:-codex}"
IFS=' ' read -r -a cmd_parts <<<"$cmd_string"
if [[ "${#cmd_parts[@]}" -eq 0 ]]; then
  echo "Error: CODEX_CMD is empty" >&2
  exit 2
fi

if ! command -v "${cmd_parts[0]}" >/dev/null 2>&1; then
  echo "Error: Codex command not found: ${cmd_parts[0]}" >&2
  echo "Fix: set CODEX_CMD to your Codex CLI command (e.g. 'codex'), then retry." >&2
  exit 1
fi

if [[ ! -t 0 ]]; then
  echo "Error: stdin is not a terminal (Codex interactive mode requires a TTY)." >&2
  echo "Fix: run this script from an interactive terminal (don’t pipe/redirect into it)." >&2
  exit 1
fi

cd "$ROOT_DIR"

agent_id="${HEADLESS_PM_AGENT_ID:-}"
if [[ -z "$agent_id" ]]; then
  host="$(hostname -s 2>/dev/null || hostname || echo host)"
  repo="$(basename "$ROOT_DIR")"
  user="${USER:-agent}"
  agent_id="${user}_${repo}_${role}_${host}"
fi

level="${HEADLESS_PM_LEVEL:-}"
if [[ -z "$level" ]]; then
  case "$role" in
    pm|architect) level="principal" ;;
    *) level="senior" ;;
  esac
fi

export HEADLESS_PM_ROLE="$role"
export HEADLESS_PM_LEVEL="$level"
export HEADLESS_PM_AGENT_ID="$agent_id"

prompt_text="$(
  cat "$prompt"
  cat <<EOF

---

## Runtime Values (Do Not Ask The User)

- Use this exact agent id for all commands: \`$agent_id\`
- Role: \`$role\`
- Level: \`$level\`

If any instructions contain placeholders like "<agent_id>" or "[your_id]", substitute them with \`$agent_id\` and proceed immediately.
EOF
)"

exec "${cmd_parts[@]}" "$prompt_text"
