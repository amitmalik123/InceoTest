"""
Centralized logging configuration for the test framework.
"""

import logging
import sys


def setup_logger(name=__name__, level=logging.INFO):
    """
    Set up and return a logger with consistent formatting.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(level)

        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Format: timestamp - logger_name - level - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


# Alias for backward compatibility
def get_logger(name=__name__, level=logging.INFO):
    """
    Get a logger instance (alias for setup_logger).

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name, level)


# Create a default logger for the framework
default_logger = setup_logger("test_framework")
