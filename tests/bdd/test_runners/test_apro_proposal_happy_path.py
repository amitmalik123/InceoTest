"""
Test runner for the APro proposal happy path feature (generated from codegen recording).
"""

import pytest
from pytest_bdd import scenario

# Import commonly used step definitions so scenario steps can be resolved
from tests.bdd.steps.account_steps import *  # noqa: F401, F403
from tests.bdd.steps.account_wizard_steps import *  # noqa: F401, F403
from tests.bdd.steps.api_steps import *  # noqa: F401, F403
from tests.bdd.steps.apro_navigation_steps import *  # noqa: F401, F403
from tests.bdd.steps.apro_proposal_steps import *  # noqa: F401, F403
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
@scenario("../features/apro_proposal_happy_path.feature", "Create Prospect Proposal Happy Path")
def test_create_prospect_proposal(auth_file, request):
    # scenario steps are executed by pytest-bdd via the @scenario decorator
    pass


# @scenario("../features/apro_proposal_happy_path.feature", "Create Client Proposal Happy Path")
# def test_create_client_proposal(auth_file, request):
#     # scenario steps are executed by pytest-bdd via the @scenario decorator
#     pass
