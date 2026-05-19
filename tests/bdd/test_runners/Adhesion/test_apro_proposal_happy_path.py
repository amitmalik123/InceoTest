"""
Test runner for the APro proposal happy path feature.
"""

import pytest
from pytest_bdd import scenario

# Import commonly used step definitions so scenario steps can be resolved
from tests.bdd.steps.account_steps import *  # noqa: F401, F403
from tests.bdd.steps.account_wizard_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_navigation_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_proposal_teardown import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_allocation_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_details_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_fees_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_generate_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_history_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_holdings_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_prospects_list_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_risk_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.apro_step_tax_management_steps import *  # noqa: F401, F403
from tests.bdd.steps.api_steps import *  # noqa: F401, F403
from tests.bdd.steps.common_steps import *  # noqa: F401, F403
from tests.bdd.steps.data_steps import *  # noqa: F401, F403
from tests.bdd.steps.database_steps import *  # noqa: F401, F403
from tests.bdd.steps.login_steps import *  # noqa: F401, F403
from tests.bdd.steps.navigation_steps import *  # noqa: F401, F403
from tests.bdd.steps.tracking_center_steps import *  # noqa: F401, F403


@pytest.mark.app("adhesion")
@pytest.mark.parametrize(
    "auth_file",
    [
        pytest.param(
            "tests/.auth/superAdvisorAuthFile.json",
            marks=pytest.mark.auth_file("tests/.auth/superAdvisorAuthFile.json"),
            id="super_advisor",
        ),
    ],
)
@scenario(
    "../../features/Adhesion/apro_proposal_happy_path.feature",
    "Create Prospect Proposal Happy Path",
)
def test_create_prospect_proposal(auth_file, request):
    # scenario steps are executed by pytest-bdd via the @scenario decorator
    pass


# @scenario("../../features/Adhesion/apro_proposal_happy_path.feature", "Create Client Proposal Happy Path")
# def test_create_client_proposal(auth_file, request):
#     # scenario steps are executed by pytest-bdd via the @scenario decorator
#     pass
