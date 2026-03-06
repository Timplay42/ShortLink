from datetime import datetime
import uuid
from operator import length_hint
from typing import Optional, Any

from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

from Shared.Config import Settings

settings = Settings()

class PostBase(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime
    active: bool


class PostCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: str

    @field_validator('title', 'description')
    @classmethod
    def length_check(cls, value: Any, info: ValidationInfo) -> str | None:
        if value is None:
            return value

        length = None
        if info.field_name == "title":
            length = settings.project.length_title

        else:
            length = settings.project.length_description

        if len(value) > length:
            raise ValueError(f'{info.field_name} must be <= {length}')

        return value


class PostRead(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    active: Optional[bool] = None
