"""Admin CMS API (super_admin only)."""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlmodel import Session

from app.shared.database import get_session
from app.auth.dependencies import require_role
from app.users.models import ServiceUser

from .service import ContentBlockService, EmailTemplateService, get_supported_variables, NotificationTemplateAdminService
from .schemas import (
    ContentBlockCreate,
    ContentBlockUpdate,
    ContentBlockResponse,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
)


router = APIRouter(prefix="/admin/cms", tags=["Admin CMS"])
public_router = APIRouter(prefix="/cms", tags=["CMS"])


def get_block_service(db: Session = Depends(get_session)) -> ContentBlockService:
    return ContentBlockService(db)


def get_email_service(db: Session = Depends(get_session)) -> EmailTemplateService:
    return EmailTemplateService(db)


def get_notification_admin_service(db: Session = Depends(get_session)) -> NotificationTemplateAdminService:
    return NotificationTemplateAdminService(db)


@router.get("/blocks", response_model=List[ContentBlockResponse])
def list_blocks(
    category: Optional[str] = Query(None),
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    items = service.list_blocks(category=category)
    return [ContentBlockResponse.model_validate(it) for it in items]


@router.get("/blocks/{block_id}", response_model=ContentBlockResponse)
def get_block(
    block_id: int,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    entity = service.get(block_id)
    return ContentBlockResponse.model_validate(entity)


@router.post("/blocks", response_model=ContentBlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(
    payload: ContentBlockCreate,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    entity = service.create(payload.model_dump())
    return ContentBlockResponse.model_validate(entity)


@router.put("/blocks/{block_id}", response_model=ContentBlockResponse)
def update_block(
    block_id: int,
    payload: ContentBlockUpdate,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    entity = service.update(block_id, payload.model_dump(exclude_unset=True))
    return ContentBlockResponse.model_validate(entity)


@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: int,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    service.delete(block_id)
    return None


@router.post("/blocks/import-missing", response_model=List[ContentBlockResponse])
def import_missing_blocks(
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    items = service.import_missing_defaults()
    return [ContentBlockResponse.model_validate(it) for it in items]


@router.post("/blocks/load-terms-default", response_model=ContentBlockResponse)
def load_terms_default(
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: ContentBlockService = Depends(get_block_service),
):
    entity = service.ensure_terms_default()
    return ContentBlockResponse.model_validate(entity)


@router.get("/email-templates", response_model=List[EmailTemplateResponse])
def list_email_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: EmailTemplateService = Depends(get_email_service),
):
    items, _ = service.search_templates(skip=skip, limit=limit, search=search)
    return [EmailTemplateResponse.model_validate(it) for it in items]


@router.post("/email-templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_email_template(
    payload: EmailTemplateCreate,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: EmailTemplateService = Depends(get_email_service),
):
    entity = service.create(payload.model_dump())
    return EmailTemplateResponse.model_validate(entity)


@router.put("/email-templates/{template_id}", response_model=EmailTemplateResponse)
def update_email_template(
    template_id: int,
    payload: EmailTemplateUpdate,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: EmailTemplateService = Depends(get_email_service),
):
    entity = service.update(template_id, payload.model_dump(exclude_unset=True))
    return EmailTemplateResponse.model_validate(entity)


@router.delete("/email-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(
    template_id: int,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: EmailTemplateService = Depends(get_email_service),
):
    service.delete(template_id)
    return None


@router.post("/email-templates/load-defaults", response_model=EmailTemplateResponse)
def load_default_email_templates(
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: EmailTemplateService = Depends(get_email_service),
):
    """Seed the default invitation email template into the DB (idempotent)."""
    entity = service.ensure_invitation_default()
    return EmailTemplateResponse.model_validate(entity)


@router.post("/email-templates/import-missing", response_model=List[EmailTemplateResponse])
def import_missing_email_templates(
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: EmailTemplateService = Depends(get_email_service),
):
    """Import/Create all standard email templates if missing (idempotent)."""
    items = service.ensure_all_defaults()
    return [EmailTemplateResponse.model_validate(it) for it in items]


@router.get("/variables")
def get_variables(
    current_user: ServiceUser = Depends(require_role("super_admin")),
):
    return get_supported_variables()


# Notification templates CRUD (admin)
@router.get("/notification-templates")
def list_notification_templates(
    template_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: NotificationTemplateAdminService = Depends(get_notification_admin_service),
):
    items = service.list(template_type=template_type, category=category)
    return items


@router.post("/notification-templates", status_code=status.HTTP_201_CREATED)
def create_notification_template(
    payload: dict,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: NotificationTemplateAdminService = Depends(get_notification_admin_service),
):
    return service.create(payload)


@router.put("/notification-templates/{template_id}")
def update_notification_template(
    template_id: int,
    payload: dict,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: NotificationTemplateAdminService = Depends(get_notification_admin_service),
):
    return service.update(template_id, payload)


@router.delete("/notification-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_template(
    template_id: int,
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: NotificationTemplateAdminService = Depends(get_notification_admin_service),
):
    service.delete(template_id)
    return None


@router.post("/notification-templates/import-missing")
def import_missing_notification_templates(
    current_user: ServiceUser = Depends(require_role("super_admin")),
    service: NotificationTemplateAdminService = Depends(get_notification_admin_service),
):
    """Import default notification templates (email + slack) if missing (idempotent)."""
    return service.import_missing_defaults()


# Public CMS endpoints (read-only)
@public_router.get("/terms-of-service")
def get_terms_of_service(
    service: ContentBlockService = Depends(get_block_service),
):
    blk = service.get_by_key("terms_of_service")
    # Auto-heal: if missing or empty, ensure default is present
    if not blk or not str(getattr(blk, "html_content", "") or "").strip():
        blk = service.ensure_terms_default()
    # We store Markdown in html_content; FE renders via markdown renderer
    return {
        "title": blk.title,
        "content_md": blk.html_content,
        "updated_at": blk.updated_at.isoformat() if getattr(blk, 'updated_at', None) else None,
    }


@public_router.get("/blocks/{key}")
def get_public_block_by_key(
    key: str,
    category: Optional[str] = Query(None),
    service: ContentBlockService = Depends(get_block_service),
):
    """Fetch a CMS content block by key for public/tenant-facing use.

    Returns 404 if the block is not found. The payload includes the title and
    raw HTML content which the frontend renders directly in a safe container.
    """
    blk = service.get_by_key(key, category=category)
    if not blk:
        raise HTTPException(status_code=404, detail="Content block not found")
    return {
        "key": blk.key,
        "category": blk.category,
        "title": blk.title,
        "html_content": blk.html_content,
        "updated_at": blk.updated_at.isoformat() if getattr(blk, 'updated_at', None) else None,
    }
