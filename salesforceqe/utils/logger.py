"""Centralized logging configuration for the test framework."""

import logging
import sys


def setup_logger(name=__name__, level=logging.INFO):
    """Return a configured logger with consistent formatting."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


default_logger = setup_logger("test_framework")
"""
Centralized logging configuration for the test framework.
"""
import logging
import sys
from pathlib import Path


# def setup_logger(name=__name__, level=logging.INFO):
#     """
#     Set up and return a logger with consistent formatting.
    
#     Args:
#         name: Logger name (typically __name__ from calling module)
#         level: Logging level (default: INFO)
    
#     Returns:
#         logging.Logger: Configured logger instance
#     """
#     logger = logging.getLogger(name)
    
#     # Only configure if not already configured
#     if not logger.handlers:
#         logger.setLevel(level)
        
#         # Console handler with formatting
#         console_handler = logging.StreamHandler(sys.stdout)
#         console_handler.setLevel(level)
        
#         # Format: timestamp - logger_name - level - message
#         formatter = logging.Formatter(
#             '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#             datefmt='%Y-%m-%d %H:%M:%S'
#         )
#         console_handler.setFormatter(formatter)
        
#         logger.addHandler(console_handler)
    
#     return logger


# Create a default logger for the framework
default_logger = setup_logger("test_framework")


class _AllureHandler(logging.Handler):
    """Logging handler that mirrors records into the Allure report as steps."""

    def emit(self, record):
        try:
            import allure  # type: ignore
        except ImportError:
            return
        try:
            message = self.format(record)
            with allure.step(message):
                pass
        except Exception:
            # Never let logging break tests
            pass


def get_allure_logger(name=__name__, level=logging.INFO):
    """
    Return a logger that writes to the console and also attaches log
    records to the Allure report (when allure-pytest is installed).

    Args:
        name: Logger name (typically __name__ from calling module).
        level: Logging level (default: INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = setup_logger(name, level)

    if not any(isinstance(h, _AllureHandler) for h in logger.handlers):
        allure_handler = _AllureHandler()
        allure_handler.setLevel(level)
        allure_handler.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        logger.addHandler(allure_handler)

    return logger
