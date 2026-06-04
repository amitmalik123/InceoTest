"""
Test runner for NAW retain-account BDD scenarios.

This keeps the runner beside the feature file so pytest can collect it when
the pipeline targets tests/features/naw, matching the STP-ICT layout.
"""

from pathlib import Path

from pytest_bdd import scenarios

from tests.steps.common_steps import *  # noqa: F401, F403
from tests.steps.naw.account_setup_step import *  # noqa: F401, F403
from tests.steps.naw.account_wizard_steps import *  # noqa: F401, F403
from tests.steps.naw.client_profile_step import *  # noqa: F401, F403
from tests.steps.naw.clients_steps import *  # noqa: F401, F403
from tests.steps.naw.construct_portfolio_step import *  # noqa: F401, F403
from tests.steps.naw.create_documents_step import *  # noqa: F401, F403
from tests.steps.naw.dashboard_steps import *  # noqa: F401, F403
from tests.steps.naw.fees_step import *  # noqa: F401, F403
from tests.steps.naw.navbar_common_steps import *  # noqa: F401, F403
from tests.steps.naw.portfolio_details_step import *  # noqa: F401, F403
from tests.steps.naw.review_all_accounts_step import *  # noqa: F401, F403
from tests.steps.naw.view_documents_step import *  # noqa: F401, F403

for feature_file in Path(__file__).parent.glob("*.feature"):
	scenarios(feature_file)