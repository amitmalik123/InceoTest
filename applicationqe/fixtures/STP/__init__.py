"""
Fixtures Module

This module consolidates all test fixtures and makes them discoverable by pytest.
All fixtures are re-exported from their specialized modules for easy importing.
"""

# Import all fixtures from specialized modules
from .api_fixtures import *  # noqa: F401, F403
from .assertion_fixtures import *  # noqa: F401, F403
from .auth_fixtures import *  # noqa: F401, F403
from .browser_fixtures import *  # noqa: F401, F403
from .data_fixtures import *  # noqa: F401, F403
from .db_fixtures import *  # noqa: F401, F403
from .hooks_fixtures import *  # noqa: F401, F403
from .page_fixtures import *  # noqa: F401, F403
