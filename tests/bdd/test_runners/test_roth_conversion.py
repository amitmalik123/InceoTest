"""
BDD Test runner for Roth Conversion feature
"""

from pytest_bdd import scenarios

# Import all step definitions
from tests.bdd.steps.account_steps import *  # noqa
from tests.bdd.steps.account_wizard_steps import *  # noqa
from tests.bdd.steps.api_steps import *  # noqa
from tests.bdd.steps.common_steps import *  # noqa
from tests.bdd.steps.database_steps import *  # noqa
from tests.bdd.steps.login_steps import *  # noqa
from tests.bdd.steps.manage_instruction_steps import *  # noqa
from tests.bdd.steps.navigation_steps import *  # noqa
from tests.bdd.steps.roth_conversion_steps import *  # noqa
from tests.bdd.steps.tracking_center_steps import *  # noqa

# Load all scenarios from roth_conversion.feature
scenarios("../features/roth_conversion.feature")
