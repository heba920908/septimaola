"""Deepseek AI provider."""

import logging
import os
from typing import Any, Optional

from openai import AsyncOpenAI

from .band_context import BAND_FACTS_TOOL, get_band_facts
from .base import AIProvider
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .tool_loop import run_tool_loop
from ..config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)

# Handler map for the get_septima_ola_facts tool (see band_context.py).
_BAND_TOOL_HANDLERS = {
    "get_septima_ola_facts": lambda args: get_band_facts(args.get("topic")),
}


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
        """Generate a message using Deepseek chat completion API.

        Attaches the get_septima_ola_facts tool so the model can ground
        content about Septima Ola in canonical band facts (see
        band_context.py). Other artists are unaffected: the model is
        instructed not to call the tool for them (see SYSTEM_PROMPT).
        """
        logger.debug(f"Calling Deepseek API for: {song_title} by {song_author}")

        async def _create(**kwargs):
            return await self._client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                temperature=0.3,
                max_tokens=800,
                stream=False,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "disabled"}},
                **kwargs,
            )

        message = await run_tool_loop(
            _create,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(song_title, song_author),
                },
            ],
            tools=[BAND_FACTS_TOOL],
            tool_handlers=_BAND_TOOL_HANDLERS,
            extract_content=self._extract_content,
        )

        logger.info("Deepseek response received (%d chars)", len(message))
        logger.debug("Deepseek full message: %s", message)

        return message

    @staticmethod
    def _extract_content(msg: Any) -> str:
        """Extract text content from a Deepseek message, with fallback.

        Some Deepseek responses put the useful text in `reasoning_content`
        when content is left empty. Defensive against both SDK objects and
        plain dicts, matching the previous inline behavior.
        """
        try:
            content_val = getattr(msg, "content", None)
            if content_val is None and hasattr(msg, "get"):
                content_val = msg.get("content")

            message = (content_val or "").strip()

            if not message:
                reasoning = getattr(msg, "reasoning_content", None)
                if reasoning is None and hasattr(msg, "get"):
                    reasoning = msg.get("reasoning_content")

                if reasoning:
                    message = str(reasoning).strip()
                    logger.warning(
                        "Deepseek response had empty 'content'; using "
                        "'reasoning_content' fallback"
                    )
            return message
        except Exception:
            return str(msg)

    async def close(self) -> None:
        await self._client.close()
