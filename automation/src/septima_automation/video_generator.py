"""Video generation using ffmpeg."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import httpx

from .config import (
    VIDEO_CODEC,
    VIDEO_DURATION,
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
)


class VideoGenerator:
    """Generate videos by combining images and audio."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def generate(
        self,
        image_url: str,
        audio_url: str,
        output_filename: Optional[str] = None,
    ) -> Path:
        """Generate a video from image and audio.

        Args:
            image_url: URL to image file
            audio_url: URL to audio file
            output_filename: Optional custom filename

        Returns:
            Path to generated video file
        """
        if output_filename is None:
            output_filename = f"daily_post_{os.urandom(4).hex()}.mp4"

        output_path = self.output_dir / output_filename

        # Download assets
        image_path = await self._download(image_url, ".jpg")
        audio_path = await self._download(audio_url, ".wav")

        try:
            await self._create_video(image_path, audio_path, output_path)
        finally:
            # Cleanup temporary files
            image_path.unlink(missing_ok=True)
            audio_path.unlink(missing_ok=True)

        return output_path

    async def _download(self, url: str, suffix: str) -> Path:
        """Download a file from URL to temp location."""
        response = await self.http_client.get(url)
        response.raise_for_status()

        temp_path = self.output_dir / f"temp_{os.urandom(4).hex()}{suffix}"
        temp_path.write_bytes(response.content)
        return temp_path

    async def _create_video(
        self,
        image_path: Path,
        audio_path: Path,
        output_path: Path,
    ) -> None:
        """Create video using ffmpeg.

        Combines static image with audio to create a video of specified duration.
        The image is scaled to fit the target dimensions.
        """
        # ffmpeg command to create video
        # - loop image for VIDEO_DURATION seconds
        # - add audio (trimmed to VIDEO_DURATION if longer)
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-c:v",
            VIDEO_CODEC,
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(VIDEO_FPS),
            "-t",
            str(VIDEO_DURATION),
            "-vf",
            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

    async def close(self):
        await self.http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
