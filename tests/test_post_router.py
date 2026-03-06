import json
import unittest
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Services.Post.router import post_router
from Services.Post.service import post_service_get


class FakeRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def setex(self, key: str, _ttl: int, value: str):
        self.store[key] = value

    async def delete(self, key: str):
        self.store.pop(key, None)


class FakePostService:
    def __init__(self):
        self.get_post_calls = 0
        self.last_update_call = None

    @staticmethod
    def _post_payload(post_id: str):
        now = datetime.now(timezone.utc).isoformat()
        return {
            "id": post_id,
            "title": "title",
            "description": "desc",
            "content": "content",
            "created_at": now,
            "updated_at": now,
            "active": True,
        }

    async def create(self, _data: dict):
        return self._post_payload(str(uuid.uuid4()))

    async def update_post_cached(self, post_id: str, post_data: dict, _redis):
        self.last_update_call = (post_id, post_data)
        payload = self._post_payload(post_id)
        payload.update({k: v for k, v in post_data.items() if v is not None})
        return payload

    async def delete(self, _post_id: str):
        return 200

    async def get_post(self, post_id: str, _redis):
        self.get_post_calls += 1
        return self._post_payload(post_id)

    async def all(self):
        return [self._post_payload(str(uuid.uuid4()))]


class PostRouterTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(post_router)

        self.redis = FakeRedis()
        self.service = FakePostService()

        self.app.state.redis_client = self.redis
        self.app.dependency_overrides[post_service_get] = lambda: self.service

        self.client = TestClient(self.app)

    def test_create_post(self):
        response = self.client.post(
            "/api/v1/post/create",
            json={"title": "hello", "description": None, "content": "world"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], "title")
        self.assertIn("id", body)

    def test_get_post_uses_cache(self):
        post_id = str(uuid.uuid4())
        cached = self.service._post_payload(post_id)
        self.redis.store[f"post:{post_id}"] = json.dumps(cached)

        response = self.client.get(f"/api/v1/post/post/{post_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], post_id)
        self.assertEqual(self.service.get_post_calls, 0)

    def test_get_post_falls_back_to_service(self):
        post_id = str(uuid.uuid4())

        response = self.client.get(f"/api/v1/post/post/{post_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], post_id)
        self.assertEqual(self.service.get_post_calls, 1)

    def test_get_post_ignores_invalid_cached_null(self):
        post_id = str(uuid.uuid4())
        self.redis.store[f"post:{post_id}"] = "null"

        response = self.client.get(f"/api/v1/post/post/{post_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], post_id)
        self.assertEqual(self.service.get_post_calls, 1)
        self.assertNotIn(f"post:{post_id}", self.redis.store)


if __name__ == "__main__":
    unittest.main()
