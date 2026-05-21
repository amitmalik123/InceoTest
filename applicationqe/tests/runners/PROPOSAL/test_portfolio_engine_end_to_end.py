"""
Test runner for Portfolio Engine End-to-End feature using pytest-bdd.

This runner:
1. Imports all step definitions to register them with pytest-bdd
2. Uses @scenario to bind Gherkin feature to pytest test
3. Receives page fixture (auto-injected by pytest-bdd) to trigger
   pytest-playwright to load auth state via browser_context_args
"""

import pytest
from pytest_bdd import scenario

# Import all step definitions before scenario decorator runs
from tests.steps.PROPOSAL.add_strategies_to_portfolio_steps import *  # noqa: F401, F403
from tests.steps.PROPOSAL.create_proposal_with_new_portfolio_steps import *  # noqa: F401, F403
from tests.steps.PROPOSAL.verify_proposal_document_steps import *  # noqa: F401, F403


@pytest.mark.smoke
@pytest.mark.regression
@scenario(
    "../../features/PROPOSAL/portfolioEngineEndToEnd.feature",
    "Complete Portfolio Engine E2E - Create Portfolio, Create Proposal, and Verify Document",
)
def test_complete_portfolio_engine_e2e__create_portfolio_create_proposal_and_verify_document(page):
    """
    Execute complete portfolio engine E2E scenario.
    
    The page fixture parameter ensures pytest-playwright creates a context
    with the auth state (via browser_context_args fixture).
    """
    pass
