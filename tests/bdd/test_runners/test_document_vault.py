"""
Test module for document_vault.feature BDD scenarios
"""

from pytest_bdd import scenarios

from tests.bdd.steps.common_steps import *  # noqa
from tests.bdd.steps.document_vault_steps import *  # noqa
from tests.bdd.steps.login_steps import *  # noqa
from tests.bdd.steps.navigation_steps import *  # noqa

# Load all scenarios from the feature file
scenarios("../features/document_vault.feature")
