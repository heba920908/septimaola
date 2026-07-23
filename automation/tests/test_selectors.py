"""Extended tests for selectors — fills gaps not covered by test_daily_post.py."""

import pytest

from septima_automation.config import VideoAsset
from septima_automation.selectors import select_random_video


def _videos(*titles: str) -> list[VideoAsset]:
    """Build a minimal list of VideoAssets."""
    return [
        VideoAsset(slug=f"clip-{i}", drive_id=f"drive-{i}", title=t, author="Artist")
        for i, t in enumerate(titles)
    ]


class TestSelectRandomVideoExtended:
    def test_returns_from_explicit_list(self):
        """Video is drawn from the provided list, not VIDEOS_CONFIG."""
        videos = _videos("La Estacion", "Aguita de Coco")
        result = select_random_video(videos=videos)
        assert result in videos

    def test_returns_correct_type(self):
        videos = _videos("Test Track")
        result = select_random_video(videos=videos)
        assert isinstance(isinstance(result, VideoAsset), bool)
        assert isinstance(result, VideoAsset)

    def test_single_clip_always_returned(self):
        videos = _videos("Only Track")
        for _ in range(10):
            assert select_random_video(videos=videos) is videos[0]

    def test_raises_when_empty_config(self, monkeypatch):
        """select_random_video raises ValueError when VIDEOS_CONFIG is empty and no videos argument passed."""
        import septima_automation.selectors as sel_module

        # Patch VIDEOS_CONFIG at the module level
        monkeypatch.setattr(sel_module, "VIDEOS_CONFIG", [])
        with pytest.raises(ValueError, match="No video assets configured"):
            select_random_video()
