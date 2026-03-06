from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class LinkBase(BaseModel):
    original_url: str
    short_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    count_redirect: int
    created_at: datetime
    updated_at: datetime
    active: bool


class LinkRead(LinkBase):
    pass


class LinkStats(BaseModel):
    original_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    count_redirect: int
    created_at: datetime
    updated_at: datetime
    active: bool


class LinkCreate(BaseModel):
    original_url: str
    title: Optional[str] = None
    description: Optional[str] = None


class LinkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None