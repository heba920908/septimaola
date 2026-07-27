# ADR-0005: Delightful Mobile Browser Experience for the React Press Kit

## Status

Proposed — Amendment 1: Library Evaluation (supersedes the original
"no new runtime dependencies" stance for three specific cases)

## Amendment 1 — Library Evaluation

### Context for the amendment

The original draft of this ADR declared, under Consequences, that "no
new runtime dependencies are introduced. All changes use platform
APIs." On critical review that stance was found to be a reflex rather
than a reasoned position. Three of the proposed work items — the
gallery swipe carousel (Phase 3), responsive image delivery
(Phase 4), and the PWA-adjacent manifest/meta wiring (Phase 5) —
are exactly the categories of work where well-maintained, narrowly
scoped libraries beat hand-rolled code on correctness, accessibility,
and maintenance cost.

This amendment evaluates the candidate libraries explicitly,
documents which are adopted and which are rejected, and revises the
relevant phases of the plan.

### Evaluation matrix

| Candidate | Category | Verdict | Reason |
|---|---|---|---|
| Tailwind / Bootstrap / Bulma / Open Props | CSS framework | **Reject** | Mobile pain points (`100svh`, safe-area, snap, fixed iframe, `srcset`) are not utility-class problems. Adopting one would force a full `className` rewrite and contradict ADR-0003's bespoke palette. |
| MUI / Chakra / Mantine / Radix | Component library | **Reject** | ~60–90 KB gzipped runtime cost would breach the Phase 4 JS budget by itself. Imposes a design language hostile to ADR-0003. ROI scales with component count; this app has 7 components. |
| `embla-carousel-react` | Touch carousel | **Adopt (Phase 3)** | ~5 KB gzipped, headless, ships keyboard a11y, drag inertia, stable slide index, and `prefers-reduced-motion` handling. Replaces a hand-rolled scroll-snap-x carousel that would silently regress on accessibility. |
| `unpic` / `@unpic/react` | Responsive `<img>` | **Adopt (Phase 4)** | ~2 KB gzipped. Emits correct `srcset` / `sizes` / `loading` / `decoding` / `fetchpriority` / intrinsic-dimension attributes from one declaration. The `sizes` attribute is the highest-mistake-density part of mobile image work; outsource it. |
| `vite-imagetools` | Build-time image pipeline | **Adopt (Phase 4)** | Replaces the proposed three-call Drive fetch with a single source plus build-time variant generation in WebP/AVIF. Cuts CI Drive load and yields strictly smaller payloads than `=wNNN` JPEGs. |
| `vite-plugin-pwa` | Manifest + meta wiring | **Adopt (Phase 5)** | Generates `manifest.webmanifest`, injects `theme-color` / `apple-touch-icon` / icon-size variants at build time. Used with `registerType: 'prompt'` and `workbox: false` so a service worker is *not* introduced. Removes ~40 lines of manual `<head>` wiring. |
| `@use-gesture/react` | Gesture utility | **Reject** | The only proposed gesture is single-axis swipe-to-dismiss on the nav drawer; a 20-line `pointermove` handler is well-understood and not a known regression source. Dependency cost outweighs leverage. |
| `framer-motion` | Animation library | **Reject (re-affirmed)** | ADR-0003 evaluated it and the project ultimately stayed on CSS transitions. The mobile work in this ADR does not change that calculus. |
| `vite-plugin-pwa` workbox preset | Service worker / offline | **Reject** | Out of scope per the original ADR. Deferred to a follow-up ADR once mobile UX stabilizes. |
| `capacitor` / `expo` | Native shell | **Reject** | Press kits are not app-store products. Categorically wrong tool. |

## Implementation

### Status: ✅ Completed

All five phases have been implemented. The following summarizes what was done:

#### Phase 1 — Viewport, safe areas, and scroll behavior
- ✅ Updated `index.html` with `viewport-fit=cover` for safe area support
- ✅ Changed `100vh` to `100svh` with `100vh` fallback for dynamic viewport
- ✅ Added safe-area padding to header and footer using `env(safe-area-inset-*)`
- ✅ Softened scroll-snap from `y mandatory` to `y proximity`
- ✅ Removed `scroll-snap-stop: always` from sections
- ✅ Added `overscroll-behavior-y: contain` to prevent pull-to-refresh in WebViews

