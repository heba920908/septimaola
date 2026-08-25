"""Track which videos have already been posted to social media.

Persistence is a plain JSON file so the history can be carried between GitHub
Actions runs through the ``actions/cache`` mechanism without needing a database.
The canonical identity of a video is its Google Drive ``drive_id``.
"""

import json
import logging
from pathlib import Path
from typing import Iterable, Optional, Set

from .config import VideoAsset

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = (
    Path(__file__).resolve().parent.parent.parent / ".state" / "posted.json"
)


class PostedTracker:
    """In-memory view over the posted-videos history file."""

    def __init__(self, path: Path, posted: Optional[Set[str]] = None) -> None:
        self.path = path
        self._posted = posted or set()

    @classmethod
    def load(cls, path: Path) -> "PostedTracker":
        """Create a tracker and populate it from the history file."""
        return cls(path, posted=cls._read(path))

    @staticmethod
    def _read(path: Path) -> Set[str]:
        if not path.exists():
            return set()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Could not read posted history at %s (%s); starting fresh", path, exc
            )
            return set()
        posted = data.get("posted_drive_ids", []) if isinstance(data, dict) else data
        if not isinstance(posted, list):
            return set()
        return {str(item) for item in posted}

    @property
    def posted_drive_ids(self) -> Set[str]:
        """Return a copy of the set of already-posted drive IDs."""
        return set(self._posted)

    def is_posted(self, video: VideoAsset) -> bool:
        """Return True if the video's drive ID has already been posted."""
        return video.drive_id in self._posted

    def filter_unposted(self, videos: Iterable[VideoAsset]) -> list[VideoAsset]:
        """Return only videos whose drive ID has not been posted yet."""
        return [v for v in videos if not self.is_posted(v)]

    def mark_posted(self, video: VideoAsset) -> None:
        """Record a video as posted in the in-memory history."""
        self._posted.add(video.drive_id)

    def reset(self) -> None:
        """Clear history so a new posting cycle can begin."""
        self._posted.clear()

    def save(self) -> None:
        """Persist the history to the state file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"posted_drive_ids": sorted(self._posted)}
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
