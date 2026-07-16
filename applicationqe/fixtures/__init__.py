"""
Fixtures Module

This module consolidates all test fixtures and makes them discoverable by pytest.
All fixtures are re-exported from their specialized modules for easy importing.
"""

# Assertion fixtures
from fixtures.assertion_fixtures import *

# Authentication fixtures
from fixtures.auth_fixtures import *

# Browser fixtures
from fixtures.browser_fixtures import *
# Data fixtures
from fixtures.data_fixtures import *

# Database fixtures
from fixtures.db_fixtures import *

# Hooks (pytest-bdd lifecycle — no __all__ entry needed, just imported for side-effects)
from fixtures.hooks_fixtures import *

# Page-object fixtures
from fixtures.page_fixtures import *