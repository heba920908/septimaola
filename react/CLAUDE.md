# CLAUDE.md — React Press Kit

## Quick Reference

```bash
cd react/
npm install          # Install dependencies
npm run dev          # Vite dev server at http://localhost:5173
npm run build        # Production build → dist/
npm run preview      # Serve production build locally
npm start            # npx serve -s dist -l 5173
```

## Checking for Errors

### Build Errors

```bash
npm run build
```

A successful build exits with code 0 and produces `dist/`. Any JSX syntax errors, missing imports, or broken references will fail the build.

### Lint / Static Analysis

There is no ESLint or TypeScript config in this project. To catch issues:

1. Run `npm run build` — Vite/Rollup will report unresolved imports, syntax errors, and React JSX issues.
2. Open the browser console after `npm run dev` to check for runtime errors (missing images, CORS, 404s).

### Common Runtime Issues

- **Google Drive images returning 429** — `Members.jsx` has retry logic (`ImageWithRetry`), but rate limits can still cause blank photos in dev. This is expected.
- **Base path mismatch** — Production uses `/septimaola/` base path (see `vite.config.js`). Dev uses `/`. If assets 404 in production, check the base path.

## Testing with Playwright MCP

This project has no automated test suite. Use the Playwright MCP tools to visually verify the built site:

### Workflow: Build → Serve → Verify

1. **Build the production bundle:**

   ```bash
   cd react/ && npm run build
   ```

2. **Start a local static server (async):**

   ```bash
   npx serve -s dist -l 5173
   ```

3. **Open the site with Playwright MCP:**

   Use `open_browser_page` to navigate to `http://localhost:5173/septimaola/` (production base path).

4. **Visual checks to perform:**

   - `screenshot_page` — capture full page, verify layout renders correctly
   - `click_element` — test hamburger menu opens/closes on mobile viewport
   - `read_page` — verify text content (band name, section headings, member names)
   - Navigate to each section anchor: `#inicio`, `#nosotros`, `#musica`, `#galeria`, `#contacto`

5. **Kill the server** when done.

### Example Playwright MCP Sequence

```
open_browser_page → http://localhost:5173/septimaola/
screenshot_page   → verify Hero section renders
click_element     → hamburger button (mobile viewport)
screenshot_page   → verify nav menu opened
read_page         → confirm all section headings present
```

### What to Verify

| Section | Check |
|---------|-------|
| Hero | Logo/title visible, gradient background renders |
| Nosotros (Members) | Member cards render, images load or gracefully hide |
| Discografía | Song cards display titles and descriptions |
| Galería | Photo grid renders, broken images are hidden (not blank boxes) |
| Contacto | Contact info and social links present |
| Navigation | Sticky header visible, hamburger menu works, anchor links scroll |

## Container Development

```bash
podman build -t septimaola-react .
podman run -it --rm -v .:/app:z -p 5173:5173 septimaola-react
```

The container runs `npm install` then starts the dev server. Use for isolated development without local Node.js.

## Architecture Notes

- **No router** — single-page app, all sections rendered in `App.jsx`
- **No state library** — only React `useState`/`useEffect`
- **No TypeScript** — plain JSX
- **Single stylesheet** — `src/styles.css` with CSS custom properties (see root CLAUDE.md for palette)
- **Google Drive CDN** — image IDs hardcoded in `Members.jsx` and `Gallery.jsx`

## Deployment

CI/CD via `.github/workflows/deploy.yml` — auto-deploys `dist/` to GitHub Pages on push to `main` or `init` branch. The production URL is `https://heba920908.github.io/septimaola/`.

## Architecture Decision Records

Feature and design decisions for this app are tracked in [`docs/decisions/`](../docs/decisions/README.md). Before making significant changes (new sections, layout shifts, external dependencies), check existing ADRs and create a new one if the change warrants it.
