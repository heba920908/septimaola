# ADR-0014: Social insights JSON report via `insights-report`

## Status

Accepted

## Context

We want to start tracking Facebook Page and Instagram professional account
metrics (followers, engagement) for Séptima Ola so a future report/dashboard
can be built on top of historical data. The `automation/` uv package already
authenticates against the Facebook Graph API for daily posting
(`FacebookPublisher`, `InstagramPublisher`), so it is the natural place to
add read-only metrics collection rather than standing up a second package.

Live testing against the `FACEBOOK_PAGE_ID` / `FACEBOOK_ACCESS_TOKEN`
credentials in `automation/.env` surfaced two distinct issues, one of which
was later resolved by reissuing the access token:

1. **Permission gap (resolved)**: initially, `GET /{ig-media-id}/insights`
   returned `(#10) Application does not have permission for this action`
   because the token's granted scopes did not include
   `instagram_manage_insights`. After the token was reissued with that
   scope added, this call succeeds.
2. **Metric-name gap (discovered after the permission fix, resolved in
   code)**: once the permission was granted, the *same* endpoint returned a
   different error —
   `(#100) metric[0] must be one of the following values: impressions,
   reach, replies, saved, likes, comments, shares, total_interactions, ...`
   and separately,
   `"Starting from version v22.0 and above, the impressions metric is no
   longer supported for the queried media."`
   The original metric list (`engagement`, `impressions`, `reach`) used
   legacy Graph API metric names that Meta deprecated/renamed as of API
   v22.0+. `total_interactions` is the modern replacement for `engagement`
   (likes + comments + shares + saves, net of removals); `impressions` has
   no direct per-media replacement and was dropped. The corrected metric set
   — `reach`, `total_interactions`, `likes`, `comments`, `shares`, `saved`,
   `views` — was confirmed live against both `IMAGE` and `VIDEO`/`REELS`
   media.
3. `GET /{page_id}/posts` still returns
   `(#10) requires pages_read_engagement permission or Page Public Content
   Access feature`, even though `pages_read_engagement` is a granted scope —
   this is an App Access Level gate (Standard vs. Advanced Access), not a
   token-scope or metric-name issue, and remains unresolved.

Given this, the script needs to degrade gracefully rather than fail outright
when an Insights call is rejected — whether due to permissions, an
unsupported metric name, or an App Access Level gate — while remaining
forward-compatible as Meta continues to evolve the API.

## Decision

- Add a new console script, `insights-report` (`uv run insights-report`),
  to the existing `automation/` uv package — not a separate package —
  following the same conventions as `daily-post` (`argparse`, `setup_logger`,
  `load_dotenv(automation/.env)`, async `main()` + sync `run()` entry point).
- Add `pydantic` as an explicit dependency (previously only transitive via
  `openai`) and model the output as pydantic `BaseModel`s:
  `PostMetric`, `FacebookAccountSnapshot`, `InstagramAccountSnapshot`,
  `SocialMetricsSnapshot`, and a top-level `SocialMetricsReport` with a
  `history: list[SocialMetricsSnapshot]` field.
- Reuse `SocialPublisher.resolve_account_context()` (in `social/base.py`) via
  a new read-only `InsightsClient(SocialPublisher)` in `social/insights.py`,
  so Page ID / Page Access Token / Instagram Business Account ID resolution
  stays consistent with the publishing code path.
- Fetch real Graph API Insights metrics — `reach`, `total_interactions`,
  `likes`, `comments`, `shares`, `saved`, `views` per Instagram media item
  (see `config.INSTAGRAM_MEDIA_INSIGHTS_METRICS`) — and Facebook Page posts
  with likes/comments totals, **best-effort**: on a permission, unsupported-
  metric, or request error, log a warning once per run and fall back to
  `null`/empty values instead of raising. This means the report is always
  generated with whatever fields the token/API version currently supports,
  and will keep working (or degrade gracefully) as Meta continues to rename
  or gate individual metrics — no code changes required to avoid a hard
  failure, only to pick up newly-available metric names.
- Output is written to `react/src/data/social-metrics.json`, gitignored
  (`react/.gitignore` → `src/data/social-metrics.json`) and regenerated on
  demand or by CI, matching the existing `public/images/` build-artifact
  convention in the React app. Each run loads the existing file (if present),
  appends a new timestamped snapshot to `history`, and writes it back — this
  favors a growing time series over a single overwritten snapshot, since the
  stated end goal is a historical report.
- Switch the shared `setup_logger()` handler from `sys.stdout` to
  `sys.stderr` so `uv run insights-report --dry-run` can print clean JSON to
  stdout for piping/inspection without log lines interleaved.

## Consequences

- **Positive**: Metrics collection reuses existing auth/config conventions
  (`social/base.py`, `config.py`, `.env`) with no new package or CI wiring
  needed; the JSON schema is pydantic-validated and directly consumable by a
  future React report component or a separate report-generation script.
- **Positive**: The script never hard-fails due to missing Insights
  permissions or renamed/unsupported metrics — it always produces a usable
  report with whatever data the current token/API version supports, and
  clearly logs/records what's missing via `insights_permission_warning` and
  per-section `*_error` fields.
- **Positive**: With `instagram_manage_insights` granted and the corrected
  metric names, Instagram media-level `reach`, `total_interactions`,
  `shares`, `saved`, and `views` are now real, live-verified data — not
  placeholders.
- **Negative**: Facebook Page post-level engagement (`GET /{page_id}/posts`)
  remains blocked by an App Access Level gate unrelated to token scopes;
  `posts` stays empty and `posts_error` populated until Advanced Access (or
  Page Public Content Access) is granted for `pages_read_engagement`.
- **Negative**: Because `social-metrics.json` is gitignored, the history
  array resets on any machine/CI runner that doesn't persist it between
  runs. Persisting history across GitHub Actions runs (e.g. via
  `actions/cache`, following the same pattern as `automation/.state/posted.json`
  in `docs/decisions/0013-posted-video-dedup.md`) is a follow-up, not
  implemented by this change.
- **Neutral**: Changing the logger to write to stderr instead of stdout is a
  shared change affecting `daily-post` too; it does not alter `daily-post`'s
  behavior since it never relied on stdout for machine-readable output.
