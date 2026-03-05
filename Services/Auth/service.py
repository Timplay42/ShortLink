import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Services.Auth.model import Permission, Role, role_permissions, user_roles


class AuthorizationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def user_has_permission(self, user_id: uuid.UUID, permission_code: str) -> bool:
        query = (
            select(Permission.id)
            .join(role_permissions, Permission.id == role_permissions.c.permission_id)
            .join(Role, Role.id == role_permissions.c.role_id)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(
                user_roles.c.user_id == user_id,
                Permission.code == permission_code,
                Permission.active.is_(True),
                Role.active.is_(True),
            )
            .limit(1)
        )
        found_permission_id = await self.session.scalar(query)
        return found_permission_id is not None
