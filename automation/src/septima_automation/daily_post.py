"""Main entry point for daily social media posting."""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from .ai.factory import create_provider
from .config import AUDIO_CONFIG
from .message_generator import MessageGenerator
from .selectors import select_daily_assets
from .social.facebook import FacebookPublisher
from .social.instagram import InstagramPublisher
from .video_generator import VideoGenerator


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

    # Check audio assets are configured
    if not AUDIO_CONFIG:
        print("ERROR: No audio assets in AUDIO_CONFIG (config.py)", file=sys.stderr)
        print("Add Google Drive IDs for 15s audio clips first.", file=sys.stderr)
        return 1

    try:
        # Select random assets
        if args.verbose:
            print("Selecting random assets...")

        image, audio = select_daily_assets()

        if args.verbose:
            print(f"  Image : {image.slug} ({image.category})")
            print(f"  Audio : {audio.title} by {audio.author}")

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
                song_title=audio.title,
                song_author=audio.author,
            )

        if args.verbose:
            print(f"\nCaption:\n{caption}\n")

        # Generate video
        if args.verbose:
            print("Generating video with ffmpeg...")

        async with VideoGenerator() as video_gen:
            video_path = await video_gen.generate(
                image_url=image.public_url,
                audio_url=audio.public_url,
            )

        if args.verbose:
            print(f"Video: {video_path}")

        if args.dry_run:
            print("\nDRY RUN — not publishing.")
            print(f"Video  : {video_path}")
            print(f"Caption:\n{caption}")
            return 0

        # Publish concurrently to all configured platforms
        results: dict[str, str | None] = {}

        async def publish_facebook() -> None:
            async with FacebookPublisher() as fb:
                results["facebook"] = await fb.publish(video_path, caption)

        async def publish_instagram() -> None:
            async with InstagramPublisher() as ig:
                results["instagram"] = await ig.publish(video_path, caption)

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
        print(f"Image    : {image.slug}")
        print(f"Audio    : {audio.title}")
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
