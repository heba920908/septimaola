"""Tests for posted-video history tracking."""

import json

from septima_automation.config import VideoAsset
from septima_automation.posted_tracker import PostedTracker


def _videos(*drive_ids: str) -> list[VideoAsset]:
    return [
        VideoAsset(slug=f"clip-{i}", drive_id=did, title=f"Title {i}", author="Artist")
        for i, did in enumerate(drive_ids)
    ]


class TestPostedTracker:
    def test_empty_when_no_file(self, tmp_path):
        tracker = PostedTracker.load(tmp_path / "posted.json")
        assert tracker.posted_drive_ids == set()

    def test_filter_unposted_removes_posted(self, tmp_path):
        path = tmp_path / "posted.json"
        path.write_text(json.dumps({"posted_drive_ids": ["a", "b"]}))
        tracker = PostedTracker.load(path)
        videos = _videos("a", "b", "c")
        assert tracker.filter_unposted(videos) == [videos[2]]

    def test_mark_and_save_roundtrip(self, tmp_path):
        path = tmp_path / "posted.json"
        tracker = PostedTracker.load(path)
        tracker.mark_posted(_videos("a")[0])
        tracker.save()
        data = json.loads(path.read_text())
        assert data["posted_drive_ids"] == ["a"]

    def test_reset_clears_history(self, tmp_path):
        path = tmp_path / "posted.json"
        path.write_text(json.dumps({"posted_drive_ids": ["a"]}))
        tracker = PostedTracker.load(path)
        tracker.reset()
        assert tracker.posted_drive_ids == set()

    def test_corrupt_file_starts_fresh(self, tmp_path):
        path = tmp_path / "posted.json"
        path.write_text("not json")
        tracker = PostedTracker.load(path)
        assert tracker.posted_drive_ids == set()
