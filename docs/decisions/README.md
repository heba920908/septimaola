# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the React press kit (`react/`).

## What is an ADR?

An ADR is a short document that captures an important architectural decision made along with its context and consequences. We use ADRs to track decisions about the website's features, structure, and technical direction.

## Format

Each ADR follows this template:

```markdown
# ADR-NNNN: Title

## Status

Proposed | Accepted | Deprecated | Superseded by ADR-NNNN

## Context

What is the issue or motivation?

## Decision

What was decided?

## Consequences

What are the resulting effects — positive, negative, and neutral?
```

## Creating a New ADR

1. Copy the template from `template.md`
2. Name the file `NNNN-short-title.md` (zero-padded sequential number)
3. Fill in all sections
4. Set status to `Proposed` initially; update to `Accepted` once implemented

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-news-slide-section.md) | News slide section | Accepted |
| [0002](0002-local-dev-npm-vite.md) | npm/npx-first local development for React press kit | Accepted |
| [0003](0003-minimalist-redesign.md) | Bold minimalist redesign of the React press kit | Proposed |
| [0004](0004-build-time-image-fetch.md) | Build-time image fetch from Google Drive | Proposed |
| [0005](0005-mobile-delightful-experience.md) | Delightful mobile browser experience for the React press kit | Proposed |
| [0006](0006-press-production-kit.md) | Press & Production Kit as an independent information surface | Accepted |
| [0007](0007-visual-stage-plot.md) | Visual stage plot diagram | Accepted |
