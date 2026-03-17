"""
Test module for E2E OAM flow using BDD approach
"""

import pytest
from pytest_bdd import scenarios

# Import fixtures FIRST (before step definitions)
from tests.fixtures.data_fixtures import test_data_manager  # noqa: F401
from tests.bdd.conftest import *  # noqa: F401,F403  - Import all page fixtures

# Import step definitions from modular files
# These must be imported BEFORE loading scenarios
from tests.bdd.steps.account_steps import *  # noqa: F401,F403
from tests.bdd.steps.account_wizard_steps import *  # noqa: F401,F403
from tests.bdd.steps.api_steps import *  # noqa: F401,F403
from tests.bdd.steps.client_accounts_steps import *  # noqa: F401,F403
from tests.bdd.steps.common_steps import *  # noqa: F401,F403
from tests.bdd.steps.database_steps import *  # noqa: F401,F403
from tests.bdd.steps.docusign_steps import *  # noqa: F401,F403
from tests.bdd.steps.login_steps import *  # noqa: F401,F403
from tests.bdd.steps.manage_instruction_steps import *  # noqa: F401,F403
from tests.bdd.steps.navigation_steps import *  # noqa: F401,F403
from tests.bdd.steps.outlook_steps import *  # noqa: F401,F403
from tests.bdd.steps.roth_conversion_steps import *  # noqa: F401,F403
from tests.bdd.steps.tracking_center_steps import *  # noqa: F401,F403
from tests.bdd.steps.trackingCenter_ItemDetail_steps import *  # noqa: F401,F403


# Load all scenarios from the feature file
# Pytest tags from feature file (@smoke, @regression, @FA_Client_Signature, etc) are automatically available
# Use -m flag to filter by tags: pytest tests/bdd/test_runners/test_OAM.py -m FA_Client_Signature
scenarios("../features/OAM.feature")