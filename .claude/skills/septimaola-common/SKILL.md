# Septima Ola Common Knowledge Base Skill

This skill is the shared knowledge base for Septima Ola content updates.
Use it whenever you need to create, revise, or validate band information that
will be displayed in the web press kit (`react/`) or in the PDF press kit
(`latex/`).

It contains canonical wording for:
- Band profile and narrative
- Crew roles
- Technical rider (audio requirements and stage input list)

## Purpose

Use this skill to make sure content updates are:
- Consistent across channels (web and PDF)
- Factually aligned with the current band profile
- Written in a reusable format for publication

This is a documentation/KB skill, not a coding framework skill.

## When To Use This Skill

Activate this skill when requests include any of the following:
- "Update member info" or "refresh bios"
- "Change press kit copy"
- "Sync React and LaTeX content"
- "Update technical rider / input list"
- "Prepare content for website and PDF"

If a task mixes design or implementation details, combine this skill with
project-specific rules, but keep this skill as source content truth.

## How To Use This Skill

Follow this workflow every time:

1. Identify target output(s)
- Confirm if the request affects `react/`, `latex/`, or both.

2. Extract relevant KB blocks
- Band narrative (about/mission/vision)
- Crew details
- Audio requirements
- Input list

3. Adapt tone and length by target
- For React: concise, scannable, section-friendly text.
- For LaTeX: editorial, complete, publication-ready copy.
- For language: Spanish by default for `react/` and `latex/` (Mexico audience),
  unless explicitly requested otherwise.

4. Keep terminology stable
- Do not rename roles/instruments unless explicitly requested.
- Preserve technical meanings in rider and channel list.

5. Produce synchronized output
- When both targets are requested, ensure key facts match across both deliverables.

6. Validate before finalizing
- Check for contradictory facts, channel mismatches, or accidental omissions.

## Output Contract

When this skill is used, output should include:
- `target`: react, latex, or both
- `changed_sections`: concise list of updated sections
- `final_copy`: ready-to-paste content, defaulting to Spanish for public
	artifacts (`react/`, `latex/`), unless another language is explicitly
	requested
- `consistency_notes`: short note if wording differs by medium (web vs PDF)

## Quick Prompt Templates

Use these when invoking this skill in a task:

- Update web copy only:
	"Using the Septima Ola common KB skill, update React sections with concise
	copy for: [section names]. Keep technical details unchanged."

- Update PDF copy only:
	"Using the Septima Ola common KB skill, rewrite LaTeX press kit text for
	[section names] with publication-ready tone, preserving canonical facts."

- Sync both targets:
	"Using the Septima Ola common KB skill, produce synchronized content for
	React and LaTeX for [topic], highlighting any wording differences by medium."

## Guardrails

- Treat this file as a KB source, not as a place to invent new facts.
- If required data is missing, mark it as `TBD` instead of guessing.
- Keep personal data limited to what the press kit needs.
- Preserve the structure of the technical rider tables when updating details.
- Keep language policy consistent: Spanish for public artifacts; English is
	acceptable for AI-rig/internal documentation files.

---

# Canonical Band Profile

Septima Ola combines reggae, ska, and rocksteady to create a distinctive sound
with catchy melodies, danceable rhythms, and socially conscious lyrics focused
on love, unity, and social justice.

The band was born from a shared passion for music among members with diverse
influences and experiences. Based in La Raza, Mexico City, Septima Ola keeps
evolving through energetic live performances and heartfelt songs.

## Objective

Spread positive messages through music and inspire people to embrace love,
peace, and social change.

## Vision

Be a leading force in reggae and ska, recognized for authentic sound,
meaningful lyrics, and artistic integrity.

## Mission

Create music that resonates with people from all walks of life and fosters
community and empowerment.

# Press & Production Kit

This surface groups professional and operational information for media,
production teams, venue staff, and booking. It is distinct from the promotional
main page. The technical rider is one section of this kit; other sections cover
hospitality, booking/logistics, and downloadable assets.

## Technical Rider

### Crew List

