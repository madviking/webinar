"""Admin CMS module tests (service + HTTP).

Covers CRUD operations for content blocks and email templates,
and variables discovery for supported templates.
"""
from __future__ import annotations

from sqlmodel import Session


class TestAdminCMSHTTP:
    def test_super_admin_can_crud_content_blocks(self, client, super_admin_headers):
        # Create content block
        resp = client.post(
            "/api/v1/admin/cms/blocks",
            headers=super_admin_headers,
            json={
                "key": "dashboard_intro",
                "title": "Dashboard Intro",
                "html_content": "<p>Welcome to your dashboard</p>",
                "variables": ["user_name"],
            },
        )
        assert resp.status_code == 201, resp.text
        created = resp.json()
        bid = created["id"]
        assert created["key"] == "dashboard_intro"
        assert created["title"] == "Dashboard Intro"
        assert created["category"] == "content"
        assert "html_content" in created and "Welcome" in created["html_content"]

        # List
        resp = client.get("/api/v1/admin/cms/blocks", headers=super_admin_headers)
        assert resp.status_code == 200
        items = resp.json()
        assert any(it["id"] == bid for it in items)

        # Get by id
        resp = client.get(f"/api/v1/admin/cms/blocks/{bid}", headers=super_admin_headers)
        assert resp.status_code == 200
        got = resp.json()
        assert got["id"] == bid
        assert got["category"] == "content"

        # Update
        resp = client.put(
            f"/api/v1/admin/cms/blocks/{bid}",
            headers=super_admin_headers,
            json={"html_content": "<p>Updated intro</p>"},
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert "Updated" in updated["html_content"]

        # Delete
        resp = client.delete(f"/api/v1/admin/cms/blocks/{bid}", headers=super_admin_headers)
        assert resp.status_code == 204

        # Verify 404 after delete
        resp = client.get(f"/api/v1/admin/cms/blocks/{bid}", headers=super_admin_headers)
        assert resp.status_code == 404

    def test_list_blocks_filters_by_category(self, client, super_admin_headers):
        # Create two blocks in different categories
        tour_resp = client.post(
            "/api/v1/admin/cms/blocks",
            headers=super_admin_headers,
            json={
                "key": "tour_filter_demo",
                "category": "product_tour",
                "title": "Tour filter demo",
                "html_content": "{}",
                "variables": [],
            },
        )
        assert tour_resp.status_code == 201, tour_resp.text
        content_resp = client.post(
            "/api/v1/admin/cms/blocks",
            headers=super_admin_headers,
            json={
                "key": "content_filter_demo",
                "category": "content",
                "title": "Content filter demo",
                "html_content": "<p>demo</p>",
                "variables": [],
            },
        )
        assert content_resp.status_code == 201, content_resp.text

        resp = client.get("/api/v1/admin/cms/blocks?category=product_tour", headers=super_admin_headers)
        assert resp.status_code == 200, resp.text
        items = resp.json()
        assert all(it["category"] == "product_tour" for it in items)
        keys = {it["key"] for it in items}
        assert "tour_filter_demo" in keys
        assert "content_filter_demo" not in keys

    def test_super_admin_can_crud_email_templates(self, client, super_admin_headers):
        # Create email template
        resp = client.post(
            "/api/v1/admin/cms/email-templates",
            headers=super_admin_headers,
            json={
                "name": "invitation",
                "category": "invitation",
                "subject_template": "Welcome to Queast, {{user_name}}",
                "body_html": "<h1>Hello {{user_name}}</h1>",
                "variables": ["user_name", "accept_url"],
            },
        )
        assert resp.status_code == 201, resp.text
        created = resp.json()
        tid = created["id"]
        assert created["name"] == "invitation"
        assert "Hello" in created["body_html"]

        # List
        resp = client.get("/api/v1/admin/cms/email-templates", headers=super_admin_headers)
        assert resp.status_code == 200
        items = resp.json()
        assert any(it["id"] == tid for it in items)

        # Update
        resp = client.put(
            f"/api/v1/admin/cms/email-templates/{tid}",
            headers=super_admin_headers,
            json={"subject_template": "Updated subject"},
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["subject_template"] == "Updated subject"

        # Delete
        resp = client.delete(f"/api/v1/admin/cms/email-templates/{tid}", headers=super_admin_headers)
        assert resp.status_code == 204

    def test_variables_endpoint_lists_supported_placeholders(self, client, super_admin_headers):
        resp = client.get("/api/v1/admin/cms/variables", headers=super_admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        # Ensure invitation variables are present
        assert "invitation" in data
        assert "user_name" in data["invitation"]

    def test_non_super_admin_forbidden(self, client, auth_headers):
        resp = client.get("/api/v1/admin/cms/blocks", headers=auth_headers)
        assert resp.status_code in (401, 403)
