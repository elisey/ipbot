"""Console logging configuration for the IP bot."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure console logging with structured format.

    Args:
        level: Logging level (default: logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
