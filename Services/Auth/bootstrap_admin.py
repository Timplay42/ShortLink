import asyncio
import os
import sys
import logging

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from Services.Auth.model import Role
from Services.Auth.seed import seed_permissions_and_roles
from Services.User.model import User
from Shared.DBSession import AsyncDatabase
from Shared.Security import hash_password

logging.basicConfig(level=logging.INFO)

async def wait_for_db(max_attempts: int, sleep_seconds: int) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            async with AsyncDatabase.get_session_maker()() as session:
                await session.execute(text("SELECT 1"))
            logging.info(f"[bootstrap] database is ready (attempt {attempt})")
            return
        except SQLAlchemyError as error:
            logging.info(f"[bootstrap] database is not ready (attempt {attempt}/{max_attempts}): {error}")
            await asyncio.sleep(sleep_seconds)
    raise RuntimeError("[bootstrap] database is not available after maximum attempts")


async def ensure_admin_user() -> None:
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin12345")
    admin_name = os.getenv("ADMIN_NAME", "System")
    admin_lastname = os.getenv("ADMIN_LASTNAME", "Admin")
    admin_description = os.getenv("ADMIN_DESCRIPTION", "Bootstrap administrator account")

    async with AsyncDatabase.get_session_maker()() as session:
        await seed_permissions_and_roles(session)

        admin_role = (
            await session.scalars(
                select(Role).where(Role.name == "admin", Role.active.is_(True))
            )
        ).first()
        if admin_role is None:
            raise RuntimeError("[bootstrap] role 'admin' not found")

        user = (
            await session.scalars(
                select(User)
                .options(selectinload(User.roles))
                .where(User.username == admin_username)
            )
        ).first()

        if user is None:
            user = User(
                name=admin_name,
                lastname=admin_lastname,
                username=admin_username,
                description=admin_description,
                password=await hash_password(admin_password),
                roles=[admin_role],
            )
            session.add(user)
            await session.commit()
            logging.info(f"[bootstrap] admin user '{admin_username}' created")
            return

        changed = False
        if admin_role not in user.roles:
            user.roles.append(admin_role)
            changed = True
        if not user.active:
            user.active = True
            changed = True

        if changed:
            await session.commit()
            logging.info(f"[bootstrap] admin user '{admin_username}' updated")
        else:
            logging.info(f"[bootstrap] admin user '{admin_username}' already configured")


async def main() -> None:
    max_attempts = int(os.getenv("DB_WAIT_MAX_ATTEMPTS", "30"))
    sleep_seconds = int(os.getenv("DB_WAIT_SLEEP_SECONDS", "2"))
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode == "wait":
        await wait_for_db(max_attempts=max_attempts, sleep_seconds=sleep_seconds)
        return
    if mode == "ensure":
        await ensure_admin_user()
        return
    if mode == "all":
        await wait_for_db(max_attempts=max_attempts, sleep_seconds=sleep_seconds)
        await ensure_admin_user()
        return

    raise ValueError(f"Unknown bootstrap mode: {mode}")


if __name__ == "__main__":
    asyncio.run(main())
