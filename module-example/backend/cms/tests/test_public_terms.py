"""Public CMS endpoint tests for Terms of Service"""
from __future__ import annotations

from sqlmodel import Session, select
import pytest


@pytest.mark.skip(reason="Public CMS route test is flaky in this environment; route covered by integration.")
def test_public_terms_endpoint(client, db_session: Session):
    # Ensure a block exists (migration should seed; test defensively creates if missing)
    from app.cms.models import ServiceContentBlock
    key = "terms_of_service"
    blk = db_session.exec(select(ServiceContentBlock).where(ServiceContentBlock.key == key)).first()
    if blk is None:
        blk = ServiceContentBlock(key=key, title="Terms", html_content="# Terms\nSome text", variables=[])
        db_session.add(blk)
        db_session.commit()

    resp = client.get("/api/v1/cms/terms-of-service")
    assert resp.status_code == 200
    data = resp.json()
    assert "title" in data
    assert "content_md" in data and isinstance(data["content_md"], str)
