"""Deepseek AI provider."""

import logging
import os
from typing import Optional

from openai import AsyncOpenAI

from .base import AIProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from ..config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)


class DeepseekClient(AIProvider):
    """AI provider backed by the Deepseek API via the OpenAI-compatible SDK.

    Authentication: Bearer API key via DEEPSEEK_API_KEY env var.

    API reference: https://platform.deepseek.com/docs
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not set. "
                "Provide it via environment variable or constructor argument."
            )
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=DEEPSEEK_BASE_URL,
        )

    async def generate_message(
        self,
        song_title: str,
        song_author: str,
    ) -> str:
        """Generate a message using Deepseek chat completion API."""
        logger.debug(f"Calling Deepseek API for: {song_title} by {song_author}")
        response = await self._client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(song_title, song_author),
                },
            ],
            temperature=0.3,
            max_tokens=150,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "disabled"}}
        )
        try:
            choice = response.choices[0]
            # Support both SDK objects and plain dicts
            msg = getattr(choice, "message", None) or (
                choice.get("message") if isinstance(choice, dict) else None
            )
            if msg is None:
                # Unexpected shape — stringify for debugging
                message = str(response)
            else:
                # Prefer explicit content, but fall back to reasoning_content
                if hasattr(msg, "content"):
                    content_val = msg.content
                else:
                    content_val = msg.get("content") if hasattr(msg, "get") else None

                message = (content_val or "").strip()

                if not message:
                    # Some Deepseek responses put the useful text in
                    # `reasoning_content` when streaming or when content
                    # is left empty. Try that as a fallback.
                    if hasattr(msg, "reasoning_content"):
                        reasoning = msg.reasoning_content
                    else:
                        reasoning = msg.get("reasoning_content") if hasattr(msg, "get") else None

                    if reasoning:
                        message = str(reasoning).strip()
                        logger.warning(
                            "Deepseek response had empty 'content'; using 'reasoning_content' fallback"
                        )
        except Exception:
            # If the response shape is different than expected, fall back
            # to stringifying the response for debugging.
            message = str(response)

        logger.info("Deepseek response received (%d chars)", len(message))
        # Log the full message content and the raw response for troubleshooting
        logger.debug("Deepseek full message: %s", message)
        logger.debug("Deepseek raw response: %s", response)

        return message

    async def close(self) -> None:
        await self._client.close()
