# AGENTS.md

This file provides cross-agent instructions for GitHub Copilot and other coding
agents working in this repository.

## Scope

Use this file for agent workflow and operational behavior.
Use `CLAUDE.md` for repository architecture and implementation context.

## Mandatory Skill For Press-Kit Content Updates

When a prompt requests updates to band information used by the press kit,
activate and follow:

- `.claude/skills/septimaola-common/SKILL.md`

Applies to updates related to:

- Band description and narrative
- Member/crew profile information
- Technical rider requirements
- Input list/channel mapping
- Text that will be consumed by `react/` and/or `latex/`

## Golden Language Rule

When updating public-facing artifacts (`react/` and `latex/`), default to
Spanish because the primary audience is in Mexico.

English is allowed for AI-rig/internal guidance artifacts, such as:

- `CLAUDE.md`
- `AGENTS.md`
- `.copilot` prompts/instructions
- `.claude` skills and operational docs

## Update Workflow

1. Determine target output: `react/`, `latex/`, or both.
2. Use canonical facts from the shared skill.
3. Adapt copy style by medium:
   - React: concise, scannable, section-friendly.
   - LaTeX: editorial, publication-ready.
   - Language: Spanish for `react/` and `latex/` unless explicitly requested
     otherwise.
4. Preserve technical semantics in rider/input list.
5. If both outputs are requested, keep key facts synchronized.
6. If operating guidance changes, update both `CLAUDE.md` and `AGENTS.md` in
   the same pass.

## Source Of Truth Priority

When data overlaps, prefer this order:

1. `about/*.md` for member bio facts
2. `.claude/skills/septimaola-common/SKILL.md` for shared press-kit copy and
   technical rider data
3. Existing target file wording (`react/` or `latex/`) only as formatting
   reference

## Guardrails

- Do not invent missing facts; keep unknowns as `TBD`.
- Keep React and LaTeX content consistent on names, roles, and technical data.
- Do not perform broad rewrites outside the requested sections.
- When canonical band-profile facts change, manually synchronize the band-only
  facts in `automation/src/septima_automation/ai/band_context.py`; exclude
  member and crew facts from that automation context.
