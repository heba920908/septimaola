# ADR-0007: Visual Stage Plot Diagram in the Press & Production Kit

## Status

Accepted

## Context

`StagePlot.jsx` currently renders the stage layout only as textual lists derived from the SKILL.md canonical data. For a press/production kit, a rendered spatial diagram communicates performer/instrument placement far faster to production teams and venue staff. ADR-0006 deferred UI placement of the stage plot; this ADR resolves that deferral.

References the canonical source: `.claude/skills/septimaola-common/SKILL.md` Stage Plot section.

## Decision

Add a visual stage diagram at the top of the `#stage-plot` subsection using a CSS-grid/positioned-`div` layout with `framer-motion` entrance animations (consistent with existing variants and the no-new-deps stack from `react/CLAUDE.md`).

### Details

- Performers shown as positioned cards with emoji instrument glyphs, name, and role; placed by stage zone (Left / Center Front / Rear Center / Right) plus an audience/FOH indicator.
- Diagram driven by a single position data array so it stays in sync with SKILL.md canonical placement.
- Existing lists (orientation, preferred placement, monitor mixes, input-to-position mapping, technical notes) and tables are retained below the diagram as authoritative detail.
- Spanish UI labels with canonical technical terms (per AGENTS.md Golden Language Rule).
- Responsive: stacks gracefully on mobile (per ADR-0005 mobile experience).

## Consequences

- **Positive**: Faster spatial comprehension; resolves ADR-0006 deferred UI item; no new dependencies; canonical data preserved as fallback detail.
- **Positive**: Data-driven layout keeps diagram aligned with SKILL.md.
- **Neutral**: Adds CSS surface area to `styles.css`; emoji rendering varies slightly across platforms.
- **Negative**: Diagram is a simplified abstraction, not an engineering-accurate scale plot.
