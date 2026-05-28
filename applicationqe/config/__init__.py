"""Configuration package.

Usage:
    from config.settings import get_settings
    settings = get_settings()
"""

from config.settings import Settings, get_settings  # noqa: F401

__all__ = [
    "Settings",
    "get_settings",
]
