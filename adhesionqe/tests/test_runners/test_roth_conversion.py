"""
BDD Test runner for Roth Conversion feature
"""

from pytest_bdd import scenarios

# Import all step definitions
from tests.steps.account_steps import *  # noqa
from tests.steps.account_wizard_steps import *  # noqa
from tests.steps.api_steps import *  # noqa
from tests.steps.common_steps import *  # noqa
from tests.steps.database_steps import *  # noqa
from tests.steps.login_steps import *  # noqa
from tests.steps.manage_instruction_steps import *  # noqa
from tests.steps.navigation_steps import *  # noqa
from tests.steps.roth_conversion_steps import *  # noqa
from tests.steps.tracking_center_steps import *  # noqa

# Load all scenarios from roth_conversion.feature
scenarios("../features/roth_conversion.feature")
