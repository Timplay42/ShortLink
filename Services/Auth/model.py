from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Shared.BaseModel import Base

if TYPE_CHECKING:
    from Services.User.model import User


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
)


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    users: Mapped[list["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles", lazy="selectin"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles", lazy="selectin"
    )


class Permission(Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=role_permissions, back_populates="permissions", lazy="selectin"
    )
