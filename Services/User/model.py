from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Services.Auth.model import user_roles
from Shared.BaseModel import Base

if TYPE_CHECKING:
    from Services.Auth.model import Role


class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    lastname: Mapped[str | None] = mapped_column(String(150), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=user_roles, back_populates="users", lazy="selectin"
    )
