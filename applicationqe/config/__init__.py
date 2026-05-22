"""Configuration package - re-exports from config.oam for backward compatibility.

This module provides backward-compatible imports for all code that references
the old 'config' path structure. All actual implementations are in config.oam.

Usage (all equivalent):
    from config.settings import settings
    from config.settings import get_settings
    from config.api_endpoints import APIEndpoints
"""

# Re-export from config.oam for backward compatibility
from config.oam.api_endpoints import APIEndpoints
from config.oam.settings import Settings, get_settings, settings  # noqa: F401

__all__ = [
    "APIEndpoints",
    "Settings",
    "get_settings",
    "settings",
]
