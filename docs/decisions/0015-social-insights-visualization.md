# ADR-0015: Social insights visualization and native AI analyzer

## Status

Accepted

## Context

Following ADR-0014, the `automation/` package can retrieve Facebook Page and Instagram professional account metrics (`social-metrics.json` and `posts-metrics.json`). However, both files are `.gitignored` to avoid repository bloat and permission/token churn. 

We need a way to visualize these insights on the web press kit (`react/`) without requiring live Graph API calls on every CI job. Furthermore, we want to correlate social media traction with Séptima Ola's event agenda (concerts, showcases, radio appearances), identify high-impact post patterns (e.g., reels vs. flyers, collaborative tagging), and generate actionable strategic recommendations.

## Decision

- **Committed Static Dataset (`react/src/data/insights-data.json`)**:
  - The raw metrics files (`social-metrics.json`, `posts-metrics.json`) remain `.gitignored`.
  - A processed, consolidated visualization document (`insights-data.json`) is **committed to git**.
  - This ensures `react/` builds offline and reliably in CI without network dependencies or missing file errors.
- **Native Python AI Analyzer (`septima_automation.ai.insights_analyzer`)**:
  - Embedded directly into `uv run insights-report` (with an optional `--no-ai` flag).
  - Strongly-typed agenda representation: replaces the raw markdown table in `.claude/skills/septimaola-common/agenda.md` with a structured Pydantic model (`AgendaEvent`) and static dataset (`AGENDA_2026`) in `automation/src/septima_automation/ai/agenda.py`.
  - Correlates post metrics with agenda dates within a $[-2, +3]$ day window around events.
  - When AI credentials (`DEEPSEEK_API_KEY` or `CODEMIE_*`) are present, invokes `AIProvider` to synthesize key patterns and strategic recommendations in Mexican Spanish.
  - Degrades gracefully to heuristic rule-based summaries if AI credentials are absent or fail, guaranteeing `insights-data.json` is always successfully built.
- **Standalone React Page Surface (`#/social-insights`)**:
  - Implemented under `react/src/components/insights/` and routed via `App.jsx` at `#/social-insights` (linked from the footer), following the architectural pattern of `PressKit.jsx` and `PrivacyNotice.jsx`.
  - Features:
    - **KPI Cards**: Total followers, reach, views, and average interactions.
    - **Time-Series Chart**: Dependency-free responsive SVG graph showing follower trajectory and interaction spikes.
    - **Agenda vs Social Impact Correlation**: Concert timeline with matching post count and engagement impact.
    - **Top Posts & Format Patterns**: High-impact post cards with badges (`#Reel`, `#Colaboración`, `#EnVivo`).
    - **AI Strategic Recommendations**: Takeaways organized by *Contenido*, *Timing*, and *Colaboraciones*.

## Consequences

- **Positive**: React press kit builds completely offline in CI without requiring Graph API access or custom build hooks.
- **Positive**: Direct integration into `uv run insights-report` allows a single command to fetch data, correlate events, run AI analysis, and produce the frontend JSON artifact.
- **Positive**: Strongly-typed `AgendaEvent` replaces error-prone markdown text parsing.
- **Positive**: Fault-tolerant execution guarantees output even without AI API keys.
- **Neutral**: Updating the agenda requires maintaining `automation/src/septima_automation/ai/agenda.py`.
