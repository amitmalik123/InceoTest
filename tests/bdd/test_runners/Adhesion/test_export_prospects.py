"""
Test runner for the Export Prospects feature.
"""

from pathlib import Path

import pytest
from pytest_bdd import scenario

from tests.bdd.steps.Adhesion import export_prospects_steps  # noqa: F401

# Import step definitions so scenario steps can be resolved
from tests.bdd.steps.Adhesion.apro_navigation_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.export_prospects_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.smart_filter_prospects_steps import *  # noqa: F401, F403
from tests.bdd.steps.Adhesion.smart_filter_steps import *  # noqa: F401, F403
from tests.bdd.steps.common_steps import *  # noqa: F401, F403
from tests.bdd.steps.login_steps import *  # noqa: F401, F403
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@pytest.fixture(autouse=True, scope="function")
def cleanup_export_file():
    """Teardown fixture to ensure export files are cleaned up after each test, regardless of pass/fail"""
    yield  # Test runs here

    # Cleanup after test completes (success or failure)
    if export_prospects_steps._exported_file_path:
        try:
            file_path = export_prospects_steps._exported_file_path
            if Path(file_path).exists():
                Path(file_path).unlink()
                logger.info(f"Cleanup: Removed leftover export file: {file_path}")
        except Exception as e:
            logger.warning(f"Cleanup: Failed to remove export file: {str(e)}")
        finally:
            # Reset the global variable for the next test
            export_prospects_steps._exported_file_path = None


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
@scenario("../../features/Adhesion/export_prospects.feature", "Export prospects list unfiltered")
def test_export_prospects_unfiltered(auth_file):
    """Test exporting unfiltered prospects list."""


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
@scenario("../../features/Adhesion/export_prospects.feature", "Export prospects list filtered")
def test_export_prospects_filtered(auth_file):
    """Test exporting filtered prospects list."""
