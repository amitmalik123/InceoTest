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

import re

from playwright.sync_api import Locator, Page

from pages.ewm.base_page import BasePage
from pages.ewm.locators.account_management_locators import AccountManagementLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountManagementPage(BasePage):
    """Page object for the Account Management / Account Suspension flow."""

    PAGE_PATH = "DNeWM/NBT/List/ClientAccounts.aspx"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        loc = AccountManagementLocators

        # -- Account Wizard: Account Management section --
        self.account_management_link: Locator = page.get_by_role(
            "link", name=loc.ACCOUNT_MANAGEMENT_LINK_TEXT
        )

        # -- Request / Type selection --
        self.request_dropdown: Locator = page.locator(loc.REQUEST_DROPDOWN)
        self.type_dropdown: Locator = page.locator(loc.TYPE_DROPDOWN)

        # -- Complete and Print button --
        self.complete_and_print_button: Locator = page.get_by_role(
            "button", name=loc.COMPLETE_AND_PRINT_BUTTON_TEXT
        )

        # -- DocuSign page (redirects to docusign.net in same tab) --
        self.docusign_continue_button: Locator = page.get_by_role(
            "button", name=loc.DOCUSIGN_CONTINUE_BUTTON_TEXT
        )
        self.docusign_finish_button: Locator = page.get_by_role(
            "button", name=loc.DOCUSIGN_FINISH_BUTTON_TEXT
        )

        # -- Post-DocuSign: Tracking ID & Close --
        self.tracking_id_element: Locator = page.locator(loc.TRACKING_ID_ELEMENT)
        self.close_button: Locator = page.get_by_role("button", name=loc.CLOSE_BUTTON_TEXT)

        # -- Tracking Center: PDF Upload --
        self.upload_pdf_input: Locator = page.locator(loc.UPLOAD_PDF_INPUT)
        self.upload_button: Locator = page.get_by_role("button", name=loc.UPLOAD_BUTTON_TEXT)

    def select_request_and_type(self, request_name: str, type_name: str) -> None:
        logger.info(f"Selecting request: '{request_name}', type: '{type_name}'")
        try:
            request_link = self.page.get_by_role("link", name=request_name, exact=True)
            request_link.wait_for(state="visible", timeout=15000)
            self.click(request_link)
            logger.info(f"Clicked request: '{request_name}'")
        except Exception:
            logger.info("Role-based click failed, trying dropdown selection")
            self.request_dropdown.wait_for(state="visible", timeout=15000)
            self.request_dropdown.select_option(label=request_name)
            logger.info(f"Selected request from dropdown: '{request_name}'")

        self.page.wait_for_timeout(1000)

        try:
            type_link = self.page.get_by_role("link", name=type_name, exact=True)
            type_link.wait_for(state="visible", timeout=15000)
            self.click(type_link)
            logger.info(f"Clicked type: '{type_name}'")
        except Exception:
            logger.info("Role-based click failed, trying dropdown selection")
            self.type_dropdown.wait_for(state="visible", timeout=15000)
            self.type_dropdown.select_option(label=type_name)
            logger.info(f"Selected type from dropdown: '{type_name}'")

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info(f"Request '{request_name}' / Type '{type_name}' selected")

    def click_complete_and_print(self) -> None:
        logger.info("Clicking 'Complete and Print' button")
        self.complete_and_print_button.wait_for(state="visible", timeout=15000)
        self.click(self.complete_and_print_button)
        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        logger.info(f"'Complete and Print' clicked — URL: {self.page.url}")

    def handle_docusign_page(self) -> None:
        logger.info("Waiting for DocuSign page to load...")
        try:
            self.page.wait_for_url(AccountManagementLocators.DOCUSIGN_URL_GLOB, timeout=30000)
            logger.info(f"DocuSign page loaded: {self.page.url}")
        except Exception:
            logger.info(
                f"URL did not match docusign pattern, current: {self.page.url}. "
                "Proceeding with current page."
            )

        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(3000)

        try:
            continue_finish = self.page.get_by_role(
                "button", name=AccountManagementLocators.DOCUSIGN_CONTINUE_FINISH_BUTTON_TEXT
            )
            continue_finish.wait_for(state="visible", timeout=10000)
            self.click(continue_finish)
            logger.info("Clicked 'Continue & Finish' button")
        except Exception:
            logger.info("Single button not found, trying separate buttons")
            try:
                self.docusign_continue_button.wait_for(state="visible", timeout=10000)
                self.click(self.docusign_continue_button)
                self.page.wait_for_timeout(2000)
                self.docusign_finish_button.wait_for(state="visible", timeout=10000)
                self.click(self.docusign_finish_button)
                logger.info("Clicked Continue and then Finish")
            except Exception:
                fallback = self.page.locator(
                    AccountManagementLocators.DOCUSIGN_FALLBACK_FINISH_CONTINUE_SELECTOR
                ).first
                fallback.wait_for(state="visible", timeout=10000)
                self.click(fallback)
                logger.info("Clicked fallback finish/continue element")

        self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        self.page.wait_for_timeout(3000)
        logger.info(f"DocuSign completed — URL: {self.page.url}")

    def fetch_tracking_id(self) -> str:
        logger.info("Fetching tracking ID...")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        try:
            self.tracking_id_element.wait_for(state="visible", timeout=10000)
            tracking_id = self.get_text(self.tracking_id_element)
            if tracking_id:
                logger.info(f"Tracking ID found: {tracking_id}")
                return tracking_id.strip()
        except Exception:
            pass  # nosec B110

        logger.info("Specific locator failed, searching page for tracking ID pattern")
        body_text = self.page.locator("body").text_content() or ""
        match = re.search(r"\b(B[\-]?\d{5,})\b", body_text)
        if match:
            tracking_id = match.group(1)
            logger.info(f"Tracking ID found via regex: {tracking_id}")
            return tracking_id

        logger.warning("Could not find tracking ID on page")
        return ""

    def click_close_button(self) -> None:
        logger.info("Clicking Close button")
        self.close_button.wait_for(state="visible", timeout=15000)
        self.click(self.close_button)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info("Close button clicked")

    def upload_pdf(self, file_path: str = "") -> None:
        import os
        import tempfile

        if not file_path or not os.path.exists(file_path):
            file_path = os.path.join(tempfile.gettempdir(), "test_upload.pdf")
            if not os.path.exists(file_path):
                _create_minimal_pdf(file_path)
            logger.info(f"Using generated test PDF: {file_path}")

        logger.info(f"Uploading PDF: {file_path}")

        try:
            self.upload_pdf_input.wait_for(state="attached", timeout=15000)
            self.upload_pdf_input.set_input_files(file_path)
            logger.info("PDF file set on input element")
        except Exception:
            file_input = self.page.locator(AccountManagementLocators.UPLOAD_PDF_INPUT).first
            file_input.set_input_files(file_path)
            logger.info("PDF file set on first available file input")

        self.page.wait_for_timeout(2000)

        try:
            self.upload_button.wait_for(state="visible", timeout=5000)
            self.click(self.upload_button)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info("Upload button clicked")
        except Exception:
            logger.info("No explicit upload button found — file may auto-upload")

        logger.info("PDF upload completed")

    def verify_tracking_id_starts_with(self, prefix: str, tracking_id: str) -> None:
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
