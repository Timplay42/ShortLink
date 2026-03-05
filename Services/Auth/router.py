from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from Services.Auth.dependencies import require_permission
from Services.Auth.permissions import USER_MANAGE_ANY
from Services.Auth.schema import TokenInfo
from Shared.UtilsJwt import validate_auth_user, get_current_active_auth_user, create_access_token, \
    create_refresh_token, get_current_auth_refresh_user

from Services.User.schema import UserCreate, UserRead
from Services.User.service import UserService
from Shared.DBSession import AsyncDatabase

auth_router = APIRouter(tags=["Auth"])

templates = Jinja2Templates(directory="Web/Templates")


@auth_router.get("/", status_code=status.HTTP_200_OK)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.get("/register", status_code=status.HTTP_200_OK)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@auth_router.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, _: UserRead = Depends(get_current_active_auth_user)):
    return templates.TemplateResponse("profile.html", {"request": request})


@auth_router.get("/admin", status_code=status.HTTP_200_OK)
async def admin_page(request: Request, _: UserRead = Depends(require_permission(USER_MANAGE_ANY))):
    return templates.TemplateResponse("admin.html", {"request": request})


@auth_router.get("/logout", status_code=200)
async def logout_page(
        request: Request,
):
    try:
        response = JSONResponse(content={"detail": "Logged out"})
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    lastname: str | None = Form(None),
    description: str | None = Form(None),
    session: AsyncSession = Depends(AsyncDatabase.get_session),
):
    user_service = UserService(session=session)
    existing_user = await user_service.get_user_by_username(username=username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username is already taken")

    user_create = UserCreate(
        name=name,
        lastname=lastname,
        username=username,
        password=password,
        description=description,
    )
    created_user = await user_service.create_user(user_create)
    return created_user


@auth_router.post("/login")
async def auth_user_issue_jwt(
        user: UserRead = Depends(validate_auth_user)
):
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    token_info = TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )
    response = JSONResponse(content=token_info.model_dump())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        secure=False, # в проде на true менять надо
        samesite="lax", # в проде на none
        httponly=True
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=False, # в проде на true менять надо
        samesite="lax", # в проде на none
        httponly=True
    )
    return response


@auth_router.post("/login_with_form/{username}/{password}")
async def auth_user_issue_jwt_path(
        username: str,
        password: str
):
    user: UserRead = await validate_auth_user(username, password)
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    token_info = TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )
    response = JSONResponse(content=token_info.model_dump())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        secure=False, # в проде на true менять надо
        samesite="lax", # в проде на none
        httponly=True
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=False, # в проде на true менять надо
        samesite="lax", # в проде на none
        httponly=True
    )
    return response


@auth_router.post("/refresh")
async def refresh_token(user: UserRead = Depends(get_current_auth_refresh_user)):
    try:
        if not user:
            raise HTTPException(401, "invalid token or user not found")

        access_token = await create_access_token(user)

        token_info = {
            "access_token": access_token,
            "token_type": "bearer"
        }
        response = JSONResponse(content=token_info)
        response.set_cookie(
            key="access_token",
            value=access_token,
            secure=False, # в проде поменять на true
            samesite="lax", # в проде поменять на none
            httponly=True
        )

        return response

    except HTTPException as e:
        if e.detail == 'Token expired':
            pass

        else:
            raise HTTPException(401, "invalid token")


@auth_router.get("/me")
async def auth_user_me(
        user: UserRead = Depends(get_current_active_auth_user)
):
    return user
