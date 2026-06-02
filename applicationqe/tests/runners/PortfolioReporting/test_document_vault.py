"""
Test module for document_vault.feature BDD scenarios
"""

from pytest_bdd import scenarios
from pytest_bdd.exceptions import NoScenariosFound

from tests.steps.PortfolioReporting.common_steps import *  # noqa
from tests.steps.PortfolioReporting.document_vault_steps import *  # noqa
from tests.steps.PortfolioReporting.login_steps import *  # noqa
from tests.steps.PortfolioReporting.navigation_steps import *  # noqa
from tests.steps.PortfolioReporting.RGLstep import *  # noqa

# Load all scenarios from the feature file (gracefully skip if all are commented out)
try:
    scenarios("../../features/PortfolioReporting/document_vault.feature")
except NoScenariosFound:
    pass
