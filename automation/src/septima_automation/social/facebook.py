"""Facebook Graph API publisher."""

import os
from pathlib import Path
from typing import Optional

import httpx

from .base import SocialPublisher


class FacebookPublisher(SocialPublisher):
    """Publish to Facebook using Graph API."""

    BASE_URL = "https://graph.facebook.com/v18.0"

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

    async def publish(
        self,
        video_path: Path,
        caption: str,
    ) -> Optional[str]:
        """Publish video to Facebook Page.

        Args:
            video_path: Path to video file
            caption: Post caption

        Returns:
            Post ID if successful
        """
        # Step 1: Initiate upload session
        with open(video_path, "rb") as video_file:
            response = await self.client.post(
                f"{self.BASE_URL}/{self.page_id}/videos",
                data={
                    "access_token": self.access_token,
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
        return data.get("id")

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
