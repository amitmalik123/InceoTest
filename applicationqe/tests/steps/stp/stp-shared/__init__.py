"""
Step definitions package for BDD tests
Imports all step definition modules to make them discoverable by pytest-bdd
"""

from . import (
    account_steps,
    account_wizard_steps,
    api_steps,
    cancel_aip_steps,
    common_steps,
    database_steps,
    dmtaddresschangeconfirmationstep,
    dmtool_steps,
    item_details_steps,
    login_steps,
    manage_instruction_steps,
    mimo_summary_confirmation_steps,
    mimo_transaction_steps,
    navigation_steps,
    print_preview_steps,
    roth_conversion_steps,
    tracking_center_steps,
    swp_transaction_steps,
    swp_confirmation_steps,
)

__all__ = [
    "account_steps",
    "account_wizard_steps",
    "api_steps",
    "cancel_aip_steps",
    "common_steps",
    "database_steps",
    "dmtaddresschangeconfirmationstep",
    "dmtool_steps",
    "item_details_steps",
    "login_steps",
    "manage_instruction_steps",
    "mimo_summary_confirmation_steps",
    "mimo_transaction_steps",
    "navigation_steps",
    "print_preview_steps",
    "roth_conversion_steps",
    "tracking_center_steps",
    "swp_transaction_steps",
    "swp_confirmation_steps",
]
# Import all step definition modules and their functions
from .account_steps import *  # noqa: F401, F403
from .account_wizard_steps import *  # noqa: F401, F403
from .api_steps import *  # noqa: F401, F403
from .common_steps import *  # noqa: F401, F403
from .database_steps import *  # noqa: F401, F403
from .login_steps import *  # noqa: F401, F403
from .manage_instruction_steps import *  # noqa: F401, F403
from .navigation_steps import *  # noqa: F401, F403
from .roth_conversion_steps import *  # noqa: F401, F403
from .tracking_center_steps import *  # noqa: F401, F403
