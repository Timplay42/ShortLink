import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str
    lastname: Optional[str] = None
    username: str
    password: str
    description: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    lastname: Optional[str] = None
    username: str
    description: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    description: Optional[str] = None
