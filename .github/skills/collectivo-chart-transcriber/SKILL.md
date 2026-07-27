---
name: collectivo-chart-transcriber
description: 'Transcribe Colectivo Latino song sheets from image files into collectivo markdown songs using collectivo/template.md, then update collectivo/README.md index. Use for OCR-style lyric/chord capture, Spanish chart normalization, and index maintenance from CL_*.jpeg screenshots.'
argument-hint: 'Image path(s) to transcribe, e.g. collectivo/.screenshots/CL_Vampiro.jpeg'
user-invocable: true
disable-model-invocation: false
model: GPT-5.3-Codex
---

# Colectivo Chart Transcriber

## Purpose
Convert scanned/photographed Colectivo Latino lyric charts into reusable markdown song files under `collectivo/`, following `collectivo/template.md`, and keep `collectivo/README.md` index synchronized.

## When To Use
Use this skill when a request includes any of these patterns:
- "Transcribe this chart image"
- "Create md from CL_*.jpeg"
- "Use collectivo template"
- "Update README index"
- "Continue with CL_<Song>.jpeg"

Typical inputs:
- `collectivo/.screenshots/CL_AguitaCoco.jpeg`
- `collectivo/.screenshots/CL_LaEstacion.jpeg`
- `collectivo/.screenshots/CL_SalsaCallejera.jpeg`
- `collectivo/.screenshots/CL_SangreLatina.jpeg`
- `collectivo/.screenshots/CL_Vampiro.jpeg`

## Workflow
1. Gather context
- Read `collectivo/template.md` and `collectivo/README.md`.
- Check if target song file already exists in `collectivo/`.
- Open the image and capture visible title, lyrics, section cues, and handwritten tonal annotations.

2. Decide create vs update
- If song file does not exist: create a new markdown file with normalized snake_case name.
- If it exists: update content to improve fidelity to the source image, avoiding duplicate files.

3. Map source into template sections
- Fill:
  - Title
  - Artist/status
  - Quick chord reference (Key, Tempo if known, Rhythm)
  - Chords used (main + secondary if visible)
  - Chord progression map (use section labels from chart when present)
  - Performance notes (band cues, solos, obbligatos, form instructions)
  - References (image source link)
- Preserve uncertain parts as `TBD` rather than inventing facts.

4. Handle ambiguity
- If bars/chord durations are not explicit, keep `{# bars}` placeholders.
- If spelling differs between heading and body, preserve observed source text and note it in performance notes when relevant.
- Prefer literal transcription over harmonic inference.

5. Update index
- Add a single bullet link in `collectivo/README.md` under `## Index` if missing.
- Do not add duplicates.

6. Verify
- Confirm file exists and has Back to Index links.
- Confirm `README.md` includes exactly one entry for the song.
- Confirm references point to the corresponding image in `.screenshots/`.

## Naming Rules
- Output file name: lowercase snake_case based on song title.
- Keep Spanish accents in visible title when clear from source, but file names should stay ASCII-safe.
- Example:
  - `Agüita de Coco` -> `aguita_de_coco.md`
  - `Salsa callejera` -> `salsa_callejera.md`

## Quality Criteria (Definition of Done)
- Song file in `collectivo/` follows template section order.
- Content is faithful to visible source text and cues.
- Uncertain values marked `TBD` (not guessed).
- `collectivo/README.md` index updated once, no duplicates.
- Internal links resolve:
  - `[<- Back to Index](README.md)`
  - screenshot link in References.

## Fast Prompt Examples
- `/collectivo-chart-transcriber collectivo/.screenshots/CL_Vampiro.jpeg`
- `Use collectivo-chart-transcriber on collectivo/.screenshots/CL_SangreLatina.jpeg and update README`
- `Transcribe CL_SalsaCallejera.jpeg with template and keep index synced`

## Guardrails
- Do not fabricate chords, BPM, or missing lines.
- Do not overwrite unrelated song files.
- Keep output in Spanish when source is Spanish.
- Keep markdown simple and consistent with existing `collectivo/*.md` files.
