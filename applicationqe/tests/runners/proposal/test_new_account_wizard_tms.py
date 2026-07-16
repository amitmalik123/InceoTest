"""
Test runner for New Account Wizard with Tax Management Services feature using pytest-bdd.
"""
from pathlib import Path

from pytest_bdd import scenarios

from tests.steps.proposal.create_proposal_with_new_client_steps import *  # noqa: F401, F403
from tests.steps.proposal.create_proposal_with_new_portfolio_steps import *  # noqa: F401, F403
from tests.steps.proposal.tax_management_services_steps import *  # noqa: F401, F403
from tests.steps.proposal.verify_proposal_document_steps import *  # noqa: F401, F403

APP_ROOT = Path(__file__).resolve().parents[3]
_FEATURES = APP_ROOT / "tests/features/proposal"

scenarios(str(_FEATURES / "naw_tms.feature"))
