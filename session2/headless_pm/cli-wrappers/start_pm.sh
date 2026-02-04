#!/usr/bin/env bash
set -euo pipefail

# NOTE: This is the *non-interactive* PM bootstrapper (register + wait for a task).
# If you want to *chat* with a PM agent, use: scripts/headless_pm/start_pm_interactive.sh

exec "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/start_agent.sh" --role pm --level "${HEADLESS_PM_LEVEL:-principal}" "$@"
