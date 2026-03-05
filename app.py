import uvicorn

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse


from Services.Auth.router import auth_router
from Services.User.router import user_router
from Shared.Config import Settings

settings = Settings()

app = FastAPI(
    title="Effective Mobile Project",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
    swagger_ui_parameters={
        "persistAuthorization": "true",
        "defaultModelRendering": "model",
    },
    debug=True,
)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://0.0.0.0:8010",
    "http://localhost:8010",
    "http://localhost:3000",
    "http://127.0.0.1:51022",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

@router.get("/ping", tags=["Server"])
async def ping_server():
    return "pong"

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/api/v1/auth/", status_code=307)


app.include_router(router)

#user_router
app.include_router(
    user_router,
    prefix=f"{settings.api_prefix}/users"
)

#auth_router
app.include_router(
    auth_router,
    prefix=f"{settings.api_prefix}/auth"
)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8010,
        reload=True
    )
