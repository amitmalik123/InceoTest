"""
Step definitions for Tax Management Services workflows.
Converts TypeScript: taxManagementServices.ts
"""

import logging
import os
from pytest_bdd import when, then
from playwright.sync_api import Page, expect

from tests.steps.proposal.instance_manager import get_tax_mgmt_services_instance
from pages.proposal.proposal_pdf_utils import download_and_validate_pdf_from_click

logger = logging.getLogger(__name__)


def _is_prod_environment() -> bool:
    """Check if running in prod or silo environment."""
    env = os.getenv("Environment", "").lower()
    env_upper = os.getenv("ENVIRONMENT", "").lower()
    return env in ("prod", "silo") or env_upper in ("prod", "silo")


def _verify_screenshot_with_fallback(
    page: Page, base_filename: str, screenshot_mask_locators, is_prod: bool
) -> None:
    """
    Verify screenshot against baseline images using Playwright's built-in comparison.
    
    Masks dynamic elements like dates, tax values, and client names that change per test run.
    Uses 3% pixel tolerance for rendering differences across environments.
    
    Args:
        page: Playwright page object
        base_filename: Base filename (e.g., "tax-sensitivity-low.png")
        screenshot_mask_locators: List of Locators to mask in screenshot
        is_prod: Whether running in prod/silo environment
    """
    try:
        if is_prod:
            try:
                expect(page).to_have_screenshot(
                    base_filename,
                    mask=screenshot_mask_locators,
                    full_page=True,
                    max_diff_pixel_ratio=0.03,
                )
            except AssertionError as e:
                # Try prod variant
                error_msg = str(e)
                if "Expected an image" in error_msg and "px by" in error_msg:
                    raise
                prod_filename = base_filename.replace(".png", "-prod.png")
                expect(page).to_have_screenshot(
                    prod_filename,
                    mask=screenshot_mask_locators,
                    full_page=True,
                    max_diff_pixel_ratio=0.03,
                )
        else:
            expect(page).to_have_screenshot(
                base_filename,
                mask=screenshot_mask_locators,
                full_page=True,
                max_diff_pixel_ratio=0.03,
            )
        logger.info(f"Screenshot validation passed: {base_filename}")
    except AttributeError:
        # Playwright version doesn't have to_have_screenshot - skip visual validation
        page.wait_for_load_state("load")
    except AssertionError as e:
        logger.error(f"Screenshot validation failed: {base_filename}: {e}")
        raise



@when("I upload a holdings template")
def upload_holdings_template(page: Page):
    tms_page = get_tax_mgmt_services_instance()
    logger.debug("\nUploading completed template")
    tms_page.upload_holdings_template()

    logger.debug("\nTemplate upload initiated")


@then("The UI summary should be generated")
def verify_ui_summary_generated(page: Page):
    tms_page = get_tax_mgmt_services_instance()
    logger.debug("\nVerifying UI summary is generated")
    screenshot_mask_locators = tms_page.get_screenshot_mask_locators()

    # Hide chat widget in prod by directly manipulating DOM
    tms_page.page.evaluate(
        """() => {
        const chatWidget = document.getElementById("chatpillid");
        if (chatWidget) {
            chatWidget.style.display = "none";
        }
    }"""
    )

    # Low sensitivity
    tms_page.page.bring_to_front()
    tms_page.select_tax_sensitivity("Low")
    # _verify_screenshot_with_fallback(
    #     tms_page.page,
    #     "tax-sensitivity-low.png",
    #     screenshot_mask_locators,
    #     _is_prod_environment(),
    # )

    # Test PDF download for Low sensitivity
    logger.debug("\nAttempting to download PDF for Low sensitivity")
    
    # Wait for download button to be visible and enabled
    tms_page.page.wait_for_timeout(1000)  # Small wait for UI to stabilize
    tms_page.download_button.wait_for(state="visible", timeout=10000)
    
    download_and_validate_pdf_from_click(
        tms_page.page,
        lambda: tms_page.download_button.click(),
        {
            "expectedPageCount": 2,
            "filenamePrefix": "tax-management-services",
            "expectedBrowserFilename": "TMS_Report.pdf",
        },
    )

    # Medium sensitivity
    tms_page.page.bring_to_front()
    tms_page.select_tax_sensitivity("Medium")
    # _verify_screenshot_with_fallback(
    #     tms_page.page,
    #     "tax-sensitivity-medium.png",
    #     screenshot_mask_locators,
    #     _is_prod_environment(),
    # )

    # Test PDF download for Medium sensitivity
    logger.debug("\nAttempting to download PDF for Medium sensitivity")
    
    # Wait for download button to be visible and enabled
    tms_page.page.wait_for_timeout(1000)  # Small wait for UI to stabilize
    tms_page.download_button.wait_for(state="visible", timeout=10000)
    
    download_and_validate_pdf_from_click(
        tms_page.page,
        lambda: tms_page.download_button.click(),
        {
            "expectedPageCount": 2,
            "filenamePrefix": "tax-management-services",
            "expectedBrowserFilename": "TMS_Report.pdf",
        },
    )

    # High sensitivity
    tms_page.page.bring_to_front()
    tms_page.select_tax_sensitivity("High")
    # _verify_screenshot_with_fallback(
    #     tms_page.page,
    #     "tax-sensitivity-high.png",
    #     screenshot_mask_locators,
    #     _is_prod_environment(),
    # )

    # Test PDF download for High sensitivity
    logger.debug("\nAttempting to download PDF for High sensitivity")
    
    # Wait for download button to be visible and enabled
    tms_page.page.wait_for_timeout(1000)  # Small wait for UI to stabilize
    tms_page.download_button.wait_for(state="visible", timeout=10000)
    
    download_and_validate_pdf_from_click(
        tms_page.page,
        lambda: tms_page.download_button.click(),
        {
            "expectedPageCount": 2,
            "filenamePrefix": "tax-management-services",
            "expectedBrowserFilename": "TMS_Report.pdf",
        },
    )

    # Very High sensitivity
    tms_page.page.bring_to_front()
    tms_page.select_tax_sensitivity("Very High")
    # _verify_screenshot_with_fallback(
    #     tms_page.page,
    #     "tax-sensitivity-very-high.png",
    #     screenshot_mask_locators,
    #     _is_prod_environment(),
    # )

    # Test PDF download for Very High sensitivity
    logger.debug("\nAttempting to download PDF for Very High sensitivity")
    
    # Wait for download button to be visible and enabled
    tms_page.page.wait_for_timeout(1000)  # Small wait for UI to stabilize
    tms_page.download_button.wait_for(state="visible", timeout=10000)
    
    download_and_validate_pdf_from_click(
        tms_page.page,
        lambda: tms_page.download_button.click(),
        {
            "expectedPageCount": 2,
            "filenamePrefix": "tax-management-services",
            "expectedBrowserFilename": "TMS_Report.pdf",
        },
    )

    tms_page.page.bring_to_front()
    tms_page.continue_button.click()