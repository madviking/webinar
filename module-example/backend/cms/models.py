"""CMS models for content blocks and email templates."""
from __future__ import annotations

from typing import List, Optional
from sqlmodel import Field, Column, JSON
import sqlalchemy as sa
from app.shared.base_model import BaseServiceModel


class ServiceContentBlock(BaseServiceModel, table=True):
    """Generic content block for admin-managed HTML snippets.

    Examples: service welcome texts, dashboard introductory text.
    """
    __tablename__ = "service_cms_blocks"

    key: str = Field(unique=True, index=True, max_length=100)
    category: str = Field(default="content", index=True, max_length=100)
    title: str = Field(max_length=255)
    html_content: str = Field(sa_column=Column("html_content", sa.Text()))
    description: Optional[str] = Field(default=None, max_length=255)
    variables: List[str] = Field(default_factory=list, sa_column=Column(JSON))


class ServiceEmailTemplate(BaseServiceModel, table=True):
    """Admin-managed email templates with subject and HTML body."""
    __tablename__ = "service_email_templates"

    name: str = Field(unique=True, index=True, max_length=100)
    category: str = Field(max_length=100)  # invitation, digest, reset, generic
    subject_template: str = Field(max_length=255)
    body_html: str = Field(sa_column=Column("body_html", sa.Text()))
    variables: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
