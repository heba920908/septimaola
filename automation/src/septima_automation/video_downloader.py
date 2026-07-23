"""Video downloader utility for downloading assets from Google Drive."""

import os
import tempfile
from pathlib import Path
from typing import Optional

import httpx


class VideoDownloader:
    """Download video assets from Google Drive URLs."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.http_client = httpx.AsyncClient(timeout=120.0, follow_redirects=True)

    async def download(self, url: str, filename: Optional[str] = None) -> Path:
        """Download a file from URL to the target output directory.

        Args:
            url: Google Drive direct download URL or any downloadable URL
            filename: Optional custom filename (defaults to randomized name)

        Returns:
            Path to the downloaded video file
        """
        if filename is None:
            filename = f"daily_post_{os.urandom(4).hex()}.mp4"

        output_path = self.output_dir / filename

        response = await self.http_client.get(url)
        response.raise_for_status()

        output_path.write_bytes(response.content)
        return output_path

    async def close(self):
        await self.http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
