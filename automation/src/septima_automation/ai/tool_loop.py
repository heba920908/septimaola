"""Shared OpenAI-compatible function-calling loop.

Both CodemieClient and DeepseekClient use the same tool-call protocol (the
OpenAI Chat Completions `tools`/`tool_calls` contract), so the round-trip
loop lives here once instead of being duplicated per provider.
"""

import json
import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

ToolHandler = Callable[[dict[str, Any]], str]


async def run_tool_loop(
    create_completion: Callable[..., Awaitable[Any]],
    *,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    tool_handlers: dict[str, ToolHandler] | None,
    max_rounds: int = 3,
    extract_content: Callable[[Any], str] | None = None,
    **create_kwargs: Any,
) -> str:
    """Run a Chat Completions request, resolving tool calls until final text.

    Args:
        create_completion: Async callable with signature
            `(messages=..., tools=..., **create_kwargs) -> ChatCompletion`,
            typically `client.chat.completions.create`.
        messages: Initial conversation messages (system/user turns).
        tools: OpenAI-compatible tool schemas, or None/empty to disable.
        tool_handlers: Mapping of tool function name to a sync callable that
            accepts the parsed JSON arguments and returns the tool result
            text. Required if `tools` is provided.
        max_rounds: Maximum number of tool-call round-trips before giving up
            and returning whatever text is available.
        extract_content: Optional callable receiving the response message
            object and returning its text content, for providers with
            non-standard content fields (e.g. Deepseek's reasoning_content
            fallback). Defaults to `(message.content or "").strip()`.
        **create_kwargs: Extra kwargs forwarded to `create_completion`
            (model, temperature, max_tokens, etc).

    Returns:
        The final assistant message content, stripped. May be empty if the
        model never produces a text response within `max_rounds`.
    """
    conversation = list(messages)
    tool_handlers = tool_handlers or {}
    content_of = extract_content or (lambda m: (m.content or "").strip())
    last_content = ""

    for round_index in range(max_rounds):
        response = await create_completion(
            messages=conversation,
            tools=tools or None,
            **create_kwargs,
        )
        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)
        last_content = content_of(message)

        if not tool_calls:
            return last_content

        logger.info(
            "Tool loop round %d: model requested %s",
            round_index,
            [(tc.function.name, tc.function.arguments) for tc in tool_calls],
        )
        conversation.append(message.model_dump(exclude_none=True))

        for tool_call in tool_calls:
            handler = tool_handlers.get(tool_call.function.name)
            if handler is None:
                result = f"Error: unknown tool '{tool_call.function.name}'"
            else:
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = handler(args)
            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    logger.warning(
        "Tool loop exhausted %d rounds without a final text response", max_rounds
    )
    return last_content
