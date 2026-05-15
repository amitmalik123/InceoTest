"""
Test module for E2E OAM flow using BDD approach
"""

import pytest
from pytest_bdd import scenarios

# Import fixtures FIRST (before step definitions)
from fixtures.data_fixtures import test_data_manager  # noqa: F401
from tests.bdd.conftest import *  # noqa: F401,F403  - Import all page fixtures

# Import step definitions from modular files
# These must be imported BEFORE loading scenarios
from tests.steps.account_steps import *  # noqa: F401,F403
from tests.steps.account_wizard_steps import *  # noqa: F401,F403
from tests.steps.api_steps import *  # noqa: F401,F403
from tests.steps.client_accounts_steps import *  # noqa: F401,F403
from tests.steps.common_steps import *  # noqa: F401,F403
from tests.steps.database_steps import *  # noqa: F401,F403
from tests.steps.docusign_steps import *  # noqa: F401,F403
from tests.steps.login_steps import *  # noqa: F401,F403
from tests.steps.manage_instruction_steps import *  # noqa: F401,F403
from tests.steps.navigation_steps import *  # noqa: F401,F403
from tests.steps.outlook_steps import *  # noqa: F401,F403
from tests.steps.roth_conversion_steps import *  # noqa: F401,F403
from tests.steps.tracking_center_steps import *  # noqa: F401,F403
from tests.steps.item_detail_steps import *  # noqa: F401,F403


# Load all scenarios from the feature files
# Pytest tags from feature files (@smoke, @regression, @FA_Client_Signature, etc) are automatically available
# Use -m flag to filter by tags: pytest tests/bdd/test_runners/test_OAM.py -m FA_Client_Signature
scenarios("../features/oam/OAM_FA.feature")
scenarios("../features/oam/OAM_OA.feature")
scenarios("../features/oam/OAM_SAU.feature")