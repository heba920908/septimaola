# ADR-0013: Posted-Video Deduplication via GitHub Actions Cache

## Status

Proposed

## Context

The daily automation (`automation/`) selects a random `VideoAsset` from
`config.py:VIDEOS_CONFIG` on every run and publishes it to Facebook and
Instagram. Because the pipeline is stateless — GitHub Actions runners are
ephemeral and there is no database — nothing prevents the same video from being
selected again on a later run. `VIDEOS_CONFIG` holds only a handful of assets
while the schedule posts several times a week, so repeats are frequent.

We want each asset to be posted at most once per cycle, and the full set to be
exhausted before any video repeats, without introducing a database.

## Decision

Track already-posted videos in a plain JSON state file
(`automation/.state/posted.json`) that lists the posted Google Drive IDs, and
persist that file between GitHub Actions runs using the `actions/cache`
restore/save pattern.

- The canonical identity of a video is its `drive_id` — the Google Drive file
  ID from which `VideoAsset.public_url` is derived.
- A new `posted_tracker.py` module loads/saves the history and filters
  `VIDEOS_CONFIG` down to only not-yet-posted assets.
- `daily_post.py` filters the candidate list before selecting a random video
  and, after a successful publish, marks the asset as posted and saves the
  state file.
- If every asset has already been posted, the history is reset so a new cycle
  begins instead of failing.
- Dry runs never mutate the history.

### State File

```json
{ "posted_drive_ids": ["1uPNmHViYyMb4EVX6saYZFfeao_IDlb6N", "…"] }
```

### GitHub Actions Cache

GitHub Actions cache entries are immutable, so we cannot overwrite the state
file in place. Instead the workflow:

1. Restores the latest entry via `actions/cache/restore` with `key: posted-videos`
   and `restore-keys: posted-videos-`.
2. Runs `daily-post`, which mutates `automation/.state/posted.json`.
3. Saves a fresh entry via `actions/cache/save` with a unique per-run key
   (`posted-videos-${{ github.run_id }}`).

Each run therefore appends a new (tiny) cache entry; old entries are evicted by
GitHub's 7-day unused-entry policy. Restore always picks the most recently
created matching entry, so the latest history wins.

## Consequences

### Positive

- No database or additional infrastructure required.
- Guarantees each asset is posted at most once per cycle.
- History is tiny (a few hundred bytes) and transparent to inspect or delete.

### Negative

- Cache is best-effort: a missed restore (e.g., cache evicted or disabled)
  silently resets the history and may cause a repeat.
- A new cache entry is created on every run; storage growth is bounded only by
  GitHub's eviction policy.
- Reposting protection only covers assets tracked in `VIDEOS_CONFIG`; a video
  added under a new `drive_id` is treated as new.

### Neutral

- State is stored outside git (`automation/.state/` is gitignored).
