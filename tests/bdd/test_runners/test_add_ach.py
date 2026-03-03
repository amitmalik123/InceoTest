"""
Test module for Add ACH E2E flow using BDD approach
"""

from pytest_bdd import scenarios

# Import all step definitions from individual step modules
from tests.bdd.steps.account_steps import *  # noqa: F401, F403
from tests.bdd.steps.account_wizard_steps import *  # noqa: F401, F403
from tests.bdd.steps.api_steps import *  # noqa: F401, F403
from tests.bdd.steps.common_steps import *  # noqa: F401, F403
from tests.bdd.steps.data_steps import *  # noqa: F401, F403
from tests.bdd.steps.database_steps import *  # noqa: F401, F403
from tests.bdd.steps.login_steps import *  # noqa: F401, F403
from tests.bdd.steps.manage_instruction_steps import *  # noqa: F401, F403
from tests.bdd.steps.navigation_steps import *  # noqa: F401, F403
from tests.bdd.steps.tracking_center_steps import *  # noqa: F401, F403

# Load all scenarios from the feature file
scenarios("../features/add_ACH.feature")
