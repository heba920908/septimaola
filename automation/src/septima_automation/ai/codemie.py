"""Codemie AI provider via Keycloak OAuth2 and OpenAI-compatible API.

This implementation uses the OpenAI library with Codemie's API, which provides
a unified interface consistent with the Deepseek provider.

Authentication flow:
    1. POST to Keycloak token endpoint with client_id + client_secret
       (grant_type=client_credentials)
    2. Receive a short-lived JWT access_token (~8h, no refresh token)
    3. Call Codemie assistant API with Bearer token via OpenAI client

API reference: https://docs.codemie.ai/user-guide/api/
"""

import logging
import os
import time
from typing import Optional

from openai import AsyncOpenAI

from .base import AIProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class CodemieClient(AIProvider):
    """AI provider backed by Codemie via Keycloak OAuth2 and OpenAI-compatible API.

    Required environment variables:
        CODEMIE_BASE_URL        Base URL of the Codemie instance
                                e.g. https://codemie.example.com
        CODEMIE_KEYCLOAK_URL    Keycloak base URL
                                e.g. https://keycloak.example.com
        CODEMIE_REALM           Keycloak realm name  (e.g. codemie-prod)
        CODEMIE_CLIENT_ID       Keycloak client ID   (e.g. api-demo-project)
        CODEMIE_CLIENT_SECRET   Keycloak client secret (from Credentials tab)

    Note: ASSISTANT_ID is not required as we use the OpenAI-compatible API
    with system prompts to configure the assistant behavior.
    """

    # Seconds before expiry to proactively refresh the token
    _TOKEN_REFRESH_BUFFER = 60

    def __init__(
        self,
        base_url: Optional[str] = None,
        keycloak_url: Optional[str] = None,
        realm: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = (base_url or os.getenv("CODEMIE_BASE_URL", "")).rstrip("/")
        self.keycloak_url = (
            keycloak_url or os.getenv("CODEMIE_KEYCLOAK_URL", "")
        ).rstrip("/")
        self.realm = realm or os.getenv("CODEMIE_REALM", "")
        self.client_id = client_id or os.getenv("CODEMIE_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("CODEMIE_CLIENT_SECRET", "")
        self.model = model or os.getenv("CODEMIE_MODEL", "gpt-4o")

        missing = [
            name
            for name, val in [
                ("CODEMIE_BASE_URL", self.base_url),
                ("CODEMIE_KEYCLOAK_URL", self.keycloak_url),
                ("CODEMIE_REALM", self.realm),
                ("CODEMIE_CLIENT_ID", self.client_id),
                ("CODEMIE_CLIENT_SECRET", self.client_secret),
            ]
            if not val
        ]
        if missing:
            raise ValueError(
                f"Missing required Codemie credentials: {', '.join(missing)}"
            )

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._openai_client: Optional[AsyncOpenAI] = None

    # ------------------------------------------------------------------
    # OAuth2 token management
    # ------------------------------------------------------------------

    @property
    def _token_endpoint(self) -> str:
        return (
            f"{self.keycloak_url}/auth/realms/{self.realm}"
            f"/protocol/openid-connect/token"
        )

    @property
    def _codemie_api_base(self) -> str:
        """Return the OpenAI-compatible API base URL for Codemie."""
        return f"{self.base_url}/code-assistant-api/v1"

    async def _fetch_token(self) -> str:
        """Request a new access token via client_credentials grant."""
        import httpx

        logger.debug("Fetching Codemie access token...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._token_endpoint,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            payload = response.json()

        self._access_token = payload["access_token"]
        expires_in: int = payload.get("expires_in", 28500)
        self._token_expires_at = time.monotonic() + expires_in
        logger.debug(f"Token acquired (expires in {expires_in}s)")

        # Recreate OpenAI client with new token
        self._openai_client = AsyncOpenAI(
            api_key=self._access_token,
            base_url=self._codemie_api_base,
        )

        return self._access_token

    async def _get_token(self) -> str:
        """Return a valid access token, refreshing it when near expiry."""
        if (
            self._access_token is None
            or time.monotonic() >= self._token_expires_at - self._TOKEN_REFRESH_BUFFER
        ):
            logger.debug("Token expired or missing; refreshing...")
            await self._fetch_token()
        return self._access_token or ""

    async def _get_client(self) -> AsyncOpenAI:
        """Return a configured OpenAI client with valid token."""
        if self._openai_client is None:
            await self._get_token()
        return self._openai_client  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # AIProvider interface
    # ------------------------------------------------------------------

    async def generate_message(
        self,
        song_title: str,
        song_author: str,
    ) -> str:
        """Generate a message via the Codemie assistant API using OpenAI-compatible endpoint.

        Uses the chat completions API with system prompt and user prompt to generate
        social media content.
        """
        logger.debug(f"Calling Codemie API for: {song_title} by {song_author}")

        client = await self._get_client()

        # Codemie uses assistant-specific endpoint; we map to chat completions
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(song_title, song_author),
                },
            ],
            temperature=0.8,
            max_tokens=150,
            stream=False,
        )

        message = response.choices[0].message.content or ""
        message = message.strip()

        logger.info("Codemie response received (%d chars)", len(message))
        logger.debug("Codemie full message: %s", message)

        return message

    async def close(self) -> None:
        """Release any held resources."""
        if self._openai_client:
            await self._openai_client.close()
            self._openai_client = None
