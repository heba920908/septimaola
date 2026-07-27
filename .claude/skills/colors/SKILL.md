# Septima Ola Design System — Minimalist Direction

This skill defines the official color palette **and** the minimalist design
direction for the Séptima Ola web page (`react/`). It is the source of truth for
visual styling. The direction is formalized in
[`docs/decisions/0003-minimalist-redesign.md`](../../../docs/decisions/0003-minimalist-redesign.md).

## Design Philosophy

### Core Principle: Radical Minimalism

Every element must justify its existence. If it doesn't communicate meaning, it doesn't belong. The design speaks through **absence** as much as presence.

- **Dark monochrome canvas.** A near-black charcoal surface is the dominant
  background. No multi-stop navy→amber gradient.
- **One vivid accent.** Electric cyan (`#00d4ff`) is the single structural
  accent. It is the brand color already present in the logo. Use it sparingly —
  emphasis, links, focus rings, active nav, key CTAs.
- **Motion as the differentiator.** Hierarchy and delight come from tasteful
  framer-motion animation (scroll reveals, hero stagger, hover lift), not from
  decorative borders or glows.
- **Negative space over ornament.** Replace borders/glows with spacing and
  subtle elevation. Generous whitespace and a clear type scale do the work.
- **One page, one message.** Each viewport (100vh section) communicates exactly
  one idea. Text is reduced to impact phrases — evocative, memorable, minimal.

## Core Palette (minimalist)

| Variable | Value | Role |
|---|---|---|
| `--bg` | `#0a0b0d` | Dominant background (near-black charcoal) |
| `--surface` | `#121418` | Card / panel surface (subtle elevation) |
| `--surface-2` | `#1a1d23` | Hovered / raised surface |
| `--accent` | `#00d4ff` | **Single accent** — links, focus, active nav, key emphasis (cyan) |
| `--accent-contrast` | `#00171d` | Text/icon color placed on top of a filled accent surface |
| `--text` | `#ffffff` | Primary text |
| `--text-muted` | `#a3acb9` | Secondary text, captions, labels |
| `--border-subtle` | `rgba(255,255,255,0.08)` | Hairline dividers (use rarely) |
| `--shadow-soft` | `0 8px 30px rgba(0,0,0,0.45)` | Soft elevation shadow |

### Demoted / legacy

| Variable | Value | Role |
|---|---|---|
| `--accent-orange` | `#f68c02` | **Demoted.** Optional secondary accent only. Not a structural color. Reconciles existing brand assets; avoid in new minimalist work. |

## Usage Rules

### Minimalism Rules (Critical)

- **Text budget:** Max 2 sentences per section. Prefer **impact phrases** in guillemets (« ») 
  with bold keywords. Example: «Donde el **reggae jamaicano** encuentra el **corazón latino**»
- **Information hierarchy:** Detailed content belongs in the **press kit PDF**, not the web.
  The web is the invitation, the PDF is the document.
- **One-page sections:** Each section fills exactly one viewport (`100vh`). 
  `scroll-snap-type: y mandatory` ensures clean section transitions.

### Visual Rules

- **Accent budget:** the cyan accent should cover **less than ~10%** of any
  viewport. If everything is accented, nothing is.
- **No gradients on text.** Headlines are solid `--text` or solid `--accent`.
- **Borders → spacing + elevation.** Prefer `--surface`/`--surface-2` elevation
  and whitespace over outlined cards. Reserve `--border-subtle` for the rare
  hairline divider.
- **Shadows are soft and minimal.** One soft shadow token; no orange glow.
- **Single CTA emphasis per view.** The primary CTA uses a filled accent; all
  other interactive elements are quieter (text + underline).
- **Ghost/outline button hover pattern:** secondary buttons (press kit, download
  links, social icons) use `color: var(--text-muted)` + `border: 1px solid
  var(--border-subtle)` at rest, and transition to `color: var(--accent)` +
  `border-color: var(--accent)` on hover/focus. No background fill, no box-shadow
  glow. This keeps the accent sparingly present as a *reveal* rather than a
  permanent fixture.

## Typography & Spacing

- **Type scale (rem):** `0.875 · 1 · 1.25 · 1.5 · 2 · 3 · 4`. Lean on high
  weight contrast: muted body (400–500) vs. heavy display headings (800).
- **Editorial feel:** increase line-height (~1.7 body) and letter-spacing on
  uppercase labels; let headlines breathe with generous margins.
- **Spacing scale (8px base):** `4 · 8 · 16 · 24 · 32 · 48 · 64 · 96` px.

## Motion Tokens

Use these consistently in framer-motion and CSS transitions.

| Token | Value | Use |
|---|---|---|
| `--dur-fast` | `150ms` | Hover, focus |
| `--dur-base` | `300ms` | Reveals, nav |
| `--dur-slow` | `600ms` | Hero stagger, parallax settle |
| `--ease-out` | `cubic-bezier(0.16,1,0.3,1)` | Default entrance easing |

- **Always** honor `prefers-reduced-motion: reduce` — disable transforms and
  large movement, keep content instantly visible.

## Migration Map (old → new)

Translation guide for a later implementation PR (current variables in
`react/src/styles.css`).

| Old variable | New variable / treatment |
|---|---|
| `--bg-start` / `--bg-end` (navy→amber gradient) | `--bg` (flat near-black) |
| `--accent` `#00d4ff` | `--accent` `#00d4ff` (kept; now the *only* accent) |
| `--accent-orange` / `-dark` / `-glow` | `--accent-orange` (demoted, optional) |
| `--accent-blue-light` | removed → use `--surface` / `--surface-2` |
| `--card-bg` / `--card-bg-hover` | `--surface` / `--surface-2` |
| `--card-shadow` / `--card-shadow-hover` | `--shadow-soft` |
| `--white` | `--text` |
| `--light-gray` | `--text-muted` |
