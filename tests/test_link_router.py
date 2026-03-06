import unittest
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from Services.Link.router import link_router
from Services.Link.service import get_link_service


class FakeLinkService:
    @staticmethod
    def _stats_payload():
        now = datetime.now(timezone.utc).isoformat()
        return {
            "original_url": "https://example.com",
            "title": "my title",
            "description": "my desc",
            "count_redirect": 3,
            "created_at": now,
            "updated_at": now,
            "active": True,
        }

    async def all(self):
        return []

    async def get_original_url(self, _short_id: str):
        return "https://example.com"

    async def create_url(self, _link_create_data):
        return "abcde"

    async def get_link(self, _short_id: str):
        return self._stats_payload()

    async def update(self, _short_id: str, _data: dict):
        return self._stats_payload()

    async def delete(self, _short_id: str):
        return 200


class LinkRouterTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(link_router)

        self.service = FakeLinkService()
        self.app.dependency_overrides[get_link_service] = lambda: self.service

        self.client = TestClient(self.app)

    def test_redirect_to_original(self):
        response = self.client.get("/api/v1/link/abcde", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "https://example.com")

    def test_create_short_url(self):
        response = self.client.post(
            "/api/v1/link/shorten",
            json={"original_url": "https://example.com", "title": None, "description": None},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "abcde")

    def test_stats_short_id(self):
        response = self.client.get("/api/v1/link/stats/abcde")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count_redirect"], 3)


if __name__ == "__main__":
    unittest.main()
