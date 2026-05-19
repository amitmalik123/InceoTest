"""Teardown fixtures for APro proposal tests.

This dedicated teardown module ensures proposals (including copies) are always cleaned up,
regardless of test outcome. Keeps teardown logic separate from step flow files.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from pages import AproProposalsPage, GlobalNavigationPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@pytest.fixture(autouse=True)
def cleanup_happy_path_proposals(proposal_page: AproProposalsPage, request):
    """Delete proposals created by APro happy path test.

    This fixture:
    - Only runs for tests marked with @pytest.mark.apro_happy_path
    - Runs after each marked test completes (pass or fail)
    - Deletes only the proposals created during the test (identified by stored data)
    - Handles both original proposals and copies
    - Prevents test data accumulation and orphaned proposals
    - Leaves other proposals in the list untouched

    Usage: Add @pytest.mark.apro_happy_path to test function or feature file.
    """
    # Only run for tests marked with apro_happy_path
    if "apro_happy_path" not in request.keywords:
        yield
        return

    yield

    # Teardown: delete the original proposal (and its copy via cascade)
    logger.info(f"Running teardown for test: {request.node.name}")
    try:
        # Get the original proposal data stored during the test
        original_data = getattr(proposal_page, "original_proposal_data", None)

        if not original_data:
            logger.info("No proposal data found to clean up (test may have failed early)")
            return

        # Navigate to APro prospects page using the same approach as the test
        logger.info("Navigating to APro prospects page for cleanup")
        gnav = GlobalNavigationPage(proposal_page.page)
        gnav.click_menu_trigger()
        gnav.click_proposals_apro()

        # Wait for prospects list to load
        proposal_page.wait_for_prospects_list(timeout=5000)

        # Find and open the original proposal
        original_client = original_data.get("client", "").strip()
        logger.info(f"Finding original proposal for client: {original_client}")

        row_index = proposal_page.find_proposal_row(
            "original", original_proposal_data=original_data
        )
        logger.info(f"Found original proposal at row {row_index}, opening it...")

        # Open the proposal - this will navigate to the History step with actions dropdown
        proposal_page.resume_proposal_from_row(row_index)
        # deleting copy
        proposal_page.delete_selected_proposal()
        # deleting original
        proposal_page.delete_selected_proposal()
        logger.info("Proposal and copy deleted successfully")

        # Clean up downloaded files
        _cleanup_downloaded_files()

    except Exception as e:
        logger.error(f"Teardown error: {e}")
        # Teardown errors should not fail the test


def _cleanup_downloaded_files() -> None:
    """Clean up downloaded PDFs and template files from test artifacts directories."""
    try:
        # Clean up PDFs from project tmp directory
        tmp_dir = Path("tmp")
        if tmp_dir.exists():
            logger.info("Cleaning up downloaded PDFs from tmp/")
            try:
                shutil.rmtree(tmp_dir)
                tmp_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not clean up tmp directory: {e}")

        # Clean up template files from system temp directory
        system_temp = Path(tempfile.gettempdir())
        logger.info(f"Cleaning up template files from system temp: {system_temp}")

        for pattern in ["Holdings_Template_*.csv", "DownloadReport.pdf"]:
            for file_path in system_temp.glob(pattern):
                try:
                    file_path.unlink()
                    logger.info(f"Deleted: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not delete {file_path}: {e}")

    except Exception as e:
        logger.warning(f"File cleanup error (non-blocking): {e}")