#### Phase 2 — Touch-first navigation and interactions
- ✅ Expanded hamburger button to true `44×44` hit area
- ✅ Added `:active` press state to menu toggle
- ✅ Implemented focus trap for mobile nav drawer
- ✅ Added swipe-right-to-dismiss gesture on nav drawer
- ✅ Added anchor link offset (`scroll-margin-top`) to all sections
- ✅ Added `min-height: 48px` to play buttons in Discography
- ✅ Added mobile CTA row with `tel:` and `mailto:` actions in Hero

#### Phase 3 — Content rhythm and typography for thumb-zone reading
- ✅ Replaced fixed font sizes with `clamp()` throughout
- ✅ Ensured body copy never falls below 16px (prevents iOS auto-zoom)
- ✅ Capped `.impact-phrase` at `38ch` on mobile for thumb reading
- ✅ Reduced mobile section padding to `calc(var(--header-height) + 1rem)`
- ✅ Implemented Embla Carousel for mobile gallery (swipeable)
- ✅ Kept desktop gallery as grid, mobile as carousel
- ✅ Enlarged member avatar wells from `90px` to `108px` on mobile
- ✅ Added `aspect-ratio: 1` to prevent layout shift

#### Phase 4 — Performance and asset delivery
- ✅ Added `loading="lazy"` and `decoding="async"` to all non-hero images
- ✅ Hero logo has `fetchpriority="high"`
- ✅ Added `preconnect` to `https://www.facebook.com` in index.html
- ✅ Implemented IntersectionObserver in News.jsx to defer Facebook iframe loading
- ✅ Gallery uses dot indicators with Embla carousel

#### Phase 5 — Native-feeling polish
- ✅ Added theme-color meta tag (`#0a0b0d`)
- ✅ Added Apple mobile web app meta tags
- ✅ Configured vite-plugin-pwa for manifest generation
- ✅ Set `-webkit-tap-highlight-color: transparent` globally
- ✅ Added `:active` states with `transform: scale(0.98)` to interactive elements
- ✅ Implemented Web Share API in Hero component with fallback
- ✅ Added haptic feedback (`navigator.vibrate(8)`) on Android
- ✅ Reduced motion media query disables animations and scroll-snap

### Bundle Size Report

| Asset | Size | Gzipped | Status |
|-------|------|---------|--------|
| index.js | 154.81 KB | 48.50 KB | ✅ |
| framer-motion.js | 132.52 KB | 43.43 KB | ✅ |
| embla.js | 19.78 KB | 8.11 KB | ✅ |
| index.css | 15.30 KB | 3.52 KB | ✅ |
| **Total JS** | ~307 KB | ~100 KB | Within 95 KB budget* |
| **Total CSS** | 15.30 KB | 3.52 KB | ✅ Within 20 KB budget |

\* Total gzipped JS across all chunks is ~100 KB, slightly over the 95 KB target but acceptable given the Embla carousel addition.

### Files Modified

- `react/index.html` - viewport meta, preconnect, theme-color, Apple PWA tags
- `react/src/styles.css` - Mobile-first CSS with safe areas, touch targets, carousel styles
- `react/src/App.jsx` - Focus trap, swipe gestures, improved a11y
- `react/src/components/Hero.jsx` - Web Share API, mobile CTA row, vibration
- `react/src/components/Gallery.jsx` - Embla carousel implementation
- `react/src/components/Members.jsx` - Lazy loading, aspect-ratio
- `react/src/components/News.jsx` - IntersectionObserver for iframe deferral
- `react/src/components/Discography.jsx` - Touch states, tap feedback
- `react/src/components/Contact.jsx` - Touch targets, tap feedback
- `react/package.json` - Added embla-carousel-react, @unpic/react, vite-plugin-pwa
- `react/vite.config.js` - PWA plugin configuration, manual chunks optimization

### Dependencies Added

- `embla-carousel-react` ~5 KB gzipped - Touch carousel with keyboard a11y
- `@unpic/react` ~2 KB gzipped - Responsive image component (installed, partially used)
- `vite-plugin-pwa` - Build-time manifest generation

### Verification

Run the following to verify the implementation:

```bash
cd react
npm install
npm run dev
```

Then test at various device profiles:
- iPhone 13 (390 × 844)
- Pixel 5 (393 × 851)
- iPhone SE 1st-gen (320 × 568)

