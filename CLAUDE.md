# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the marketing and promotional repository for **Septima Ola**, a reggae/ska/rocksteady band based in Mexico City. It contains several sub-projects:

- `react/` — Primary deliverable: a single-page digital press kit (React + Vite), deployed to GitHub Pages
- `latex/` — PDF press kit slide deck (Beamer/LuaLaTeX), compiled via container
- `mdcovers/` — Markdown chord/bass sheets for 30+ live cover songs
- `about/` — Source-of-truth band member bios (Markdown); feed both the React app and LaTeX slides
- `ai/` — Python multi-agent system (Google ADK) for generating illustrated slide content
- `covers/` — LaTeX experiment for music notation (proof-of-concept, not active)

## React Web App (`/react`)

### Commands

```bash
npm run dev       # Vite dev server (port 5173)
npm run build     # Production build → react/dist/
npm run preview   # Serve the dist/ build
npm start         # npx serve -s dist -l 5173
```

### Container (Podman/Docker)

```bash
podman build -t septimaola-react .
podman run -it --rm -v .:/app:z -p 5173:5173 septimaola-react
```

### Architecture

Flat component structure — no routing, no state management library, no TypeScript, single `styles.css` file.

- `App.jsx` — root component: sticky nav, hamburger menu (useState/useEffect), renders all page sections
- `components/Members.jsx` — band member cards with expand/collapse; includes `ImageWithRetry` which handles 429 rate-limit errors from Google Drive CDN (`lh3.googleusercontent.com`) with up to 2 retries and incremental delays
- `components/Gallery.jsx` — photo grid (Google Drive images, hides cards on error)
- Google Drive image IDs are hardcoded in `Members.jsx` and `Gallery.jsx`

CI/CD: `.github/workflows/deploy.yml` auto-deploys to GitHub Pages on push to `main` or `init` branches.

**No test suite, no linting config.**

### Color Palette

All colors are defined as CSS custom properties in `react/src/styles.css` (`:root`). Always use these variables — never introduce raw hex values in new work.

| Variable | Value | Role |
|---|---|---|
| `--bg-start` | `#0a3d62` | Background gradient start (deep navy) |
| `--bg-end` | `#8b5a1a` | Background gradient end (warm amber) |
| `--accent` | `#00d4ff` | Primary accent — headings, borders, highlights (cyan) |
| `--accent-orange` | `#f68c02` | Secondary accent — CTAs, roles, links (vibrant orange) |
| `--accent-orange-dark` | `#ad6201` | Hover state for orange elements |
| `--accent-orange-glow` | `rgba(246,140,2,0.35)` | Box-shadow glow for orange elements |
| `--accent-blue-light` | `rgba(1,149,194,0.777)` | Mid-blue tint (used in card backgrounds) |
| `--white` | `#ffffff` | Primary text on dark backgrounds |
| `--light-gray` | `#e8f4f8` | Body text, secondary labels (blue-tinted near-white) |
| `--card-bg` | `rgba(1,149,194,0.10)` | Card/panel background (translucent blue) |
| `--card-bg-hover` | `rgba(1,149,194,0.18)` | Card hover state |
| `--card-shadow` | `0 4px 18px rgba(0,0,0,0.25)` | Default card shadow |
| `--card-shadow-hover` | `0 8px 28px rgba(246,140,2,0.18)` | Card hover shadow (orange tint) |

**Implicit colors** (used directly in the stylesheet, not as variables):

- `#0d2b47` — body gradient midpoint (dark navy)
- `rgba(6,30,55,0.85)` — sticky header background
- `rgba(6,22,44,0.98)` — mobile slide-out nav background

**Design language:** deep navy-to-amber gradient background, cyan primary accent for structural elements (borders, section headings), orange secondary accent for all interactive elements (buttons, links, CTAs). Text is always white or `--light-gray` on dark surfaces.

## LaTeX Press Kit (`/latex`)

```bash
cd latex/
podman build -t latex-build .
# Standard:
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode slides.tex
# Fedora/SELinux:
podman run --rm -it --user root:root -v .:/data:z latex-build latexmk -pdf -interaction=nonstopmode slides.tex
```

`slides.tex` is the main document; shared config in `loadslides.tex`; custom Beamer theme in `latex/styles/`. Background images and logo are downloaded separately (Google Drive/Mega.nz), not committed to the repo.

## Chord Sheets (`/mdcovers`)

Each file follows a strict template with sections: Quick Chord Reference, Chord Progression Map, Performance Notes, and links to YouTube + lacuerda.net. Use `la_dosis_perfecta.md` as the template. Prefer `chords.lacuerda.net` for Latin songs. When adding a song, also update `mdcovers/README.md`.

## Source of Truth Flow

`about/*.md` bios are the canonical source for band member information. When updating the React app's `Members.jsx` or the LaTeX `slides.tex`, pull content from `about/` rather than editing those files directly.

- To update `Members.jsx` from bios: use `.github/prompts/react-update.prompt.md`
- To update `slides.tex` from bios: use `.github/agents/presskit-updater.agent.md`

## AI Agent (`/ai/press_kit_agent`)

Python multi-agent system using Google ADK. Requires `.env` with `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `MODEL`, `IMAGE_MODEL`. Three agents: band background answerer → slide content writer → image generation (Vertex AI Imagen, stored in GCS).
