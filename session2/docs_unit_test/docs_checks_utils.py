from __future__ import annotations

import os
import re
import subprocess
from fnmatch import fnmatch
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "docs").is_dir():
            return candidate
    raise AssertionError(f"Could not locate repo root from {start}")


def list_repo_markdown_files(repo_root: Path) -> list[str]:
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=repo_root,
        )
        paths = [p.decode("utf-8") for p in raw.split(b"\x00") if p]
        files = [p for p in paths if p.lower().endswith(".md")]
        files.sort()
        return files
    except Exception:
        # Fallback for non-git environments (e.g. source tarballs).
        ignore_dir_names = {
            ".git",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "__pycache__",
            "node_modules",
            "claude_venv",
            "venv",
            ".venv",
            "dist",
            "build",
            ".next",
            "coverage",
            "htmlcov",
            "test-results",
            "playwright-report",
            "logs",
        }

        files: list[str] = []
        for root, dirnames, filenames in os.walk(repo_root):
            dirnames[:] = [d for d in dirnames if d not in ignore_dir_names]
            for name in filenames:
                if not name.lower().endswith(".md"):
                    continue
                rel_path = Path(root, name).relative_to(repo_root).as_posix()
                files.append(rel_path)

        files.sort()
        return files


def list_repo_tracked_markdown_files(repo_root: Path) -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z", "--cached"], cwd=repo_root)
    paths = [p.decode("utf-8") for p in raw.split(b"\x00") if p]
    files = [p for p in paths if p.lower().endswith(".md")]
    files.sort()
    return files


def matches_any_glob(rel_path: str, patterns: list[str]) -> bool:
    return any(matches_glob(rel_path, pattern) for pattern in patterns)


def matches_glob(rel_path: str, pattern: str) -> bool:
    rel_path = rel_path.strip("/")
    pattern = pattern.strip("/")

    if "/" not in pattern:
        return fnmatch(rel_path, pattern)

    parts = pattern.split("/")
    out = ["^"]
    for i, part in enumerate(parts):
        if part == "**":
            if i == len(parts) - 1:
                out.append(r".*")
            else:
                out.append(r"(?:[^/]+/)*")
            continue
        seg = []
        for ch in part:
            if ch == "*":
                seg.append(r"[^/]*")
            elif ch == "?":
                seg.append(r"[^/]")
            else:
                seg.append(re.escape(ch))
        out.append("".join(seg))
        out.append("/")

    if out and out[-1] == "/":
        out.pop()
    out.append("$")
    return re.match("".join(out), rel_path) is not None
