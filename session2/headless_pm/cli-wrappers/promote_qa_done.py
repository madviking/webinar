#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


def _run_client(args: list[str]) -> str:
    cmd = [sys.executable, "headless/client/headless_pm_client.py", *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        msg = (res.stdout or "").strip() or (res.stderr or "").strip() or f"exit={res.returncode}"
        raise SystemExit(f"Headless PM client failed: {' '.join(cmd)}\n{msg}")
    return res.stdout


def _load_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception as e:
        raise SystemExit(f"Failed to parse JSON from Headless PM client output: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk promote qa_done tasks to committed.")
    parser.add_argument("--agent-id", type=str, default=None, help="Agent id for status updates (required with --apply).")
    parser.add_argument("--apply", action="store_true", help="Actually update tasks. Default is dry-run.")
    parser.add_argument(
        "--notes",
        type=str,
        default="Promoted from qa_done to committed (code merged).",
        help="Notes to attach to each status update (only with --apply).",
    )
    args = parser.parse_args()

    items = _load_json(_run_client(["tasks", "list", "--status", "qa_done"]))
    if not isinstance(items, list):
        raise SystemExit("Unexpected payload: tasks list --status qa_done did not return a JSON list.")

    ids = [int(t.get("id")) for t in items if isinstance(t, dict) and t.get("id") is not None]
    ids.sort()

    if not ids:
        print("No qa_done tasks.")
        return

    print(f"qa_done tasks: {len(ids)}")
    print("ids:", " ".join(str(i) for i in ids))

    if not args.apply:
        print("\nDry-run only. Re-run with --apply --agent-id <id> to promote to committed.")
        return

    if not args.agent_id:
        raise SystemExit("--agent-id is required with --apply")

    for tid in ids:
        _run_client(
            [
                "tasks",
                "status",
                str(tid),
                "--status",
                "committed",
                "--agent-id",
                str(args.agent_id),
                "--notes",
                str(args.notes),
            ]
        )

    print("Done.")


if __name__ == "__main__":
    main()

