"""
Test module for TMS.feature BDD scenarios
"""

from pytest_bdd import scenarios

from tests.bdd.steps.PR.common_steps import *  # noqa
from tests.bdd.steps.PR.login_steps import *  # noqa
from tests.bdd.steps.PR.navigation_steps import *  # noqa
from tests.bdd.steps.PR.TMSstep import *  # noqa

# Load all scenarios from the feature file
scenarios("../../features/PR/TMS.feature")
