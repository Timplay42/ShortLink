import jwt

from datetime import datetime, timedelta
from fastapi import Form, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from Services.User.schema import UserRead, UserBase
from Services.User.service import UserService
from Shared.Config import Settings
from Shared.DBSession import AsyncDatabase
from Shared.Security import validate_password

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.api_prefix}/auth/login')


async def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path,
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
):
    with open(private_key, "rb") as key_file:
        private_key = key_file.read()

    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire)

    return jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm)


async def create_jwt(
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
):
    jwt_payload = {'token_type': token_type}
    jwt_payload.update(token_data)
    return await encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(user: UserRead):
    jwt_payload = {
        "sub": str(user.id),
    }
    return await create_jwt(
        token_type='access',
        token_data=jwt_payload,
    )


async def create_refresh_token(user: UserRead):
    jwt_payload = {
        "sub": str(user.id)
    }
    return await create_jwt(
        token_type='refresh',
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    )


async def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path,
        algorithm: str = settings.auth_jwt.algorithm
):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    with open(public_key, "rb") as key_file:
        public_key = key_file.read()

    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=[algorithm]
        )
        if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
            raise HTTPException(
                status_code=401,
                detail="Token expired",
            )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def validate_auth_user(
        username: str = Form(),
        password: str = Form()
) -> UserRead:
    unauth_exception = HTTPException(
        status_code=401,
        detail="Unauthorized, invalid username or password",
    )
    user = None
    async for session in AsyncDatabase.get_session():
        user_service = UserService(session=session)
        user = await user_service.get_user_by_username(username)

    if not user:
        raise unauth_exception

    if not await validate_password(
        password,
        user.password
    ):
        raise unauth_exception

    if not user.active:
        raise HTTPException(status_code=401, detail="User is inactive")

    return user


async def decode_exc_token(token):
    payload = await decode_jwt(token)
    return payload


async def get_current_auth_refresh_user(
        request: Request,
) -> UserRead:
    token = request.cookies.get('refresh_token')
    payload = await decode_exc_token(token)

    user_id = payload['sub']

    user = None
    async for session in AsyncDatabase.get_session():
        user_service = UserService(session=session)
        user = await user_service.id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="invalid token")

    return user


async def get_current_auth_user(
        request: Request,
) -> UserRead:
    token = request.cookies.get('access_token')
    payload = await decode_exc_token(token)

    user_id = payload.get("sub")
    token_type = payload.get("token_type")

    if token_type != "access":
        raise HTTPException(status_code=401, detail="invalid token type")

    user = None
    async for session in AsyncDatabase.get_session():
        user_service = UserService(session)
        user = await user_service.id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="invalid token")

    return user



async def get_current_active_auth_user(
        user: UserRead = Depends(get_current_auth_user)
):
    if user.active:
        return user

    raise HTTPException(401, "User not active")
