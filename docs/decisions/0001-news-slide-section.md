# ADR-0001: News Slide Section

## Status

Accepted

## Context

The press kit site currently presents static information (band members, discography, gallery, contact). There is no way to communicate upcoming gigs, releases, or announcements to visitors. A dynamic news/announcements area would keep the page feeling current and give promoters a reason to revisit.

## Decision

Add a news slide (carousel/slider) section to the React press kit page. The section will:

- Display a rotating set of news cards (upcoming shows, releases, press mentions)
- Be placed in a prominent position on the page (e.g., between Hero and Members, or after Hero)
- Support manual navigation (prev/next) and optionally auto-advance
- Content will be hardcoded in the component initially (no CMS or API)

## Implementation Decisions

The following decisions were made during implementation:

- **Placement:** Immediately after `<Hero />`, before the Biografía section — the first content a visitor sees below the fold.
- **One card at a time:** Single focused card (full-width) rather than multiple side-by-side cards, for clarity and consistency with the mobile-first layout.
- **Auto-advance:** 5-second interval, paused while the cursor is over the slider (`onMouseEnter`/`onMouseLeave`). The timer resets on any manual navigation.
- **Navigation controls:** Prev/next arrow buttons (←/→) flanking dot indicators. Dots double as direct-jump buttons. Both wrap around at the ends.
- **No new dependencies:** Implemented with vanilla React (`useState`, `useEffect`, `useRef`) and CSS — no carousel library added, keeping the flat architecture intact.
- **Fade-in animation on card change:** A `newsCardIn` CSS keyframe (opacity + translateY) is triggered by forcing a React remount via the card's `key` prop (`key={item.id}`), rather than a CSS track/translate approach. This avoids needing to manage track widths or slide positions.
- **News item schema:** `{ id, type, title, date, description, embed?, image?, link?, linkLabel? }`. The `type` field drives the badge label (e.g., "Concierto", "Grabación", "Prensa").
- **Image preview:** Each news item optionally includes an `image` URL (from Instagram, Facebook, or any external source). When present, the card switches to a two-column grid layout (thumbnail on the left, text on the right). On mobile the image stacks above the body at 16:9 aspect ratio. Images that fail to load are hidden gracefully via `onError`.
- **Social embed (iframe):** Each news item optionally includes an `embed` URL (the `src` from a Facebook/Instagram "copy code" embed snippet). When present, the card renders the social post inline via an `<iframe>`. A client-side allowlist (`ALLOWED_EMBED_ORIGINS`) restricts iframes to trusted origins (`facebook.com/plugins/`, `instagram.com/p/`, `instagram.com/reel/`) to prevent XSS. Embed takes precedence over `image` when both are set.
  - **Facebook:** Use the `src` attribute from the `<iframe>` in the "copy code" embed snippet (e.g., `https://www.facebook.com/plugins/post.php?href=...`).
  - **Instagram:** Convert the `<blockquote>` embed code to an iframe URL by appending `/embed/` to the post/reel permalink (e.g., `https://www.instagram.com/reel/DYgTnsgMoNt/embed/`). This avoids injecting third-party `<script>` tags into the React app.
- **Navigation link:** "Noticias" added as the first link in both desktop and mobile (hamburger) navigation menus, pointing to `#noticias`.
- **Styling:** Follows existing design conventions — `border-top: 3px solid var(--accent)` (cyan) matching `.member-card`, `--accent-orange` background for the type badge, `--card-bg`/`--card-shadow` CSS variables for the card surface.

## Files Changed

- `react/src/components/News.jsx` — new component
- `react/src/styles.css` — news slider styles appended
- `react/src/App.jsx` — import, `<News />` render, nav link added

## Consequences

- **Positive:** Visitors see up-to-date information; the page feels alive and maintained.
- **Positive:** Promoters/venues get immediate visibility into the band's activity.
- **Negative:** Content must be manually updated in the source code for now.
- **Neutral:** Adds one more component to the flat architecture; no routing or state library changes required.

## Amendment (2026-06-04): Automated Content Generation

### Context

Manual updates in `News.jsx` created an operational bottleneck and caused stale content between releases.

### Decision

Move from hardcoded `NEWS_ITEMS` to build-generated data and keep the existing slider UX.

- News data is generated during CI build using Meta APIs.
- Fetch scope is Facebook-only (latest 3 posts from Septima Ola).
- Generated data is written to a JSON file consumed by the React component.
- No workflow auto-commit is performed; data is regenerated per build/deploy run.
- A manual `workflow_dispatch` trigger is available to force a refresh/deploy.

