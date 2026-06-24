# ADR-0006: Press & Production Kit as an Independent Information Surface

## Status

Proposed

## Context

The current React press kit is optimized as a promotional, public-facing
single-page experience for fans, media, and general discovery. Its primary job
is to communicate identity, music, visuals, and contact pathways quickly.

Beyond promotion, the band needs to expose operational and professional
information aimed at a different audience: media outlets, production teams,
venue staff, and booking operations. This includes the technical rider (stage
plot, channel lists, monitor mixes, FOH notes), but is not limited to it.
Future needs include hospitality requirements, booking and logistics details,
and downloadable assets (PDF rider, stage plot, hi-res photos).

Naming this surface narrowly as a "technical rider" would be too restrictive,
because it must also hold information unrelated to audio/stage engineering.
A broader umbrella keeps the surface coherent as it grows.

Placing this material directly into the promotional flow can dilute the
homepage narrative, increase cognitive load for non-professional visitors, and
create information architecture tension between marketing content and
operational/professional documentation.

## Decision

Establish an independent information surface named **Press & Production Kit**,
separate from the promotional main page. The technical rider becomes one section
within this broader kit rather than the umbrella concept itself.

Initial intended structure of the Press & Production Kit:

- Technical Rider (audio requirements, input list, stage plot)
- Hospitality Rider (catering, dressing room, accommodation) `TBD`
- Booking & Logistics (contacts, fees, load-in) `TBD`
- Downloads (PDF rider, stage plot, hi-res photos) `TBD`

For this phase, implementation is intentionally limited to documentation and
content readiness:

- Capture this architectural/product direction in ADR form.
- Reframe the canonical knowledge base so the technical rider lives under the
  Press & Production Kit umbrella, and complete the Stage Plot content.
- Defer React UI integration and routing/page changes to a later decision and
  implementation phase.

This keeps the promotional page focused while allowing the kit to mature in
parallel.

## Consequences

- Positive: Preserves a clear promotional narrative on the current main page.
- Positive: Reduces scope creep in the existing React surface.
- Positive: A broader name accommodates non-rider information (hospitality,
  booking/logistics, downloads) without future renaming.
- Positive: Improves operational clarity by preparing canonical content in one
  place before UI decisions.
- Positive: Enables cleaner future options (separate route, standalone kit page,
  or separate artifact) without forcing immediate front-end coupling.
- Negative: The Press & Production Kit is not yet directly reachable from the
  public web experience until a follow-up implementation phase is approved.
- Negative: Introduces an extra step in delivery planning (future integration
  task/ADR required).
- Neutral: No React code changes are made in this phase by design.
