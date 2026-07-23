import pytest
from septima_automation.social.base import SocialPublisher


class DummyClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    async def get(self, url, params=None):
        self.calls.append(("get", url, params))

        class Response:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        return Response(self.payload)


@pytest.mark.asyncio
async def test_resolve_account_context_prefers_matching_page():
    class Publisher(SocialPublisher):
        async def publish(self, video_path, caption, video_url=None):
            return None

        async def check_credentials(self):
            return True

    client = DummyClient(
        {
            "data": [
                {
                    "id": "page-1",
                    "access_token": "page-token-1",
                    "instagram_business_account": {"id": "ig-1"},
                },
                {
                    "id": "page-2",
                    "access_token": "page-token-2",
                    "instagram_business_account": {"id": "ig-2"},
                },
            ]
        }
    )
    publisher = Publisher()

    page_id, page_token, instagram_id = await publisher.resolve_account_context(
        client,
        "user-token",
        page_id="page-2",
    )

    assert page_id == "page-2"
    assert page_token == "page-token-2"
    assert instagram_id == "ig-2"