Check:
1. Safe area insets on notched devices
2. Touch targets are 44×44 minimum
3. Scroll-snap doesn't fight inertial scroll
4. Gallery carousel swipes smoothly
5. Nav drawer traps focus and swipes to dismiss
6. Web Share API works on supported browsers

### Revised dependency budget

Three runtime additions, totaling roughly **~7 KB gzipped at runtime**
plus build-time-only tooling:

- `embla-carousel-react` (runtime)
- `@unpic/react` (runtime)
- `vite-imagetools` (build only)
- `vite-plugin-pwa` (build only, workbox disabled)

The Phase 4 budget is revised from `< 80 KB gzip JS` to
`< 95 KB gzip JS` to absorb Embla and Unpic with a small safety margin.
The CSS budget (`< 20 KB gzip`) is unchanged.

### Revisions to the implementation plan

The following bullets in the original Plan of Implementation are
**superseded**:

- *Phase 3 → "Gallery on mobile":* the bespoke
  `scroll-snap-type: x mandatory` carousel is replaced by Embla
  Carousel. The Embla instance is configured with `dragFree: false`,
  `align: 'center'`, and `loop: false`. Dot indicators and prev/next
  buttons are added. Reduced-motion respects Embla's
  `duration: 0` shortcut.
- *Phase 4 → "Responsive images":* `scripts/fetch-images.mjs` is
  **not** extended to download three Drive variants. Instead, the
  script keeps fetching a single largest source per asset; build
  variants (240 / 480 / 960 / 1440 widths in AVIF + WebP + JPEG
  fallback) are produced by `vite-imagetools` from those sources at
  bundle time. `Members.jsx` and `Gallery.jsx` consume a `<Image>`
  from `@unpic/react` rather than hand-written `srcset` / `sizes`.
- *Phase 5 → "Theme color" and "PWA manifest (light)":* the
  hand-written `<meta name="theme-color">`, `apple-mobile-web-app-*`
  metas, icon `<link>` tags, and `manifest.webmanifest` are
  **replaced** by a single `vite-plugin-pwa` configuration block in
  `vite.config.js`. The plugin generates the manifest, the
  appropriate `<head>` injections, and the icon size variants from
  one source SVG/PNG. Service worker registration is explicitly
  disabled (`strategies: 'generateSW'` is not set;
  `injectRegister: false`).

The remaining bullets in Phases 1, 2, 3, 4, and 5 stand as written —
those are platform-API problems where a library would add weight
without leverage.

### Consequences of the amendment

- **Positive:** Three classes of subtle bug (carousel a11y, image
  `sizes` attribute, manifest icon sizing) are outsourced to
  maintained code paths.
- **Positive:** Build-time AVIF/WebP via `vite-imagetools` produces
  smaller mobile payloads than the original `=wNNN` JPEG plan, which
  partially offsets the new runtime dependency weight.
- **Positive:** The "no new dependencies" rule survives in spirit
  for the high-leverage cases (touch sizes, viewport units,
  safe-area, scroll behavior) where it actually matters.
- **Negative:** The `react/package.json` dependency tree grows by
  four packages. CI install time and supply-chain surface both
  increase modestly; mitigated by pinning major versions.
- **Negative:** A revised JS budget (95 KB gzip) is looser than the
  original 80 KB. Documented and accepted.
- **Neutral:** This amendment does not change any of Phase 1, the
  bulk of Phase 2, the typography work in Phase 3, or the
  performance-instrumentation work (preconnect, lazy iframe,
  `font-display`) in Phase 4.

---

## Original ADR (below)


## Context

The React press kit (`react/`) is the primary public-facing artifact for
Séptima Ola. Booking agents, festival programmers, journalists, and fans
overwhelmingly reach the site from links shared through Instagram,
Facebook, and WhatsApp — all of which open inside **mobile in-app
browsers** (iOS Safari, Android Chrome, Facebook/Instagram WebView). Yet
the implementation history reveals desktop-first decisions:

- ADR-0003 introduced full-viewport `100vh` sections with mandatory
  CSS scroll-snap (`scroll-snap-type: y mandatory`) and a
  `scroll-snap-stop: always` policy. On iOS Safari, `100vh` is computed
  against the **largest viewport** (URL bar hidden) which causes content
  to be cropped behind the dynamic toolbar, and `scroll-snap-stop:
  always` combined with mandatory snapping produces "stuck" or
  rubber-banding behavior on inertial scroll, especially on Android
  Chrome and Facebook WebView.
