"""
Test module for RGL.feature BDD scenarios
"""

from pytest_bdd import scenarios

from tests.bdd.steps.PortfolioReporting.common_steps import *  # noqa
from tests.bdd.steps.PortfolioReporting.login_steps import *  # noqa
from tests.bdd.steps.PortfolioReporting.navigation_steps import *  # noqa
from tests.bdd.steps.PortfolioReporting.RGLstep import *  # noqa

# Load all scenarios from the feature file
scenarios("../../features/PortfolioReporting/RGL.feature")