### Fallback Behavior

- Timeline embed fallback was removed to keep the UX consistent (cards-only).
- If API data is unavailable, generator keeps cached/seed Facebook card items so cards still render.
- If a post has no description text, the card renders without description content.

### Operational Notes

- CI uses repository secrets for Facebook credentials (`FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_TOKEN`, optional `FACEBOOK_PAGE_SLUG`).
- Build logs include source counts and warning messages for easier troubleshooting.

## Amendment (2026-06-04): Client-Side Facebook JS SDK (Supersedes Build-Time Generation, Superseded on 2026-06-18)

### Context

The build-time generator (`generate-news.cjs`) required server-side credentials
(Page/User access tokens) and a separate CI step to refresh data per deploy. A
runtime approach using the official Facebook JavaScript SDK is simpler to operate
(the SDK auto-manages the user access token in the browser) and removes the build
script from the critical path.

### Decision

Fetch Facebook posts client-side in the React app and drop the build-time generator.

- `News.jsx` loads the official Facebook JS SDK (`connect.facebook.net/.../sdk.js`)
  at runtime, initializes it with a public **App ID**, and reads the latest posts
  via `FB.api('/{page-id}/posts', ...)` using the logged-in user's access token.
- Configuration is provided through public (non-secret) Vite env vars:
  `VITE_FACEBOOK_APP_ID` (required to initialize the SDK) and
  `VITE_FACEBOOK_PAGE_ID` (optional, defaults to `septimaolaoficial`).
- Seed cards are committed to `react/src/data/news.json` and rendered as the
  initial/fallback content.
- The build-time generator, its npm scripts (`generate-news`, `predev`,
  `prebuild`), the `facebook-nodejs-business-sdk` dependency, and the CI
  "Generate news data" step were removed. No JSON is generated at build time.

### Fallback Behavior

- The slider always renders the committed seed cards first.
- A live fetch only replaces them when `VITE_FACEBOOK_APP_ID` is set **and** an
  admin/editor of the page is logged into Facebook in that browser session.
- Any failure (no App ID, no connected session, SDK load error, API error) keeps
  the seed cards — visitors never see an empty section.

### Consequences

- **Positive:** No server-side tokens or build-time generation step; the SDK
  manages the user token automatically in the browser.
- **Positive:** Seed content is version-controlled and reviewable.
- **Negative:** A Meta **App ID is still required** for the SDK to initialize, and
  the browser SDK only returns the band's posts to a logged-in page admin — public
  visitors always see the committed seed cards. Until an app exists, the section is
  effectively static.
- **Neutral:** Adds a third-party script (`sdk.js`) loaded lazily at runtime,
  guarded by the existing `ALLOWED_EMBED_ORIGINS` iframe allowlist.

## Amendment (2026-06-18): Public Facebook Page Plugin Embed (Supersedes Client-Side JS SDK)

### Context

The client-side JS SDK approach still required a Meta App ID and a logged-in
page admin/editor to fetch posts. This created operational friction and left
public visitors on seed content.

At the same time, extracting the latest posts by scraping
`https://www.facebook.com/septimaolaoficial` in a custom script is brittle and
high-risk because Facebook markup frequently changes and scraping can violate
platform terms.

### Decision

Replace custom SDK/API fetching with the official Facebook Page Plugin timeline
embed.

- `News.jsx` now renders a single iframe using
  `https://www.facebook.com/plugins/page.php` with `tabs=timeline`.
- The plugin reads from the public page URL
  `https://www.facebook.com/septimaolaoficial`.
- `VITE_FACEBOOK_APP_ID`, `VITE_FACEBOOK_PAGE_ID`, SDK runtime loading, and
  token/session-dependent logic were removed.
- The obsolete build-time generator (`react/scripts/generate-news.cjs`) and seed
  data file (`react/src/data/news.json`) were removed.
- CI build env no longer requires Facebook-related secrets for the React build.

### Consequences

- **Positive:** No App ID, no access tokens, and no admin login requirement.
- **Positive:** No brittle scraping workflow and lower maintenance burden.
- **Positive:** Noticias remains live by displaying the page timeline directly.
- **Tradeoff:** Visual presentation follows Facebook's plugin widget instead of
  the custom card slider design.
- **Neutral:** The section still relies on third-party iframe availability and
  browser/privacy settings.

