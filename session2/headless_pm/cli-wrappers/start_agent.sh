#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
CLIENT="$ROOT_DIR/headless/client/headless_pm_client.py"

role="${HEADLESS_PM_ROLE:-}"
level="${HEADLESS_PM_LEVEL:-}"
agent_id="${HEADLESS_PM_AGENT_ID:-}"
connection_type="${HEADLESS_PM_CONNECTION_TYPE:-client}"
create_start_doc="${HEADLESS_PM_CREATE_START_DOC:-0}"
PY="${HEADLESS_PM_PYTHON:-python}"

usage() {
  cat <<'EOF'
Usage:
  scripts/headless_pm/start_agent.sh --role backend_dev --level senior [--agent-id your_id]

Env (optional):
  HEADLESS_PM_URL                Default: http://localhost:6969
  API_KEY_HEADLESS_PM            Required (read from repo root .env.local or .env via client)
  HEADLESS_PM_ROLE               Alternative to --role
  HEADLESS_PM_LEVEL              Alternative to --level
  HEADLESS_PM_AGENT_ID           Alternative to --agent-id
  HEADLESS_PM_CONNECTION_TYPE    Default: client
  HEADLESS_PM_CREATE_START_DOC   Default: 0 (set to 1 to create a "Starting task" doc)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --role) role="${2:-}"; shift 2 ;;
    --level) level="${2:-}"; shift 2 ;;
    --agent-id) agent_id="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$role" || -z "$level" ]]; then
  echo "Error: --role and --level are required (or set HEADLESS_PM_ROLE/HEADLESS_PM_LEVEL)." >&2
  usage >&2
  exit 2
fi

if [[ -z "$agent_id" ]]; then
  host="$(hostname -s 2>/dev/null || hostname || echo host)"
  repo="$(basename "$ROOT_DIR")"
  user="${USER:-agent}"
  agent_id="${user}_${repo}_${role}_${host}"
fi

if ! "$PY" -c 'import requests' >/dev/null 2>&1; then
  echo "Error: no usable Python found with 'requests' installed." >&2
  echo "Fix: activate a venv that has requests, or set HEADLESS_PM_PYTHON to that interpreter." >&2
  exit 1
fi

echo "Headless PM: registering agent_id='$agent_id' role='$role' level='$level' ..." >&2
"$PY" "$CLIENT" register --agent-id "$agent_id" --role "$role" --level "$level" --connection-type "$connection_type" >/dev/null

echo "Headless PM: waiting for next task (server may long-poll up to ~3 minutes)..." >&2
while true; do
  task_json="$("$PY" "$CLIENT" tasks next --role "$role" --level "$level")" || true

  task_id="$(
    python - <<'PY' <<<"$task_json"
import json, sys
data = json.load(sys.stdin)

def find_task_id(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("id"), int):
            return obj["id"]
        for key in ("task", "next_task", "data"):
            if key in obj:
                tid = find_task_id(obj[key])
                if tid is not None:
                    return tid
    return None

tid = find_task_id(data)
print("" if tid is None else str(tid))
PY
  )"

  if [[ -z "$task_id" ]]; then
    continue
  fi

  echo "Headless PM: claiming task_id=$task_id ..." >&2
  "$PY" "$CLIENT" tasks lock "$task_id" --agent-id "$agent_id" >/dev/null
  "$PY" "$CLIENT" tasks status "$task_id" --status under_work --agent-id "$agent_id" --notes "Auto-claimed by start_agent.sh" >/dev/null

  if [[ "$create_start_doc" == "1" ]]; then
    "$PY" "$CLIENT" documents create \
      --type update \
      --title "Starting task $task_id" \
      --content "Claimed task $task_id and setting status to under_work." \
      --author-id "$agent_id" >/dev/null || true
  fi

  out="/tmp/headless_pm_${agent_id}_task_${task_id}.json"
  printf "%s\n" "$task_json" >"$out"
  echo "Headless PM: wrote task JSON to $out" >&2

  printf "%s\n" "$task_json"
  exit 0
done
