import json
from typing import List

from fastapi import APIRouter, Request
from redis.asyncio import Redis

from Services.Post.schema import PostRead, PostCreate, PostUpdate
from Services.Post.service import post_service
from Shared.Config import Settings

settings = Settings()

post_router = APIRouter(prefix=f'{settings.api_prefix}/post', tags=["Post"])


@post_router.post('/create', name='create post', response_model=PostRead)
async def create_post(post_data: PostCreate, post_service=post_service):
    return await post_service.create(post_data.model_dump())


@post_router.patch('/update/{post_id}', name='update post', response_model=PostRead)
async def update_post(post_id: str, request: Request, post_data: PostUpdate, post_service=post_service):
    return await post_service.update_post_cached(post_id, post_data.model_dump(), request.app.state.redis_client)


@post_router.delete('/delete/{post_id}', name='delete post', status_code=200)
async def delete_post(post_id: str, request: Request, post_service=post_service):
    redis_client: Redis = request.app.state.redis_client
    await redis_client.delete(f"post:{post_id}")
    return await post_service.delete(post_id)


@post_router.get('/post/{post_id}', name='get post by id', response_model=PostRead)
async def get_post(post_id: str, request: Request, post_service=post_service):
    redis_client: Redis = request.app.state.redis_client
    cached_post = await redis_client.get(f"post:{post_id}")

    if cached_post is not None:
        cached_post_data = json.loads(cached_post)
        if isinstance(cached_post_data, dict):
            return PostRead(**cached_post_data)
        await redis_client.delete(f"post:{post_id}")

    return await post_service.get_post(post_id, redis_client)


@post_router.get('/posts', name='get posts', response_model=List[PostRead])
async def get_posts(post_service=post_service):
    return await post_service.all()
