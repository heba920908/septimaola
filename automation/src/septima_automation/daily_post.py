"""Main entry point for daily social media posting."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from .ai.factory import create_provider
from .config import VIDEOS_CONFIG
from .logger import setup_logger
from .message_generator import MessageGenerator
from .selectors import select_random_video
from .social.facebook import FacebookPublisher
from .social.instagram import InstagramPublisher
from .video_downloader import VideoDownloader

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate and publish daily social media post for Séptima Ola"
    )
    parser.add_argument(
        "--provider",
        choices=["deepseek", "codemie"],
        default=None,
        help=(
            "AI provider to use for message generation. "
            "Overrides the AI_PROVIDER env var. "
            "Default: deepseek"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate content and video but skip publishing",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--skip-facebook",
        action="store_true",
        help="Skip Facebook publishing",
    )
    parser.add_argument(
        "--skip-instagram",
        action="store_true",
        help="Skip Instagram publishing",
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI generation and use a local fallback caption",
    )
    return parser.parse_args()


async def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Initialize logger with verbose flag
    setup_logger(verbose=args.verbose)

    # Load environment variables from automation/.env (local dev)
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    logger.info("Starting Séptima Ola daily social media automation...")

    # Check video assets are configured
    if not VIDEOS_CONFIG:
        logger.error("No video assets in VIDEOS_CONFIG (config.py)")
        logger.error("Add Google Drive IDs for videos first.")
        return 1

    try:
        # Select random video
        logger.info("Selecting random video...")
        video = select_random_video()
        logger.info(f"  Video: {video.slug} - {video.title} by {video.author}")

        # Generate AI message
        provider_name = args.provider or None  # factory reads AI_PROVIDER env if None
        if args.verbose:
            from .config import AI_PROVIDER_DEFAULT
            import os

            resolved = args.provider or os.getenv("AI_PROVIDER", AI_PROVIDER_DEFAULT)
            logger.debug(f"Generating message via '{resolved}'...")

        async with create_provider(provider_name) as ai:
            message_gen = MessageGenerator(ai)
            caption = await message_gen.generate_post(
                song_title=video.title,
                song_author=video.author,
                skip_ai=args.skip_ai,
            )

        logger.debug(f"Caption generated:\n{caption}\n")

        # Download video
        logger.info("Downloading video from Google Drive...")
        async with VideoDownloader() as downloader:
            video_path = await downloader.download(url=video.public_url)

        logger.info(f"Video downloaded: {video_path}")

        if args.dry_run:
            logger.info("DRY RUN — not publishing.")
            logger.info(f"Video: {video_path}")
            logger.debug(f"Caption:\n{caption}")
            # Clean up downloaded video during dry run too
            video_path.unlink(missing_ok=True)
            return 0

        # Publish concurrently to all configured platforms
        results: dict[str, str | None] = {}

        async def publish_facebook() -> None:
            async with FacebookPublisher() as fb:
                results["facebook"] = await fb.publish(
                    video_path=video_path,
                    caption=caption,
                    video_url=video.public_url,
                )

        async def publish_instagram() -> None:
            async with InstagramPublisher() as ig:
                results["instagram"] = await ig.publish(
                    video_path=video_path,
                    caption=caption,
                    video_url=video.public_url,
                )

        tasks = []
        if not args.skip_facebook:
            tasks.append(publish_facebook())
            logger.info("Publishing to Facebook...")
        if not args.skip_instagram:
            tasks.append(publish_instagram())
            logger.info("Publishing to Instagram...")

        if tasks:
            gathered = await asyncio.gather(*tasks, return_exceptions=True)
            for exc in gathered:
                if isinstance(exc, Exception):
                    logger.error(f"Publish error: {exc}")

        # Cleanup temp video
        video_path.unlink(missing_ok=True)
        logger.info("✓ Social media posting complete!")

        # Summary
        logger.info("=" * 50)
        logger.info("Daily Post Summary")
        logger.info("=" * 50)
        logger.info(f"Video    : {video.slug}")
        logger.info(f"Title    : {video.title}")
        logger.info(f"Facebook : {results.get('facebook', 'SKIPPED')}")
        logger.info(f"Instagram: {results.get('instagram', 'SKIPPED') or 'Not implemented'}")

        return 0 if any(results.values()) else 1

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


def run() -> None:
    """Synchronous entry point for uv run / pip scripts."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    run()
