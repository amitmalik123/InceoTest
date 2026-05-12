"""
Test runner for the Smart Filter feature.
"""

import pytest
from pytest_bdd import scenario

# Import step definitions so scenario steps can be resolved
from tests.bdd.steps.Adhesion.apro_navigation_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.smart_filter_prospects_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.smart_filter_steps import *  # noqa: F401, F403
from tests.bdd.steps.common_steps import *  # noqa: F401, F403
from tests.bdd.steps.login_steps import *  # noqa: F401, F403


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
@scenario("../../features/Adhesion/smart_filter.feature", "Smart filter filtering")
def test_smart_filter_filtering(auth_file):
    """Test the smart filter functionality on the prospects page."""
