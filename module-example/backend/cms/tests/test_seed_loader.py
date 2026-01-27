"""CMS seeds: ensure file-backed defaults exist and load."""
from __future__ import annotations

from app.cms.seeds.loader import (
    DEFAULT_CONTENT_BLOCKS,
    DEFAULT_NOTIFICATION_TEMPLATES,
    render_email_html,
)


def test_default_content_blocks_loaded_from_disk():
    keys = {b["key"] for b in DEFAULT_CONTENT_BLOCKS}
    assert "terms_of_service" in keys
    assert "signal_scoring_tour" in keys


def test_default_notification_templates_loaded_from_disk():
    keys = {(d.get("name"), d.get("template_type")) for d in DEFAULT_NOTIFICATION_TEMPLATES}
    assert ("daily_digest_email", "email") in keys
    assert ("high_value_slack", "slack") in keys


def test_render_email_html_injects_style():
    html = render_email_html("email_templates/daily_digest.html", style="<style>/*seed-style*/</style>")
    assert html is not None
    assert "seed-style" in html
    assert "__STYLE__" not in html

