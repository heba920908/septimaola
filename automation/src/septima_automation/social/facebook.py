"""Facebook Graph API publisher."""

import logging
import os
from pathlib import Path
from typing import Optional

import httpx

from .base import SocialPublisher

logger = logging.getLogger(__name__)


class FacebookPublisher(SocialPublisher):
    """Publish to Facebook using Graph API."""

    BASE_URL = "https://graph.facebook.com/v25.0"
    API_VERSION = "v25.0"

    def __init__(
        self,
        page_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")

        if not self.page_id or not self.access_token:
            raise ValueError("FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN required")

        self.client = httpx.AsyncClient(timeout=120.0)

    async def check_credentials(self) -> bool:
        """Verify Facebook credentials work."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/me",
                params={
                    "access_token": self.access_token,
                    "fields": "id,name",
                },
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def _resolve_target(self) -> tuple[str, str]:
        page_id, page_token, _ = await self.resolve_account_context(
            self.client,
            self.access_token,
            page_id=self.page_id,
            api_version=self.API_VERSION,
        )

        if page_id and page_token:
            self.page_id = page_id
            return page_id, page_token

        return self.page_id or "", self.access_token

    async def publish(
        self,
        video_path: Path,
        caption: str,
        video_url: Optional[str] = None,
    ) -> Optional[str]:
        """Publish video to Facebook Page.

        Args:
            video_path: Path to video file
            caption: Post caption
            video_url: Optional direct URL of the video (ignored for Facebook)

        Returns:
            Post ID if successful
        """
        target_page_id, target_token = await self._resolve_target()
        logger.info(f"Publishing to Facebook (page={target_page_id})...")
        with open(video_path, "rb") as video_file:
            response = await self.client.post(
                f"{self.BASE_URL}/{target_page_id}/videos",
                data={
                    "access_token": target_token,
                    "description": caption,
                    "published": "true",
                },
                files={
                    "file": (
                        video_path.name,
                        video_file,
                        "video/mp4",
                    ),
                },
            )

        response.raise_for_status()
        data = response.json()
        post_id = data.get("id")
        logger.info(f"✓ Facebook post published: {post_id}")
        return post_id

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
