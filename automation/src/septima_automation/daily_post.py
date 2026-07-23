"""Main entry point for daily social media posting."""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from .ai.factory import create_provider
from .config import VIDEOS_CONFIG
from .message_generator import MessageGenerator
from .selectors import select_random_video
from .social.facebook import FacebookPublisher
from .social.instagram import InstagramPublisher
from .video_downloader import VideoDownloader


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
    return parser.parse_args()


async def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Load environment variables from automation/.env (local dev)
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    # Check video assets are configured
    if not VIDEOS_CONFIG:
        print("ERROR: No video assets in VIDEOS_CONFIG (config.py)", file=sys.stderr)
        print("Add Google Drive IDs for videos first.", file=sys.stderr)
        return 1

    try:
        # Select random video
        if args.verbose:
            print("Selecting random video...")

        video = select_random_video()

        if args.verbose:
            print(f"  Video : {video.slug} - {video.title} by {video.author}")

        # Generate AI message
        provider_name = args.provider or None  # factory reads AI_PROVIDER env if None
        if args.verbose:
            from .config import AI_PROVIDER_DEFAULT
            import os

            resolved = args.provider or os.getenv("AI_PROVIDER", AI_PROVIDER_DEFAULT)
            print(f"Generating message via '{resolved}'...")

        async with create_provider(provider_name) as ai:
            message_gen = MessageGenerator(ai)
            caption = await message_gen.generate_post(
                song_title=video.title,
                song_author=video.author,
            )

        if args.verbose:
            print(f"\nCaption:\n{caption}\n")

        # Download video
        if args.verbose:
            print("Downloading video from Google Drive...")

        async with VideoDownloader() as downloader:
            video_path = await downloader.download(url=video.public_url)

        if args.verbose:
            print(f"Video: {video_path}")

        if args.dry_run:
            print("\nDRY RUN — not publishing.")
            print(f"Video  : {video_path}")
            print(f"Caption:\n{caption}")
            # Clean up downoladed video during dry run too
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
        if not args.skip_instagram:
            tasks.append(publish_instagram())

        if tasks:
            gathered = await asyncio.gather(*tasks, return_exceptions=True)
            for exc in gathered:
                if isinstance(exc, Exception):
                    print(f"Publish error: {exc}", file=sys.stderr)

        # Cleanup temp video
        video_path.unlink(missing_ok=True)

        # Summary
        print("\n=== Daily Post Summary ===")
        print(f"Video    : {video.slug}")
        print(f"Title    : {video.title}")
        print(f"Facebook : {results.get('facebook', 'SKIPPED')}")
        print(f"Instagram: {results.get('instagram', 'SKIPPED') or 'Not implemented'}")

        return 0 if any(results.values()) else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def run() -> None:
    """Synchronous entry point for uv run / pip scripts."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    run()
