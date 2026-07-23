"""Instagram Graph API publisher."""

import os
from pathlib import Path
from typing import Optional

import httpx

from .base import SocialPublisher


class InstagramPublisher(SocialPublisher):
    """Publish to Instagram using Graph API."""

    BASE_URL = "https://graph.facebook.com/v18.0"

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

        # Step 1: Create media container
        # POST /{ig-user-id}/media
        response = await self.client.post(
            f"{self.BASE_URL}/{self.account_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": self.access_token,
            },
        )
        response.raise_for_status()
        container_id = response.json().get("id")
        if not container_id:
            raise ValueError("Failed to create Instagram media container")

        # Step 2: Poll container status
        # Poll every 5 seconds for up to 2 minutes
        import asyncio

        max_attempts = 24
        for attempt in range(max_attempts):
            await asyncio.sleep(5)
            status_resp = await self.client.get(
                f"{self.BASE_URL}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": self.access_token,
                },
            )
            status_resp.raise_for_status()
            status_code = status_resp.json().get("status_code")

            if status_code == "FINISHED":
                break
            elif status_code == "ERROR":
                raise ValueError(
                    f"Instagram video processing failed: {status_resp.json()}"
                )
        else:
            raise TimeoutError("Timed out waiting for Instagram video processing")

        # Step 3: Publish container
        # POST /{ig-user-id}/media_publish
        publish_resp = await self.client.post(
            f"{self.BASE_URL}/{self.account_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": self.access_token,
            },
        )
        publish_resp.raise_for_status()
        return publish_resp.json().get("id")

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
