"""Tests for the social insights analyzer and agenda correlation engine."""

from datetime import date
import pytest

from septima_automation.ai.agenda import AgendaEvent
from septima_automation.ai.insights_analyzer import (
    correlate_posts_with_agenda,
    detect_post_patterns,
    rank_top_posts,
    build_time_series_points,
    run_insights_analysis,
    MetricKPIs,
)
from septima_automation.social.insights import (
    FacebookAccountSnapshot,
    InstagramAccountSnapshot,
    PostMetric,
    PostsMetricsReport,
    SocialMetricsSnapshot,
)


def test_detect_post_patterns():
    # Reel / Video
    patterns_reel = detect_post_patterns("¡Música!", "VIDEO", "https://instagram.com/reel/123")
    assert "Reel / Video" in patterns_reel

    # Collab / Live / Agenda
    patterns_collab = detect_post_patterns(
        "Nos vemos en vivo en cabina de FIV Radio con Colectivo Latino Oficial",
        "IMAGE",
        "https://facebook.com/post/456",
    )
    assert "Imagen / Arte" in patterns_collab
    assert "Colaboración / Medios" in patterns_collab
    assert "En Vivo / Cabina" in patterns_collab
    assert "Convocatoria a Evento" in patterns_collab


def test_correlate_posts_with_agenda():
    events = [
        AgendaEvent(
            date="2026-08-20",
            title="Live en Rock Titanio",
            venue="Titanio Records",
            event_type="Foro",
        ),
        AgendaEvent(
            date="2026-06-13",
            title="Acústico en FIV",
            venue="Faro IV",
            event_type="Cultural",
        ),
    ]

    posts = [
        (
            "facebook",
            PostMetric(
                id="p1",
                timestamp="2026-08-21T10:00:00+00:00",
                caption="Gracias a Rock Titanio por invitarnos",
                like_count=10,
                comments_count=2,
                reach=150,
                views=300,
                total_interactions=15,
            ),
        ),
        (
            "instagram",
            PostMetric(
                id="p2",
                timestamp="2026-08-19T18:00:00+00:00",
                caption="Mañana en vivo en Titanio TV",
                like_count=25,
                comments_count=5,
                reach=400,
                views=900,
                total_interactions=50,
            ),
        ),
        (
            "facebook",
            PostMetric(
                id="p3",
                timestamp="2026-01-01T00:00:00+00:00",
                caption="Unrelated post",
                like_count=1,
            ),
        ),
    ]

    correlations = correlate_posts_with_agenda(posts, events)
    assert len(correlations) == 2

    titanio_corr = next(c for c in correlations if c.event_title == "Live en Rock Titanio")
    assert titanio_corr.correlated_posts_count == 2
    assert titanio_corr.total_reach == 550
    assert titanio_corr.total_views == 1200
    assert titanio_corr.total_interactions == 65
    assert titanio_corr.traction_score == "Alto"
    assert "Rock Titanio" in titanio_corr.highlight_caption or "Titanio TV" in titanio_corr.highlight_caption

    fiv_corr = next(c for c in correlations if c.event_title == "Acústico en FIV")
    assert fiv_corr.correlated_posts_count == 0
    assert fiv_corr.traction_score == "Moderado"


def test_rank_top_posts():
    posts = [
        (
            "instagram",
            PostMetric(
                id="p1",
                caption="Post 1 low engagement",
                like_count=2,
                reach=50,
                views=100,
                total_interactions=2,
            ),
        ),
        (
            "instagram",
            PostMetric(
                id="p2",
                caption="Post 2 high engagement",
                like_count=40,
                reach=600,
                views=1500,
                total_interactions=70,
            ),
        ),
    ]

    ranked = rank_top_posts(posts, limit=1)
    assert len(ranked) == 1
    assert ranked[0].id == "p2"
    assert ranked[0].views == 1500


def test_build_time_series_points():
    history = [
        SocialMetricsSnapshot(
            generated_at="2026-08-01T10:00:00+00:00",
            facebook=FacebookAccountSnapshot(followers_count=350),
            instagram=InstagramAccountSnapshot(followers_count=240),
        ),
        SocialMetricsSnapshot(
            generated_at="2026-08-20T10:00:00+00:00",
            facebook=FacebookAccountSnapshot(followers_count=358),
            instagram=InstagramAccountSnapshot(followers_count=251),
        ),
    ]

    posts = [
        (
            "instagram",
            PostMetric(
                id="p1",
                timestamp="2026-08-20T12:00:00+00:00",
                views=500,
                reach=200,
                total_interactions=30,
            ),
        )
    ]

    points = build_time_series_points(history, posts)
    assert len(points) >= 2
    last_point = points[-1]
    assert last_point.date == "2026-08-20"
    assert last_point.facebook_followers == 358
    assert last_point.instagram_followers == 251
    assert last_point.views == 500


@pytest.mark.asyncio
async def test_run_insights_analysis_heuristic_fallback():
    snapshot = SocialMetricsSnapshot(
        facebook=FacebookAccountSnapshot(followers_count=358, fan_count=358),
        instagram=InstagramAccountSnapshot(followers_count=251, media_count=117),
    )
    posts_report = PostsMetricsReport(
        since="2026-06-01",
        until="2026-08-27T00:00:00+00:00",
        facebook_posts=[
            PostMetric(
                id="fb1",
                timestamp="2026-08-20T12:00:00+00:00",
                caption="En vivo en Rock Titanio",
                like_count=5,
                comments_count=1,
            )
        ],
        instagram_posts=[
            PostMetric(
                id="ig1",
                timestamp="2026-08-20T14:00:00+00:00",
                caption="Reel en vivo con Colectivo Latino",
                media_type="VIDEO",
                like_count=30,
                reach=400,
                views=1000,
                total_interactions=45,
            )
        ],
    )

    doc = await run_insights_analysis(
        snapshot=snapshot,
        posts_report=posts_report,
        report_history=[snapshot],
        ai_provider=None,
        use_ai=False,
    )

    assert doc.kpis.facebook_followers == 358
    assert doc.kpis.instagram_followers == 251
    assert doc.kpis.total_analyzed_posts == 2
    assert doc.kpis.total_views == 1000
    assert len(doc.top_posts) == 2
    assert len(doc.agenda_correlations) > 0
    assert len(doc.ai_analysis.recommendations) >= 3
    assert "Séptima Ola" in doc.ai_analysis.executive_summary
