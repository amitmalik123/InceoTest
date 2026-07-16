"""
Test runner for Portfolio Engine End-to-End feature using pytest-bdd.
"""
from pathlib import Path

from pytest_bdd import scenarios

from tests.steps.proposal.add_strategies_to_portfolio_steps import *  # noqa: F401, F403
from tests.steps.proposal.create_proposal_with_new_portfolio_steps import *  # noqa: F401, F403
from tests.steps.proposal.verify_proposal_document_steps import *  # noqa: F401, F403

APP_ROOT = Path(__file__).resolve().parents[3]
_FEATURES = APP_ROOT / "tests/features/proposal"

scenarios(str(_FEATURES / "portfolio_engine_e2e.feature"))
