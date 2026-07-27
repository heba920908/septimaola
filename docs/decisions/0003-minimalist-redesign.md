# ADR-0003: Bold Minimalist Redesign of the React Press Kit — AMENDMENT 1: One-Page Scroll Experience

## Status

Accepted — Amendment 1 Implemented (One-Page Scroll + Radical Minimalism)

## Amendment 1: One-Page Scroll Experience with Radical Text Reduction

### Context Update

After initial implementation of the minimalist redesign, the page remained content-heavy with long text blocks (Biografía: 350+ words, Members: 100-300 words each). Playwright inspection revealed that users were not engaging with the dense text content. The decision was made to embrace **radical minimalism**: each section becomes a single viewport (`100vh`), scroll-snap ensures each section locks into view, and text is reduced to **impact phrases** that capture the essence rather than the details.

### Amendment Decision

**One-Page Section Architecture:**
- Each major section (Hero, Noticias, Biografía, Integrantes, Música, Galería, Contacto) is a `100vh` full-page section
- CSS `scroll-snap-type: y mandatory` ensures scroll jumps to next/prev section
- `scroll-snap-align: start` and `scroll-snap-stop: always` for clean section locks
- Reduced motion fallback disables snap for accessibility

**Radical Text Minimalism:**
- Biografía reduced from 350+ words to **2 sentences + 2 mission cards** (~50 words)
- Members reduced from verbose bios to **name + instrument only** (~6 words per member)
- Discography: song titles only, hover reveals play button
- Impact phrases serve as section "anchors":
  - Noticias: «Cada concierto es una **ola nueva**»
  - Biografía: «Donde el **reggae jamaicano** encuentra el **corazón latino**»
  - Integrantes: «**Seis almas**, un solo latido»
  - Música: «**Cuatro canciones**. Una revolución sonora.»
  - Galería: «**Imágenes** que hablan más que mil canciones»
  - Contacto: «**Únete** a la ola»

**Visual Language Evolution:**
- Member cards → Initial-only placeholders (awaiting photos)
- Gallery → Placeholder grid (awaiting high-res images)
- Discography → Horizontal list with minimal hover interaction
- Contact → Email as hero element, social links as secondary

### Impact of Amendment

- **Positive:** Dramatically faster comprehension; each section communicates its essence in seconds
- **Positive:** Mobile experience vastly improved (no endless scrolling)
- **Positive:** Professional, high-end aesthetic similar to premium agency sites
- **Negative:** Detailed bios moved to press kit PDF (externalized)
- **Negative:** Requires high-quality imagery to work (current placeholders)

## Context

The React press kit (`react/`) is functional but visually static and noisy. A
live inspection (Vite dev server + Playwright, baseline screenshots
`current-full.png` and `current-mobile.png`) surfaced the following:

- **No motion.** The page has hover effects only — no entrance or scroll
  animations. It reads as flat and dated.
- **Noisy palette.** A multi-stop navy→amber background gradient combined with
  dual cyan + orange accents, plus many borders, glows, and shadows. Everything
  competes for attention; nothing stands out.
- **Dense text blocks.** Biografía (four long paragraphs) plus Visión/Misión
  create heavy text walls. (Content is intentionally preserved — see Decision.)
