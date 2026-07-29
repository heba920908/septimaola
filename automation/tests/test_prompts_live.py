"""Live integration tests for prompt quality using LLM-as-grader.

These tests require live LLM access and are skipped by default.
Run with: uv run pytest automation/tests/test_prompts_live.py --live -v
"""

import logging
import os
import pytest
import pytest_asyncio

from septima_automation.ai.prompts import build_user_prompt, SYSTEM_PROMPT
from septima_automation.ai.factory import create_provider

# Import graders
from graders import CodemieGrader, SOCIAL_MEDIA_RUBRIC

logger = logging.getLogger(__name__)


# Thresholds for quality gates
MIN_TOTAL_SCORE = 3.5
MIN_TONE_SCORE = 3.0
MIN_LENGTH_SCORE = 4.0


def has_codemie_credentials():
    """Check if all required Codemie credentials are available."""
    required = [
        "CODEMIE_BASE_URL",
        "CODEMIE_TOKEN_URL",
        "CODEMIE_CLIENT_ID",
        "CODEMIE_CLIENT_SECRET",
    ]
    return all(os.getenv(var) for var in required)


def has_deepseek_credentials():
    """Check if Deepseek API key is available."""
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def log_generation(
    provider: str, song_title: str, song_author: str, response: str
) -> None:
    """Log a live provider response for prompt-quality review."""
    logger.info(
        "Live %s generation for %r by %r:\n%s",
        provider,
        song_title,
        song_author,
        response,
    )


@pytest_asyncio.fixture
async def codemie_provider():
    """Fixture for Codemie provider."""
    provider = create_provider("codemie")
    yield provider
    await provider.close()


@pytest_asyncio.fixture
async def deepseek_provider():
    """Fixture for Deepseek provider."""
    provider = create_provider("deepseek")
    yield provider
    await provider.close()


@pytest_asyncio.fixture
async def grader():
    """Fixture for Codemie grader."""
    grader_obj = CodemieGrader("codemie")
    yield grader_obj
    await grader_obj.close()


class TestBuildUserPromptLive:
    """Live tests for build_user_prompt function output quality."""

    @pytest.mark.asyncio
    @pytest.mark.live
    @pytest.mark.skipif(
        not has_codemie_credentials(),
        reason="Missing required Codemie credentials",
    )
    async def test_codemie_generates_valid_content(self, codemie_provider, grader):
        """Validate Codemie generates quality social media content.

        This test generates content using Codemie and validates it using
        the LLM-as-grader pattern.
        """
        response = await codemie_provider.generate_message(
            "Redemption Song", "Bob Marley"
        )
        log_generation("Codemie", "Redemption Song", "Bob Marley", response)

        assert response, "Response should not be empty"
        assert len(response) > 20, "Response should be substantive"

        # Use grader to evaluate quality
        result = await grader.evaluate(
            response,
            rubric=SOCIAL_MEDIA_RUBRIC,
            context={
                "song_title": "Redemption Song",
                "song_author": "Bob Marley",
                "expected_language": "es",
                "expected_tone": "positive",
            },
        )
        logger.info(
            "Codemie grader result: total=%.2f passed=%s criteria=%s feedback=%s",
            result.total,
            result.passed,
            result.criteria,
            result.feedback,
        )

        assert result.total >= MIN_TOTAL_SCORE, (
            f"Quality score {result.total:.2f} below threshold {MIN_TOTAL_SCORE}. "
            f"Feedback: {result.feedback}"
        )
        assert result.criteria.get("tone_match", 0) >= MIN_TONE_SCORE
        assert result.criteria.get("length", 0) >= MIN_LENGTH_SCORE

    @pytest.mark.asyncio
    @pytest.mark.live
    @pytest.mark.skipif(
        not has_deepseek_credentials(),
        reason="Missing DEEPSEEK_API_KEY",
    )
    async def test_deepseek_generates_valid_content(self, deepseek_provider, grader):
        """Validate Deepseek generates quality social media content."""
        response = await deepseek_provider.generate_message(
            "Three Little Birds", "Bob Marley"
        )
        log_generation("Deepseek", "Three Little Birds", "Bob Marley", response)

        assert response, "Response should not be empty"
        assert len(response) > 20, "Response should be substantive"

        result = await grader.evaluate(
            response,
            rubric=SOCIAL_MEDIA_RUBRIC,
            context={
                "song_title": "Three Little Birds",
                "song_author": "Bob Marley",
                "expected_language": "es",
                "expected_tone": "positive",
            },
        )
        logger.info(
            "Deepseek grader result: total=%.2f passed=%s criteria=%s feedback=%s",
            result.total,
            result.passed,
            result.criteria,
            result.feedback,
        )

        assert result.total >= MIN_TOTAL_SCORE, (
            f"Quality score {result.total:.2f} below threshold {MIN_TOTAL_SCORE}. "
            f"Feedback: {result.feedback}"
        )

    @pytest.mark.asyncio
    @pytest.mark.live
    @pytest.mark.skipif(
        not has_codemie_credentials(),
        reason="Missing required Codemie credentials",
    )
    @pytest.mark.parametrize(
        "song_title,song_author",
        [
            ("La Bamba", "Ritchie Valens"),
            ("Oye Cómo Va", "Santana"),
            ("Guantanamera", "Celia Cruz"),
            ("Despacito", "Luis Fonsi"),
        ],
    )
    async def test_codemie_handles_various_songs(
        self, codemie_provider, grader, song_title, song_author
    ):
        """Test prompt works with different Latin music songs."""
        response = await codemie_provider.generate_message(song_title, song_author)
        log_generation("Codemie", song_title, song_author, response)

        assert response, f"Empty response for {song_title}"

        # Quick quality check - no grader needed for basic validation
        assert len(response) > 10, "Response too short"
        assert any(char in response for char in ["🎵", "🎶", "🎷", "🎸", "🎹"]), (
            "Response should contain a musical emoji"
        )


