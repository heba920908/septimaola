"""Facebook Page and Instagram account insights/metrics collection.

This module fetches read-only engagement data for the JSON report generated
by ``insights_report.py``. It intentionally reuses
``SocialPublisher.resolve_account_context`` from ``social/base.py`` so it
follows the same Page ID / Page Access Token / Instagram Business Account ID
resolution logic as the existing ``FacebookPublisher`` and
``InstagramPublisher`` classes.

Permission/versioning note
---------------------------
``GET /{ig-media-id}/insights`` requires the ``instagram_manage_insights``
scope. If it is missing, the API returns::

    {"error": {"code": 10, "message": "(#10) Application does not have
    permission for this action"}}

Additionally, as of Graph API v22.0+ the legacy ``engagement`` and
``impressions`` metric names are rejected outright (independent of
permissions) — see ``config.INSTAGRAM_MEDIA_INSIGHTS_METRICS`` for the
current metric names (``total_interactions`` replaces ``engagement``).

``fetch_media_insights`` treats both permission errors and unsupported-
metric errors as soft failures: it logs a warning once per run and returns
an empty dict rather than raising, so a single bad/renamed metric never
crashes the whole report.
"""

import logging
import os
from datetime import date, datetime, time, timezone
from typing import List, Optional

import httpx
from pydantic import BaseModel, Field

from ..config import (
    DEFAULT_POSTS_LIMIT,
    FACEBOOK_API_VERSION,
    FACEBOOK_BASE_URL,
    INSTAGRAM_MEDIA_INSIGHTS_METRICS,
)
from .base import SocialPublisher

logger = logging.getLogger(__name__)


class PostMetric(BaseModel):
    """Engagement data for a single Facebook post or Instagram media item."""

    id: str
    permalink: Optional[str] = None
    caption: Optional[str] = None
    media_type: Optional[str] = None
    timestamp: Optional[str] = None
    like_count: Optional[int] = None
    comments_count: Optional[int] = None
    # Populated best-effort from GET /{id}/insights; null when the
    # `instagram_manage_insights` permission is unavailable or a metric is
    # not supported for this media type/API version.
    reach: Optional[int] = None
    total_interactions: Optional[int] = None
    shares: Optional[int] = None
    saved: Optional[int] = None
    views: Optional[int] = None


class FacebookAccountSnapshot(BaseModel):
    """Facebook Page-level account metrics available with the current token.

    Post-level data lives in ``PostsMetricsReport`` instead (see the
    2026-08-27 amendment to ADR-0014) — this model is account-fields-only.
    """

    page_id: Optional[str] = None
    name: Optional[str] = None
    fan_count: Optional[int] = None
    followers_count: Optional[int] = None


class InstagramAccountSnapshot(BaseModel):
    """Instagram Business Account metrics available with the current token.

    Media-level data lives in ``PostsMetricsReport`` instead (see the
    2026-08-27 amendment to ADR-0014) — this model is account-fields-only.
    """

    account_id: Optional[str] = None
    username: Optional[str] = None
    followers_count: Optional[int] = None
    media_count: Optional[int] = None


class SocialMetricsSnapshot(BaseModel):
    """A single point-in-time account-metrics collection run."""

    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    facebook: Optional[FacebookAccountSnapshot] = None
    instagram: Optional[InstagramAccountSnapshot] = None


class SocialMetricsReport(BaseModel):
    """Top-level JSON document written to react/src/data/social-metrics.json.

    A growing time series of account-level snapshots (followers, fan
    count, media count) — one entry appended per run.
    """

    history: List[SocialMetricsSnapshot] = Field(default_factory=list)


class PostsMetricsReport(BaseModel):
    """Top-level JSON document written to react/src/data/posts-metrics.json.

    Fully overwritten on every run (no history/append) — a fresh snapshot
    of Facebook posts and Instagram media within [``since``, ``until``],
    capped at the run's ``--limit``. See the 2026-08-27 amendment to
    ADR-0014.
    """

    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    since: str
    until: str
    facebook_posts: List[PostMetric] = Field(default_factory=list)
    facebook_posts_error: Optional[str] = None
    instagram_posts: List[PostMetric] = Field(default_factory=list)
    instagram_posts_error: Optional[str] = None
    insights_permission_warning: Optional[str] = None


