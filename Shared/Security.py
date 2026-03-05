import bcrypt


async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode("utf-8")


async def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode("utf-8"))


if __name__ == "__main__":
    import asyncio
    print(asyncio.run(hash_password('admin')))