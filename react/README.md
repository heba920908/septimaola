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

## Local Development with Podman

### Build the container image

```bash
cd react
podman build -t septimaola-react .
```

### Run with volume mount (for live development)

```bash
podman run -it --rm -v .:/app:z -p 5173:5173 septimaola-react
```

Then open http://localhost:5173 in your browser.

## Validation with Playwright MCP (Podman Only)

Use Podman as the only validation runtime (no npm fallback for verification).

1. Start the app with Podman:

```bash
cd react
podman build -t septimaola-react .
podman run --rm -v /absolute/path/to/septimaola/react:/app:z -p 5173:5173 septimaola-react
```

2. Run Playwright MCP checks against `http://127.0.0.1:5173`:

- Capture a full-page screenshot.
- Verify headings for `#biografia`, `#integrantes`, `#musica`, `#galeria`, and `#contacto`.
- Confirm hero tagline contains `Reggae · Ska · Rocksteady`.
- Confirm nav links include `Noticias`, `Biografía`, `Integrantes`, `Música`, `Galería`, `Contacto`.
- Inspect recent console events; unexpected app errors fail validation.

3. Stop the running Podman container after verification.

---

**Notes:**
- The Dockerfile installs dependencies, builds the app, and serves it on port 80 (mapped to 5173 on your host).
- Volume mounting allows you to edit `src/` files and see changes after a rebuild.
- Use `-it` flags for interactive mode; remove them if running in background.
