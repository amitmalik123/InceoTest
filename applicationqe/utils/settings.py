"""
Backward-compatible shim — all imports from utils.settings are forwarded
to config.settings (the canonical implementation).

New code should import directly from config.settings:
    from config.settings import get_settings
    settings = get_settings()

Existing imports continue to work unchanged:
    from utils.settings import settings          # module-level singleton
    from utils.settings import Settings          # compat class
    Settings(env='test11')                       # env kwarg silently ignored,
                                                 # returns the singleton
"""
from config.settings import get_settings  # noqa: F401


class Settings:
    """
    Backward-compat facade accepting the legacy ``env`` kwarg.
    The active environment is determined by TEST_CONFIG_PATH; the ``env``
    parameter is silently ignored so existing call-sites continue to work.
    """
    def __new__(cls, env=None):
        return get_settings()


# Matches the old module-level singleton
settings = get_settings()

__all__ = ["Settings", "settings", "get_settings"]
