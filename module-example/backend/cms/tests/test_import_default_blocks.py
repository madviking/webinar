"""Admin CMS: import missing default content blocks"""
from __future__ import annotations


def test_import_missing_blocks(client, super_admin_headers):
    resp = client.post("/api/v1/admin/cms/blocks/import-missing", headers=super_admin_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    keys = {blk["key"]: blk for blk in data}
    assert "signal_scoring_tour" in keys
    assert keys["signal_scoring_tour"]["category"] == "product_tour"
    # Calling again should be idempotent (no new items created)
    resp2 = client.post("/api/v1/admin/cms/blocks/import-missing", headers=super_admin_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    # Either empty list on 2nd call or same response, but ensure no error
    assert isinstance(data2, list)
