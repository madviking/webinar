"""Services for CMS content blocks and email templates."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.crud_base import BaseService
from .models import ServiceContentBlock, ServiceEmailTemplate
from .repository import ContentBlockRepository, EmailTemplateRepository
from .seeds.loader import DEFAULT_CONTENT_BLOCKS, DEFAULT_NOTIFICATION_TEMPLATES, render_email_html
from app.notifications.repository import NotificationRepository
from app.notifications.models import NotificationTemplate


class ContentBlockService(BaseService[ServiceContentBlock]):
    model = ServiceContentBlock
    repo_class = ContentBlockRepository

    def __init__(self, db: Session):
        super().__init__(db)

    @staticmethod
    def _normalize_category(raw: Optional[str]) -> str:
        category = (raw or "content").strip()
        return category or "content"

    def validate_create(self, data: Dict[str, Any]) -> None:
        key = (data.get("key") or "").strip()
        title = (data.get("title") or "").strip()
        html = (data.get("html_content") or "").strip()
        data["category"] = self._normalize_category(data.get("category"))
        if not key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="key is required")
        if not title:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title is required")
        if not html:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="html_content is required")
        if self.repo.get_by_key(key):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Block '{key}' already exists")

    def validate_update(self, entity: ServiceContentBlock, updates: Dict[str, Any]) -> None:
        if "key" in updates and updates["key"] is not None:
            new_key = updates["key"].strip()
            if not new_key:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="key cannot be empty")
            existing = self.repo.get_by_key(new_key)
            if existing and existing.id != entity.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="key already exists")
        if "category" in updates and updates["category"] is not None:
            updates["category"] = self._normalize_category(updates.get("category"))
        if "html_content" in updates and updates["html_content"] is not None:
            if not str(updates["html_content"]).strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="html_content cannot be empty")

    def list_blocks(self, *, category: Optional[str] = None) -> List[ServiceContentBlock]:
        return self.repo.list_all(category=category)

    def get_by_key(self, key: str, *, category: Optional[str] = None) -> Optional[ServiceContentBlock]:
        return self.repo.get_by_key(key, category=category)

    # --- Defaults seeding for content blocks ---
    def _default_blocks(self) -> List[ServiceContentBlock]:
        if not DEFAULT_CONTENT_BLOCKS:
            raise RuntimeError("CMS seed content blocks missing (cms/seeds/templates/content_blocks/defaults.json)")
        return [ServiceContentBlock(**data) for data in DEFAULT_CONTENT_BLOCKS]

    def import_missing_defaults(self) -> List[ServiceContentBlock]:
        """Create default content blocks if missing (idempotent)."""
        created: List[ServiceContentBlock] = []
        for default in self._default_blocks():
            existing = self.repo.get_by_key(default.key)
            if not existing:
                created.append(self.repo.create(default))
        return created

    def ensure_terms_default(self) -> ServiceContentBlock:
        """Create or update the ToS content block with default Markdown."""
        defaults = {blk.key: blk for blk in self._default_blocks()}
        tos = defaults["terms_of_service"]
        existing = self.repo.get_by_key("terms_of_service")
        if existing:
            existing.category = tos.category
            existing.title = tos.title
            existing.html_content = tos.html_content
            existing.description = tos.description
            existing.variables = tos.variables
            return self.repo.update(existing)
        else:
            return self.repo.create(tos)


class EmailTemplateService(BaseService[ServiceEmailTemplate]):
    model = ServiceEmailTemplate
    repo_class = EmailTemplateRepository

    def __init__(self, db: Session):
        super().__init__(db)

    def validate_create(self, data: Dict[str, Any]) -> None:
        name = (data.get("name") or "").strip()
        category = (data.get("category") or "").strip()
        subject = (data.get("subject_template") or "").strip()
        body_html = (data.get("body_html") or "").strip()
        if not name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name is required")
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category is required")
        if not subject:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="subject_template is required")
        if not body_html:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="body_html is required")
        if self.repo.get_by_name(name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Template '{name}' already exists")

    def validate_update(self, entity: ServiceEmailTemplate, updates: Dict[str, Any]) -> None:
        if "name" in updates and updates["name"] is not None:
            new_name = updates["name"].strip()
            if not new_name:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name cannot be empty")
            existing = self.repo.get_by_name(new_name)
            if existing and existing.id != entity.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="name already exists")
        if "subject_template" in updates and updates["subject_template"] is not None:
            if not str(updates["subject_template"]).strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="subject_template cannot be empty")
        if "body_html" in updates and updates["body_html"] is not None:
            if not str(updates["body_html"]).strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="body_html cannot be empty")

    def search_templates(self, *, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Tuple[List[ServiceEmailTemplate], int]:
        return self.repo.search(skip=skip, limit=limit, search=search)

    def ensure_invitation_default(self) -> ServiceEmailTemplate:
        """Create or update a sensible default invitation email template from built-ins.

        Uses EmailTemplates to generate an HTML with placeholder tokens, not concrete values.
        """
        from app.email.templates import EmailTemplates  # local import to avoid cycles

        existing = self.repo.get_by_name("invitation")

        # Build placeholder context to keep tokens in place after replacement
        placeholder_ctx = {
            "user_name": "{user_name}",
            "inviter_name": "{inviter_name}",
            "tenant_name": "{tenant_name}",
            "accept_url": "{accept_url}",
            "temporary_password": "{temporary_password}",
            "email": "{email}",
        }
        html = EmailTemplates(self.db).render_invitation(placeholder_ctx)

        subject = "Welcome to Queast — invited by {inviter_name}"

        if existing:
            existing.category = "invitation"
            existing.subject_template = subject
            existing.body_html = html
            existing.variables = [
                "user_name",
                "inviter_name",
                "tenant_name",
                "accept_url",
                "temporary_password",
                "email",
            ]
            return self.repo.update(existing)
        else:
            entity = ServiceEmailTemplate(
                name="invitation",
                category="invitation",
                subject_template=subject,
                body_html=html,
                variables=[
                    "user_name",
                    "inviter_name",
                    "tenant_name",
                    "accept_url",
                    "temporary_password",
                    "email",
                ],
                is_active=True,
            )
            return self.repo.create(entity)

    def ensure_daily_digest_default(self) -> ServiceEmailTemplate:
        """Create or update default daily digest email template.

        The body uses dynamic placeholders and {{assignments_html}} so that the
        rendered email always reflects the current simplified list markup from
        EmailTemplates._augment_digest_context().
        """
        from app.email.templates import EmailTemplates  # local import to avoid cycles

        existing = self.repo.get_by_name("daily_digest")

        style = EmailTemplates(self.db).notification_style
        html = render_email_html("email_templates/daily_digest.html", style=style)
        if not html:
            raise RuntimeError("CMS seed email template missing (cms/seeds/templates/email_templates/daily_digest.html)")

        subject = "Queast digest — {count} new opportunities"

        if existing:
            existing.category = "daily_digest"
            existing.subject_template = subject
            existing.body_html = html
            existing.variables = [
                "user_name",
                "count",
                "assignments",
                "app_url",
                "assignments_html",
                "smart_signals",
                "smart_signals_total_open",
                "smart_signals_section_html",
            ]
            return self.repo.update(existing)
        else:
            entity = ServiceEmailTemplate(
                name="daily_digest",
                category="daily_digest",
                subject_template=subject,
                body_html=html,
                variables=[
                    "user_name",
                    "count",
                    "assignments",
                    "app_url",
                    "assignments_html",
                    "smart_signals",
                    "smart_signals_total_open",
                    "smart_signals_section_html",
                ],
                is_active=True,
            )
            return self.repo.create(entity)

    def ensure_weekly_digest_default(self) -> ServiceEmailTemplate:
        """Create or update default weekly digest email template from built-ins.

        Uses the daily digest renderer for initial content; admins can customize
        via CMS. Subject reflects weekly period.
        """
        from app.email.templates import EmailTemplates  # local import to avoid cycles

        existing = self.repo.get_by_name("weekly_digest")

        templates = EmailTemplates(self.db)
        style = templates.notification_style
        html = render_email_html("email_templates/weekly_digest.html", style=style)
        if not html:
            raise RuntimeError("CMS seed email template missing (cms/seeds/templates/email_templates/weekly_digest.html)")

        subject = "Your Weekly Jobs Digest - {count} new opportunities"

        if existing:
            existing.category = "weekly_digest"
            existing.subject_template = subject
            existing.body_html = html
            existing.variables = [
                "user_name",
                "count",
                "assignments",
                "app_url",
                "assignments_html",
                "smart_signals",
                "smart_signals_total_open",
                "smart_signals_section_html",
            ]
            return self.repo.update(existing)
        else:
            entity = ServiceEmailTemplate(
                name="weekly_digest",
                category="weekly_digest",
                subject_template=subject,
                body_html=html,
                variables=[
                    "user_name",
                    "count",
                    "assignments",
                    "app_url",
                    "assignments_html",
                    "smart_signals",
                    "smart_signals_total_open",
                    "smart_signals_section_html",
                ],
                is_active=True,
            )
            return self.repo.create(entity)

    def ensure_password_reset_default(self) -> ServiceEmailTemplate:
        """Create or update default password reset email template from built-ins."""
        from app.email.templates import EmailTemplates  # local import to avoid cycles

        existing = self.repo.get_by_name("password_reset")

        placeholder_ctx = {
            "user_name": "{user_name}",
            "reset_url": "{reset_url}",
        }
        html = EmailTemplates(self.db).render_password_reset(placeholder_ctx)

        subject = "Password Reset Request - Queast"

        if existing:
            existing.category = "password_reset"
            existing.subject_template = subject
            existing.body_html = html
            existing.variables = [
                "user_name",
                "reset_url",
            ]
            return self.repo.update(existing)
        else:
            entity = ServiceEmailTemplate(
                name="password_reset",
                category="password_reset",
                subject_template=subject,
                body_html=html,
                variables=[
                    "user_name",
                    "reset_url",
                ],
                is_active=True,
            )
            return self.repo.create(entity)

    def ensure_usage_alert_default(self) -> ServiceEmailTemplate:
        """Create or update default usage alert email template from built-ins."""
        from app.email.templates import EmailTemplates  # local import to avoid cycles

        existing = self.repo.get_by_name("usage_alert")

        placeholder_ctx = {
            "tenant_name": "{tenant_name}",
            "usage_type": "{usage_type}",
            "percentage": "{percentage}",
            "current_usage": "{current_usage}",
            "limit": "{limit}",
            "remaining": "{remaining}",
            "app_url": "{app_url}",
        }
        html = EmailTemplates(self.db).render_usage_alert(placeholder_ctx)

        subject = "Usage Alert: {usage_type} at {percentage}% of limit"

        if existing:
            existing.category = "usage_alert"
            existing.subject_template = subject
            existing.body_html = html
            existing.variables = [
                "tenant_name",
                "usage_type",
                "percentage",
                "current_usage",
                "limit",
                "remaining",
                "app_url",
            ]
            return self.repo.update(existing)
        else:
            entity = ServiceEmailTemplate(
                name="usage_alert",
                category="usage_alert",
                subject_template=subject,
                body_html=html,
                variables=[
                    "tenant_name",
                    "usage_type",
                    "percentage",
                    "current_usage",
                    "limit",
                    "remaining",
                    "app_url",
                ],
                is_active=True,
            )
            return self.repo.create(entity)

    def ensure_all_defaults(self) -> List[ServiceEmailTemplate]:
        """Ensure all standard email templates exist (idempotent)."""
        results: List[ServiceEmailTemplate] = []
        results.append(self.ensure_invitation_default())
        results.append(self.ensure_daily_digest_default())
        results.append(self.ensure_weekly_digest_default())
        results.append(self.ensure_password_reset_default())
        results.append(self.ensure_usage_alert_default())
        return results


def get_supported_variables() -> dict:
    """Return supported variables for known template categories."""
    return {
        "invitation": [
            "user_name",
            "inviter_name",
            "tenant_name",
            "accept_url",
            "temporary_password",
            "email",
        ],
        "daily_digest": [
            "user_name",
            "count",
            "app_url",
            "assignments",
        ],
        "usage_alert": [
            "tenant_name",
            "usage_type",
            "percentage",
            "current_usage",
            "limit",
            "remaining",
            "app_url",
        ],
        "password_reset": [
            "user_name",
            "reset_url",
        ],
        "notification_generic": [
            "recipient_name",
            "notification_title",
            "notification_message",
            "action_url",
            "action_text",
            "sender_name",
            "current_year",
        ],
    }


class NotificationTemplateAdminService:
    """Thin admin service around NotificationRepository for NotificationTemplate CRUD."""
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)

    def list(self, template_type: Optional[str] = None, category: Optional[str] = None) -> List[NotificationTemplate]:
        return self.repo.get_templates_by_criteria(template_type=template_type, category=category)

    def get(self, template_id: int) -> NotificationTemplate:
        entity = self.db.get(NotificationTemplate, template_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Template not found")
        return entity

    def create(self, data: Dict[str, Any]) -> NotificationTemplate:
        # Basic validation similar to NotificationService
        required = ['name', 'template_type', 'category', 'body_template']
        for f in required:
            if not data.get(f):
                raise HTTPException(status_code=400, detail=f"Missing required field: {f}")
        if data['template_type'] not in {'email', 'slack'}:
            raise HTTPException(status_code=400, detail="Invalid template type")
        if data['template_type'] == 'email' and not data.get('subject_template'):
            raise HTTPException(status_code=400, detail="Email templates must have a subject_template")
        return self.repo.create_template(data)

    def update(self, template_id: int, updates: Dict[str, Any]) -> NotificationTemplate:
        entity = self.get(template_id)
        for k, v in updates.items():
            if v is not None:
                setattr(entity, k, v)
        return self.repo.update_template(entity)

    def delete(self, template_id: int) -> None:
        entity = self.get(template_id)
        self.db.delete(entity)
        self.db.commit()

    def import_missing_defaults(self) -> List[NotificationTemplate]:
        """Ensure a baseline set of notification templates exist (idempotent)."""
        created: List[NotificationTemplate] = []
        existing_by_key: dict[tuple[str, str], NotificationTemplate] = {}

        # Helper to check existence by (name, template_type)
        def _get(name: str, template_type: str) -> Optional[NotificationTemplate]:
            key = (name, template_type)
            if key in existing_by_key:
                return existing_by_key[key]
            tpl = self.repo.get_template_by_name(name, template_type)
            if tpl:
                existing_by_key[key] = tpl
            return tpl

        if not DEFAULT_NOTIFICATION_TEMPLATES:
            raise RuntimeError("CMS seed notification templates missing (cms/seeds/templates/notification_templates/defaults.json)")

        for data in DEFAULT_NOTIFICATION_TEMPLATES:
            name = data["name"]
            template_type = data["template_type"]
            if not _get(name, template_type):
                created.append(self.repo.create_template(data))

        return created
