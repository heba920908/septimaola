"""Codemie AI provider via Keycloak OAuth2 client_credentials.

Authentication flow:
    1. POST to Keycloak token endpoint with client_id + client_secret
       (grant_type=client_credentials)
    2. Receive a short-lived JWT access_token (~8h, no refresh token)
    3. Call Codemie assistant API with Bearer token

API reference: https://docs.codemie.ai/user-guide/api/
"""

import logging
import os
import time
from typing import Optional

import httpx

from .base import AIProvider
from .prompts import build_user_prompt

logger = logging.getLogger(__name__)


class CodemieClient(AIProvider):
    """AI provider backed by Codemie via Keycloak OAuth2.

    Required environment variables:
        CODEMIE_BASE_URL        Base URL of the Codemie instance
                                e.g. https://codemie.example.com
        CODEMIE_KEYCLOAK_URL    Keycloak base URL
                                e.g. https://keycloak.example.com
        CODEMIE_REALM           Keycloak realm name  (e.g. codemie-prod)
        CODEMIE_CLIENT_ID       Keycloak client ID   (e.g. api-demo-project)
        CODEMIE_CLIENT_SECRET   Keycloak client secret (from Credentials tab)
        CODEMIE_ASSISTANT_ID    UUID of the Codemie assistant to call
    """

    # Codemie API path for calling an assistant
    _ASSISTANT_PATH = "/code-assistant-api/v1/assistants/{assistant_id}/model"

    # Seconds before expiry to proactively refresh the token
    _TOKEN_REFRESH_BUFFER = 60

    def __init__(
        self,
        base_url: Optional[str] = None,
        keycloak_url: Optional[str] = None,
        realm: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        assistant_id: Optional[str] = None,
    ):
        self.base_url = (base_url or os.getenv("CODEMIE_BASE_URL", "")).rstrip("/")
        self.keycloak_url = (
            keycloak_url or os.getenv("CODEMIE_KEYCLOAK_URL", "")
        ).rstrip("/")
        self.realm = realm or os.getenv("CODEMIE_REALM", "")
        self.client_id = client_id or os.getenv("CODEMIE_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("CODEMIE_CLIENT_SECRET", "")
        self.assistant_id = assistant_id or os.getenv("CODEMIE_ASSISTANT_ID", "")

        missing = [
            name
            for name, val in [
                ("CODEMIE_BASE_URL", self.base_url),
                ("CODEMIE_KEYCLOAK_URL", self.keycloak_url),
                ("CODEMIE_REALM", self.realm),
                ("CODEMIE_CLIENT_ID", self.client_id),
                ("CODEMIE_CLIENT_SECRET", self.client_secret),
                ("CODEMIE_ASSISTANT_ID", self.assistant_id),
            ]
            if not val
        ]
        if missing:
            raise ValueError(
                f"Missing required Codemie credentials: {', '.join(missing)}"
            )

        self._http = httpx.AsyncClient(timeout=30.0)

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    # ------------------------------------------------------------------
    # OAuth2 token management
    # ------------------------------------------------------------------

    @property
    def _token_endpoint(self) -> str:
        return (
            f"{self.keycloak_url}/auth/realms/{self.realm}"
            f"/protocol/openid-connect/token"
        )

    async def _fetch_token(self) -> str:
        """Request a new access token via client_credentials grant."""
        logger.debug("Fetching Codemie access token...")
        response = await self._http.post(
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

        return self._access_token

    async def _get_token(self) -> str:
        """Return a valid access token, refreshing it when near expiry."""
        if (
            self._access_token is None
            or time.monotonic() >= self._token_expires_at - self._TOKEN_REFRESH_BUFFER
        ):
            logger.debug("Token expired or missing; refreshing...")
            await self._fetch_token()
        return self._access_token  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # AIProvider interface
    # ------------------------------------------------------------------

    async def generate_message(
        self,
        song_title: str,
        song_author: str,
    ) -> str:
        """Generate a message via the Codemie assistant API.

        The prompt is sent as the `text` field. The response is extracted
        from the `generated` field of the JSON response.
        """
        logger.debug(f"Calling Codemie assistant for: {song_title} by {song_author}")
        token = await self._get_token()

        url = self.base_url + self._ASSISTANT_PATH.format(
            assistant_id=self.assistant_id
        )

        response = await self._http.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "text": build_user_prompt(song_title, song_author),
            },
        )
        response.raise_for_status()
        data = response.json()
        message = data["generated"].strip()
        logger.debug(f"Codemie response received ({len(message)} chars)")
        return message

    async def close(self) -> None:
        await self._http.aclose()
