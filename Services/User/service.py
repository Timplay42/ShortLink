import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from Services.Auth.model import Role
from Services.User.model import User
from Services.User.schema import UserCreate, UserUpdate
from Shared.DBSession import AsyncDatabase
from Shared.DBStandartFunc import BaseRepository
from Shared.Security import hash_password


class UserService(BaseRepository):
    model = User

    async def get_user_by_username(self, username: str):
        return (
            await self.session.scalars(
                select(self.model)
                .where(self.model.username == username)
            )
        ).first()

    async def get_user_by_id(self, user_id: uuid.UUID):
        return await self.id(str(user_id))

    async def get_user_by_username_password(self, username: str, password: str):
        return (
            await self.session.scalars(
                select(self.model)
                .where(
                    and_(
                        self.model.username == username,
                        self.model.password == password,
                    )
                )
            )
        ).first()


    async def create_user(self, user: UserCreate):
        role = (
            await self.session.scalars(
                select(Role).where(Role.name == "user", Role.active.is_(True))
            )
        ).first()
        if role is None:
            raise HTTPException(status_code=500, detail="Default role 'user' is not configured")

        user_password_hash = await hash_password(user.password)
        user_model = User(
            name=user.name,
            lastname=user.lastname,
            username=user.username,
            password=user_password_hash,
            description=user.description,
            roles=[role],
        )
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        return user_model



    async def delete_user(self, user_id: uuid.UUID):
        update_data = {
            'active': False
        }
        await self.update(str(user_id), update_data)
        return 200


    async def update_user(self, user_id, user_update_data: UserUpdate):
        if user_update_data.password:
            user_update_data.password = await hash_password(user_update_data.password)

        return await self.update(user_id, user_update_data.model_dump())

    async def assign_role(self, user_id: uuid.UUID, role_name: str):
        user = (
            await self.session.scalars(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
        ).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        role = (
            await self.session.scalars(
                select(Role).where(Role.name == role_name, Role.active.is_(True))
            )
        ).first()
        if role is None:
            raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")

        if role not in user.roles:
            user.roles.append(role)
            await self.session.commit()
            await self.session.refresh(user)
        return user


async def get_user_service(
    session: AsyncSession = Depends(AsyncDatabase.get_session),
):
    return UserService(session)


user_service_dep: UserService = Depends(get_user_service)
