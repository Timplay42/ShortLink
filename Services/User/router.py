import uuid
from typing import List

from fastapi import APIRouter, Depends

from Services.Auth.dependencies import ensure_self_or_admin, require_permission
from Services.Auth.permissions import USER_CREATE, USER_MANAGE_ANY, USER_READ
from Services.User.schema import UserRead, UserCreate, UserUpdate
from Services.User.service import user_service_dep

user_router = APIRouter(tags=["User"])


@user_router.get('/all', description='get all user', response_model=List[UserRead])
async def get_all_users(
    _: UserRead = Depends(ensure_self_or_admin),
    service_user=user_service_dep,
):
    return await service_user.all()


@user_router.post(
    "/create_user", name="create user", response_model=UserRead
)
async def create_user(
    user_data: UserCreate,
    _: UserRead = Depends(require_permission(USER_CREATE)),
    service_user=user_service_dep
):
    return await service_user.create_user(user_data)


@user_router.delete("/{user_id}", name="delete user", status_code=200)
async def delete_user(
    user_id: uuid.UUID,
    _: UserRead = Depends(ensure_self_or_admin),
    service_user=user_service_dep,
):
    return await service_user.delete_user(user_id)


@user_router.patch("/{user_id}", name="update user", response_model=UserRead)
async def update_teacher(
    user_id: uuid.UUID,
    update_data: UserUpdate,
    _: UserRead = Depends(ensure_self_or_admin),
    service_user=user_service_dep,
):
    return await service_user.update_user(user_id, update_data)


@user_router.post("/{user_id}/roles/{role_name}", response_model=UserRead)
async def assign_role(
    user_id: uuid.UUID,
    role_name: str,
    _: UserRead = Depends(require_permission(USER_MANAGE_ANY)),
    service_user=user_service_dep,
):
    return await service_user.assign_role(user_id=user_id, role_name=role_name)
