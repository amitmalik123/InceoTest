"""
Test module for document_vault.feature BDD scenarios
"""

from pytest_bdd import scenarios
from pytest_bdd.exceptions import NoScenariosFound

from tests.bdd.steps.PR.common_steps import *  # noqa
from tests.bdd.steps.PR.document_vault_steps import *  # noqa
from tests.bdd.steps.PR.login_steps import *  # noqa
from tests.bdd.steps.PR.navigation_steps import *  # noqa
from tests.bdd.steps.PR.RGLstep import *  # noqa

# Load all scenarios from the feature file (gracefully skip if all are commented out)
try:
    scenarios("../features/PR/document_vault.feature")
except NoScenariosFound:
    pass
