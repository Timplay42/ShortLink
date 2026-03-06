from contextlib import asynccontextmanager

import uvicorn
import redis.asyncio as redis
import logging

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from Shared.Config import Settings
from Services.Link.router import link_router
from Services.Post.router import post_router

settings = Settings()

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('Application startup')
    redis_client = redis.from_url(settings.redis.connect_path, db=settings.redis.db)
    app.state.redis_client = redis_client

    yield

    await redis_client.close()
    logging.info('Application end')


app = FastAPI(
    title="ShortLink",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
    lifespan=lifespan,
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

app.include_router(router)
app.include_router(post_router)
app.include_router(link_router)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8010,
        reload=True
    )
