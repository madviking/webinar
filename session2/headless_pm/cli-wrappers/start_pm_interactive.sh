#!/usr/bin/env bash
set -euo pipefail

# Interactive PM session (you can chat with it).
# This uses Codex interactive mode with the PM role prompt.

exec "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/start_codex_pm.sh"

