# CLAUDE.md — React Press Kit

## Quick Reference

```bash
cd react
npm install
npm run dev
```

## Checking for Errors

Use local npm/npx first for runtime verification. Use Podman only as an optional fallback.

### Runtime and UI Verification

```bash
cd react
npm install
npm run dev
```

Then run browser verification against `http://127.0.0.1:5173` using this priority:

1. Integrated browser tools first (for example: `open_browser_page`, `read_page`, `screenshot_page`, `click_element`, `type_in_page`).
2. Playwright MCP as fallback.
3. Any available browser automation tooling if the above are unavailable.

Optional fallback:

```bash
cd react
podman build -t septimaola-react .
podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
```

### Lint / Static Analysis

There is no ESLint or TypeScript config in this project. To catch issues:

1. Run the npm workflow above and verify UI behavior with browser automation tools (integrated first, Playwright MCP fallback).
2. Review browser console events from your browser tool output to detect runtime errors.

### Common Runtime Issues

- **Images not loading** — Run `npm run fetch:images` to download them. Check `public/images/` exists.
- **Base path mismatch** — Production uses `/septimaola/` base path (see `vite.config.js`). Dev uses `/`. If assets 404 in production, check the base path.
- **Facebook timeline embed console noise** — Third-party iframe scripts may emit warnings/errors unrelated to app code.

## Testing with Browser Tools (Integrated First)

This project has no automated test suite. Verify the npm-served app with integrated browser tools first, then Playwright MCP as fallback.

### Workflow: npm Serve → Verify

1. **Start the app with npm:**

   ```bash
   cd react
   npm install
   npm run dev
   ```

   Optional fallback:

   ```bash
   cd react
   podman build -t septimaola-react .
   podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
   ```

2. **Open the site with browser automation tools (integrated first):**

   Use `open_browser_page` to navigate to `http://127.0.0.1:5173`.

3. **Visual checks to perform:**

   - `screenshot_page` — capture full page, verify layout renders correctly
   - `run_playwright_code` — verify section IDs/headings and nav link set
   - `read_page` — inspect accessibility tree and recent console events
   - Navigate to each section anchor: `#noticias`, `#biografia`, `#integrantes`, `#musica`, `#galeria`, `#contacto`

4. **Stop the running server** when done.

### Example Integrated Browser Tool Sequence

```
open_browser_page → http://127.0.0.1:5173
screenshot_page   → verify Hero section renders
run_playwright_code → verify headings for biografia/integrantes/musica/galeria/contacto
read_page         → inspect recent console events and navigation links
```

If integrated tools are unavailable in your environment, run an equivalent sequence with Playwright MCP.

### What to Verify

| Section | Check |
|---------|-------|
| Hero | Logo/title visible, gradient background renders, tagline present |
| Noticias | Slider cards render with Facebook posts |
| Biografía | Text blocks and Visión/Misión cards render |
| Integrantes | Member cards render, images load or gracefully hide |
| Discografía | Song cards display titles and descriptions |
| Galería | Photo grid renders, broken images are hidden (not blank boxes) |
| Contacto | Contact info and social links present |
| Navigation | Sticky header visible, links include Noticias/Biografía/Integrantes/Música/Galería/Contacto |

## News Automation Scope

- News generation is Facebook-only.
- Instagram fetching is intentionally not used to keep the pipeline simpler and more stable.

## Container Development

```bash
podman build -t septimaola-react .
podman run --rm -v .:/app:z -p 5173:5173 septimaola-react
```

The container runs dependency installation and starts the Vite dev server. Use this as a fallback for isolated development without local Node.js.

## Architecture Notes

- **No router** — single-page app, all sections rendered in `App.jsx`
- **No state library** — only React `useState`/`useEffect`
- **No TypeScript** — plain JSX
- **Single stylesheet** — `src/styles.css` with CSS custom properties (see root CLAUDE.md for palette)
- **Images** — Downloaded at build time from Google Drive to `public/images/`, then served as static assets

## Image Pipeline

Images are no longer fetched at runtime from Google Drive's CDN. Instead, a build-time script downloads them once and they are served as local static assets.

### How it works

1. **Manifest** (`scripts/fetch-images.mjs`) contains `{ slug, driveId }` entries for member photos and gallery images.
2. **Fetch script** downloads from `https://lh3.googleusercontent.com/d/<id>` to `public/images/{members,gallery}/<slug>.jpg`.
3. **Auto-run** via npm lifecycle:
   - `predev` — fetches before starting the Vite dev server
   - `prebuild` — fetches before creating the production bundle
4. **Idempotent** — existing files are skipped; use `--force` to refresh all.
5. **Gitignored** — `public/images/` is not committed; CI re-fetches on every build.

### Adding a new image

1. Add a new `{ slug, id }` entry to the appropriate section in `scripts/fetch-images.mjs`.
2. Reference the image by slug in `Members.jsx` or `Gallery.jsx`:
   ```jsx
   <img src={`${import.meta.env.BASE_URL}images/members/<slug>.jpg`} ... />
   ```
3. Run `npm run fetch:images` (or just `npm run dev` / `npm run build`).

### Commands

```bash
cd react
npm run fetch:images      # Download images once
npm run fetch:images -- --force  # Re-download all images
```

## Deployment

CI/CD via `.github/workflows/deploy.yml` — auto-deploys `dist/` to GitHub Pages on push to `main` or `init` branch. The production URL is `https://heba920908.github.io/septimaola/`.

## Architecture Decision Records

Feature and design decisions for this app are tracked in [`docs/decisions/`](../docs/decisions/README.md). Before making significant changes (new sections, layout shifts, external dependencies), check existing ADRs and create a new one if the change warrants it.
