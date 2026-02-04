#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys
from typing import Any


RESTART_MARKER = "HEADLESS_PM_TASK_COMPLETE"


def _get_last_assistant_text(payload: dict[str, Any]) -> str:
    # Best-effort: schema may evolve; keep this robust.
    msg = payload.get("last-assistant-message") or payload.get("last_assistant_message")
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        content = msg.get("content") or msg.get("text")
        if isinstance(content, str):
            return content
    return ""


def main() -> int:
    if len(sys.argv) < 2:
        return 0

    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        return 0

    if payload.get("type") != "agent-turn-complete":
        return 0

    last_text = _get_last_assistant_text(payload)
    if RESTART_MARKER not in last_text:
        return 0

    if os.environ.get("HEADLESS_PM_NOTIFY_DEBUG", "").strip() == "1":
        try:
            with open("/tmp/headless_pm_codex_notify.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"event": "marker_detected", "cwd": payload.get("cwd")}) + "\n")
        except Exception:
            pass

    tmux_pane = os.environ.get("TMUX_PANE", "").strip()
    role = os.environ.get("HEADLESS_PM_ROLE", "").strip()
    if not tmux_pane or not role:
        return 0

    # Restart the current tmux pane with a fresh Codex session for the same role.
    # This keeps context bounded per-task.
    root_dir = payload.get("cwd") or os.getcwd()
    root_dir = os.path.abspath(str(root_dir))

    cmd = f"cd {shlex.quote(root_dir)} && ./scripts/headless_pm/start_codex_role.sh {shlex.quote(role)}"

    try:
        subprocess.run(
            ["tmux", "respawn-pane", "-k", "-t", tmux_pane, cmd],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