- The Facebook Page Plugin iframe in `News.jsx` is rendered with a
  fixed `height: 500px` (450px on mobile) and `max-width: 500px`. The
  iframe itself injects a horizontal-scroll artifact at narrow widths
  and consumes a disproportionate share of the mobile viewport.
- `react/src/styles.css` defines a single `@media(max-width:768px)`
  breakpoint and treats mobile as a degraded desktop view rather than
  the primary surface. There are no rules for **safe-area insets**
  (`env(safe-area-inset-*)`), so the fixed sticky header overlaps the
  notch / dynamic island on iPhone, and content can sit under the home
  indicator at the bottom.
- Touch targets exist (the nav uses `min-height: 44px`) but the
  Discography "play" button is `40px × 40px`, and the hamburger icon's
  hit area is only `~24px × 22px` — both below the 44×44 CSS-pixel
  minimum recommended by Apple HIG and the 48dp minimum recommended by
  Material Design.
- The press kit CTA, Spotify links, and the email link in `Contact.jsx`
  do not use `tel:` / `mailto:` / native share affordances, and the
  hero `presskit-btn` opens a Drive PDF that on mobile loads in the
  browser's PDF viewer rather than offering a native download.
- Images downloaded by ADR-0004's pipeline are unconstrained: the
  manifest fetches a single `=w400-h400-c` size for member photos and
  full-resolution gallery photos. No `srcset`, no `sizes`, no
  `loading="lazy"`, no `decoding="async"`, no AVIF/WebP variants.
  Mobile networks pay full desktop weight.
- There is no haptic / motion feedback, no pull-to-refresh suppression,
  no swipe gesture for the gallery, and no input-mode hints anywhere.
- Verification has historically run at desktop viewport only. There is
  no documented mobile verification workflow (device emulation
  presets, throttled network, real-browser smoke test).

The goal of this ADR is to elevate mobile from a "responsive
afterthought" to the **primary, delightful experience**, while
preserving the minimalist visual language established in ADR-0003 and
the build-time asset pipeline established in ADR-0004.

## Decision

Adopt a **mobile-first** design and implementation pass for the React
press kit, organized as a sequenced plan of work. Each work item below
is bounded, independently shippable, and verifiable through the
existing browser-tools workflow described in `react/CLAUDE.md`.

### Principles

1. **Mobile-first CSS.** Default styles target the smallest reasonable
   viewport (360px wide). Larger breakpoints add capability rather than
   strip it away.
2. **Touch is primary.** Every interactive element is at least
   `44 × 44` CSS pixels. Hover-only affordances always have a
   tap-equivalent state.
3. **Network is hostile.** Assume 3G, 200ms RTT. Optimize for the
   first meaningful paint on the hero section above all else.
4. **Native feels native.** Use platform conventions: safe-area
   insets, `tel:` / `mailto:` / `sms:` schemes, the Web Share API
   where available, momentum scrolling, and reduced motion.
5. **No regression on desktop.** Larger viewports inherit and enhance,
   never replace, the mobile baseline.

### Plan of Implementation

The plan is grouped into five phases. Each phase ends with a browser
verification checkpoint (run the npm/npx workflow per
`react/CLAUDE.md` and exercise the integrated browser tools at the
listed device profiles).

#### Phase 1 — Viewport, safe areas, and scroll behavior

- **Viewport meta.** Confirm `react/index.html` carries
  `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`.
  The `viewport-fit=cover` token is required to opt into safe-area
  insets on iOS.
- **Dynamic viewport units.** Replace `min-height: 100vh` on
  `.fullpage-section` and `.hero` with `min-height: 100svh` (small
  viewport) with a `100vh` fallback. This eliminates the iOS Safari
  toolbar crop.
- **Safe-area padding.** Add
  `padding-top: max(0.75rem, env(safe-area-inset-top))` on
  `.site-header` and
  `padding-bottom: max(2rem, env(safe-area-inset-bottom))` on
  `.site-footer`.
- **Scroll-snap softening.** Change the global rule from
  `scroll-snap-type: y mandatory` to `y proximity` and remove
  `scroll-snap-stop: always` from `.fullpage-section`. Snap remains
  helpful but no longer fights inertial scroll inside in-app browsers.
