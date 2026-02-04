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
    parser = argparse.ArgumentParser(
        description="Find under_work tasks with no lock and move them back to created/pending (dry-run by default)."
    )
    parser.add_argument("--role", type=str, default=None, help="Optional target role filter.")
    parser.add_argument("--apply", action="store_true", help="Actually update tasks. Default is dry-run.")
    parser.add_argument("--agent-id", type=str, default=None, help="Agent id for status updates (required with --apply).")
    parser.add_argument(
        "--to",
        type=str,
        choices=["created", "pending"],
        default=None,
        help="Destination status for stale tasks (required with --apply).",
    )
    parser.add_argument(
        "--notes",
        type=str,
        default="Stale under_work with no lock; returning to backlog for re-triage.",
        help="Notes to attach to each status update (only with --apply).",
    )
    args = parser.parse_args()

    cmd = ["tasks", "list", "--status", "under_work"]
    if args.role:
        cmd += ["--role", str(args.role)]
    items = _load_json(_run_client(cmd))
    if not isinstance(items, list):
        raise SystemExit("Unexpected payload: tasks list --status under_work did not return a JSON list.")

    stale: list[dict[str, Any]] = []
    for t in items:
        if not isinstance(t, dict):
            continue
        if t.get("locked_by") is None and t.get("locked_at") is None:
            stale.append(t)

    if not stale:
        print("No stale under_work tasks (no-lock).")
        return

    stale_sorted = sorted(stale, key=lambda x: int(x.get("id") or 0))
    print(f"stale under_work (no lock): {len(stale_sorted)}")
    for t in stale_sorted:
        print(f"  #{t.get('id')} [{t.get('target_role')}] {t.get('title')}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply --to created|pending --agent-id <id> to update.")
        return

    if not args.agent_id:
        raise SystemExit("--agent-id is required with --apply")
    if not args.to:
        raise SystemExit("--to is required with --apply")

    for t in stale_sorted:
        _run_client(
            [
                "tasks",
                "status",
                str(t.get("id")),
                "--status",
                str(args.to),
                "--agent-id",
                str(args.agent_id),
                "--notes",
                str(args.notes),
            ]
        )

    print("Done.")


if __name__ == "__main__":
    main()

