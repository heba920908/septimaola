"""Non-live tests for the shared tool-call loop and provider integration.

These use mocked chat-completion responses; no real LLM/network calls.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from openai import BadRequestError

from septima_automation.ai.tool_loop import run_tool_loop


def _bad_request_error(message: str) -> BadRequestError:
    request = httpx.Request("POST", "https://codemie.example.com")
    response = httpx.Response(400, request=request, json={"detail": message})
    return BadRequestError(message, response=response, body=None)


def _tool_call(name: str, arguments: str, call_id: str = "call_1"):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def _response(content: str | None, tool_calls=None, finish_reason="stop"):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    # model_dump is required by run_tool_loop to append the assistant turn.
    message.model_dump = lambda exclude_none=True: {
        "role": "assistant",
        "content": content,
        **({"tool_calls": tool_calls} if tool_calls else {}),
    }
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice])


class TestRunToolLoop:
    @pytest.mark.asyncio
    async def test_no_tool_call_returns_content_immediately(self):
        create = AsyncMock(return_value=_response("hola mundo"))
        result = await run_tool_loop(
            create,
            messages=[{"role": "user", "content": "hi"}],
            tools=None,
            tool_handlers=None,
        )
        assert result == "hola mundo"
        create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_tool_call_is_resolved_then_final_text_returned(self):
        tool_response = _response(
            None, tool_calls=[_tool_call("get_facts", '{"topic": "origen"}')]
        )
        final_response = _response("contenido final con el dato")
        create = AsyncMock(side_effect=[tool_response, final_response])

        handled_args = []

        def handler(args):
            handled_args.append(args)
            return "dato del origen"

        result = await run_tool_loop(
            create,
            messages=[{"role": "user", "content": "genera algo"}],
            tools=[{"type": "function", "function": {"name": "get_facts"}}],
            tool_handlers={"get_facts": handler},
        )

        assert result == "contenido final con el dato"
        assert handled_args == [{"topic": "origen"}]
        assert create.await_count == 2

        # Second call's conversation should include the tool result message.
        second_call_kwargs = create.await_args_list[1].kwargs
        tool_messages = [
            m for m in second_call_kwargs["messages"] if m.get("role") == "tool"
        ]
        assert len(tool_messages) == 1
        assert tool_messages[0]["content"] == "dato del origen"
        assert tool_messages[0]["tool_call_id"] == "call_1"

    @pytest.mark.asyncio
    async def test_unknown_tool_name_reports_error_without_raising(self):
        tool_response = _response(
            None, tool_calls=[_tool_call("nonexistent_tool", "{}")]
        )
        final_response = _response("recovered anyway")
        create = AsyncMock(side_effect=[tool_response, final_response])

        result = await run_tool_loop(
            create,
            messages=[{"role": "user", "content": "hi"}],
            tools=[{"type": "function", "function": {"name": "get_facts"}}],
            tool_handlers={"get_facts": lambda args: "unused"},
        )
        assert result == "recovered anyway"

    @pytest.mark.asyncio
    async def test_malformed_tool_arguments_do_not_raise(self):
        tool_response = _response(
            None, tool_calls=[_tool_call("get_facts", "not-json")]
        )
        final_response = _response("still finished")
        create = AsyncMock(side_effect=[tool_response, final_response])

        received = []
        result = await run_tool_loop(
            create,
            messages=[{"role": "user", "content": "hi"}],
            tools=[{"type": "function", "function": {"name": "get_facts"}}],
            tool_handlers={"get_facts": lambda args: received.append(args) or "ok"},
        )
        assert result == "still finished"
        assert received == [{}]

    @pytest.mark.asyncio
    async def test_max_rounds_cap_returns_last_content(self):
        """If the model keeps requesting tools forever, bail out rather
        than looping indefinitely."""
        always_tool_call = _response("", tool_calls=[_tool_call("get_facts", "{}")])
        create = AsyncMock(return_value=always_tool_call)

        result = await run_tool_loop(
            create,
            messages=[{"role": "user", "content": "hi"}],
            tools=[{"type": "function", "function": {"name": "get_facts"}}],
            tool_handlers={"get_facts": lambda args: "fact"},
            max_rounds=2,
        )
        assert result == ""
        assert create.await_count == 2

    @pytest.mark.asyncio
    async def test_extract_content_hook_used_for_reasoning_fallback(self):
        """Deepseek-style responses may need a custom content extractor."""
        message = SimpleNamespace(content="", tool_calls=None)
        message.reasoning_content = "fallback text"
        message.model_dump = lambda exclude_none=True: {"role": "assistant"}
        choice = SimpleNamespace(message=message, finish_reason="stop")
        response = SimpleNamespace(choices=[choice])
        create = AsyncMock(return_value=response)

        def extract(msg):
            return msg.content or msg.reasoning_content

        result = await run_tool_loop(
            create,
            messages=[{"role": "user", "content": "hi"}],
            tools=None,
            tool_handlers=None,
            extract_content=extract,
        )
        assert result == "fallback text"


class TestCodemieToolFallback:
    """Codemie may reject the `tools` parameter on models without function
    calling; generate_chat_completion should retry once without tools."""

    @pytest.mark.asyncio
    async def test_falls_back_when_tools_rejected(self, monkeypatch):
        monkeypatch.setenv("CODEMIE_BASE_URL", "https://codemie.example.com")
        monkeypatch.setenv(
            "CODEMIE_TOKEN_URL",
            "https://keycloak.example.com/realms/test/protocol/openid-connect/token",
        )
        monkeypatch.setenv("CODEMIE_CLIENT_ID", "client")
        monkeypatch.setenv("CODEMIE_CLIENT_SECRET", "secret")

        from septima_automation.ai.codemie import CodemieClient

        client = CodemieClient()

        bad_request_error = _bad_request_error("tools not supported")

        calls = []

        async def fake_create(**kwargs):
            calls.append(kwargs)
            if kwargs.get("tools"):
                raise bad_request_error
            return _response("fallback content")

        mock_openai_client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
        )
        client._get_client = AsyncMock(return_value=mock_openai_client)

        result = await client.generate_chat_completion(
            [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "user"},
            ],
            tools=[{"type": "function", "function": {"name": "get_facts"}}],
            tool_handlers={"get_facts": lambda args: "fact"},
        )

        assert result == "fallback content"
        assert calls[0]["tools"] is not None
        assert calls[1]["tools"] is None
        # Fallback should inject BAND_CONTEXT_SUMMARY as an extra system
        # message right after the original system prompt.
        fallback_messages = calls[1]["messages"]
        assert fallback_messages[0]["role"] == "system"
        assert fallback_messages[1]["role"] == "system"
        assert "Septima Ola" in fallback_messages[1]["content"]
        assert fallback_messages[2]["content"] == "user"

        await client.close()

    @pytest.mark.asyncio
    async def test_reraises_bad_request_when_no_tools_were_used(self, monkeypatch):
        """If tools weren't involved, a BadRequestError is a real failure
        and must propagate rather than being silently swallowed."""
        monkeypatch.setenv("CODEMIE_BASE_URL", "https://codemie.example.com")
        monkeypatch.setenv(
            "CODEMIE_TOKEN_URL",
            "https://keycloak.example.com/realms/test/protocol/openid-connect/token",
        )
        monkeypatch.setenv("CODEMIE_CLIENT_ID", "client")
        monkeypatch.setenv("CODEMIE_CLIENT_SECRET", "secret")

        from septima_automation.ai.codemie import CodemieClient

        client = CodemieClient()

        bad_request_error = _bad_request_error("bad request")

        async def fake_create(**kwargs):
            raise bad_request_error

        mock_openai_client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
        )
        client._get_client = AsyncMock(return_value=mock_openai_client)

        with pytest.raises(BadRequestError):
            await client.generate_chat_completion(
                [{"role": "user", "content": "hi"}],
                tools=None,
                tool_handlers=None,
            )

        await client.close()


class TestDeepseekToolIntegration:
    """DeepseekClient.generate_message should attach the band-facts tool
    and resolve tool calls the same way as Codemie, per the shared
    tool_loop implementation."""

    @pytest.mark.asyncio
    async def test_generate_message_resolves_tool_call(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

        from septima_automation.ai.deepseek import DeepseekClient

        client = DeepseekClient()

        tool_response = _response(
            None,
            tool_calls=[_tool_call("get_septima_ola_facts", '{"topic": "perfil"}')],
        )
        final_response = _response("Despertar de Septima Ola: reggae y ska. 🎶")

        create = AsyncMock(side_effect=[tool_response, final_response])
        client._client.chat.completions.create = create

        result = await client.generate_message("Despertar", "Septima Ola")

        assert result == "Despertar de Septima Ola: reggae y ska. 🎶"
        assert create.await_count == 2
        first_kwargs = create.await_args_list[0].kwargs
        assert first_kwargs["tools"][0]["function"]["name"] == "get_septima_ola_facts"
        assert first_kwargs["max_tokens"] == 800

        await client.close()

    @pytest.mark.asyncio
    async def test_generate_message_falls_back_to_reasoning_content(self, monkeypatch):
        """Content extraction must still honor the reasoning_content
        fallback after the tool-loop refactor."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")

        from septima_automation.ai.deepseek import DeepseekClient

        client = DeepseekClient()

        message = SimpleNamespace(
            content="", tool_calls=None, reasoning_content="texto de respaldo"
        )
        message.model_dump = lambda exclude_none=True: {"role": "assistant"}
        choice = SimpleNamespace(message=message, finish_reason="stop")
        response = SimpleNamespace(choices=[choice])

        create = AsyncMock(return_value=response)
        client._client.chat.completions.create = create

        result = await client.generate_message("Redemption Song", "Bob Marley")
        assert result == "texto de respaldo"

        await client.close()
