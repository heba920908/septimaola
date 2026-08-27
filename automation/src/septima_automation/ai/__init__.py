"""AI provider package for Séptima Ola automation."""

from .base import AIProvider
from .deepseek import DeepseekClient
from .codemie import CodemieClient
from .factory import create_provider, ProviderName
from .agenda import AgendaEvent, AGENDA_2026
from .insights_analyzer import (
    run_insights_analysis,
    InsightsDataDocument,
    MetricKPIs,
    TimeSeriesPoint,
    TopPostItem,
    AgendaCorrelationItem,
    AIAnalysisSummary,
    AIRecommendation,
)

__all__ = [
    "AIProvider",
    "DeepseekClient",
    "CodemieClient",
    "create_provider",
    "ProviderName",
    "AgendaEvent",
    "AGENDA_2026",
    "run_insights_analysis",
    "InsightsDataDocument",
    "MetricKPIs",
    "TimeSeriesPoint",
    "TopPostItem",
    "AgendaCorrelationItem",
    "AIAnalysisSummary",
    "AIRecommendation",
]
