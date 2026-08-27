"""CLI entry point for generating the Facebook/Instagram metrics JSON reports.

Usage:
    uv run insights-report
    uv run insights-report --since 2026-06-01
    uv run insights-report --limit 20 --verbose
    uv run insights-report --dry-run          # print JSON, don't write files
    uv run insights-report --output /tmp/social-metrics.json \\
        --posts-output /tmp/posts-metrics.json

Writes two files (see docs/decisions/0014-social-insights-json-report.md,
2026-08-27 amendment):

- ``social-metrics.json`` — a growing ``history`` of account-level snapshots
  (followers, fan count, media count). Appended to on every run.
- ``posts-metrics.json`` — Facebook posts and Instagram media within the
  last ``--since`` days (default 90), capped at ``--limit`` items (default
  90). Fully overwritten on every run — no history.

See automation/README.md for credential setup and current permission
limitations (media-level insights require `instagram_manage_insights`,
which is not yet granted to the automation's access token).
"""

import argparse
import asyncio
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from .ai.factory import create_provider
from .ai.insights_analyzer import run_insights_analysis
from .config import (
    DEFAULT_POSTS_LIMIT,
    DEFAULT_POSTS_SINCE_DAYS,
    INSIGHTS_DATA_OUTPUT_PATH,
    INSIGHTS_OUTPUT_PATH,
    POSTS_OUTPUT_PATH,
)
from .logger import setup_logger
from .social.insights import InsightsClient, SocialMetricsReport

logger = logging.getLogger(__name__)


def _parse_since(value: str) -> date:
    """Parse a `--since` CLI value as an ISO date (YYYY-MM-DD)."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid --since value {value!r}; expected YYYY-MM-DD"
        ) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Facebook Page and Instagram account/post metrics, correlate with "
            "band agenda events, synthesize AI insights, and write JSON reports."
        )
    )
    parser.add_argument(
        "--since",
        type=_parse_since,
        default=None,
        help=(
            "Only fetch posts/media created on or after this date "
            f"(YYYY-MM-DD). Defaults to {DEFAULT_POSTS_SINCE_DAYS} days ago."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_POSTS_LIMIT,
        help=(
            "Max number of posts/media to fetch per platform "
            f"(default: {DEFAULT_POSTS_LIMIT})"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INSIGHTS_OUTPUT_PATH,
        help=f"Path to write the account-metrics report to (default: {INSIGHTS_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--posts-output",
        type=Path,
        default=POSTS_OUTPUT_PATH,
        help=f"Path to write the posts-metrics report to (default: {POSTS_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--insights-data-output",
        type=Path,
        default=INSIGHTS_DATA_OUTPUT_PATH,
        help=f"Path to write the React visualization dataset to (default: {INSIGHTS_DATA_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AIProvider invocation and use fast heuristic rule-based synthesis",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated reports as JSON instead of writing to disk",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def _load_existing_report(path: Path) -> SocialMetricsReport:
    """Load an existing account-metrics report file, or start fresh."""
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

    since = args.since or (date.today() - timedelta(days=DEFAULT_POSTS_SINCE_DAYS))

    logger.info(
        "Fetching Séptima Ola social media metrics (since=%s, limit=%d)...",
        since.isoformat(),
        args.limit,
    )

    try:
        async with InsightsClient() as client:
            snapshot, posts_report = await client.build_reports(since, limit=args.limit)
    except ValueError as exc:
        logger.error(f"Missing credentials: {exc}")
        return 1
    except Exception as exc:
        logger.exception(f"Fatal error while fetching metrics: {exc}")
        return 1

    report = _load_existing_report(args.output)
    report.history.append(snapshot)

    # Resolve AI provider if enabled
    ai_provider = None
    if not args.no_ai:
        try:
            ai_provider = create_provider()
        except Exception as exc:
            logger.info("AI provider not configured (%s); falling back to heuristic analyzer", exc)

    logger.info("Running social metrics & agenda correlation analysis...")
    insights_data = await run_insights_analysis(
        snapshot=snapshot,
        posts_report=posts_report,
        report_history=report.history,
        ai_provider=ai_provider,
        use_ai=not args.no_ai and ai_provider is not None,
    )

    social_payload = report.model_dump_json(indent=2, exclude_none=False)
    posts_payload = posts_report.model_dump_json(indent=2, exclude_none=False)
    insights_data_payload = insights_data.model_dump_json(indent=2, exclude_none=False)

    if args.dry_run:
        logger.info("DRY RUN — not writing to disk.")
        print(
            f'{{"social_metrics": {social_payload}, '
            f'"posts_metrics": {posts_payload}, '
            f'"insights_data": {insights_data_payload}}}'
        )
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(social_payload + "\n", encoding="utf-8")

    args.posts_output.parent.mkdir(parents=True, exist_ok=True)
    args.posts_output.write_text(posts_payload + "\n", encoding="utf-8")

    args.insights_data_output.parent.mkdir(parents=True, exist_ok=True)
    args.insights_data_output.write_text(insights_data_payload + "\n", encoding="utf-8")

    # Summary
    logger.info("=" * 50)
    logger.info("Insights Report & Analysis Summary")
    logger.info("=" * 50)
    if snapshot.facebook:
        logger.info(
            f"Facebook : {snapshot.facebook.name or snapshot.facebook.page_id} "
            f"(fans={snapshot.facebook.fan_count}, "
            f"followers={snapshot.facebook.followers_count})"
        )
    else:
        logger.info("Facebook : SKIPPED (no page resolved)")

    if snapshot.instagram:
        logger.info(
            f"Instagram: @{snapshot.instagram.username or snapshot.instagram.account_id} "
            f"(followers={snapshot.instagram.followers_count}, "
            f"media_count={snapshot.instagram.media_count})"
        )
    else:
        logger.info("Instagram: SKIPPED (no account resolved)")

    logger.info(
        f"Posts    : facebook={len(posts_report.facebook_posts)}, "
        f"instagram={len(posts_report.instagram_posts)} "
        f"(since={posts_report.since})"
    )
    logger.info(
        f"Analysis : {len(insights_data.top_posts)} top posts, "
        f"{len(insights_data.agenda_correlations)} agenda events, "
        f"{len(insights_data.ai_analysis.recommendations)} recommendations"
    )

    if posts_report.facebook_posts_error:
        logger.warning(f"Facebook posts error: {posts_report.facebook_posts_error}")
    if posts_report.instagram_posts_error:
        logger.warning(f"Instagram posts error: {posts_report.instagram_posts_error}")
    if posts_report.insights_permission_warning:
        logger.warning(posts_report.insights_permission_warning)

    logger.info(
        f"Account report written to {args.output} ({len(report.history)} snapshot(s) total)"
    )
    logger.info(f"Posts report written to {args.posts_output} (overwritten, no history)")
    logger.info(f"Visualization dataset written to {args.insights_data_output}")

    return 0


def run() -> None:
    """Synchronous entry point for uv run / pip scripts."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    run()
