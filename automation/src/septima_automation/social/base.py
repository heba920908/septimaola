"""Base class for social media publishers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class SocialPublisher(ABC):
    """Abstract base class for social media publishers."""

    @abstractmethod
    async def publish(
        self,
        video_path: Path,
        caption: str,
    ) -> Optional[str]:
        """Publish video with caption.

        Args:
            video_path: Path to video file
            caption: Post caption text

        Returns:
            Published post ID/URL if successful
        """
        pass

    @abstractmethod
    async def check_credentials(self) -> bool:
        """Verify credentials are valid."""
        pass
