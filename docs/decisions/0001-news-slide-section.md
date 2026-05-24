# ADR-0001: News Slide Section

## Status

Proposed

## Context

The press kit site currently presents static information (band members, discography, gallery, contact). There is no way to communicate upcoming gigs, releases, or announcements to visitors. A dynamic news/announcements area would keep the page feeling current and give promoters a reason to revisit.

## Decision

Add a news slide (carousel/slider) section to the React press kit page. The section will:

- Display a rotating set of news cards (upcoming shows, releases, press mentions)
- Be placed in a prominent position on the page (e.g., between Hero and Members, or after Hero)
- Support manual navigation (prev/next) and optionally auto-advance
- Content will be hardcoded in the component initially (no CMS or API)

## Consequences

- **Positive:** Visitors see up-to-date information; the page feels alive and maintained.
- **Positive:** Promoters/venues get immediate visibility into the band's activity.
- **Negative:** Content must be manually updated in the source code for now.
- **Neutral:** Adds one more component to the flat architecture; no routing or state library changes required.
