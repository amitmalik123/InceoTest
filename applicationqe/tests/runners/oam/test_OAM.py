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

# Financial Advisor (FA) Feature Files
scenarios("../../features/oam/OAM_FA_OnlineSubmit.feature")
scenarios("../../features/oam/OAM_FA_CompletePrint.feature")
scenarios("../../features/oam/OAM_FA_FinishLater.feature")

# Operations & Admin (OA) Feature Files
scenarios("../../features/oam/OAM_OA_CompleteAndPrint.feature")

# Self-Service Users (SAU) Feature Files
scenarios("../../features/oam/OAM_SAU_OnlineSubmit_SignerNotRequired.feature")
scenarios("../../features/oam/OAM_SAU_OnlineSubmit_AuthSignRequriedFA.feature")
scenarios("../../features/oam/OAM_SAU_OnlineSubmit_AuthSignRequriedSAU.feature")
scenarios("../../features/oam/OAM_SAU_CompleteAndPrint.feature")
scenarios("../../features/oam/OAM_SAU_OneInperson.feature")
scenarios("../../features/oam/OAM_SAU_BlueBanner.feature")
scenarios("../../features/oam/OAM_SAU_Prod_OnlineSubmit_AUthSignerFA.feature")