class TestCrossProviderConsistency:
    """Tests to validate consistency between Codemie and Deepseek."""

    @pytest.mark.asyncio
    @pytest.mark.live
    @pytest.mark.skipif(
        not (has_codemie_credentials() and has_deepseek_credentials()),
        reason="Missing credentials for one or both providers",
    )
    async def test_both_providers_generate_spanish_content(
        self, codemie_provider, deepseek_provider
    ):
        """Both providers should generate Spanish-language content."""
        song_title = "One Love"
        song_author = "Bob Marley"

        codemie_response = await codemie_provider.generate_message(
            song_title, song_author
        )
        deepseek_response = await deepseek_provider.generate_message(
            song_title, song_author
        )
        log_generation("Codemie", song_title, song_author, codemie_response)
        log_generation("Deepseek", song_title, song_author, deepseek_response)

        # Spanish indicators
        spanish_words = [
            "canción",
            "música",
            "ritmo",
            "vida",
            "amor",
            "alma",
            "corazón",
        ]

        codemie_has_spanish = any(
            word in codemie_response.lower() for word in spanish_words
        )
        deepseek_has_spanish = any(
            word in deepseek_response.lower() for word in spanish_words
        )

        assert codemie_has_spanish, (
            f"Codemie response lacks Spanish: {codemie_response[:100]}"
        )
        assert deepseek_has_spanish, (
            f"Deepseek response lacks Spanish: {deepseek_response[:100]}"
        )

    @pytest.mark.asyncio
    @pytest.mark.live
    @pytest.mark.skipif(
        not (has_codemie_credentials() and has_deepseek_credentials()),
        reason="Missing credentials for one or both providers",
    )
    async def test_both_providers_include_emoji(
        self, codemie_provider, deepseek_provider
    ):
        """Both providers should include musical emojis."""
        song_title = "No Woman No Cry"
        song_author = "Bob Marley"

        codemie_response = await codemie_provider.generate_message(
            song_title, song_author
        )
        deepseek_response = await deepseek_provider.generate_message(
            song_title, song_author
        )
        log_generation("Codemie", song_title, song_author, codemie_response)
        log_generation("Deepseek", song_title, song_author, deepseek_response)

        emojis = ["🎵", "🎶", "🎷", "🎸", "🎹", "🎺", "🥁", "🎤", "🎧"]

        assert any(e in codemie_response for e in emojis), (
            "Codemie response missing emoji"
        )
        assert any(e in deepseek_response for e in emojis), (
            "Deepseek response missing emoji"
        )


class TestPromptStructure:
    """Tests for validating prompt structure and content (no live LLM needed)."""

    def test_build_user_prompt_includes_song_info(self):
        """User prompt should include song title and author."""
        prompt = build_user_prompt("Test Song", "Test Artist")

        assert "Test Song" in prompt
        assert "Test Artist" in prompt
        assert "Canción:" in prompt
        assert "Artista:" in prompt

    def test_build_user_prompt_specifies_requirements(self):
        """User prompt should specify output requirements."""
        prompt = build_user_prompt("Song", "Artist")

        assert "2-3 oraciones" in prompt.lower() or "2-3" in prompt
        assert "inspirador" in prompt.lower() or "positivo" in prompt.lower()
        assert "fun-fact" in prompt.lower() or "dato" in prompt.lower()

    def test_system_prompt_contains_constraints(self):
        """System prompt should contain key constraints."""
        assert "español" in SYSTEM_PROMPT.lower()
        assert "méxico" in SYSTEM_PROMPT.lower()
        assert (
            "positiv" in SYSTEM_PROMPT.lower() or "optimista" in SYSTEM_PROMPT.lower()
        )
