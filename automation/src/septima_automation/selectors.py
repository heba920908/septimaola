"""Random selectors for video assets."""

import random
from typing import List, Optional

from .config import VideoAsset, VIDEOS_CONFIG


def select_random_video(
    videos: Optional[List[VideoAsset]] = None,
) -> VideoAsset:
    """Select a random video asset.

    Args:
        videos: Optional list of videos to choose from (defaults to VIDEOS_CONFIG)

    Returns:
        Randomly selected VideoAsset

    Raises:
        ValueError: If no videos available
    """
    candidates = videos or VIDEOS_CONFIG

    if not candidates:
        raise ValueError(
            "No video assets configured. "
            "Please add video assets to VIDEOS_CONFIG in config.py"
        )

    return random.choice(candidates)
