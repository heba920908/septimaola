"""Tests for the social metrics insights report (InsightsClient + CLI)."""

import json
from pathlib import Path

import pytest
from septima_automation.social.insights import (
    InsightsClient,
    SocialMetricsReport,
    SocialMetricsSnapshot,
)


class FakeResponse:
    """Minimal httpx.Response stand-in for use with FakeAsyncClient."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx

            request = httpx.Request("GET", "https://example.test")
            raise httpx.HTTPStatusError(
                f"status {self.status_code}",
                request=request,
                response=httpx.Response(
                    self.status_code, request=request, json=self._payload
                ),
            )

    def json(self):
        return self._payload


class FakeAsyncClient:
    """Fake httpx.AsyncClient that dispatches canned responses by URL suffix."""

    def __init__(self, routes):
        # routes: list of (url_predicate, response_payload, status_code)
        self.routes = routes
        self.calls = []

    async def get(self, url, params=None):
        self.calls.append((url, params))
        for predicate, payload, status in self.routes:
            if predicate(url, params or {}):
                return FakeResponse(payload, status_code=status)
        raise AssertionError(f"No fake route matched: {url} {params}")

    async def aclose(self):
        pass


def make_client(routes) -> InsightsClient:
    client = InsightsClient(page_id="page-1", access_token="user-token")
    client.client = FakeAsyncClient(routes)
    return client


ACCOUNTS_ROUTE = (
    lambda url, params: url.endswith("/me/accounts"),
    {
        "data": [
            {
                "id": "page-1",
                "name": "Séptima Ola",
                "access_token": "page-token-1",
                "instagram_business_account": {"id": "ig-1"},
            }
        ]
    },
    200,
)


@pytest.mark.asyncio
async def test_build_snapshot_success_with_graceful_insights_fallback():
    """Snapshot assembles account + media data; missing insights permission
    degrades to None instead of raising."""

    routes = [
        ACCOUNTS_ROUTE,
        (
            lambda url, params: url == "https://graph.facebook.com/v25.0/page-1",
            {"id": "page-1", "name": "Séptima Ola", "fan_count": 358, "followers_count": 358},
            200,
        ),
        (
            lambda url, params: url.endswith("/page-1/posts"),
            {
                "error": {
                    "message": "(#10) requires pages_read_engagement",
                    "code": 10,
                }
            },
            400,
        ),
        (
            lambda url, params: url == "https://graph.facebook.com/v25.0/ig-1",
            {"id": "ig-1", "username": "septimaolaoficial", "followers_count": 251, "media_count": 117},
            200,
        ),
        (
            lambda url, params: url.endswith("/ig-1/media"),
            {
                "data": [
                    {
                        "id": "media-1",
                        "caption": "hello",
                        "timestamp": "2026-08-27T00:00:00+0000",
                        "media_type": "IMAGE",
                        "like_count": 10,
                        "comments_count": 2,
                        "permalink": "https://instagram.com/p/xyz",
                    }
                ]
            },
            200,
        ),
        (
            lambda url, params: url.endswith("/media-1/insights"),
            {"error": {"message": "(#10) missing permission", "code": 10}},
            400,
        ),
    ]

    client = make_client(routes)
    snapshot = await client.build_snapshot(limit=5)

    assert snapshot.facebook.fan_count == 358
    assert snapshot.facebook.followers_count == 358
    assert snapshot.facebook.posts == []
    assert "pages_read_engagement" in snapshot.facebook.posts_error

    assert snapshot.instagram.username == "septimaolaoficial"
    assert snapshot.instagram.followers_count == 251
    assert len(snapshot.instagram.media) == 1
    media_item = snapshot.instagram.media[0]
    assert media_item.like_count == 10
    assert media_item.comments_count == 2
    # Insights permission missing -> soft-failed to None, not raised
    assert media_item.reach is None
    assert media_item.total_interactions is None
    assert media_item.shares is None
    assert media_item.saved is None
    assert media_item.views is None

    assert snapshot.insights_permission_warning is not None
    assert "instagram_manage_insights" in snapshot.insights_permission_warning


@pytest.mark.asyncio
async def test_build_snapshot_with_working_insights_permission():
    """When insights succeed, values are populated (forward-compatible once
    instagram_manage_insights is granted)."""

    routes = [
        ACCOUNTS_ROUTE,
        (
            lambda url, params: url == "https://graph.facebook.com/v25.0/page-1",
            {"id": "page-1", "name": "Séptima Ola", "fan_count": 358, "followers_count": 358},
            200,
        ),
        (
            lambda url, params: url.endswith("/page-1/posts"),
            {"data": []},
            200,
        ),
        (
            lambda url, params: url == "https://graph.facebook.com/v25.0/ig-1",
            {"id": "ig-1", "username": "septimaolaoficial", "followers_count": 251, "media_count": 117},
            200,
        ),
        (
            lambda url, params: url.endswith("/ig-1/media"),
            {
                "data": [
                    {
                        "id": "media-1",
                        "caption": "hello",
                        "timestamp": "2026-08-27T00:00:00+0000",
                        "media_type": "IMAGE",
                        "like_count": 10,
                        "comments_count": 2,
                        "permalink": "https://instagram.com/p/xyz",
                    }
                ]
            },
            200,
        ),
        (
            lambda url, params: url.endswith("/media-1/insights"),
            {
                "data": [
                    {"name": "reach", "values": [{"value": 80}]},
                    {"name": "total_interactions", "values": [{"value": 12}]},
                    {"name": "shares", "values": [{"value": 3}]},
                    {"name": "saved", "values": [{"value": 1}]},
                    {"name": "views", "values": [{"value": 200}]},
                ]
            },
            200,
        ),
    ]

    client = make_client(routes)
    snapshot = await client.build_snapshot(limit=5)

    media_item = snapshot.instagram.media[0]
    assert media_item.reach == 80
    assert media_item.total_interactions == 12
    assert media_item.shares == 3
    assert media_item.saved == 1
    assert media_item.views == 200
    assert snapshot.insights_permission_warning is None
    assert snapshot.facebook.posts_error is None


def test_report_round_trip_appends_history(tmp_path: Path):
    """Simulate the CLI's load-append-write cycle across two runs."""

    output_path = tmp_path / "social-metrics.json"

    report = SocialMetricsReport()
    report.history.append(SocialMetricsSnapshot())
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    # Second run loads existing history and appends
    loaded = SocialMetricsReport.model_validate_json(output_path.read_text())
    loaded.history.append(SocialMetricsSnapshot())
    output_path.write_text(loaded.model_dump_json(indent=2), encoding="utf-8")

    final = SocialMetricsReport.model_validate_json(output_path.read_text())
    assert len(final.history) == 2


def test_report_handles_missing_file_gracefully(tmp_path: Path):
    """Loading a report from a nonexistent path should start fresh, not raise."""
    from septima_automation.insights_report import _load_existing_report

    report = _load_existing_report(tmp_path / "does-not-exist.json")
    assert report.history == []


def test_report_handles_corrupt_file_gracefully(tmp_path: Path):
    """Corrupt JSON should log a warning and start fresh rather than crash."""
    from septima_automation.insights_report import _load_existing_report

    bad_path = tmp_path / "corrupt.json"
    bad_path.write_text("not valid json {{{", encoding="utf-8")

    report = _load_existing_report(bad_path)
    assert report.history == []
