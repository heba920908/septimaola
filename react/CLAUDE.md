# CLAUDE.md — React Press Kit

## Quick Reference

```bash
cd react
podman build -t septimaola-react .
podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
```

## Checking for Errors

Validation for this project must use Podman + Playwright MCP. Do not use local npm fallback commands for verification.

### Runtime and UI Verification

```bash
cd react
podman build -t septimaola-react .
podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
```

Then use Playwright MCP against `http://127.0.0.1:5173`.

### Lint / Static Analysis

There is no ESLint or TypeScript config in this project. To catch issues:

1. Run the Podman workflow above and verify UI behavior with Playwright MCP.
2. Review browser console events from Playwright output to detect runtime errors.

### Common Runtime Issues

- **Google Drive images returning 429** — `Members.jsx` has retry logic (`ImageWithRetry`), but rate limits can still cause blank photos in dev. This is expected.
- **Base path mismatch** — Production uses `/septimaola/` base path (see `vite.config.js`). Dev uses `/`. If assets 404 in production, check the base path.
- **Facebook timeline embed console noise** — Third-party iframe scripts may emit warnings/errors unrelated to app code.

## Testing with Playwright MCP

This project has no automated test suite. Use Playwright MCP to verify the Podman-served app.

### Workflow: Podman Serve → Verify

1. **Start the app with Podman:**

   ```bash
   cd react
   podman build -t septimaola-react .
   podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
   ```

2. **Open the site with Playwright MCP:**

   Use `open_browser_page` to navigate to `http://127.0.0.1:5173`.

3. **Visual checks to perform:**

   - `screenshot_page` — capture full page, verify layout renders correctly
   - `run_playwright_code` — verify section IDs/headings and nav link set
   - `read_page` — inspect accessibility tree and recent console events
   - Navigate to each section anchor: `#noticias`, `#biografia`, `#integrantes`, `#musica`, `#galeria`, `#contacto`

4. **Kill the Podman run** when done.

### Example Playwright MCP Sequence

```
open_browser_page → http://127.0.0.1:5173
screenshot_page   → verify Hero section renders
run_playwright_code → verify headings for biografia/integrantes/musica/galeria/contacto
read_page         → inspect recent console events and navigation links
```

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
