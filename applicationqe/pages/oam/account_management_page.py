"""
Account Management Page Object.

Handles the Account Management flow on the Account Wizard page:
  Account Wizard -> Account Management section -> Request & Type selection
  -> Complete and Print -> DocuSign -> Tracking

Locator strategy: Placeholder locators marked with TODO — run the Flow
Recorder to capture real DOM and replace them:

    $env:TEST_ENV="test11"
    pytest scripts/record_flow.py -v -s --headed

DOM evidence: Not yet captured — locators below are best-guess placeholders.
"""

from playwright.sync_api import Locator, Page

from locators.oam import account_management_locators
from pages.oam.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountManagementPage(BasePage):
    """Page object for the Account Management / Account Suspension flow."""

    PAGE_PATH = "DNeWM/NBT/List/ClientAccounts.aspx"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        locators = account_management_locators.initialize_locators(page)
        self.account_management_link: Locator = locators["account_management_link"]
        self.request_dropdown: Locator = locators["request_dropdown"]
        self.type_dropdown: Locator = locators["type_dropdown"]
        self.complete_and_print_button: Locator = locators["complete_and_print_button"]
        self.docusign_continue_button: Locator = locators["docusign_continue_button"]
        self.docusign_finish_button: Locator = locators["docusign_finish_button"]
        self.tracking_id_element: Locator = locators["tracking_id_element"]
        self.close_button: Locator = locators["close_button"]
        self.upload_pdf_input: Locator = locators["upload_pdf_input"]
        self.upload_button: Locator = locators["upload_button"]

    # ------------------------------------------------------------------
    # Navigation to Account Management
    # ------------------------------------------------------------------

    def select_request_and_type(self, request_name: str, type_name: str) -> None:
        """
        On the Account Wizard page, select a request and type under
        Account Management.

        Args:
            request_name: e.g. "Account Information change"
            type_name: e.g. "Account Suspension"
        """
        logger.info(f"Selecting request: '{request_name}', type: '{type_name}'")

        # Click the request link/option
        # Strategy: try role-based first, then dropdown, then text
        try:
            request_link = self.page.get_by_role("link", name=request_name, exact=True)
            request_link.wait_for(state="visible", timeout=120000)
            self.click(request_link)
            logger.info(f"Clicked request: '{request_name}'")
        except Exception:
            logger.info("Role-based click failed, trying dropdown selection")
            self.request_dropdown.wait_for(state="visible", timeout=120000)
            self.request_dropdown.select_option(label=request_name)
            logger.info(f"Selected request from dropdown: '{request_name}'")

        self.page.wait_for_timeout(1000)

        # Select the type
        try:
            type_link = self.page.get_by_role("link", name=type_name, exact=True)
            type_link.wait_for(state="visible", timeout=120000)
            self.click(type_link)
            logger.info(f"Clicked type: '{type_name}'")
        except Exception:
            logger.info("Role-based click failed, trying dropdown selection")
            self.type_dropdown.wait_for(state="visible", timeout=120000)
            self.type_dropdown.select_option(label=type_name)
            logger.info(f"Selected type from dropdown: '{type_name}'")

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Request '{request_name}' / Type '{type_name}' selected")

    # ------------------------------------------------------------------
    # Complete and Print
    # ------------------------------------------------------------------

    def click_complete_and_print(self) -> None:
        """Click the 'Complete and Print' button."""
        logger.info("Clicking 'Complete and Print' button")
        self.complete_and_print_button.wait_for(state="visible", timeout=120000)
        self.click(self.complete_and_print_button)
        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        logger.info(f"'Complete and Print' clicked — URL: {self.page.url}")

    # ------------------------------------------------------------------
    # DocuSign flow (redirects to docusign.net in same tab)
    # ------------------------------------------------------------------

    def handle_docusign_page(self) -> None:
        """
        Handle the DocuSign redirect page.
        Waits for DocuSign to load, then clicks Continue & Finish.
        """
        logger.info("Waiting for DocuSign page to load...")

        # Wait for URL to contain docusign or for the page to load
        try:
            self.page.wait_for_url("**/docusign**", timeout=120000)
            logger.info(f"DocuSign page loaded: {self.page.url}")
        except Exception:
            logger.info(
                f"URL did not match docusign pattern, current: {self.page.url}. "
                "Proceeding with current page."
            )

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(3000)  # DocuSign JS needs time

        # Try "Continue & Finish" as a single button first
        try:
            continue_finish = self.page.get_by_role("button", name="Continue & Finish")
            continue_finish.wait_for(state="visible", timeout=120000)
            self.click(continue_finish)
            logger.info("Clicked 'Continue & Finish' button")
        except Exception:
            # Fall back to separate Continue then Finish
            logger.info("Single button not found, trying separate buttons")
            try:
                self.docusign_continue_button.wait_for(state="visible", timeout=120000)
                self.click(self.docusign_continue_button)
                self.page.wait_for_timeout(2000)
                self.docusign_finish_button.wait_for(state="visible", timeout=120000)
                self.click(self.docusign_finish_button)
                logger.info("Clicked Continue and then Finish")
            except Exception:
                # Last resort: look for any button with finish/continue text
                fallback = self.page.locator(
                    "button:has-text('Finish'), button:has-text('Continue'), "
                    "a:has-text('Finish'), input[value*='Finish']"
                ).first
                fallback.wait_for(state="visible", timeout=120000)
                self.click(fallback)
                logger.info("Clicked fallback finish/continue element")

        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)
        logger.info(f"DocuSign completed — URL: {self.page.url}")

    # ------------------------------------------------------------------
    # Tracking ID & Close
    # ------------------------------------------------------------------

    def fetch_tracking_id(self) -> str:
        """
        Fetch the tracking ID from the confirmation/tracking page.

        Returns:
            The tracking ID text.
        """
        logger.info("Fetching tracking ID...")
        self.page.wait_for_load_state("domcontentloaded", timeout=120000)

        # Strategy 1: specific locator
        try:
            self.tracking_id_element.wait_for(state="visible", timeout=120000)
            tracking_id = self.get_text(self.tracking_id_element)
            if tracking_id:
                logger.info(f"Tracking ID found: {tracking_id}")
                return tracking_id.strip()
        except Exception:
            pass  # nosec B110

        # Strategy 2: search page for text pattern starting with B
        logger.info("Specific locator failed, searching page for tracking ID pattern")
        body_text = self.page.locator("body").text_content() or ""
        import re

        # Look for patterns like B12345, B-12345, etc.
        match = re.search(r"\b(B[\-]?\d{5,})\b", body_text)
        if match:
            tracking_id = match.group(1)
            logger.info(f"Tracking ID found via regex: {tracking_id}")
            return tracking_id

        logger.warning("Could not find tracking ID on page")
        return ""

    def click_close_button(self) -> None:
        """Click the Close button after fetching the tracking ID."""
        logger.info("Clicking Close button")
        self.close_button.wait_for(state="visible", timeout=120000)
        self.click(self.close_button)
        self.page.wait_for_load_state("domcontentloaded", timeout=120000)
        logger.info("Close button clicked")

    # ------------------------------------------------------------------
    # PDF Upload (on Tracking Center)
    # ------------------------------------------------------------------

    def upload_pdf(self, file_path: str = "") -> None:
        """
        Upload a PDF file on the tracking center page.

        Args:
            file_path: Path to the PDF file. If empty, creates a minimal test PDF.
        """
        import os
        import tempfile

        if not file_path or not os.path.exists(file_path):
            # Create a minimal test PDF for upload
            file_path = os.path.join(tempfile.gettempdir(), "test_upload.pdf")
            if not os.path.exists(file_path):
                _create_minimal_pdf(file_path)
            logger.info(f"Using generated test PDF: {file_path}")

        logger.info(f"Uploading PDF: {file_path}")

        # Look for file input on the page
        try:
            self.upload_pdf_input.wait_for(state="attached", timeout=120000)
            self.upload_pdf_input.set_input_files(file_path)
            logger.info("PDF file set on input element")
        except Exception:
            # Some apps hide the file input — try finding any file input
            file_input = self.page.locator("input[type='file']").first
            file_input.set_input_files(file_path)
            logger.info("PDF file set on first available file input")

        self.page.wait_for_timeout(2000)

        # Click Upload/Submit button if present
        try:
            self.upload_button.wait_for(state="visible", timeout=5000)
            self.click(self.upload_button)
            self.page.wait_for_load_state("domcontentloaded", timeout=120000)
            logger.info("Upload button clicked")
        except Exception:
            logger.info("No explicit upload button found — file may auto-upload")

        logger.info("PDF upload completed")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def verify_tracking_id_starts_with(self, prefix: str, tracking_id: str) -> None:
        """
        Verify that the tracking ID starts with the expected prefix.

        Args:
            prefix: Expected prefix (e.g. "B")
            tracking_id: The tracking ID to validate
        """
        logger.info(f"Verifying tracking ID '{tracking_id}' starts with '{prefix}'")
        assert tracking_id.startswith(
            prefix
        ), f"Tracking ID '{tracking_id}' does not start with '{prefix}'"
        logger.info(f"Tracking ID verification passed: {tracking_id}")


def _create_minimal_pdf(path: str) -> None:
    """Create a minimal valid PDF file for testing uploads."""
    pdf_content = (
        b"%PDF-1.0\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n190\n%%EOF"
    )
    with open(path, "wb") as f:
        f.write(pdf_content)
