# ADR-0002: npm/npx-First Local Development for React Press Kit

## Status

Accepted

## Context

Local instructions and verification guidance in the repository emphasized running
the React app via `podman run -it ...` as the primary path. This has been
fragile across environments (Docker-only setups, Podman variants, WSL-based
workflows, and CI/local differences).

The React app already uses Vite and provides a native local development command
with automatic reload support. Using the framework-native workflow first reduces
environment coupling and removes interactive terminal dependencies.

## Decision

Use the React/Vite native workflow as the primary local development and
verification path:

- Run `npm install` once, then `npm run dev` from `react/`.
- Treat `npm run dev` (Vite, equivalent to `npx vite`) as the default runtime
  for local development and browser-based verification (integrated tools first,
  Playwright MCP fallback).
- Keep Podman/Docker as an optional fallback for isolated environments.
- Update the container fallback command to non-interactive usage (`podman run
  --rm ...`) and remove reliance on `-it`.
- Keep the existing Dockerfile and container workflow available as fallback,
  not as the primary instruction.

## Consequences

- **Positive:** More portable and less fragile local setup across Linux, macOS,
  Windows/WSL, Docker, and Podman environments.
- **Positive:** Faster feedback loop from native Vite HMR in day-to-day
  development.
- **Positive:** Verification instructions align with the framework-native
  workflow already defined in `package.json`.
- **Negative:** Developers now need a compatible local Node.js runtime
  (Node 18+) for the primary path.
- **Neutral:** Podman/Docker remains available for teams that prefer or require
  containerized local execution.
