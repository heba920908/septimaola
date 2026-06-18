---
alwaysApply: false
globs: "react/**/*.{jsx,css}"
---

# React Visual Verification

After making any change to a JSX or CSS file under `react/`, verify the page renders correctly before considering the task done.

## Pre-flight

Ensure the app is running and reachable on port 5173. The preferred method is via the Podman container with a volume mount so that source changes are reflected without rebuilding the image:

```bash
# 1. Build the image (only needed once or after Dockerfile changes)
cd react
podman build -t septimaola-react .

# 2. Run with live volume mount
podman run -it --rm -v .:/app:z -p 5173:5173 septimaola-react
```

The volume mount (`-v .:/app:z`) lets you edit `src/` files and see changes after a rebuild inside the container. The app is then served at `http://localhost:5173`.

Do not use local npm fallback for verification in this repository; use Podman for validation.

## Recommended MCP

Use **Playwright MCP** (`@playwright/mcp`) for all browser-based verification steps below. If Playwright MCP is not configured in your Cursor MCP settings, add it before running this rule:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Verification Steps

### 1. Navigate and Screenshot

Navigate to `http://127.0.0.1:5173` and take a full-page screenshot. Confirm the page loads without a blank screen or error overlay.

### 2. Section Visibility

Scroll through the page and confirm all six sections render with their expected headings:

| Section ID     | Expected heading                 | Key element           |
| -------------- | -------------------------------- | --------------------- |
| `#noticias`    | "Noticias"                      | `.news-slider` with news cards |
| `#biografia`   | "¿Quiénes somos?"                | `.container p` blocks + `.vision-mission` cards |
| `#integrantes` | "Integrantes"                    | `.members-grid` with member cards |
| `#musica`      | "Discografía / Material"         | `.songs-grid` with song cards |
| `#galeria`     | "Galería"                        | `.gallery-grid` |
| `#contacto`    | "Contacto"                       | `.contact-info`, social links |

For Noticias specifically:

- Cards should render (Facebook-only data source).
- The old timeline fallback message (`No fue posible generar las tarjetas...`) should not appear.
- If an item has empty description, the card should render without description text.

### 3. Hero Section

Confirm `.hero-content` is visible and contains the text "Reggae · Ska · Rocksteady".

### 4. Navigation Bar

Confirm the sticky header renders with all six nav links: **Noticias**, **Biografía**, **Integrantes**, **Música**, **Galería**, **Contacto**.

### 5. CSS Design Language

After any CSS change, verify the design language is consistent:

- **Background**: deep navy-to-amber gradient (`--bg-start: #0a3d62` → `--bg-end: #8b5a1a`)
- **Primary accent**: cyan (`--accent: #00d4ff`) on section headings and borders
- **Secondary accent**: orange (`--accent-orange: #f68c02`) on CTAs and interactive links
- **Text**: white or `--light-gray` on all dark surfaces — no unreadable contrast
- **No raw hex values**: any colors introduced in CSS changes must use the CSS custom properties defined in `:root` in `styles.css`, never raw hex literals

### 6. Image Load Failures (Expected Behavior)

Gallery (`.gallery-grid`) and Members (`.members-grid`) images are served from Google Drive CDN (`lh3.googleusercontent.com`). These images may fail to load or be hidden:

- `Gallery.jsx` hides images with `display: none` on `onError`
- `Members.jsx` uses `ImageWithRetry` — up to 2 retries with 1 s / 2 s delays on 429 errors, then hides the image

**These are not failures.** Missing images from Google Drive CDN should not block verification. Only flag if the card layout itself breaks (overlapping elements, invisible text, broken grid structure).

### 7. Console Errors

Note any unexpected JavaScript console errors captured by Playwright. Errors related to Google Drive image loading (network/CORS/429) are expected and can be ignored.

Facebook plugin/embed warnings or errors emitted from third-party iframe scripts can also be treated as expected, as long as the app layout and interactions remain stable.

## Pass Criteria

The change is verified when all of the following hold:

1. All six sections scroll into view and display their expected headings
2. The background gradient and accent colors are visually consistent with the design language
3. No layout breakage: no overlapping elements, no invisible text, grids render correctly
4. No unexpected JS console errors (Drive CDN and Facebook iframe/plugin errors are exempt)

## Scope

This rule targets the **local dev server only** (`http://localhost:5173`). Deployment to GitHub Pages (`https://heba920908.github.io/septimaola/`) is handled automatically by CI/CD on push to `main` or `init` and is out of scope for this verification step.
