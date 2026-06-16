"""
Test module for E2E OAM flow using BDD approach.

Dynamically discovers and loads all feature files from tests/features/oam directory,
including subdirectories. This allows new feature files to be added without
modifying this test runner.
"""

import pytest
from pathlib import Path
from pytest_bdd import scenarios

# Import fixtures FIRST (before step definitions)
from fixtures.data_fixtures import test_data_manager  # noqa: F401
from tests.conftest import *  # noqa: F401,F403  - Import all page fixtures

# Import step definitions from modular files
# These must be imported BEFORE loading scenarios
from tests.steps.oam.account_steps import *  # noqa: F401,F403
from tests.steps.oam.account_wizard_steps import *  # noqa: F401,F403
from tests.steps.oam.client_accounts_steps import *  # noqa: F401,F403
from tests.steps.oam.common_steps import *  # noqa: F401,F403
from tests.steps.oam.database_steps import *  # noqa: F401,F403
from tests.steps.oam.docusign_steps import *  # noqa: F401,F403
from tests.steps.oam.login_steps import *  # noqa: F401,F403
from tests.steps.oam.navigation_steps import *  # noqa: F401,F403
from tests.steps.oam.outlook_steps import *  # noqa: F401,F403
from tests.steps.oam.tracking_center_steps import *  # noqa: F401,F403
from tests.steps.oam.item_detail_steps import *  # noqa: F401,F403


# Dynamically load all feature files from tests/features/oam
# Pytest tags from feature files (@smoke, @regression, etc) are automatically available
# Use -m flag to filter by tags: pytest tests/runners/oam/test_OAM.py -m smoke

# Get absolute path to features/oam directory
# __file__ = tests/runners/oam/test_OAM.py
# parent = tests/runners/oam
# parent.parent.parent = tests
features_oam_dir = Path(__file__).parent.parent.parent / "features" / "oam"

# Find all .feature files recursively
feature_files = sorted(features_oam_dir.rglob("*.feature"))

# Load each feature file using absolute paths (works on both Windows and Linux)
for feature_file in feature_files:
    # Use absolute path for maximum pipeline compatibility
    # pytest-bdd scenarios() works with both absolute and relative paths
    scenarios(str(feature_file.absolute()))
