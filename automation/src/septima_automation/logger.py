"""Logging configuration for Séptima Ola automation."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "septima_automation",
    level: int = logging.INFO,
    verbose: bool = False,
) -> logging.Logger:
    """Configure and return a logger for the automation system.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (INFO, DEBUG, etc.)
        verbose: If True, set to DEBUG level for detailed output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Set level
    log_level = logging.DEBUG if verbose else level
    logger.setLevel(log_level)

    # Create console handler with timestamp and level
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create formatter: [LEVEL] [TIME] message
    formatter = logging.Formatter(
        fmt="[%(levelname)-8s] %(asctime)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance. If already configured, returns existing logger.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name or "septima_automation")
