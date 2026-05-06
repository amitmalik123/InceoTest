

import logging
import os
from typing import Optional
from dotenv import load_dotenv
try:
    from concurrent_log_handler import ConcurrentRotatingFileHandler
    _use_concurrent = True
except ImportError:
    from logging.handlers import RotatingFileHandler
    _use_concurrent = False

load_dotenv()
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

def get_logger(name: Optional[str] = None, level: Optional[int] = None, log_dir: Optional[str] = None) -> logging.Logger:
    """
    Creates and returns a configured logger instance.

    Parameters:
    - name: Optional name of the logger.
    - level: Logging level (default: LOG_LEVEL from .env).
    - log_dir: Directory to store log files (default: ../logs).

    Returns:
    - Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate configuration
    if getattr(logger, '_is_configured', False):
        return logger

    effective_level = level if level is not None else LOG_LEVEL
    logger.setLevel(effective_level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (optional, controlled by .env)
    log_to_console = os.getenv("LOG_TO_CONSOLE", "false").lower() == "true"
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(effective_level)
        logger.addHandler(console_handler)

    # File handler with rotation
    resolved_log_dir = log_dir or os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(resolved_log_dir, exist_ok=True)
    log_file_path = os.path.join(resolved_log_dir, 'framework.log')

    try:
        if _use_concurrent:
            file_handler = ConcurrentRotatingFileHandler(
                log_file_path,
                maxBytes=5_000_000,  # 5 MB
                backupCount=3,       # Keep 3 backups
                delay=True           # Delay opening the file until first write
            )
        else:
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=5_000_000,  # 5 MB
                backupCount=3,       # Keep 3 backups
                delay=True           # Delay opening the file until first write
            )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(effective_level)
        logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        # If file rotation fails, fall back to basic file handler
        try:
            basic_handler = logging.FileHandler(log_file_path, mode='a')
            basic_handler.setFormatter(formatter)
            basic_handler.setLevel(effective_level)
            logger.addHandler(basic_handler)
        except Exception:
            # If all file logging fails, at least log to console
            if not log_to_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                console_handler.setLevel(effective_level)
                logger.addHandler(console_handler)

    # Mark as configured
    logger._is_configured = True
    return logger
