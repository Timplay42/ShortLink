import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from Services.Auth.permissions import USER_MANAGE_ANY
from Services.Auth.service import AuthorizationService
from Services.User.model import User
from Shared.DBSession import AsyncDatabase
from Shared.UtilsJwt import get_current_active_auth_user

async def get_authorization_service(
    session: AsyncSession = Depends(AsyncDatabase.get_session),
) -> AuthorizationService:
    return AuthorizationService(session=session)


def require_permission(permission_code: str):
    async def dependency(
        current_user: User = Depends(get_current_active_auth_user),
        authorization_service: AuthorizationService = Depends(get_authorization_service),
    ) -> User:
        is_allowed = await authorization_service.user_has_permission(
            user_id=current_user.id,
            permission_code=permission_code,
        )
        if not is_allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return dependency



async def ensure_self_or_admin(
    user_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_active_auth_user),
    authorization_service: AuthorizationService = Depends(get_authorization_service),
) -> User:
    if user_id is not None:
        if current_user.id == user_id:
            return current_user

    is_admin = await authorization_service.user_has_permission(
        user_id=current_user.id,
        permission_code=USER_MANAGE_ANY,
    )
    if is_admin:
        return current_user

    raise HTTPException(status_code=403, detail="Forbidden")
