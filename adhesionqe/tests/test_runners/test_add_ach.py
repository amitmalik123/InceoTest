"""
Test module for Add ACH E2E flow using BDD approach
"""

from pytest_bdd import scenarios

# Import all step definitions from individual step modules
from tests.steps.account_steps import *  # noqa: F401, F403
from tests.steps.account_wizard_steps import *  # noqa: F401, F403
from tests.steps.api_steps import *  # noqa: F401, F403
from tests.steps.common_steps import *  # noqa: F401, F403
from tests.steps.data_steps import *  # noqa: F401, F403
from tests.steps.database_steps import *  # noqa: F401, F403
from tests.steps.login_steps import *  # noqa: F401, F403
from tests.steps.manage_instruction_steps import *  # noqa: F401, F403
from tests.steps.navigation_steps import *  # noqa: F401, F403
from tests.steps.tracking_center_steps import *  # noqa: F401, F403

# Load all scenarios from the feature file
scenarios("../features/add_ACH.feature")
