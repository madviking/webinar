from __future__ import annotations


class TestPublicCMSBlocks:
    def test_get_block_by_key_returns_404_when_missing(self, client):
        resp = client.get("/api/v1/cms/blocks/not_existing_key")
        assert resp.status_code == 404

    def test_get_block_by_key_returns_html_content(self, client, super_admin_headers):
        # Seed a block via admin
        create = client.post(
            "/api/v1/admin/cms/blocks",
            headers=super_admin_headers,
            json={
                "key": "dashboard_latest",
                "title": "Latest",
                "html_content": "<p>Some latest news</p>",
                "description": "Dashboard latest card",
                "variables": [],
            },
        )
        assert create.status_code == 201, create.text

        # Fetch via public endpoint (no auth required)
        resp = client.get("/api/v1/cms/blocks/dashboard_latest")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["key"] == "dashboard_latest"
        assert data["title"] == "Latest"
        assert data["category"] == "content"
        assert "html_content" in data and "Some latest news" in data["html_content"]

    def test_category_filtering_respects_blocks(self, client, super_admin_headers):
        create = client.post(
            "/api/v1/admin/cms/blocks",
            headers=super_admin_headers,
            json={
                "key": "public_filter_demo",
                "category": "product_tour",
                "title": "Filter demo",
                "html_content": "{}",
            },
        )
        assert create.status_code == 201, create.text

        wrong_category = client.get("/api/v1/cms/blocks/public_filter_demo?category=content")
        assert wrong_category.status_code == 404

        right_category = client.get("/api/v1/cms/blocks/public_filter_demo?category=product_tour")
        assert right_category.status_code == 200, right_category.text
        data = right_category.json()
        assert data["category"] == "product_tour"
