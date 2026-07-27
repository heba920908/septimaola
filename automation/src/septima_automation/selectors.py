"""Random selectors for video assets."""

import logging
import random
from typing import List, Optional

from .config import VideoAsset, VIDEOS_CONFIG

logger = logging.getLogger(__name__)


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
    candidates = videos if videos is not None else VIDEOS_CONFIG

    if not candidates:
        logger.error("No video assets configured in VIDEOS_CONFIG")
        raise ValueError(
            "No video assets configured. "
            "Please add video assets to VIDEOS_CONFIG in config.py"
        )

    selected = random.choice(candidates)
    logger.debug(f"Selected video: {selected.slug} ({len(candidates)} available)")
    return selected
