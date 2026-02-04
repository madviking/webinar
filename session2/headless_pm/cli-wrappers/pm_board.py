#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
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
    parser = argparse.ArgumentParser(description="Headless PM board snapshot (counts + ready queues).")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text.")
    parser.add_argument("--show-created", action="store_true", help="List created tasks.")
    parser.add_argument("--show-under-work", action="store_true", help="List under_work tasks.")
    args = parser.parse_args()

    tasks = _load_json(_run_client(["tasks", "list"]))
    if not isinstance(tasks, list):
        raise SystemExit("Unexpected payload: tasks list did not return a JSON list.")

    status_counts: Counter[str] = Counter()
    created_by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    under_work_by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for t in tasks:
        if not isinstance(t, dict):
            continue
        status = str(t.get("status") or "unknown")
        role = str(t.get("target_role") or "unknown")
        status_counts[status] += 1
        if status == "created":
            created_by_role[role].append(t)
        if status == "under_work":
            under_work_by_role[role].append(t)

    if args.json:
        payload = {
            "status_counts": dict(status_counts),
            "created_by_role": {
                role: [{"id": int(x.get("id")), "title": str(x.get("title") or "")} for x in sorted(items, key=lambda y: int(y.get("id") or 0))]
                for role, items in created_by_role.items()
            },
            "under_work_by_role": {
                role: [
                    {
                        "id": int(x.get("id")),
                        "title": str(x.get("title") or ""),
                        "locked_by": x.get("locked_by"),
                        "locked_at": x.get("locked_at"),
                    }
                    for x in sorted(items, key=lambda y: int(y.get("id") or 0))
                ]
                for role, items in under_work_by_role.items()
            },
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print("== Status counts ==")
    for status, count in sorted(status_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{status:>18}: {count}")

    print("\n== Created (ready queue) ==")
    if not created_by_role:
        print("(none)")
    for role in sorted(created_by_role):
        items = sorted(created_by_role[role], key=lambda x: int(x.get("id") or 0))
        print(f"{role}: {len(items)}")
        if args.show_created:
            for t in items:
                print(f"  #{t.get('id')} {t.get('title')}")

    print("\n== Under work ==")
    if not under_work_by_role:
        print("(none)")
    for role in sorted(under_work_by_role):
        items = sorted(under_work_by_role[role], key=lambda x: int(x.get("id") or 0))
        print(f"{role}: {len(items)}")
        if args.show_under_work:
            for t in items:
                lock = "locked" if t.get("locked_by") else "NO_LOCK"
                print(f"  #{t.get('id')} {t.get('title')} [{lock}]")


if __name__ == "__main__":
    main()

