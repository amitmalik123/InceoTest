"""
Test module for RGL.feature BDD scenarios
"""

from pytest_bdd import scenarios

from tests.bdd.steps.PR.common_steps import *  # noqa
from tests.bdd.steps.PR.login_steps import *  # noqa
from tests.bdd.steps.PR.navigation_steps import *  # noqa
from tests.bdd.steps.PR.RGLstep import *  # noqa

# Load all scenarios from the feature file
scenarios("../../features/PR/RGL.feature")
