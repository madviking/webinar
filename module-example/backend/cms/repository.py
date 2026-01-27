"""Repositories for CMS content blocks and email templates."""
from __future__ import annotations

from typing import List, Optional, Tuple
from sqlmodel import Session, select
from sqlalchemy import func

from app.shared.repositories.base import BaseRepository
from .models import ServiceContentBlock, ServiceEmailTemplate


class ContentBlockRepository(BaseRepository[ServiceContentBlock]):
    def __init__(self, db: Session):
        super().__init__(db, ServiceContentBlock)

    def get_by_key(self, key: str, category: Optional[str] = None) -> Optional[ServiceContentBlock]:
        stmt = select(ServiceContentBlock).where(ServiceContentBlock.key == key)
        if category:
            stmt = stmt.where(ServiceContentBlock.category == category)
        return self.db.exec(stmt).first()

    def list_all(self, *, category: Optional[str] = None) -> List[ServiceContentBlock]:
        stmt = select(ServiceContentBlock)
        if category:
            stmt = stmt.where(ServiceContentBlock.category == category)
        stmt = stmt.order_by(ServiceContentBlock.id)
        return list(self.db.exec(stmt).all())


class EmailTemplateRepository(BaseRepository[ServiceEmailTemplate]):
    def __init__(self, db: Session):
        super().__init__(db, ServiceEmailTemplate)

    def get_by_name(self, name: str) -> Optional[ServiceEmailTemplate]:
        stmt = select(ServiceEmailTemplate).where(ServiceEmailTemplate.name == name)
        return self.db.exec(stmt).first()

    def search(self, *, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Tuple[List[ServiceEmailTemplate], int]:
        base = select(ServiceEmailTemplate)
        if search:
            like = f"%{search}%"
            base = base.where(ServiceEmailTemplate.name.ilike(like))
        total_stmt = select(func.count()).select_from(base.subquery())
        total = int(self.db.exec(total_stmt).one())
        items = list(self.db.exec(base.order_by(ServiceEmailTemplate.id).offset(skip).limit(limit)).all())
        return items, total
