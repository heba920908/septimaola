"""Codemie AI provider via Keycloak OAuth2 and Chat Completions API."""

import logging
import os
import time
from typing import Optional

from openai import AsyncOpenAI

from .base import AIProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class CodemieClient(AIProvider):
    """AI provider backed by Codemie's OpenAI-compatible Chat Completions API.

    Required environment variables:
        CODEMIE_BASE_URL        Codemie origin or API base URL
        CODEMIE_TOKEN_URL       Keycloak OAuth token endpoint
        CODEMIE_CLIENT_ID       Keycloak client ID
        CODEMIE_CLIENT_SECRET   Keycloak client secret
    """

    _TOKEN_REFRESH_BUFFER = 60

    def __init__(
        self,
        base_url: Optional[str] = None,
        token_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = self._normalize_base_url(
            base_url or os.getenv("CODEMIE_BASE_URL", "")
        )
        self.token_url = (token_url or os.getenv("CODEMIE_TOKEN_URL", "")).rstrip("/")
        self.client_id = client_id or os.getenv("CODEMIE_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("CODEMIE_CLIENT_SECRET", "")
        self.model = model or os.getenv("CODEMIE_MODEL", "gemini-3.5-flash")

        missing = [
            name
            for name, value in [
                ("CODEMIE_BASE_URL", self.base_url),
                ("CODEMIE_TOKEN_URL", self.token_url),
                ("CODEMIE_CLIENT_ID", self.client_id),
                ("CODEMIE_CLIENT_SECRET", self.client_secret),
            ]
            if not value
        ]
        if missing:
            raise ValueError(
                f"Missing required Codemie credentials: {', '.join(missing)}"
            )

        self._access_token: Optional[str] = None
        self._token_expires_at = 0.0
        self._openai_client: Optional[AsyncOpenAI] = None

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        """Accept either the Codemie origin or a legacy API base URL."""
        return (
            base_url.rstrip("/")
            .removesuffix("/code-assistant-api/v1")
            .removesuffix("/code-assistant-api")
        )

    @property
    def _codemie_api_base(self) -> str:
        """Return an API base with a trailing slash for OpenAI URL joining."""
        return f"{self.base_url}/code-assistant-api/v1/"

    async def _fetch_token(self) -> str:
        """Request a new OAuth2 access token via client credentials."""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            payload = response.json()

        access_token = payload["access_token"]
        if not isinstance(access_token, str):
            raise ValueError("Codemie token response did not include an access token")

        self._access_token = access_token
        expires_in = payload.get("expires_in", 28500)
        self._token_expires_at = time.monotonic() + int(expires_in)
        self._openai_client = AsyncOpenAI(
            api_key=access_token,
            base_url=self._codemie_api_base,
        )
        return access_token

    async def _get_token(self) -> str:
        """Return a valid token, refreshing before expiry."""
        if (
            self._access_token is None
            or time.monotonic() >= self._token_expires_at - self._TOKEN_REFRESH_BUFFER
        ):
            await self._fetch_token()
        return self._access_token or ""

    async def _get_client(self) -> AsyncOpenAI:
        """Return an OpenAI-compatible client with a valid access token."""
        await self._get_token()
        if self._openai_client is None:
            raise RuntimeError(
                "Codemie client was not initialized after token retrieval"
            )
        return self._openai_client

    async def generate_message(self, song_title: str, song_author: str) -> str:
        """Generate a daily message via Codemie Chat Completions."""
        return await self.generate_chat_completion(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(song_title, song_author)},
            ]
        )

    async def generate_chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Send role-based messages to Codemie and return the completion text."""
        client = await self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=0.8,
            max_tokens=2000,
            stream=False,
        )
        message = (response.choices[0].message.content or "").strip()
        logger.info("Codemie response received (%d chars)", len(message))
        return message

    async def close(self) -> None:
        """Release provider resources."""
        if self._openai_client:
            await self._openai_client.close()
            self._openai_client = None
