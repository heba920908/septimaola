"""Deepseek AI provider."""

import os
from typing import Optional

from openai import AsyncOpenAI

from .base import AIProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from ..config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


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
        response = await self._client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(song_title, song_author),
                },
            ],
            temperature=0.5,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()

    async def close(self) -> None:
        await self._client.close()