| Name | Role | ID |
| --- | --- | --- |
| [Alfred Herrera](alfred.md) | Guitarra / stage manager | TBD |
| [Arthur](arthur.md) | Bajo electrico / stage manager | TBD |
| [Levi'Sax](levi_sax.md) | Sax tenor | TBD |
| [Rodrigo Mera](rodrigo_mera.md) | Violinist and Arranger | TBD |
| [Sandy Robinsuell](sandy_robinsuell.md) | Keyboardist and Backing Vocalist | TBD |
| [lemanu](lemanu.md) | Drummer | TBD |

### Audio Requirements

- The show requires a complete Front of House (FOH) mix position and an
	independent stage monitoring area.
- FOH should be placed approximately 20 m from the front of the stage at around
	1 m height for accurate audience-reference mixing.
- The PA system must be professional-grade. No specific brand is mandatory, but
	Electro-Voice, Bose, or JBL are recommended.
- Stage monitoring should include anti-feedback capability.
- Mixing console: minimum 8 input channels (6-member band), with enough aux
	sends for monitor mixes.
- System output must reach at least 100 dB SPL.
- Guitar and bass require either direct boxes (DI) or monitor amplifiers.
- Violin and sax require direct boxes (DI).
- Sax channel should include compression.

### Input List

| Channel | Instrument | Mic/DI | Aux | Equipment | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Kick Drum | Dynamic mic | Mix 1 (Drums) | Drum mic stand | Required |
| 2 | Snare Drum | Dynamic mic | Mix 1 (Drums) | Drum mic stand | Required |
| 3 | Overhead (Drums) | Condenser mic | Mix 1 (Drums) | Boom stand + phantom power | Can be mono if channels are limited |
| 4 | Bass | DI (preferred) or amp mic | Mix 1 / Mix 2 | Active DI box or bass amp | DI or monitor amplifier required |
| 5 | Guitar | DI or amp mic | Mix 2 (Frontline) | DI box or guitar amp | DI or monitor amplifier required |
| 6 | Keyboard L | DI | Mix 2 / Mix 3 | Active DI box | If needed, can be summed to mono |
| 7 | Keyboard R / Backing Vocal | DI or vocal dynamic mic | Mix 2 / Mix 3 | DI box or vocal mic + stand | Use as keyboard R when stereo is available |
| 8 | Violin | DI | Mix 2 (Frontline) | Active DI box | DI required |
| 9 | Sax | DI or clip mic | Mix 2 (Frontline) | DI box or sax mic + compressor | Compression required |

### Stage Plot

#### Stage Orientation

- Audience is in front of the stage.
- FOH position should be centered at approximately 20 m from the stage front
	and around 1 m height.
- Drum kit remains rear-center as timing anchor.

#### Preferred On-Stage Placement

- Stage Left (from audience view): Arthur (Bass), Sandy (Keyboard/Backing Vocal)
- Center Front: Alfred Herrera (Guitar / Lead Vocal)
- Rear Center: lemanu (Drums)
- Stage Right: Rodrigo Mera (Violin), Levi'Sax (Sax)

#### Monitor Mix Layout

- Mix 1 (Drums): Kick, Snare, Overhead, Bass reference
	- Primary users: lemanu, Arthur
- Mix 2 (Frontline): Bass, Guitar, Violin, Sax, selective keys/vocal as needed
	- Primary users: Alfred, Rodrigo, Levi'Sax, Sandy
- Mix 3 (Keys/Vocal reference): Keyboard and backing vocal priority
	- Primary user: Sandy

#### Input-to-Position Mapping (Reference)

- Ch 1 Kick Drum -> Rear Center (Drums) -> Mix 1
- Ch 2 Snare Drum -> Rear Center (Drums) -> Mix 1
- Ch 3 Overhead -> Rear Center (Drums) -> Mix 1
- Ch 4 Bass -> Stage Left -> Mix 1 / Mix 2
- Ch 5 Guitar -> Center Front -> Mix 2
- Ch 6 Keyboard L -> Stage Left -> Mix 2 / Mix 3
- Ch 7 Keyboard R or Backing Vocal -> Stage Left -> Mix 2 / Mix 3
- Ch 8 Violin -> Stage Right -> Mix 2
- Ch 9 Sax -> Stage Right -> Mix 2 (compression required)

#### Technical Notes

- Minimum stage console capacity: 8 channels with enough aux sends for monitor
	distribution; 9 channels preferred to keep all listed inputs discrete.
- Use active DI for Bass, Keys, Violin, and Sax where possible.
- Guitar and Bass can use DI or amplifier miking based on venue inventory.
- Monitor system must include anti-feedback control.
- Target system output remains at least 100 dB SPL.

#### Scope Note

This section defines canonical stage-plot content for technical coordination.
UI placement in the promotional React page is intentionally deferred and tracked
by architecture decisions under `docs/decisions/`.

## Hospitality Rider

`TBD` — catering, dressing room, and accommodation requirements.

## Booking & Logistics

`TBD` — booking contacts, fees, load-in/load-out, and scheduling details.

## Downloads

`TBD` — downloadable assets (PDF rider, stage plot, hi-res photos).


