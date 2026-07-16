"""
Test runner for Portfolio Engine Widgets feature using pytest-bdd.
"""
from pathlib import Path

from pytest_bdd import scenarios

from tests.steps.proposal.add_strategies_to_portfolio_steps import *  # noqa: F401, F403
from tests.steps.proposal.verify_portfolio_engine_widgets_steps import *  # noqa: F401, F403

APP_ROOT = Path(__file__).resolve().parents[3]
_FEATURES = APP_ROOT / "tests/features/proposal"

scenarios(str(_FEATURES / "portfolio_engine_widgets.feature"))
