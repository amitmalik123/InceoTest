"""
Test module for TMS.feature BDD scenarios
"""

from pytest_bdd import scenarios

from tests.bdd.steps.common_steps import *  # noqa
from tests.bdd.steps.login_steps import *  # noqa
from tests.bdd.steps.navigation_steps import *  # noqa
from tests.bdd.steps.TMSstep import *  # noqa

# Load all scenarios from the feature file
scenarios("../features/TMS.feature")
