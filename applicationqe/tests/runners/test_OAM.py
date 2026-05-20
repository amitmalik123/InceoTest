"""
Test module for E2E OAM flow using BDD approach
"""

import pytest
from pytest_bdd import scenarios

# Import fixtures FIRST (before step definitions)
from fixtures.data_fixtures import test_data_manager  # noqa: F401
from tests.conftest import *  # noqa: F401,F403  - Import all page fixtures

# Import step definitions from modular files
# These must be imported BEFORE loading scenarios
from tests.steps.oam.account_steps import *  # noqa: F401,F403
from tests.steps.oam.account_wizard_steps import *  # noqa: F401,F403
from tests.steps.oam.api_steps import *  # noqa: F401,F403
from tests.steps.oam.client_accounts_steps import *  # noqa: F401,F403
from tests.steps.oam.common_steps import *  # noqa: F401,F403
from tests.steps.oam.database_steps import *  # noqa: F401,F403
from tests.steps.oam.docusign_steps import *  # noqa: F401,F403
from tests.steps.oam.login_steps import *  # noqa: F401,F403
from tests.steps.oam.manage_instruction_steps import *  # noqa: F401,F403
from tests.steps.oam.navigation_steps import *  # noqa: F401,F403
from tests.steps.oam.outlook_steps import *  # noqa: F401,F403
from tests.steps.oam.roth_conversion_steps import *  # noqa: F401,F403
from tests.steps.oam.tracking_center_steps import *  # noqa: F401,F403
from tests.steps.oam.item_detail_steps import *  # noqa: F401,F403


# Load all scenarios from the feature files
# Pytest tags from feature files (@smoke, @regression, @FA_Client_Signature, etc) are automatically available
# Use -m flag to filter by tags: pytest tests/runners/oam/test_OAM.py -m FA_Client_Signature
scenarios("../../features/oam/OAM_FA.feature")
scenarios("../../features/oam/OAM_OA.feature")
scenarios("../../features/oam/OAM_SAU.feature")