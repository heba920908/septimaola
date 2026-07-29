"""Tests for daily post functionality."""

import pytest

from septima_automation.config import VideoAsset
from septima_automation.selectors import select_random_video


class TestConfig:
    """Test configuration data structures."""

    def test_video_asset_public_url(self):
        """Test VideoAsset generates correct direct download URL."""
        asset = VideoAsset("test", "xyz789", "Test Video", "Artist")
        assert "drive.google.com" in asset.public_url
        assert "xyz789" in asset.public_url


class TestSelectors:
    """Test asset selectors."""

    def test_select_random_video(self):
        """Test random video selection."""
        # If config is empty, populate with mock to test selection
        videos = [
            VideoAsset("slug-1", "drive-1", "Title 1", "Author 1"),
            VideoAsset("slug-2", "drive-2", "Title 2", "Author 2"),
        ]
        video = select_random_video(videos)
        assert video is not None
        assert isinstance(video, VideoAsset)
        assert video.slug in ["slug-1", "slug-2"]

    def test_select_random_video_empty_config(self):
        """Test that empty video config raises error."""
        with pytest.raises(ValueError):
            select_random_video([])


class TestDailyPostCLI:
    """Test CLI behavior for daily-post."""

    def test_parse_args_default_disables_facebook(self):
        from septima_automation.daily_post import parse_args

        args = parse_args([])

        assert not args.facebook
        assert not args.skip_facebook

    def test_parse_args_facebook_flag_enables_publishing(self):
        from septima_automation.daily_post import parse_args

        args = parse_args(["--facebook"])

        assert args.facebook
        assert not args.skip_facebook


class TestVideoDownload:
    """Test video downloader (requires network access)."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires network access")
    async def test_video_download(self):
        """Test downloading with real assets."""
        from septima_automation.video_downloader import VideoDownloader

        async with VideoDownloader():
            # This test requires actual URLs
            pass
