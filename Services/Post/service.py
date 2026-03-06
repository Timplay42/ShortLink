import json

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

from Shared.DBSession import AsyncDatabase
from Shared.DBStandartFunc import BaseRepository
from Services.Post.model import Post

class PostService(BaseRepository):
    model = Post


    async def update_redis_cached_data(self, post_id: str, post_db_object: Post, redis_client: Redis):
        if post_db_object is None:
            await redis_client.delete(f"post:{post_id}")
            return

        post_json = json.dumps(jsonable_encoder(post_db_object))
        await redis_client.setex(
            f"post:{post_id}",
            3600,  # TTL 1 час
            post_json
        )

    async def get_post(self, post_id: str, redis_client: Redis):
        post_db_object: Post = await self.id(post_id)
        if post_db_object is None:
            await redis_client.delete(f"post:{post_id}")
            raise HTTPException(status_code=404, detail="not found")

        await self.update_redis_cached_data(post_id, post_db_object, redis_client)

        return post_db_object


    async def update_post_cached(self, post_id: str, post_data: dict, redis_client: Redis):
        post_db_object: Post = await self.update(post_id, post_data)

        await self.update_redis_cached_data(post_id, post_db_object, redis_client)

        return post_db_object


async def post_service_get(session=Depends(AsyncDatabase.get_session)):
    return PostService(session)


post_service: PostService = Depends(post_service_get)
