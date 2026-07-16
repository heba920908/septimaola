"""Random selectors for images and audio assets."""

import random
from typing import List, Optional

from .config import ImageAsset, AudioAsset, IMAGES_CONFIG, AUDIO_CONFIG


def select_random_image(
    images: Optional[List[ImageAsset]] = None,
    exclude_categories: Optional[List[str]] = None,
) -> ImageAsset:
    """Select a random image, optionally filtering by category.

    Args:
        images: Optional list of images to choose from (defaults to IMAGES_CONFIG)
        exclude_categories: Categories to exclude (e.g., ["members"])

    Returns:
        Randomly selected ImageAsset

    Raises:
        ValueError: If no images available after filtering
    """
    candidates = images or IMAGES_CONFIG

    if exclude_categories:
        candidates = [
            img for img in candidates if img.category not in exclude_categories
        ]

    if not candidates:
        raise ValueError("No images available after filtering")

    return random.choice(candidates)


def select_random_audio(
    audio_clips: Optional[List[AudioAsset]] = None,
) -> AudioAsset:
    """Select a random audio clip.

    Args:
        audio_clips: Optional list to choose from (defaults to AUDIO_CONFIG)

    Returns:
        Randomly selected AudioAsset

    Raises:
        ValueError: If no audio clips available
    """
    candidates = audio_clips or AUDIO_CONFIG

    if not candidates:
        raise ValueError(
            "No audio clips configured. "
            "Please add audio assets to AUDIO_CONFIG in config.py"
        )

    return random.choice(candidates)


def select_daily_assets() -> tuple[ImageAsset, AudioAsset]:
    """Select both image and audio for daily post.

    Returns:
        Tuple of (selected_image, selected_audio)
    """
    image = select_random_image()
    audio = select_random_audio()
    return image, audio
