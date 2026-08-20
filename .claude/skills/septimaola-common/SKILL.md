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
- When canonical band-profile facts change, manually synchronize the band-only
	facts in `automation/src/septima_automation/ai/band_context.py`. Do not add
	member or crew facts to that automation context.

---

# Canonical Band Profile

Septima Ola combines reggae, ska, and rocksteady to create a distinctive sound
with catchy melodies, danceable rhythms, and socially conscious lyrics focused
on love, unity, and social justice.

The band was born from a shared passion for music among members with diverse
influences and experiences. Based in La Raza, Mexico City, Septima Ola keeps
evolving through energetic live performances and heartfelt songs.

## History

Séptima Ola was born in November 2025, making its debut at the FARO de Indios
Verdes under the name "The Soul Groove Collective", with a set of original songs
and covers that had the cultural venue dancing and singing along.

## The start of a new wave

In an era where the world seems more divided than ever, Séptima Ola emerges as
a response: sounds made in Mexico for restless hearts seeking movement and
inspiration. Come, be part of a wave born from our land and expanding without
limits in a fusion of Ska, Reggae, and Rocksteady rhythms with notes and sounds
drawn from Jazz.

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
| [Gil](gil.md) | Batería | TBD |
| [Levi'Sax](levi_sax.md) | Sax tenor | TBD |
| [Rodrigo Mera](rodrigo_mera.md) | Violinist and Arranger | TBD |
| [Sandy Robinsuell](sandy_robinsuell.md) | Keyboardist and Backing Vocalist | TBD |
| Itzel Calzada | Sound Engineer | TBD |
| Mirna Mera | Photographer | TBD |

### Former Members and Crew

| Name | Role | Status |
| --- | --- | --- |
| [LeManu](lemanu.md) | Drummer | Former (2025--2026) |
| Rams | Guitarist | Former |

### Audio Requirements

- The show requires a complete Front of House (FOH) mix position and an
	independent stage monitoring area.
- FOH should be placed approximately 20 m from the front of the stage at around
	1 m height for accurate audience-reference mixing.
- The PA system must be professional-grade. No specific brand is mandatory, but
	Electro-Voice, Bose, or JBL are recommended.
- Stage monitoring should include anti-feedback capability.
- Mixing console: minimum 9 input channels (6-member band), with enough aux
	sends for 3 monitor mixes.
- The drum kit requires three input channels: kick (bombo), snare (caja), and
	overhead (mono if channels are limited).
- System output must reach at least 100 dB SPL.
- Guitar and bass require either direct boxes (DI) or monitor amplifiers.
- Violin and sax require direct boxes (DI).
- Sax channel should include compression.

### Input List

| Channel | Instrument | Mic/DI | Aux | Equipment | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Kick (Bombo) | Dynamic mic | Mix 1 (Drums) | Drum mic stand | Required |
| 2 | Snare (Caja) | Dynamic mic | Mix 1 (Drums) | Drum mic stand | Required |
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

#### Preferred On-Stage Placement

- Stage Left (from audience view): Arthur (Bass), Rodrigo Mera (Violin)
- Center: Sandy (Backing Vocal), Gil (Drums) 
- Stage Right: Levi'Sax (Sax), Alfred Herrera (Guitar / Lead Vocal) 

#### Monitor Mix Layout

- Mix 1 (Drums): Kick, Snare, Overhead; bass as needed
	- Primary user: Gil
- Mix 2 (Frontline): Guitar, Violin, Sax, Bass, and selective keys as needed
	- Primary users: Alfred, Rodrigo, Levi'Sax, Arthur
- Mix 3 (Keys/Vocal reference): Keyboard and backing vocal priority
	- Primary user: Sandy

#### Input-to-Position Mapping (Reference)

- Ch 1 Kick (Bombo) -> Center -> Mix 1
- Ch 2 Snare (Caja) -> Center -> Mix 1
- Ch 3 Overhead (Drums) -> Center -> Mix 1
- Ch 4 Bass -> Stage Left -> Mix 1 / Mix 2
- Ch 5 Guitar -> Stage Right -> Mix 2
- Ch 6 Keyboard L -> Center -> Mix 2 / Mix 3
- Ch 7 Keyboard R or Backing Vocal -> Center -> Mix 2 / Mix 3
- Ch 8 Violin -> Stage Left -> Mix 2
- Ch 9 Sax -> Stage Right -> Mix 2 (compression required)

#### Technical Notes

- Minimum stage console capacity: 9 channels with enough aux sends for 3 monitor
	mixes.
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

Canonical operational, financial, and logistical terms for event booking, performance formats, and travel coordination.

### Performance Rates & Show Format

- **Performance Fee:** $3,000 MXN per show hour (tarifa base por hora de presentación).
- **Standard Show Duration:** The regular "Séptima Ola" live set lasts approximately **40 minutes** (repertorio principal de temas originales y fusión reggae/ska/rocksteady).
- **Extended Show Customization:** If the event or venue requires more than one hour (e.g., 60, 90, or 120+ minutes), the band can enhance and extend the performance to fulfill the required duration. Thanks to the musicians' high musical versatility, the extended set can include classic reggae and ska covers as well as popular covers from other genres (rock, pop, latin, jazz) adapted into the band's distinctive style, alongside extended musical arrangements, instrumental solos, and interactive dynamics.

### Geographic Scope & Travel Policy

- **Base Location:** La Raza, Ciudad de México (CDMX).
- **Local Coverage (CDMX & Estado de México):** Base fee applies. Local ground transportation and equipment transfer within Mexico City and the State of Mexico metropolitan area are handled directly by the band.
- **Foráneo / Outside CDMX and Estado de México:** Shows outside CDMX and Estado de México require additional transportation, toll, and travel expenses covered or reimbursed by the promoter/organizer.

### Transportation Benchmark Costs (Market Estimates)

Traveling party size for out-of-town dates consists of **8 people** (6 on-stage musicians + 2 production crew members: Sound Engineer and Photographer), plus full backline, instruments, and hardware.

| Transportation Method | Typical Cost Per Person | Total Estimated Cost (8 Pax + Gear) | Details & Inclusions |
| --- | --- | --- | --- |
| **Private Van / Minibus with Driver** *(Recommended)* | $700 – $1,500 MXN | $5,500 – $12,000 MXN / trip | 13–15+ passenger van (Toyota Hiace / Mercedes Sprinter) accommodating all 8 passengers plus instrument cargo; includes vehicle rental ($3,500–$6,000/day), fuel, highway tolls (casetas), and driver per diem. |
| **Intercity Bus (Autobús de Línea)** | $700 – $1,800 MXN (round trip) | $5,600 – $14,400 MXN (round trip) | Commercial line buses (ADO, Primera Plus, ETN) for regional trips (150–450 km). Requires additional local taxi/cargo transit for drums and heavy gear. |
| **Air Travel (Vuelos Nacionales)** | $1,800 – $4,000 MXN (round trip) | $18,000 – $38,000+ MXN total | Standard domestic airline tickets (Volaris, VivaAerobus, Aeromexico) for long-haul destinations (e.g., Monterrey, Guadalajara, Tijuana, Cancún) plus musical instrument baggage/cargo fees ($1,000–$2,000 MXN per leg). |

#### Additional Travel & Hospitality Considerations (Foráneo)

- **Meals / Per Diem (Viáticos):** $350 – $500 MXN per person per day (~$2,800 – $4,000 MXN total/day for 8 people) when meals are not directly provided by the event catering.
- **Lodging / Accommodation:** 3 to 4 double rooms (or safe group lodging) in close proximity to the venue when schedules require an overnight stay.

### Production Schedule & Stage Timings

- **Load-in & Setup:** 90–120 minutes prior to soundcheck.
- **Soundcheck:** 45–60 minutes prior to venue doors opening.
- **Strike & Load-out:** 30–45 minutes following the conclusion of the performance.

### Booking Contact

- **Email:** `septimaolaoficial@gmail.com`
- **Official Website:** [septimaola.com](https://septimaola.com)
- **Direct Channels:** Social media @septimaolaoficial (Instagram, Facebook, TikTok).

## Downloads

`TBD` — downloadable assets (PDF rider, stage plot, hi-res photos).

## Experience

* [agenda.md](agenda.md) — shows and presentations that were given by septima ola and the expertise

## Songs Inventory

Each song in the repertoire has a fact sheet under `7aola/songs/`. Load the
relevant file when song-specific details (description, lyrics, chords, key,
tempo, time signature, composer, discovery links) are needed for content
generation or press-kit updates.

| Song | File | Composer |
| --- | --- | --- |
| Arenga | [arenga.md](../../7aola/songs/arenga.md) | Levi Sax |
| Desde mi ventana | [desde_mi_ventana.md](../../7aola/songs/desde_mi_ventana.md) | Alfred YearckLei |
| A Contraluz | [a_contraluz.md](../../7aola/songs/a_contraluz.md) | Rodrigo Mera |
| Acelera | [acelera.md](../../7aola/songs/acelera.md) | Robinsuel |
| Despertar | [despertar.md](../../7aola/songs/despertar.md) | TBD |
| TQM | [tqm.md](../../7aola/songs/tqm.md) | Levi Sax |

When the skill is activated for a task that involves songs, load the relevant
song file(s) alongside the canonical band facts in this skill. Prefer song-file
data over `band_context.py` snippets when the two overlap, as the song files
are the authoring surface.

