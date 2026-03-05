from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from Services.Auth.model import Permission, Role, role_permissions
from Services.Auth.permissions import USER_CREATE, USER_MANAGE_ANY, USER_READ


async def seed_permissions_and_roles(session: AsyncSession) -> None:
    default_permissions = [USER_READ, USER_CREATE, USER_MANAGE_ANY]

    existing_permissions = await session.scalars(
        select(Permission).where(Permission.code.in_(default_permissions))
    )
    existing_codes = {permission.code for permission in existing_permissions}

    for code in default_permissions:
        if code not in existing_codes:
            session.add(Permission(code=code))

    admin_role = (await session.scalars(select(Role).where(Role.name == "admin"))).first()
    user_role = (await session.scalars(select(Role).where(Role.name == "user"))).first()

    if admin_role is None:
        admin_role = Role(name="admin", description="Full access")
        session.add(admin_role)
    if user_role is None:
        user_role = Role(name="user", description="Limited user access")
        session.add(user_role)

    await session.flush()

    permissions = list(
        await session.scalars(
            select(Permission).where(Permission.code.in_(default_permissions))
        )
    )
    permission_ids_by_code = {permission.code: permission.id for permission in permissions}
    admin_permission_ids = {
        permission_ids_by_code[USER_READ],
        permission_ids_by_code[USER_CREATE],
        permission_ids_by_code[USER_MANAGE_ANY],
    }
    user_permission_ids = {permission_ids_by_code[USER_READ]}

    await _sync_role_permissions(session, admin_role.id, admin_permission_ids)
    await _sync_role_permissions(session, user_role.id, user_permission_ids)
    await session.commit()


async def _sync_role_permissions(session: AsyncSession, role_id, target_permission_ids: set) -> None:
    existing_permission_ids = set(
        await session.scalars(
            select(role_permissions.c.permission_id).where(role_permissions.c.role_id == role_id)
        )
    )

    to_add = target_permission_ids - existing_permission_ids
    to_remove = existing_permission_ids - target_permission_ids

    if to_add:
        await session.execute(
            insert(role_permissions),
            [{"role_id": role_id, "permission_id": permission_id} for permission_id in to_add],
        )

    if to_remove:
        await session.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id.in_(to_remove),
            )
        )
