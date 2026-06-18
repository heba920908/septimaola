# React Presskit — SÉPTIMA OLA

A Vite + React frontend for Séptima Ola's press kit. Content and UI in Spanish.

## News (Noticias)

Noticias now uses the official Facebook Page Plugin iframe and displays the
public timeline directly from:

- https://www.facebook.com/septimaolaoficial

How it works:

- `News.jsx` renders `https://www.facebook.com/plugins/page.php?...` with
  `tabs=timeline` and responsive width.
- No Facebook App ID, access token, or admin login is required.
- There is no build-time news generation and no local seed JSON file.

This keeps the section live and operational without CI secrets or manual token
refresh workflows.

## Local Development (npm/npx First)

Use the native Vite dev server for day-to-day development and automatic reload.

```bash
cd react
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

Notes:

- `npm run dev` runs Vite (equivalent to `npx vite`) with HMR enabled.
- Source changes under `src/` reload automatically.

## Optional Container Fallback (Podman)

Use this only if you cannot run the local Node.js workflow.

### Build the container image

```bash
cd react
podman build -t septimaola-react .
```

### Run with volume mount (for live development)

```bash
podman run --rm -v .:/app:z -p 5173:5173 septimaola-react
```

Then open http://localhost:5173 in your browser.

## Validation with Browser Tools

Use the local npm/npx dev server as the primary validation runtime.

Browser tool priority:

1. Use integrated browser tools first (for example: `open_browser_page`, `read_page`, `screenshot_page`, `click_element`, `type_in_page`).
2. Use Playwright MCP as fallback.
3. If neither is available, use any available browser automation tool and apply the same checks.

1. Start the app with npm:

```bash
cd react
npm install
npm run dev
```

Optional fallback if local Node.js is unavailable:

```bash
cd react
podman build -t septimaola-react .
podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
```

2. Run browser checks against `http://127.0.0.1:5173`:

- Capture a full-page screenshot.
- Verify headings for `#biografia`, `#integrantes`, `#musica`, `#galeria`, and `#contacto`.
- Confirm hero tagline contains `Reggae · Ska · Rocksteady`.
- Confirm nav links include `Noticias`, `Biografía`, `Integrantes`, `Música`, `Galería`, `Contacto`.
- Inspect recent console events; unexpected app errors fail validation.

3. Stop the running dev server after verification.

---

**Notes:**
- The Dockerfile installs dependencies and runs the Vite dev server on port 5173.
- Local npm/npx workflow is preferred for the fastest feedback loop.
- Podman fallback can use `-v .:/app:z` on SELinux systems; on non-SELinux hosts, `-v .:/app` also works.
