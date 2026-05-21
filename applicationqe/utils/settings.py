"""Backward-compatibility shim — settings now live in config/settings.py.

All existing imports continue to work without modification:

    from utils.settings import settings      # lazy singleton
    from utils.settings import Settings      # class
    from utils.settings import get_settings  # factory function

New code should import directly from config.settings.
"""
from config.settings import Settings, get_settings  # noqa: F401

__all__ = ["Settings", "settings", "get_settings"]


def __getattr__(name: str):
    """Forward the 'settings' lazy singleton to config.settings."""
    if name == "settings":
        return get_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
