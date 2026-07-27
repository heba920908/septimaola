"""Instagram Graph API publisher."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

import httpx

from .base import SocialPublisher

logger = logging.getLogger(__name__)


class InstagramPublisher(SocialPublisher):
    """Publish to Instagram using Graph API."""

    BASE_URL = "https://graph.facebook.com/v25.0"
    API_VERSION = "v25.0"

    def __init__(
        self,
        account_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.account_id = account_id or os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")

        if not self.account_id or not self.access_token:
            raise ValueError("INSTAGRAM_ACCOUNT_ID and FACEBOOK_ACCESS_TOKEN required")

        self.client = httpx.AsyncClient(timeout=120.0)

    async def check_credentials(self) -> bool:
        """Verify Instagram credentials work."""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{self.account_id}",
                params={
                    "access_token": self.access_token,
                    "fields": "id,username",
                },
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def _resolve_target(self) -> tuple[str, str]:
        _, page_token, instagram_account_id = await self.resolve_account_context(
            self.client,
            self.access_token,
            page_id=None,
            api_version=self.API_VERSION,
        )

        if instagram_account_id and page_token:
            self.account_id = instagram_account_id
            return instagram_account_id, page_token

        return self.account_id or "", self.access_token

    async def publish(
        self,
        video_path: Path,
        caption: str,
        video_url: Optional[str] = None,
    ) -> Optional[str]:
        """Publish video to Instagram.

        Instagram requires a 2-step process:
        1. Create a media container using a publicly accessible video URL
        2. Wait for the video processing to complete (poll status)
        3. Publish the container

        Args:
            video_path: Path to video file (not used, Instagram requires public URL)
            caption: Post caption
            video_url: Publicly accessible video URL (e.g. Google Drive direct download URL)

        Returns:
            Post ID if successful
        """
        if not video_url:
            raise ValueError(
                "Instagram publishing requires a publicly accessible video_url."
            )

        target_account_id, target_token = await self._resolve_target()
        logger.info(f"Publishing to Instagram (account={target_account_id})...")

        # Step 1: Create media container
        # POST /{ig-user-id}/media
        logger.debug("Creating Instagram media container...")
        response = await self.client.post(
            f"{self.BASE_URL}/{target_account_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": target_token,
            },
        )
        response.raise_for_status()
        container_id = response.json().get("id")
        if not container_id:
            raise ValueError("Failed to create Instagram media container")
        logger.debug(f"Media container created: {container_id}")

        # Step 2: Poll container status
        # Poll every 5 seconds for up to 2 minutes
        logger.debug("Waiting for Instagram video processing...")
        max_attempts = 24
        for attempt in range(max_attempts):
            await asyncio.sleep(5)
            status_resp = await self.client.get(
                f"{self.BASE_URL}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": target_token,
                },
            )
            status_resp.raise_for_status()
            status_code = status_resp.json().get("status_code")
            logger.debug(f"Status check {attempt+1}/{max_attempts}: {status_code}")

            if status_code == "FINISHED":
                logger.debug("Video processing finished")
                break
            elif status_code == "ERROR":
                logger.error(f"Instagram video processing failed: {status_resp.json()}")
                raise ValueError(
                    f"Instagram video processing failed: {status_resp.json()}"
                )
        else:
            logger.error("Timed out waiting for Instagram video processing")
            raise TimeoutError("Timed out waiting for Instagram video processing")

        # Step 3: Publish container
        # POST /{ig-user-id}/media_publish
        logger.debug("Publishing Instagram media container...")
        publish_resp = await self.client.post(
            f"{self.BASE_URL}/{target_account_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": target_token,
            },
        )
        publish_resp.raise_for_status()
        post_id = publish_resp.json().get("id")
        logger.info(f"✓ Instagram post published: {post_id}")
        return post_id

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
