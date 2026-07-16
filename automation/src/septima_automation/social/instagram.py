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
    ) -> Optional[str]:
        """Publish video to Instagram.

        Instagram requires a 2-step process:
        1. Create a media container
        2. Publish the container

        Args:
            video_path: Path to video file
            caption: Post caption

        Returns:
            Post ID if successful
        """
        # For Instagram, we need to host the video publicly
        # In production, upload to a temporary hosting or use Facebook's resumable upload
        # For this implementation, we'll use a simplified approach

        # Step 1: Create media container
        # Note: This requires a publicly accessible video URL
        # In a real implementation, you'd need to upload the video first

        # For now, return None as placeholder
        # Real implementation would:
        # 1. Upload video to a public URL (or use Facebook's resumable upload)
        # 2. Create container: POST /{ig-user-id}/media
        # 3. Publish: POST /{ig-user-id}/media_publish

        raise NotImplementedError(
            "Instagram publishing requires a publicly accessible video URL. "
            "Consider using Facebook's resumable upload or host video temporarily."
        )

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
