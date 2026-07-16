"""Deepseek AI provider."""

import os
from typing import Optional

import httpx

from .base import AIProvider
from ..config import DEEPSEEK_API_URL, DEEPSEEK_MODEL

SYSTEM_PROMPT = (
    "Eres un asistente creativo para Séptima Ola, "
    "una banda de reggae/ska/rocksteady de La Raza, "
    "Ciudad de México. Generas mensajes inspiradores "
    "y auténticos para redes sociales."
)


class DeepseekClient(AIProvider):
    """AI provider backed by the Deepseek API.

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
        self._client = httpx.AsyncClient(timeout=30.0)

    async def generate_message(
        self,
        song_title: str,
        song_author: str,
    ) -> str:
        """Generate a message using Deepseek chat completion API."""
        response = await self._client.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": self._build_prompt(song_title, song_author),
                    },
                ],
                "temperature": 0.8,
                "max_tokens": 150,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    async def close(self) -> None:
        await self._client.aclose()
