"""Canonical Septima Ola band facts, exposed as an LLM function-calling tool.

Source of truth: `.claude/skills/septimaola-common/SKILL.md` (sections
"Canonical Band Profile", "History", "The start of a new wave"). This module
intentionally mirrors only band-level narrative facts — no crew/member bios
and no technical rider data — because those are consulted for content
generation about the band's music, not for stage/production coordination.

Keep this module in sync manually whenever SKILL.md's canonical band profile
changes (see AGENTS.md and .claude/skills/septimaola-common/SKILL.md).
"""

import unicodedata

# Spanish facts, keyed by topic. Values feed both the AI generation prompt
# (via the get_septima_ola_facts tool) and the grader's grounding reference.
BAND_FACTS: dict[str, str] = {
    "perfil": (
        "Septima Ola combina reggae, ska y rocksteady, creando un sonido "
        "distintivo con melodias pegajosas, ritmos bailables y letras "
        "socialmente conscientes sobre el amor, la unidad y la justicia "
        "social."
    ),
    "origen": (
        "La banda tiene su base en La Raza, Ciudad de Mexico, y sigue "
        "evolucionando a traves de presentaciones en vivo energeticas y "
        "canciones sinceras."
    ),
    "historia": (
        "Septima Ola nacio en noviembre de 2025, debutando en el FARO de "
        'Indios Verdes bajo el nombre "The Soul Groove Collective", con '
        "canciones originales y covers que hicieron bailar y cantar al "
        "publico de ese recinto cultural."
    ),
    "mision": (
        "En una epoca donde el mundo parece mas dividido que nunca, "
        "Septima Ola surge como respuesta: sonidos hechos en Mexico para "
        "corazones inquietos que buscan movimiento e inspiracion, una ola "
        "que nace de nuestra tierra y se expande sin limites fusionando "
        "ska, reggae y rocksteady con notas de jazz."
    ),
}

# Compact digest used as a fallback system-message injection when the target
# model does not support tool calling (see CodemieClient/DeepseekClient).
BAND_CONTEXT_SUMMARY: str = (
    "Septima Ola es una banda con base en La Raza, Ciudad de Mexico, que "
    "combina reggae, ska y rocksteady con notas de jazz. Nacio en noviembre "
    'de 2025 y debuto en el FARO de Indios Verdes como "The Soul Groove '
    'Collective". Su musica busca inspirar unidad, movimiento y justicia '
    "social para corazones inquietos hechos en Mexico."
)

# Canonical tokens used by tests to deterministically confirm that generated
# content actually grounds itself in real band facts (as opposed to the
# grader merely believing it did).
SEPTIMA_OLA_MARKERS: tuple[str, ...] = (
    "reggae",
    "ska",
    "rocksteady",
    "La Raza",
    "Ciudad de Mexico",
    "FARO",
)

# OpenAI-compatible function-calling tool schema. Both CodemieClient and
# DeepseekClient may attach this tool so the model can request Septima Ola
# facts before writing grounded copy about the band.
BAND_FACTS_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "get_septima_ola_facts",
        "description": (
            "Devuelve datos canonicos verificados sobre la banda Septima "
            "Ola (perfil musical, origen, historia o mision). Usa esta "
            "herramienta antes de escribir contenido sobre Septima Ola; "
            "nunca inventes datos sobre la banda."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "enum": sorted(BAND_FACTS.keys()),
                    "description": (
                        "Tema especifico a consultar. Si se omite, se "
                        "devuelven todos los datos disponibles."
                    ),
                }
            },
        },
    },
}


def get_band_facts(topic: str | None = None) -> str:
    """Return canonical Septima Ola facts for a topic, or all facts.

    Never raises: an unrecognized topic (e.g. a hallucinated tool argument)
    falls back to returning every known fact plus a note, so a malformed
    tool call cannot break the generation/grading loop.
    """
    if topic and topic in BAND_FACTS:
        return BAND_FACTS[topic]

    all_facts = " ".join(BAND_FACTS.values())
    if topic:
        return (
            f"(Tema '{topic}' no reconocido; se devuelven todos los datos "
            f"disponibles.) {all_facts}"
        )
    return all_facts


def _normalize(text: str) -> str:
    """Fold accents and case for tolerant comparison (e.g. Septima/Séptima)."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.casefold().strip()


def is_septima_ola(artist: str) -> bool:
    """Return True if `artist` refers to Septima Ola, accent/case-insensitive."""
    return _normalize(artist) == _normalize("Septima Ola")
