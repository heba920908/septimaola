"""Tests for MessageGenerator — uses AsyncMock for the AI provider."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from septima_automation.message_generator import MessageGenerator
from septima_automation.config import HASHTAGS


def _make_generator(
    ai_response: str = "Mensaje inspirador de prueba. 🎵",
) -> MessageGenerator:
    """Return a MessageGenerator with a mocked AI provider."""
    mock_provider = MagicMock()
    mock_provider.generate_message = AsyncMock(return_value=ai_response)
    return MessageGenerator(ai_provider=mock_provider)


class TestGeneratePostFormat:
    """Test the structure and content of the generated post."""

    @pytest.mark.asyncio
    async def test_generate_post_contains_ai_message(self):
        """AI provider response appears at the top of the post."""
        ai_text = "Ritmo que une almas. 🎷"
        gen = _make_generator(ai_response=ai_text)
        post = await gen.generate_post("Redemption Song", "Bob Marley")
        assert post.startswith(ai_text)

    @pytest.mark.asyncio
    async def test_generate_post_contains_song_credit_line(self):
        """Post includes the 'Canción destacada' attribution line."""
        gen = _make_generator()
        post = await gen.generate_post("La Raza", "Séptima Ola")
        assert "Canción destacada: La Raza (Séptima Ola)" in post

    @pytest.mark.asyncio
    async def test_generate_post_contains_hashtags(self):
        """Post ends with at least one hashtag from the pool."""
        gen = _make_generator()
        post = await gen.generate_post("Exodus", "Bob Marley")
        assert any(tag in post for tag in HASHTAGS)

    @pytest.mark.asyncio
    async def test_generate_post_default_hashtag_count(self):
        """Default selection picks exactly 4 hashtags."""
        gen = _make_generator()
        post = await gen.generate_post("One Love", "Bob Marley")
        # Last non-empty line is the space-joined hashtag string
        last_line = [line for line in post.splitlines() if line.strip()][-1]
        hashtags_in_post = [t for t in last_line.split() if t.startswith("#")]
        assert len(hashtags_in_post) == 4

    @pytest.mark.asyncio
    async def test_generate_post_custom_hashtags_used_verbatim(self):
        """When custom_hashtags provided, those exact tags are used."""
        gen = _make_generator()
        custom = ["#TestTag1", "#TestTag2"]
        post = await gen.generate_post(
            "Test Song", "Test Artist", custom_hashtags=custom
        )
        assert "#TestTag1" in post
        assert "#TestTag2" in post
        # None of the default pool should appear
        for default_tag in HASHTAGS:
            assert default_tag not in post

    @pytest.mark.asyncio
    async def test_generate_post_calls_provider_with_correct_args(self):
        """AI provider is called with the exact song title and author."""
        mock_provider = MagicMock()
        mock_provider.generate_message = AsyncMock(return_value="msg")
        gen = MessageGenerator(ai_provider=mock_provider)
        await gen.generate_post("Pressure Drop", "Toots and the Maytals")
        mock_provider.generate_message.assert_awaited_once_with(
            "Pressure Drop", "Toots and the Maytals"
        )


class TestSelectHashtags:
    """Test the internal _select_hashtags helper directly."""

    def test_count_defaults_to_four(self):
        gen = _make_generator()
        result = gen._select_hashtags()
        assert len(result) == 4

    def test_count_never_exceeds_pool_size(self):
        """Requesting more hashtags than exist returns at most len(HASHTAGS)."""
        gen = _make_generator()
        result = gen._select_hashtags(count=9999)
        assert len(result) == len(HASHTAGS)

    def test_all_returned_tags_are_from_pool(self):
        """Every returned hashtag belongs to the configured HASHTAGS pool."""
        gen = _make_generator()
        for _ in range(20):
            for tag in gen._select_hashtags():
                assert tag in HASHTAGS

    def test_returns_list(self):
        gen = _make_generator()
        result = gen._select_hashtags(count=2)
        assert isinstance(result, list)
        assert len(result) == 2
