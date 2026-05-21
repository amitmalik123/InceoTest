"""
Test runner for Portfolio Engine Widgets feature using pytest-bdd.

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
from tests.steps.PROPOSAL.verify_portfolio_engine_widgets_steps import *  # noqa: F401, F403


@pytest.mark.smoke
@pytest.mark.regression
@scenario(
    "../../features/PROPOSAL/portfolioEngineWidgets.feature",
    "Verify Portfolio Engine Widgets Load",
)
def test_verify_portfolio_engine_widgets_load(page):
    """
    Execute portfolio engine widgets load scenario.
    
    The page fixture parameter ensures pytest-playwright creates a context
    with the auth state (via browser_context_args fixture).
    """
    pass
