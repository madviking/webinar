"""Pydantic schemas for CMS admin DTOs."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Literal


class ContentBlockCreate(BaseModel):
    key: str = Field(..., min_length=2, max_length=100)
    category: str = Field(default="content", min_length=2, max_length=100)
    title: str = Field(..., min_length=2, max_length=255)
    html_content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=255)
    variables: List[str] = Field(default_factory=list)


class ContentBlockUpdate(BaseModel):
    key: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    html_content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=255)
    variables: Optional[List[str]] = None


class ContentBlockResponse(BaseModel):
    id: int
    key: str
    category: str
    title: str
    html_content: str
    description: Optional[str] = None
    variables: List[str] = []
    model_config = ConfigDict(from_attributes=True)


class EmailTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=100)
    subject_template: str = Field(..., min_length=1, max_length=255)
    body_html: str = Field(..., min_length=1)
    variables: List[str] = Field(default_factory=list)
    is_active: bool = True


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    subject_template: Optional[str] = Field(None, min_length=1, max_length=255)
    body_html: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    subject_template: str
    body_html: str
    variables: List[str] = []
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# Notification Templates (wrapping app.notifications.models.NotificationTemplate)
class NotificationTemplateCreate(BaseModel):
    name: str
    template_type: Literal['email', 'slack']
    category: str
    subject_template: Optional[str] = None
    body_template: str
    variables: List[str] = Field(default_factory=list)
    is_active: bool = True
    is_default: bool = False


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[Literal['email', 'slack']] = None
    category: Optional[str] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class NotificationTemplateResponse(BaseModel):
    id: int
    name: str
    template_type: str
    category: str
    subject_template: Optional[str] = None
    body_template: str
    variables: List[str] = []
    is_active: bool
    is_default: bool
    model_config = ConfigDict(from_attributes=True)
