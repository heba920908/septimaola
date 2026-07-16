"""Tests for daily post functionality."""

import pytest

from septima_automation.config import ImageAsset, AudioAsset, IMAGES_CONFIG
from septima_automation.selectors import select_random_image, select_random_audio


class TestConfig:
    """Test configuration data structures."""

    def test_image_asset_public_url(self):
        """Test ImageAsset generates correct public URL."""
        asset = ImageAsset("test", "abc123", "gallery")
        assert asset.public_url == "https://lh3.googleusercontent.com/d/abc123"

    def test_audio_asset_public_url(self):
        """Test AudioAsset generates correct download URL."""
        asset = AudioAsset("test", "xyz789", "Test Song", "Artist")
        assert "drive.google.com" in asset.public_url
        assert "xyz789" in asset.public_url


class TestSelectors:
    """Test asset selectors."""

    def test_select_random_image(self):
        """Test random image selection."""
        if IMAGES_CONFIG:
            image = select_random_image()
            assert image is not None
            assert isinstance(image, ImageAsset)

    def test_select_random_image_with_filter(self):
        """Test random image selection with category filter."""
        if IMAGES_CONFIG:
            image = select_random_image(exclude_categories=["members"])
            assert image.category != "members"

    def test_select_random_audio_empty_config(self):
        """Test that empty audio config raises error."""
        with pytest.raises(ValueError):
            select_random_audio([])


class TestVideoGeneration:
    """Test video generation (requires ffmpeg)."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires ffmpeg and network access")
    async def test_video_generation(self):
        """Test video generation with real assets."""
        from septima_automation.video_generator import VideoGenerator

        async with VideoGenerator() as gen:
            # This test requires actual URLs
            pass