def _parse_item_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Best-effort parse of a Graph API timestamp (`created_time`/`timestamp`).

    Returns ``None`` if missing/unparseable so filtering can skip (keep)
    the item rather than dropping data on a formatting surprise.
    """
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _filter_since(items: List[PostMetric], since: date) -> List[PostMetric]:
    """Drop items whose timestamp predates ``since`` (client-side re-check).

    The Graph API `since` query param is passed best-effort on the request
    itself, but its support is inconsistent across edges/API versions, so
    this filter re-enforces the window regardless of what the API returned.
    Items with a missing/unparseable timestamp are kept rather than dropped.
    """
    since_dt = datetime.combine(since, time.min, tzinfo=timezone.utc)
    filtered = []
    for item in items:
        parsed = _parse_item_timestamp(item.timestamp)
        if parsed is not None and parsed < since_dt:
            continue
        filtered.append(item)
    return filtered


class InsightsClient(SocialPublisher):
    """Read-only client for Facebook/Instagram account and media metrics.

    Subclasses ``SocialPublisher`` solely to reuse ``resolve_account_context``;
    ``publish`` is not supported by this client.
    """

    BASE_URL = FACEBOOK_BASE_URL
    API_VERSION = FACEBOOK_API_VERSION

    def __init__(
        self,
        page_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")

        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN required")

        self.client = httpx.AsyncClient(timeout=60.0)
        self._insights_warning_logged = False

    async def check_credentials(self) -> bool:
        """Verify the access token is valid."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/me",
                params={"access_token": self.access_token, "fields": "id,name"},
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def publish(self, video_path, caption, video_url=None):  # noqa: D102
        raise NotImplementedError("InsightsClient is read-only and cannot publish.")

    async def _resolve_context(self) -> tuple[Optional[str], str, Optional[str]]:
        """Resolve (page_id, page_access_token, instagram_business_account_id)."""
        page_id, page_token, instagram_account_id = await self.resolve_account_context(
            self.client,
            self.access_token,
            page_id=self.page_id,
            api_version=self.API_VERSION,
        )
        resolved_page_id = page_id or self.page_id
        resolved_token = page_token or self.access_token
        return resolved_page_id, resolved_token, instagram_account_id

    async def fetch_media_insights(
        self,
        media_id: str,
        access_token: str,
        metrics: Optional[List[str]] = None,
    ) -> dict:
        """Best-effort fetch of GET /{media_id}/insights.

        Returns a dict of metric name -> value. On any permission, unsupported
        -metric, or request error, logs a single warning per client instance
        and returns an empty dict instead of raising, so callers always get a
        usable (possibly all-None) PostMetric.
        """
        metrics = metrics or INSTAGRAM_MEDIA_INSIGHTS_METRICS
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{media_id}/insights",
                params={
                    "metric": ",".join(metrics),
                    "access_token": access_token,
                },
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as exc:
            if not self._insights_warning_logged:
                logger.warning(
                    "Media insights unavailable (missing "
                    "instagram_manage_insights permission, or an "
                    "unsupported/renamed metric for this media type): %s",
                    exc.response.text if exc.response is not None else exc,
                )
                self._insights_warning_logged = True
            return {}
        except Exception as exc:
            if not self._insights_warning_logged:
                logger.warning("Media insights request failed: %s", exc)
                self._insights_warning_logged = True
            return {}

        result: dict = {}
        for entry in payload.get("data", []):
            values = entry.get("values") or []
            if values:
                result[entry.get("name")] = values[0].get("value")
        return result

    async def fetch_facebook_account(
        self, page_id: str, access_token: str
    ) -> FacebookAccountSnapshot:
        """Fetch Facebook Page fan/follower counts."""
        snapshot = FacebookAccountSnapshot(page_id=page_id)
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{page_id}",
                params={
                    "fields": "id,name,fan_count,followers_count",
                    "access_token": access_token,
                },
            )
            response.raise_for_status()
            data = response.json()
            snapshot.name = data.get("name")
            snapshot.fan_count = data.get("fan_count")
            snapshot.followers_count = data.get("followers_count")
        except Exception as exc:
            logger.warning("Could not fetch Facebook Page fields: %s", exc)
        return snapshot

    async def fetch_facebook_posts(
        self,
        page_id: str,
        access_token: str,
        since: date,
        limit: int = DEFAULT_POSTS_LIMIT,
    ) -> tuple[List[PostMetric], Optional[str]]:
        """Fetch recent Facebook Page posts with basic engagement fields.

        ``since`` is passed as the Graph API ``since`` query param
        (best-effort — Meta's support for it on this edge is inconsistent)
        and additionally re-enforced client-side by dropping any post whose
        ``created_time`` predates it, so correctness never depends on the
        API honoring the parameter. Results are capped at ``limit`` items
        after filtering.

        Note: as of this writing this endpoint returns
        "(#10) requires pages_read_engagement permission or Page Public
        Content Access feature" even though the scope is granted — this is
        an App Access Level gate. Failures are returned as an error string
        rather than raised.
        """
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{page_id}/posts",
                params={
                    "fields": (
                        "id,message,created_time,permalink_url,"
                        "likes.summary(true),comments.summary(true)"
                    ),
                    "limit": limit,
                    "since": since.isoformat(),
                    "access_token": access_token,
                },
            )
            response.raise_for_status()
            data = response.json().get("data", [])
        except httpx.HTTPStatusError as exc:
            message = (
                exc.response.json().get("error", {}).get("message")
                if exc.response is not None
                else str(exc)
            )
            logger.warning("Could not fetch Facebook posts: %s", message)
            return [], message
        except Exception as exc:
            logger.warning("Could not fetch Facebook posts: %s", exc)
            return [], str(exc)

        posts = [
            PostMetric(
                id=item.get("id"),
                permalink=item.get("permalink_url"),
                caption=item.get("message"),
                timestamp=item.get("created_time"),
                like_count=(item.get("likes") or {}).get("summary", {}).get("total_count"),
                comments_count=(item.get("comments") or {})
                .get("summary", {})
                .get("total_count"),
            )
            for item in data
        ]
        posts = _filter_since(posts, since)[:limit]
        return posts, None

    async def fetch_instagram_account(
        self, account_id: str, access_token: str
    ) -> InstagramAccountSnapshot:
        """Fetch Instagram Business Account basics."""
        snapshot = InstagramAccountSnapshot(account_id=account_id)
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{account_id}",
                params={
                    "fields": "id,username,followers_count,media_count",
                    "access_token": access_token,
                },
            )
            response.raise_for_status()
            data = response.json()
            snapshot.username = data.get("username")
            snapshot.followers_count = data.get("followers_count")
            snapshot.media_count = data.get("media_count")
        except Exception as exc:
            logger.warning("Could not fetch Instagram account fields: %s", exc)
        return snapshot

    async def fetch_instagram_media(
        self,
        account_id: str,
        access_token: str,
        since: date,
        limit: int = DEFAULT_POSTS_LIMIT,
        with_insights: bool = True,
    ) -> tuple[List[PostMetric], Optional[str]]:
        """Fetch recent Instagram media with engagement fields.

        ``since`` is passed as the Graph API ``since`` query param
        (best-effort) and additionally re-enforced client-side by dropping
        any item whose ``timestamp`` predates it, so correctness never
        depends on the API honoring the parameter. Results are capped at
        ``limit`` items after filtering.

        When ``with_insights`` is True, also attempts (best-effort) to
        enrich each item with reach/total_interactions/shares/saved/views via
        ``fetch_media_insights``.
        """
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{account_id}/media",
                params={
                    "fields": (
                        "id,caption,timestamp,media_type,"
                        "like_count,comments_count,permalink"
                    ),
                    "limit": limit,
                    "since": since.isoformat(),
                    "access_token": access_token,
                },
            )
            response.raise_for_status()
            data = response.json().get("data", [])
        except httpx.HTTPStatusError as exc:
            message = (
                exc.response.json().get("error", {}).get("message")
                if exc.response is not None
                else str(exc)
            )
            logger.warning("Could not fetch Instagram media: %s", message)
            return [], message
        except Exception as exc:
            logger.warning("Could not fetch Instagram media: %s", exc)
            return [], str(exc)

        media: List[PostMetric] = []
        for item in data:
            metric = PostMetric(
                id=item.get("id"),
                permalink=item.get("permalink"),
                caption=item.get("caption"),
                media_type=item.get("media_type"),
                timestamp=item.get("timestamp"),
                like_count=item.get("like_count"),
                comments_count=item.get("comments_count"),
            )
            media.append(metric)

        media = _filter_since(media, since)[:limit]

        if with_insights:
            for metric in media:
                insights = await self.fetch_media_insights(metric.id, access_token)
                metric.reach = insights.get("reach")
                metric.total_interactions = insights.get("total_interactions")
                metric.shares = insights.get("shares")
                metric.saved = insights.get("saved")
                metric.views = insights.get("views")
        return media, None

    async def build_snapshot(self) -> SocialMetricsSnapshot:
        """Fetch account-level fields only and assemble a single snapshot.

        Post/media-level data is fetched separately by ``build_reports`` —
        see the 2026-08-27 amendment to ADR-0014.
        """
        page_id, page_token, instagram_account_id = await self._resolve_context()

        facebook_snapshot: Optional[FacebookAccountSnapshot] = None
        if page_id:
            facebook_snapshot = await self.fetch_facebook_account(page_id, page_token)

        instagram_snapshot: Optional[InstagramAccountSnapshot] = None
        if instagram_account_id:
            instagram_snapshot = await self.fetch_instagram_account(
                instagram_account_id, page_token
            )

        return SocialMetricsSnapshot(
            facebook=facebook_snapshot,
            instagram=instagram_snapshot,
        )

    async def build_posts_report(
        self,
        since: date,
        limit: int = DEFAULT_POSTS_LIMIT,
        page_id: Optional[str] = None,
        page_token: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
    ) -> PostsMetricsReport:
        """Fetch Facebook posts and Instagram media within [since, now].

        If the account-context args are omitted, resolves them via
        ``_resolve_context()`` first (prefer ``build_reports`` to resolve
        once and get both documents in a single call).
        """
        if page_id is None and page_token is None and instagram_account_id is None:
            page_id, page_token, instagram_account_id = await self._resolve_context()

        until = datetime.now(timezone.utc)

        facebook_posts: List[PostMetric] = []
        facebook_posts_error: Optional[str] = None
        if page_id:
            facebook_posts, facebook_posts_error = await self.fetch_facebook_posts(
                page_id, page_token, since=since, limit=limit
            )

        instagram_posts: List[PostMetric] = []
        instagram_posts_error: Optional[str] = None
        if instagram_account_id:
            instagram_posts, instagram_posts_error = await self.fetch_instagram_media(
                instagram_account_id, page_token, since=since, limit=limit
            )

        warning = None
        if self._insights_warning_logged:
            warning = (
                "Media-level insights (reach/total_interactions/shares/"
                "saved/views) were unavailable for at least one item — "
                "either the access token is missing the "
                "instagram_manage_insights permission, or the API rejected "
                "a metric name for that media type/API version. See "
                "automation/README.md for details."
            )

        return PostsMetricsReport(
            since=since.isoformat(),
            until=until.isoformat(),
            facebook_posts=facebook_posts,
            facebook_posts_error=facebook_posts_error,
            instagram_posts=instagram_posts,
            instagram_posts_error=instagram_posts_error,
            insights_permission_warning=warning,
        )

    async def build_reports(
        self, since: date, limit: int = DEFAULT_POSTS_LIMIT
    ) -> tuple[SocialMetricsSnapshot, PostsMetricsReport]:
        """Resolve account context once and build both output documents."""
        page_id, page_token, instagram_account_id = await self._resolve_context()

        facebook_snapshot: Optional[FacebookAccountSnapshot] = None
        if page_id:
            facebook_snapshot = await self.fetch_facebook_account(page_id, page_token)

        instagram_snapshot: Optional[InstagramAccountSnapshot] = None
        if instagram_account_id:
            instagram_snapshot = await self.fetch_instagram_account(
                instagram_account_id, page_token
            )

        social_metrics = SocialMetricsSnapshot(
            facebook=facebook_snapshot,
            instagram=instagram_snapshot,
        )

        posts_report = await self.build_posts_report(
            since,
            limit=limit,
            page_id=page_id,
            page_token=page_token,
            instagram_account_id=instagram_account_id,
        )

        return social_metrics, posts_report

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
