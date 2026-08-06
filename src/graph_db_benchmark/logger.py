"""
Structured logging module for graph database benchmark.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "graph_db_benchmark", level: str = "INFO") -> logging.Logger:
    """
    Configures and returns a logger instance with formatted console output.

    Args:
        name: Name of logger instance.
        level: String representation of log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
