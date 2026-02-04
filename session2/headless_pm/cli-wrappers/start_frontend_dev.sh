#!/usr/bin/env bash
set -euo pipefail

exec "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/start_agent.sh" --role frontend_dev --level "${HEADLESS_PM_LEVEL:-senior}" "$@"

