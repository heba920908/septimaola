"""Non-live tests for band_context.py (no LLM calls, no token cost)."""

from septima_automation.ai.band_context import (
    BAND_CONTEXT_SUMMARY,
    BAND_FACTS,
    BAND_FACTS_TOOL,
    SEPTIMA_OLA_MARKERS,
    get_band_facts,
    is_septima_ola,
)


class TestBandFacts:
    def test_all_topics_have_non_empty_facts(self):
        assert BAND_FACTS, "BAND_FACTS should not be empty"
        for topic, text in BAND_FACTS.items():
            assert isinstance(text, str) and text.strip(), (
                f"Fact for topic {topic!r} should be a non-empty string"
            )

    def test_get_band_facts_returns_known_topic(self):
        for topic in BAND_FACTS:
            assert get_band_facts(topic) == BAND_FACTS[topic]

    def test_get_band_facts_no_topic_returns_all(self):
        result = get_band_facts(None)
        for text in BAND_FACTS.values():
            assert text in result

    def test_get_band_facts_unknown_topic_does_not_raise(self):
        """A hallucinated tool argument must not break the tool loop."""
        result = get_band_facts("not_a_real_topic")
        assert isinstance(result, str) and result
        for text in BAND_FACTS.values():
            assert text in result

    def test_band_context_summary_is_non_empty(self):
        assert isinstance(BAND_CONTEXT_SUMMARY, str) and BAND_CONTEXT_SUMMARY.strip()


class TestBandFactsTool:
    def test_tool_schema_shape(self):
        assert BAND_FACTS_TOOL["type"] == "function"
        fn = BAND_FACTS_TOOL["function"]
        assert fn["name"] == "get_septima_ola_facts"
        assert isinstance(fn["description"], str) and fn["description"]

        params = fn["parameters"]
        assert params["type"] == "object"
        topic_schema = params["properties"]["topic"]
        assert topic_schema["type"] == "string"
        assert set(topic_schema["enum"]) == set(BAND_FACTS.keys())


class TestIsSeptimaOla:
    def test_matches_exact(self):
        assert is_septima_ola("Septima Ola")

    def test_matches_with_accent(self):
        assert is_septima_ola("Séptima Ola")

    def test_matches_case_insensitive(self):
        assert is_septima_ola("septima ola")
        assert is_septima_ola("SEPTIMA OLA")

    def test_matches_with_surrounding_whitespace(self):
        assert is_septima_ola("  Séptima Ola  ")

    def test_does_not_match_other_artist(self):
        assert not is_septima_ola("Bob Marley")
        assert not is_septima_ola("Septima")


class TestSeptimaOlaMarkers:
    def test_markers_are_non_empty_strings(self):
        assert SEPTIMA_OLA_MARKERS
        for marker in SEPTIMA_OLA_MARKERS:
            assert isinstance(marker, str) and marker

    def test_markers_appear_in_band_facts(self):
        """Every marker should be traceable back to at least one fact,
        otherwise a grounding assertion built on it would be untestable."""
        all_facts = " ".join(BAND_FACTS.values()) + " " + BAND_CONTEXT_SUMMARY
        for marker in SEPTIMA_OLA_MARKERS:
            assert marker in all_facts, (
                f"Marker {marker!r} should appear in BAND_FACTS or BAND_CONTEXT_SUMMARY"
            )
