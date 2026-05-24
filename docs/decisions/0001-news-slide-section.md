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
