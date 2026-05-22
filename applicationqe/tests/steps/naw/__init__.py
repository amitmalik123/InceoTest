# src/step_definitions/__init__.py

"""
Step definitions package for BDD tests
Imports all step definition modules to make them discoverable by pytest-bdd
"""

# Import all step definition modules
from .. import common_steps

from ..baw import baw_dashboard_steps, baw_login_steps, naa_coach_steps, search_work_item_steps, shell_process_steps

from . import (
    account_setup_step,
    account_wizard_steps,
    tracking_center_steps,
    view_documents_step,
)

__all__ = [
    "common_steps",
    "account_setup_step",
    "account_wizard_steps",
    "baw_dashboard_steps",
    "baw_login_steps",
    "naa_coach_steps",
    "search_work_item_steps",
    "shell_process_steps",
    "tracking_center_steps",
    "view_documents_step",
]