- **Quality gaps found during inspection:**
  - Gallery has only three images and a **duplicate Google Drive ID** (entries
    #2 and #3 share `1LmL-xTYYOU-jf1WVThT4N3Y9vLytwvWy`).
  - The Facebook Page Plugin iframe is fixed at `width=500`, causing a
    horizontal-scroll artifact on mobile.
  - Discography "Ver más" links are placeholders pointing at a generic Spotify
    search.
  - 3 console errors / 2 warnings, mostly third-party Facebook iframe noise
    (expected per `react/CLAUDE.md`).

Architectural constraints to respect: no router, no state-management library,
no TypeScript, a single `styles.css` driven by CSS custom properties, Google
Drive-hosted images, and a third-party Facebook iframe.

The goal is a **bold, minimalist, motion-forward** press kit that reads as
premium and memorable, while keeping all existing copy.

## Decision

Adopt a bold minimalist redesign direction. The visual system is defined in the
[`colors` skill](../../.claude/skills/colors/SKILL.md), which is the source of
truth for palette, type, spacing, and motion tokens.

### Palette: dark monochrome + single accent

- Replace the navy→amber gradient with a flat **near-black charcoal** base
  (`--bg #0a0b0d`).
- Use **electric cyan `#00d4ff` as the single structural accent** — it is the
  brand color already present in the logo. Recommended over orange because cyan
  is the logo-native hue and reads cleaner on near-black.
- **Demote orange** (`#f68c02`) to an optional, rarely-used secondary accent so
  existing brand assets still reconcile, but it is no longer structural.
- Cards become subtle dark **surfaces** with soft elevation instead of
  translucent-blue panels with colored borders and glows.

### Layout & minimalism

- Flatten gradients, borders, and glows; rely on whitespace and elevation.
- Restructure the hero: oversized display type, a single accent CTA, quieter
  supporting text.
- Re-pace the dense sections (Biografía, Visión/Misión) into rhythmic,
  well-spaced blocks. **All copy is preserved** — this is a visual re-pacing,
  not a content cut.

### Navigation

- Minimalist sticky header with an animated active-link underline.
- Refined mobile slide-over panel consistent with the new palette.

### Motion (framer-motion)

Add **framer-motion** as a dependency. This is a deliberate deviation from the
project's "no libraries" tenet, accepted because motion is the core
differentiator of this redesign. Animation set ("rich but tasteful"):

- Hero headline stagger / fade-up on load.
- Per-section scroll reveal via `whileInView` with `viewport={{ once: true }}`.
- Card hover lift, animated nav underline, and subtle hero/gallery parallax.
- **Mandatory** `prefers-reduced-motion: reduce` fallback: disable transforms
  and large movement; content remains instantly visible.

### Local development & verification

Reaffirm ADR-0002 (npm/npx-first). During this work, two blockers were hit and
should be documented for future contributors:

- A prior Podman run left `react/node_modules` **owned by root**, so a local
  `npm install` could not clean/reinstall it.
- The npm optional-dependency bug (`@rollup/rollup-linux-x64-gnu` missing) broke
  `npm run dev` against the stale tree.

Working fallback used for browser verification: build the image
(`podman build -t septimaola-react .`) and run it with the repo mounted plus an
**anonymous volume masking `node_modules`** so the container uses its own fresh
install:

```bash
podman run --rm -v "$(pwd)":/app:z -v /app/node_modules -p 5173:5173 \
  localhost/septimaola-react
```

### Cleanups to fold into implementation

- Deduplicate the Gallery image IDs.
- Make the Facebook iframe responsive to remove the mobile horizontal scroll.
- Replace placeholder Discography links with real targets, or mark them clearly
  as TODO.

### Scope of this ADR

This ADR records the **direction only**. It does not change `react/src/**` and
does not yet run `npm install framer-motion`. Implementation is a separate,
follow-up effort tracked against this decision.

## Consequences

- **Positive:** A striking, modern, memorable press kit; motion creates a clear
  "wow" factor; stronger visual hierarchy from a restrained palette and
  generous whitespace.
- **Positive:** A single documented design system (colors skill) keeps future
  styling consistent.
- **Negative:** framer-motion adds a runtime dependency and bundle weight,
  deviating from the "no libraries" architecture tenet (explicitly accepted).
- **Negative:** Significant CSS/JSX churn during implementation and an ongoing
  accessibility obligation to honor reduced-motion preferences.
- **Neutral:** All existing content is retained; only presentation changes.
- **Neutral:** Orange remains documented but demoted, preserving compatibility
  with existing brand assets.
