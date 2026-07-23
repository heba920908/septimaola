"""Message generator that combines AI output with post formatting."""

import logging
import random
from typing import List, Optional

from .ai.base import AIProvider
from .config import HASHTAGS

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Generates complete social media posts."""

    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def generate_post(
        self,
        song_title: str,
        song_author: str,
        custom_hashtags: Optional[List[str]] = None,
        skip_ai: bool = False,
    ) -> str:
        """Generate a complete social media post.

        Args:
            song_title: Title of featured song
            song_author: Author/artist of featured song
            custom_hashtags: Optional override for hashtags

        Returns:
            Formatted post text
        """
        logger.debug(f"Generating post for: {song_title} by {song_author}")
        if skip_ai:
            logger.info("Skipping AI generation; using local fallback caption")
            ai_message = self._build_fallback_message(song_title, song_author)
        else:
            try:
                ai_message = await self.ai_provider.generate_message(song_title, song_author)
            except Exception as exc:
                logger.warning(
                    "AI provider failed for %s by %s; using fallback caption: %s",
                    song_title,
                    song_author,
                    exc,
                )
                ai_message = self._build_fallback_message(song_title, song_author)
        hashtags = custom_hashtags or self._select_hashtags()
        logger.debug(f"Selected hashtags: {hashtags}")

        lines = [
            ai_message,
            "",
            f"Canción destacada: {song_title} ({song_author})",
            "",
            " ".join(hashtags),
        ]

        post = "\n".join(lines)
        logger.debug(f"Post generated ({len(post)} chars)")
        return post

    def _build_fallback_message(self, song_title: str, song_author: str) -> str:
        """Return a simple caption when the AI provider is unavailable."""
        return (
            f"Ritmo, energía y sabor para seguir compartiendo la música de "
            f"{song_title} de {song_author}. Gracias por acompañarnos."
        )

    def _select_hashtags(self, count: int = 4) -> List[str]:
        """Select a random subset of hashtags."""
        return random.sample(HASHTAGS, min(count, len(HASHTAGS)))
