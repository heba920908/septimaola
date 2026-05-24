# React Presskit — SÉPTIMA OLA

A Vite + React frontend for Séptima Ola's press kit. Content and UI in Spanish.

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

---

**Notes:**
- The Dockerfile installs dependencies, builds the app, and serves it on port 80 (mapped to 5173 on your host).
- Volume mounting allows you to edit `src/` files and see changes after a rebuild.
- Use `-it` flags for interactive mode; remove them if running in background.
