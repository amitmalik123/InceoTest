"""
Test runner for the Global Search feature.
"""

import pytest
from pytest_bdd import scenario

# Import commonly used step definitions so scenario steps can be resolved
from tests.steps.account_steps import *  # noqa: F401, F403
from tests.steps.global_search_steps import *  # noqa: F401, F403
from tests.steps.common_steps import *  # noqa: F401, F403
from tests.steps.data_steps import *  # noqa: F401, F403
from tests.steps.login_steps import *  # noqa: F401, F403
from tests.steps.navigation_steps import *  # noqa: F401, F403


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
@scenario("../features/global_search.feature", "Global Search")
def test_global_search(auth_file):
    """Test the global search workflow."""
