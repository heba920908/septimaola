"""Message generator that combines AI output with post formatting."""

import random
from typing import List, Optional

from .ai.base import AIProvider
from .config import HASHTAGS


class MessageGenerator:
    """Generates complete social media posts."""

    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def generate_post(
        self,
        song_title: str,
        song_author: str,
        custom_hashtags: Optional[List[str]] = None,
    ) -> str:
        """Generate a complete social media post.

        Args:
            song_title: Title of featured song
            song_author: Author/artist of featured song
            custom_hashtags: Optional override for hashtags

        Returns:
            Formatted post text
        """
        ai_message = await self.ai_provider.generate_message(song_title, song_author)
        hashtags = custom_hashtags or self._select_hashtags()

        lines = [
            ai_message,
            "",
            f"Canción destacada: {song_title} ({song_author})",
            "",
            " ".join(hashtags),
        ]

        return "\n".join(lines)

    def _select_hashtags(self, count: int = 4) -> List[str]:
        """Select a random subset of hashtags."""
        return random.sample(HASHTAGS, min(count, len(HASHTAGS)))
