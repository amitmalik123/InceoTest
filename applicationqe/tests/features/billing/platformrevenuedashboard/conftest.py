"""
Revenue Dashboard — conftest.py

All tests under tests/features/billing/platformrevenuedashboard/ inherit these fixtures
and step definitions. This is the shared common layer for ALL Revenue Dashboard
sub-modules (SGM, and any future sub-folders).

Fixtures provided (auto-discovered by pytest):
  - revenue_dashboard_subfolder   — override in sub-module conftest to name the folder
  - settings_data                 — loads base_url / credentials from YAML + env vars
  - page                          — Playwright Page (sync, chromium)
  - login_page                    — LoginPage page-object
  - navigation_page               — NavigationPage page-object
  - logged_in_page                — already-authenticated Page

Step definitions re-exported (auto-discovered by pytest-bdd):
  - Given the user is logged into the application
  - And  the user verifies login is successful
  - When the user navigates to Strategist Group Model
  - When the user verifies Strategist Group Model page is loaded
  - When the user clicks the Family tab
  - When the user submits the form
  - When the user confirms the submission
  - Then the user logs out
"""

import sys
from pathlib import Path

# ── Make sure applicationqe/ root is always on sys.path ──────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[4]  # applicationqe/
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ── Re-export all fixtures + step definitions from the shared common module ───
# Use import * so that pytestbdd_stepdef_* fixture names (which contain spaces)
# are also added to conftest's namespace and discovered by pytest-bdd.
from tests.steps.billing.platformrevenuedashboard.revenue_dashboard_common_steps import *  # noqa: F401,F403

# ── BDD lifecycle hooks — registered once here for all Revenue Dashboard tests ─
from fixtures.billing_fixture import (  # noqa: F401
    pytest_bdd_before_scenario,
    pytest_bdd_after_scenario,
    pytest_bdd_before_step,
    pytest_bdd_after_step,
    pytest_bdd_step_error,
)
