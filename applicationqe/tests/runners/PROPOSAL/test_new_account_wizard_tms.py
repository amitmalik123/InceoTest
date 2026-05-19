"""
Test runner for New Account Wizard with Tax Management Services feature using pytest-bdd.

This runner:
1. Imports all step definitions to register them with pytest-bdd
2. Uses @scenario to bind Gherkin feature to pytest test
3. Receives page fixture (auto-injected by pytest-bdd) to trigger
   pytest-playwright to load auth state via browser_context_args
"""

import pytest
from pytest_bdd import scenario

# Import step definitions with proper pytest-bdd decorators
# These must be imported BEFORE @scenario is evaluated
from tests.steps.PROPOSAL.create_proposal_with_new_client_steps import *  # noqa: F401, F403
from tests.steps.PROPOSAL.create_proposal_with_new_portfolio_steps import *  # noqa: F401, F403
from tests.steps.PROPOSAL.tax_management_services_steps import *  # noqa: F401, F403
from tests.steps.PROPOSAL.verify_proposal_document_steps import *  # noqa: F401, F403


@pytest.mark.smoke
@pytest.mark.regression
@scenario(
    "../../features/PROPOSAL/newAccoutWizardTMSTest.feature",
    "Complete New Account Wizard TMS E2E - Create Proposal and Verify Document",
)
def test_complete_new_account_wizard_tms_e2e__create_proposal_and_verify_document(page):
    """
    Execute complete new account wizard TMS E2E scenario.
    
    The page fixture parameter ensures pytest-playwright creates a context
    with the auth state (via browser_context_args fixture).
    """
    pass
