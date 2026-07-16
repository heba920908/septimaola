"""Extended tests for selectors — fills gaps not covered by test_daily_post.py."""

import pytest

from septima_automation.config import ImageAsset, AudioAsset
from septima_automation.selectors import (
    select_random_image,
    select_random_audio,
    select_daily_assets,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _images(*categories: str) -> list[ImageAsset]:
    """Build a minimal list of ImageAssets with the given categories."""
    return [
        ImageAsset(slug=f"img-{i}", drive_id=f"drive-{i}", category=cat)
        for i, cat in enumerate(categories)
    ]


def _audio(*titles: str) -> list[AudioAsset]:
    """Build a minimal list of AudioAssets."""
    return [
        AudioAsset(slug=f"clip-{i}", drive_id=f"drive-{i}", title=t, author="Artist")
        for i, t in enumerate(titles)
    ]


# ---------------------------------------------------------------------------
# select_random_image — extended cases
# ---------------------------------------------------------------------------


class TestSelectRandomImageExtended:
    def test_returns_from_explicit_list(self):
        """Image is drawn from the provided list, not IMAGES_CONFIG."""
        images = _images("promo", "promo")
        result = select_random_image(images=images)
        assert result in images

    def test_returns_correct_type(self):
        result = select_random_image(images=_images("gallery"))
        assert isinstance(result, ImageAsset)

    def test_single_item_always_returned(self):
        """Single-item list always returns that item."""
        images = _images("promo")
        for _ in range(10):
            assert select_random_image(images=images) is images[0]

    def test_empty_list_falls_back_to_global_config(self):
        """Empty explicit list is falsy, so IMAGES_CONFIG is used as fallback.

        This is a known behaviour of the `images or IMAGES_CONFIG` pattern:
        an empty list argument is treated the same as None.  The test
        documents this quirk rather than asserting a raise.
        """
        # IMAGES_CONFIG is populated, so no ValueError is expected here
        result = select_random_image(images=[])
        assert isinstance(result, ImageAsset)

    def test_raises_when_filter_excludes_all(self):
        """Exclusion that removes every candidate raises ValueError."""
        images = _images("members", "members", "members")
        with pytest.raises(ValueError, match="No images available"):
            select_random_image(images=images, exclude_categories=["members"])

    def test_exclude_categories_filters_correctly(self):
        """Images in excluded categories never appear in results."""
        images = _images("members", "gallery", "gallery", "promo")
        for _ in range(30):
            result = select_random_image(images=images, exclude_categories=["members"])
            assert result.category != "members"

    def test_multiple_exclusions(self):
        """Multiple categories can be excluded simultaneously."""
        images = _images("members", "gallery", "promo", "promo")
        for _ in range(30):
            result = select_random_image(
                images=images, exclude_categories=["members", "gallery"]
            )
            assert result.category == "promo"


# ---------------------------------------------------------------------------
# select_random_audio — extended cases
# ---------------------------------------------------------------------------


class TestSelectRandomAudioExtended:
    def test_returns_from_explicit_list(self):
        """Audio is drawn from the provided list."""
        clips = _audio("Redemption Song", "One Love")
        result = select_random_audio(audio_clips=clips)
        assert result in clips

    def test_returns_correct_type(self):
        clips = _audio("Test Track")
        result = select_random_audio(audio_clips=clips)
        assert isinstance(result, AudioAsset)

    def test_single_clip_always_returned(self):
        clips = _audio("Only Track")
        for _ in range(10):
            assert select_random_audio(audio_clips=clips) is clips[0]


# ---------------------------------------------------------------------------
# select_daily_assets
# ---------------------------------------------------------------------------


class TestSelectDailyAssets:
    def test_raises_when_audio_config_is_empty(self, monkeypatch):
        """select_daily_assets propagates ValueError from empty AUDIO_CONFIG."""
        import septima_automation.selectors as sel_module

        # Patch AUDIO_CONFIG at the module level used by the selector
        monkeypatch.setattr(sel_module, "AUDIO_CONFIG", [])
        with pytest.raises(ValueError, match="No audio clips configured"):
            select_daily_assets()

    def test_returns_tuple_of_correct_types(self, monkeypatch):
        """Returns (ImageAsset, AudioAsset) when both configs are populated."""
        import septima_automation.selectors as sel_module

        monkeypatch.setattr(sel_module, "AUDIO_CONFIG", _audio("Track A"))
        # IMAGES_CONFIG already populated in the real module; use it as-is
        image, audio = select_daily_assets()
        assert isinstance(image, ImageAsset)
        assert isinstance(audio, AudioAsset)
