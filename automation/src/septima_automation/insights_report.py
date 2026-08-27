"""CLI entry point for generating the Facebook/Instagram metrics JSON report.

Usage:
    uv run insights-report
    uv run insights-report --limit 20 --verbose
    uv run insights-report --dry-run          # print JSON, don't write the file
    uv run insights-report --output /tmp/social-metrics.json

See automation/README.md for credential setup and current permission
limitations (media-level insights require `instagram_manage_insights`,
which is not yet granted to the automation's access token).
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from .config import DEFAULT_MEDIA_LIMIT, INSIGHTS_OUTPUT_PATH
from .logger import setup_logger
from .social.insights import InsightsClient, SocialMetricsReport

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Facebook Page and Instagram account metrics and append "
            "a snapshot to the JSON report used by the React press kit."
        )
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_MEDIA_LIMIT,
        help=f"Number of recent posts/media to fetch (default: {DEFAULT_MEDIA_LIMIT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INSIGHTS_OUTPUT_PATH,
        help=f"Path to write the JSON report to (default: {INSIGHTS_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated snapshot as JSON instead of writing to disk",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def _load_existing_report(path: Path) -> SocialMetricsReport:
    """Load an existing report file, or start a fresh one if missing/invalid."""
    if not path.exists():
        return SocialMetricsReport()
    try:
        return SocialMetricsReport.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning(
            "Could not parse existing report at %s (%s); starting fresh", path, exc
        )
        return SocialMetricsReport()


async def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    setup_logger(verbose=args.verbose)

    # Load environment variables from automation/.env (local dev)
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)

    logger.info("Fetching Séptima Ola social media metrics...")

    try:
        async with InsightsClient() as client:
            snapshot = await client.build_snapshot(limit=args.limit)
    except ValueError as exc:
        logger.error(f"Missing credentials: {exc}")
        return 1
    except Exception as exc:
        logger.exception(f"Fatal error while fetching metrics: {exc}")
        return 1

    report = _load_existing_report(args.output)
    report.history.append(snapshot)

    payload = report.model_dump_json(indent=2, exclude_none=False)

    if args.dry_run:
        logger.info("DRY RUN — not writing to disk.")
        print(payload)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload + "\n", encoding="utf-8")

    # Summary
    logger.info("=" * 50)
    logger.info("Insights Report Summary")
    logger.info("=" * 50)
    if snapshot.facebook:
        logger.info(
            f"Facebook : {snapshot.facebook.name or snapshot.facebook.page_id} "
            f"(fans={snapshot.facebook.fan_count}, "
            f"followers={snapshot.facebook.followers_count}, "
            f"posts_fetched={len(snapshot.facebook.posts)})"
        )
        if snapshot.facebook.posts_error:
            logger.warning(f"Facebook posts error: {snapshot.facebook.posts_error}")
    else:
        logger.info("Facebook : SKIPPED (no page resolved)")

    if snapshot.instagram:
        logger.info(
            f"Instagram: @{snapshot.instagram.username or snapshot.instagram.account_id} "
            f"(followers={snapshot.instagram.followers_count}, "
            f"media_count={snapshot.instagram.media_count}, "
            f"media_fetched={len(snapshot.instagram.media)})"
        )
        if snapshot.instagram.media_error:
            logger.warning(f"Instagram media error: {snapshot.instagram.media_error}")
    else:
        logger.info("Instagram: SKIPPED (no account resolved)")

    if snapshot.insights_permission_warning:
        logger.warning(snapshot.insights_permission_warning)

    logger.info(f"Report written to {args.output} ({len(report.history)} snapshot(s) total)")

    return 0


def run() -> None:
    """Synchronous entry point for uv run / pip scripts."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    run()
