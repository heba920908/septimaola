"""Codemie AI provider via Keycloak OAuth2 and Chat Completions API."""

import logging
import os
import time
from typing import Any, Optional

from openai import AsyncOpenAI, BadRequestError

from .band_context import BAND_CONTEXT_SUMMARY, BAND_FACTS_TOOL, get_band_facts
from .base import AIProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .tool_loop import run_tool_loop

logger = logging.getLogger(__name__)

# Handler map for the get_septima_ola_facts tool (see band_context.py).
_BAND_TOOL_HANDLERS = {
    "get_septima_ola_facts": lambda args: get_band_facts(args.get("topic")),
}


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
        self.model = model or os.getenv("CODEMIE_MODEL", "gpt-4.1")

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
        """Generate a daily message via Codemie Chat Completions.

        Attaches the get_septima_ola_facts tool so the model can ground
        content about Septima Ola in canonical band facts (see
        band_context.py). Other artists are unaffected: the model is
        instructed not to call the tool for them (see SYSTEM_PROMPT).
        """
        return await self.generate_chat_completion(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(song_title, song_author)},
            ],
            tools=[BAND_FACTS_TOOL],
            tool_handlers=_BAND_TOOL_HANDLERS,
        )

    async def generate_chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: Optional[list[dict[str, Any]]] = None,
        tool_handlers: Optional[dict[str, Any]] = None,
        temperature: float = 0.8,
    ) -> str:
        """Send role-based messages to Codemie and return the completion text.

        If `tools` is provided, resolves any tool_calls via `tool_handlers`
        before returning the final text (see tool_loop.run_tool_loop). If the
        deployment/model rejects the `tools` parameter (HTTP 400), retries
        once without tools, injecting BAND_CONTEXT_SUMMARY as a system
        message so grounding can still be attempted without native
        function-calling support.
        """
        client = await self._get_client()

        async def _create(**kwargs):
            return await client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=2000,
                stream=False,
                **kwargs,
            )

        try:
            message = await run_tool_loop(
                _create,
                messages=messages,
                tools=tools,
                tool_handlers=tool_handlers,
            )
        except BadRequestError:
            if not tools:
                raise
            logger.warning(
                "Codemie model %s rejected the 'tools' parameter; retrying "
                "without tools using the band-context summary fallback",
                self.model,
            )
            fallback_messages = [
                messages[0],
                {"role": "system", "content": BAND_CONTEXT_SUMMARY},
                *messages[1:],
            ]
            response = await _create(messages=fallback_messages, tools=None)
            message = (response.choices[0].message.content or "").strip()

        logger.info("Codemie response received (%d chars)", len(message))
        return message

    async def close(self) -> None:
        """Release provider resources."""
        if self._openai_client:
            await self._openai_client.close()
            self._openai_client = None