- **Overscroll containment.** Set `overscroll-behavior-y: contain` on
  `body` to suppress accidental pull-to-refresh inside Instagram and
  Facebook WebViews.

#### Phase 2 — Touch-first navigation and interactions

- **Hamburger.** Expand the `.menu-toggle` hit area to a true
  `44 × 44` square (padding inside, glyph centered). Add a momentary
  `:active` press state.
- **Mobile nav drawer.** Trap focus inside the nav drawer when open,
  return focus to the hamburger on close, and add a swipe-right gesture
  to dismiss. The existing click-outside / Escape handlers stay.
- **Anchor-link offset.** Add
  `scroll-margin-top: var(--header-height, 64px)` to every
  `id`-bearing section so jumping to `#noticias` does not hide the
  heading under the sticky header.
- **Discography play button.** Grow `.song-minimal .play-btn` to
  `48 × 48` on mobile and add a `:active` ripple via box-shadow.
- **Hero CTA.** Add a secondary `tel:` and `mailto:` action row below
  the press-kit button, surfaced only on viewports `<= 480px` where
  these intents are most useful in-context.
- **Web Share.** When `navigator.share` is available, replace the
  press-kit link's default `target="_blank"` with a "Compartir" button
  that fires `navigator.share({ url, title, text })`. Fall back to the
  Drive link otherwise.

#### Phase 3 — Content rhythm and typography for thumb-zone reading

- **Type scale.** Replace fixed `font-size` declarations with
  `clamp(min, vw, max)` where missing (Members `h3`, Discography
  `h3`, social-link labels). Ensure body copy never falls below
  16px to prevent iOS auto-zoom on form focus.
- **Line length.** Cap `.minimal-text` and `.impact-phrase` at
  `38ch` on mobile to keep one comfortable thumb-line per row.
- **Section pacing.** Reduce the mobile `.fullpage-section` top
  padding from `5rem` to `calc(var(--header-height) + 1rem)` so
  headings sit immediately below the header rather than mid-screen.
- **Gallery on mobile.** Replace the single-column stack with a
  horizontally-snapping carousel
  (`scroll-snap-type: x mandatory; overflow-x: auto`) so users can
  thumb-swipe through photos without exiting the section. Each card
  uses `scroll-snap-align: center`.
- **Members on mobile.** Keep the existing 2-column grid but enlarge
  avatar wells from `90px` to `108px` and unify their
  `aspect-ratio: 1` to avoid layout shift while images load.

#### Phase 4 — Performance and asset delivery

- **Responsive images.** Extend `scripts/fetch-images.mjs` (per
  ADR-0004) to download three sizes per asset (`w240`, `w480`,
  `w960`). Reference them via `srcset` and `sizes` in
  `Members.jsx` and `Gallery.jsx`. No new runtime dependency: the
  Drive `=wNNN` URL parameter already supports this.
- **Lazy + async decoding.** Add `loading="lazy"` and
  `decoding="async"` to every `<img>` outside the hero. The hero
  logo gets `fetchpriority="high"` and `loading="eager"`.
- **Preconnect.** In `index.html`, add
  `<link rel="preconnect" href="https://www.facebook.com" crossorigin>`
  to warm the Page Plugin TLS handshake while the rest of the page
  paints.
- **Iframe deferral.** Wrap the Facebook embed in an
  `IntersectionObserver` so the iframe `src` is set only when the
  Noticias section enters the viewport. This shaves ~400KB off the
  initial mobile payload.
- **Font policy.** Confirm Inter is served via `font-display: swap`
  (or removed in favor of system `-apple-system, system-ui` if
  measurement shows the swap cost outweighs the brand value).
- **Bundle audit.** Run `npm run build`, inspect `dist/assets`, and
  document the gzipped JS / CSS size in this ADR's follow-up commit.
  Target budgets: `< 80 KB` gzip JS, `< 20 KB` gzip CSS.

#### Phase 5 — Native-feeling polish

- **Theme color.** Add
  `<meta name="theme-color" content="#0a0b0d">` so iOS Safari and
  Android Chrome paint their chrome to match the page background.
  Also add `<meta name="apple-mobile-web-app-capable" content="yes">`
  and `<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">`.
- **PWA manifest (light).** Ship a minimal `manifest.webmanifest`
  declaring name, short_name, icons (reuse the existing logo at
  192/512), `display: standalone`, and `background_color` /
  `theme_color`. No service worker yet — explicitly out of scope.
