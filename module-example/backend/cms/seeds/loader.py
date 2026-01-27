from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _read_text(rel_path: str) -> Optional[str]:
    path = (_TEMPLATES_DIR / rel_path).resolve()
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    content = content.strip()
    return content or None


def _read_json(rel_path: str) -> Any:
    content = _read_text(rel_path)
    if not content:
        return None
    return json.loads(content)


def load_default_content_blocks() -> list[dict[str, Any]]:
    """Load default CMS content blocks from disk."""
    meta = _read_json("content_blocks/defaults.json")
    if not isinstance(meta, list):
        return []

    out: list[dict[str, Any]] = []
    for item in meta:
        if not isinstance(item, dict):
            continue
        content_path = (item.get("content_path") or "").strip()
        if not content_path:
            continue
        html_content = _read_text(content_path)
        if not html_content:
            continue
        out.append(
            {
                "key": (item.get("key") or "").strip(),
                "category": (item.get("category") or "content").strip() or "content",
                "title": (item.get("title") or "").strip(),
                "html_content": html_content,
                "description": (item.get("description") or None),
                "variables": item.get("variables") or [],
            }
        )
    return [b for b in out if b["key"] and b["title"]]


DEFAULT_CONTENT_BLOCKS: list[dict[str, Any]] = load_default_content_blocks()


def render_email_html(rel_path: str, *, style: str) -> Optional[str]:
    """Render an HTML seed template with the computed style injected."""
    html = _read_text(rel_path)
    if not html:
        return None
    return html.replace("__STYLE__", style or "").strip() or None


def load_default_notification_templates() -> list[dict[str, Any]]:
    """Load baseline notification templates (email + slack) from disk."""
    data = _read_json("notification_templates/defaults.json")
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, dict)]


DEFAULT_NOTIFICATION_TEMPLATES: list[dict[str, Any]] = load_default_notification_templates()

