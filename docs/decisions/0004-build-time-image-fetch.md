# ADR-0004: Build-Time Image Fetch from Google Drive

## Status

Accepted

## Context

The previous revision of `react/src/components/Members.jsx` and
`react/src/components/Gallery.jsx` rendered band photos by constructing
`https://lh3.googleusercontent.com/d/<fileId>=w400-h400-c` URLs at runtime and
loading them in `<img>` tags directly from the browser. This approach surfaced
recurring issues:

- **Rate limiting (HTTP 429).** Google Drive's image CDN aggressively rate-limits
  hot-linked image requests, especially during dev reloads and from CI. The
  workaround was a custom `ImageWithRetry` component implementing exponential
  backoff, but rate-limit failures still produced visible blank placeholders for
  users.
- **Runtime fragility.** Each visitor's browser made fresh requests to Drive;
  any transient Drive outage or ID revocation immediately broke the live site.
- **No build-time validation.** A bad/expired Drive ID was only noticed in
  production, not during build.
- **Cache hostility.** Drive image responses are not optimized for long-lived
  HTTP caching, costing repeat-visit performance.
- **Bundle inefficiency.** Vite could not fingerprint, optimize, or
  compression-tune assets it never saw.

The minimalist redesign (ADR-0003) currently sidesteps the problem by rendering
first-letter avatars and placeholder gallery tiles. The decision was made to
restore the original photographs without reintroducing the runtime CDN
dependency.

## Decision

Move image acquisition from **runtime fetch in the browser** to **build-time
fetch on the build host**, with the React app consuming local static assets.

### Pipeline

1. A Node ESM script `react/scripts/fetch-images.mjs` holds an inline manifest
   of `{ slug, driveId }` entries grouped into `members` and `gallery`.
2. The script downloads each Drive image, with retry-with-backoff on 429/5xx,
   and writes it to `react/public/images/<group>/<slug>.jpg`.
3. The script is idempotent: existing files are skipped unless `--force` is
   passed. This keeps incremental builds fast.
4. The script is wired into npm lifecycle as `predev` and `prebuild`, so
   `npm run dev` and `npm run build` both ensure images are present before
   serving/bundling.
5. Components reference the assets via
   `${import.meta.env.BASE_URL}images/<group>/<slug>.jpg`, which resolves
   correctly under both the dev base path (`/`) and the production GitHub
   Pages base path (`/septimaola/`).

### Storage policy

`react/public/images/` is **gitignored**. Rationale:

- Keeps the Git repository small.
- Forces the manifest in `fetch-images.mjs` to remain the single source of
  truth for which photos are part of the site.
- Aligns with how the project already excludes other generated artifacts
  (e.g., LaTeX background imagery is not committed either).

The trade-off — CI must reach Drive on every build — is accepted because the
download is small (under 10 photos) and the retry logic plus build-time
visibility make failures recoverable and actionable, unlike runtime failures
that silently degrade the user experience.

### Failure semantics

- **Member images** are required. A failed download (after retries) fails the
  build with non-zero exit, so we never deploy a press kit missing band
  members.
- **Gallery images** are optional. A failed download logs a warning and
  continues; the affected `<img>` tag's `onError` handler hides it gracefully
  client-side.

### Scope

This ADR covers the React press kit only. The LaTeX press kit and the AI
agent project have their own asset workflows and are unaffected.

## Consequences

- **Positive:** End users no longer suffer 429 errors or blank avatars; images
  are served from the same origin as the rest of the site, fingerprinted by
  Vite and cached by GitHub Pages CDN.
- **Positive:** Bad Drive IDs surface at build time, not in production.
- **Positive:** The `ImageWithRetry` component and its complexity are removed.
- **Positive:** Adding a new photo is a single-line manifest edit, with no
  component code change beyond referencing the new slug.
- **Negative:** CI builds depend on Drive availability and Drive's rate
  limits. A widespread Drive outage during a deploy window will block deploys.
  Mitigation: retry/backoff in the script; the gitignore policy can be
  reversed (commit `public/images/`) if outages prove disruptive.
- **Negative:** First-time `npm run dev` is slower because images download
  before Vite serves. Subsequent runs are unaffected (idempotent skip).
- **Neutral:** Introduces a small Node script (no new npm dependencies; uses
  built-in `fetch` and `fs`).
- **Neutral:** The previous `ImageWithRetry` runtime-retry pattern is
  superseded by build-time retries; documented here so future contributors do
  not reintroduce it.

## Reversal Path

If the Drive dependency in CI proves problematic, flip a single line in
`.gitignore` to *include* `public/images/` and commit the downloaded assets.
The components require no change. The manifest remains authoritative and the
fetch script remains the canonical way to refresh assets.
