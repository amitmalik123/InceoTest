"""
Step definitions package for BDD tests
Imports all step definition modules to make them discoverable by pytest-bdd
"""

from . import (
    account_steps,
    account_wizard_steps,
    api_steps,
    common_steps,
    database_steps,
    item_details_steps,
    login_steps,
    navigation_steps,
    outlook_steps,
    print_preview_steps,
    tracking_center_steps,
)

__all__ = [
    "account_steps",
    "account_wizard_steps",
    "api_steps",
    "common_steps",
    "database_steps",
    "item_details_steps",
    "login_steps",
    "navigation_steps",
    "outlook_steps",
    "print_preview_steps",
    "tracking_center_steps",
]
# Import all step definition modules and their functions
from .account_steps import *  # noqa: F401, F403
from .account_wizard_steps import *  # noqa: F401, F403
from .api_steps import *  # noqa: F401, F403
from .common_steps import *  # noqa: F401, F403
from .database_steps import *  # noqa: F401, F403
from .login_steps import *  # noqa: F401, F403
from .navigation_steps import *  # noqa: F401, F403
from .outlook_steps import *  # noqa: F401, F403
from .print_preview_steps import *  # noqa: F401, F403
from .tracking_center_steps import *  # noqa: F401, F403