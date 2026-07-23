"""Base class for social media publishers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple


class SocialPublisher(ABC):
    """Abstract base class for social media publishers."""

    @abstractmethod
    async def publish(
        self,
        video_path: Path,
        caption: str,
        video_url: Optional[str] = None,
    ) -> Optional[str]:
        """Publish video with caption.

        Args:
            video_path: Path to video file
            caption: Post caption text
            video_url: Optional direct URL of the video (useful for platforms like Instagram)

        Returns:
            Published post ID/URL if successful
        """
        pass

    async def resolve_account_context(
        self,
        client,
        access_token: str,
        page_id: Optional[str] = None,
        api_version: str = "v25.0",
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Resolve the page id, page access token, and Instagram business account id."""
        if not access_token:
            return None, None, None

        try:
            response = await client.get(
                f"https://graph.facebook.com/{api_version}/me/accounts",
                params={
                    "access_token": access_token,
                    "fields": "id,name,access_token,instagram_business_account",
                },
            )
            response.raise_for_status()
        except Exception:
            return None, None, None

        data = response.json().get("data", [])
        if not data:
            return None, None, None

        matching_page = None
        if page_id:
            matching_page = next(
                (item for item in data if str(item.get("id")) == str(page_id)),
                None,
            )

        page = matching_page or data[0]
        instagram_business_account = page.get("instagram_business_account") or {}
        return (
            page.get("id"),
            page.get("access_token"),
            instagram_business_account.get("id"),
        )

    @abstractmethod
    async def check_credentials(self) -> bool:
        """Verify credentials are valid."""
        pass
