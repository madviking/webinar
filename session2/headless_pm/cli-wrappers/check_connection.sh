#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

PY="${HEADLESS_PM_PYTHON:-python}"

if ! "$PY" -c 'import requests' >/dev/null 2>&1; then
  echo "Error: no usable Python found with 'requests' installed." >&2
  echo "Fix: activate a venv that has requests, or set HEADLESS_PM_PYTHON to that interpreter." >&2
  exit 1
fi

"$PY" "$ROOT_DIR/headless/client/headless_pm_client.py" context
