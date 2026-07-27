"""Factory for creating AI provider instances by name."""

import logging
import os
from typing import Literal, Optional

from .base import AIProvider
from .deepseek import DeepseekClient
from .codemie import CodemieClient

logger = logging.getLogger(__name__)

ProviderName = Literal["deepseek", "codemie"]

_DEFAULT_PROVIDER: ProviderName = "deepseek"


def create_provider(
    name: Optional[str] = None,
) -> AIProvider:
    """Create and return an AI provider instance.

    The provider is selected by:
    1. The ``name`` argument (if supplied)
    2. The ``AI_PROVIDER`` environment variable
    3. Default: ``deepseek``

    Args:
        name: Provider name — "deepseek" or "codemie"

    Returns:
        Configured AIProvider instance (credentials loaded from env)

    Raises:
        ValueError: If an unknown provider name is given
    """
    provider_name: str = name or os.getenv("AI_PROVIDER", _DEFAULT_PROVIDER)
    logger.debug(f"Creating AI provider: {provider_name}")

    if provider_name == "deepseek":
        logger.info("Using Deepseek AI provider")
        return DeepseekClient()
    elif provider_name == "codemie":
        logger.info("Using Codemie AI provider")
        return CodemieClient()
    else:
        logger.error(f"Unknown AI provider: {provider_name}")
        raise ValueError(
            f"Unknown AI provider '{provider_name}'. "
            f"Valid options: 'deepseek', 'codemie'."
        )