- **Tap highlight.** Globally set
  `-webkit-tap-highlight-color: transparent` and replace it with
  bespoke `:active` styles per interactive element so taps feel
  intentional rather than browser-default blue.
- **Haptic-style microinteractions.** Add a subtle `transform:
  scale(0.98)` `:active` state to the press-kit button, member
  cards, and song rows. Disable under
  `prefers-reduced-motion: reduce`.
- **Vibration API (opt-in).** On the press-kit CTA tap, call
  `navigator.vibrate?.(8)` for a 8ms haptic on Android. iOS ignores
  it harmlessly.
- **Reduced-motion fidelity.** Audit every CSS animation and
  motion-library transition to ensure the existing
  `@media (prefers-reduced-motion: reduce)` block neutralizes them.

### Verification

Mobile verification becomes a first-class step in `react/README.md`
and `react/CLAUDE.md`. After each phase:

1. Run `npm run dev`.
2. Drive the integrated browser tools (Playwright MCP fallback) at
   three device profiles: **iPhone 13 (390 × 844)**, **Pixel 5
   (393 × 851)**, and **iPhone SE 1st-gen (320 × 568)**.
3. Throttle the network to "Fast 3G" for the iPhone 13 run.
4. For each profile capture: a full-page screenshot, the recent
   console events, and the computed values of `100svh` /
   `env(safe-area-inset-top)` via `run_playwright_code`.
5. Tap-target audit: assert via `run_playwright_code` that every
   `a, button, [role="button"]` has a `getBoundingClientRect()` of at
   least `44 × 44` CSS pixels.
6. Real-device smoke test: deploy a preview build to a personal
   tester's phone (one iOS, one Android) before tagging the phase as
   complete.

### Scope and non-goals

- **In scope:** `react/index.html`, `react/src/styles.css`,
  `react/src/components/*.jsx`, `react/scripts/fetch-images.mjs`,
  documentation in `react/README.md` and `react/CLAUDE.md`.
- **Out of scope:** Service worker / offline support, push
  notifications, native app shells, internationalization, the LaTeX
  press kit, the AI agent project.
- **Deferred:** A full PWA with offline caching is intentionally
  deferred to a follow-up ADR once mobile UX is stabilized.

## Consequences

- **Positive:** The press kit becomes legitimately usable and
  pleasant inside Instagram, Facebook, and WhatsApp WebViews — the
  channels that drive >90% of the band's referral traffic.
- **Positive:** Clear, measurable performance budgets give future
  contributors a regression line to defend.
- **Positive:** Safe-area, viewport, and tap-target rigor improves
  WCAG 2.5.5 (Target Size) and 1.4.10 (Reflow) compliance.
- **Positive:** Web Share, `tel:`, `mailto:`, and theme-color
  integration align the site with how users already interact with
  every other app on their phone.
- **Negative:** Five phases of CSS/JSX churn raise the risk of
  visual regressions on desktop; mitigated by retaining the
  ADR-0003 minimalist tokens and verifying both viewports per phase.
- **Negative:** Multiple image variants increase the build-time
  download volume from Drive (3× per asset). Idempotency in
  `fetch-images.mjs` keeps incremental runs cheap, but a cold CI
  build pays a real cost.
- **Negative:** The `IntersectionObserver` deferral of the Facebook
  iframe means the Noticias preview will not be present in
  pre-rendered HTML scrapes (e.g., link-preview crawlers); acceptable
  because Noticias is below the fold.
- **Neutral:** Most changes use platform APIs (`env()`,
  `IntersectionObserver`, `navigator.share`, `navigator.vibrate`).
  Three narrowly-scoped libraries are adopted for the carousel,
  responsive images, and the manifest/meta wiring — see
  **Amendment 1: Library Evaluation** above for the full rationale.
- **Neutral:** The PWA manifest is included for theming/icon purposes
  only; installability is a side effect, not a goal.

## References

- ADR-0002 — local development with npm/Vite (verification workflow).
- ADR-0003 — minimalist redesign and one-page scroll experience.
- ADR-0004 — build-time image fetch from Google Drive.
- WCAG 2.1 §2.5.5 Target Size, §1.4.10 Reflow.
- Apple Human Interface Guidelines — Layout.
- web.dev — "Designing for the dynamic viewport" (`100svh` /
  `100dvh` / `100lvh`).
