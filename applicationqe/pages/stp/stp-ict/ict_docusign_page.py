from playwright.sync_api import Page

from pages.base_page import BasePage
from locators.stp.stp_ict import ict_docusign_locators as docusign_locators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DocuSignPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def verify_docusign_page_loaded(self, timeout: int = 30000) -> None:
        """Wait for navigation to DocuSign URL and page load."""
        logger.info("Waiting for DocuSign page to load...")
        self.page.wait_for_url(lambda url: docusign_locators.DOCUSIGN_URL_PATTERN in url, timeout=timeout)
        logger.info(f"DocuSign URL reached: {self.page.url}")
        self.page.wait_for_load_state('domcontentloaded', timeout=timeout)
        logger.info("DocuSign page loaded")

    def check_ersd_consent_checkbox(self, timeout: int = 10000) -> None:
        """Check the ERSD consent checkbox using the input element directly with force click."""
        logger.info("Checking ERSD consent checkbox...")
        checkbox = self.page.locator("input[type='checkbox']").first
        self.wait_for_element(checkbox, state='attached', timeout=timeout)
        if not checkbox.is_checked():
            checkbox.click(force=True)
        logger.info("ERSD consent checkbox checked")

    def click_ersd_continue_button(self, timeout: int = 10000) -> None:
        """Click the Continue button in the ERSD modal."""
        logger.info("Clicking ERSD Continue button...")
        continue_button = self.page.get_by_role("button", name="Continue")
        self.wait_for_element(continue_button, state='visible', timeout=timeout)
        continue_button.click()
        logger.info("ERSD Continue button clicked")

    def _click_tab_button_and_handle_adopt(self, btn_locator, label: str, adopt_timeout: int = 6000) -> None:
        """Click a signing tab button (force click to bypass viewport), then handle Adopt modal."""
        btn_locator.scroll_into_view_if_needed()
        btn_locator.click(force=True)
        logger.info(f"{label} clicked")
        try:
            adopt_btn = self.page.locator('button:has-text("Adopt")').first
            self.wait_for_element(adopt_btn, state='visible', timeout=adopt_timeout)
            adopt_btn.click()
            logger.info(f"Adopt dialog confirmed for {label}")
        except Exception:
            logger.info(f"No Adopt dialog for {label} (auto-applied or already adopted)")

    def click_finish_button(self, timeout: int = 10000) -> None:
        """Complete DocuSign signing: click ALL required signature/initial tabs then Finish."""
        logger.info("Starting sign and finish process...")

        # -- 1. Click every required SignHere button --------------------------
        sig_buttons = self.page.locator("button[data-qa^='signature-tab-required']")
        count = sig_buttons.count()
        logger.info(f"Found {count} signature tab button(s)")
        for i in range(count):
            btn = sig_buttons.nth(i)
            try:
                self.wait_for_element(btn, state='attached', timeout=5000)
                self._click_tab_button_and_handle_adopt(btn, f"Signature tab {i + 1}")
                self.page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"Signature tab {i + 1} click failed: {e}")

        # -- 2. Click every required InitialHere button ------------------------
        init_buttons = self.page.locator("button[data-qa^='initials-tab-required']")
        count = init_buttons.count()
        logger.info(f"Found {count} initials tab button(s)")
        for i in range(count):
            btn = init_buttons.nth(i)
            try:
                self.wait_for_element(btn, state='attached', timeout=5000)
                self._click_tab_button_and_handle_adopt(btn, f"Initials tab {i + 1}")
                self.page.wait_for_timeout(500)
            except Exception as e:
                logger.warning(f"Initials tab {i + 1} click failed: {e}")

        # -- 3. Click Finish ---------------------------------------------------
        logger.info("Clicking Finish button...")
        finish_button = self.page.locator(docusign_locators.FINISH_BUTTON)
        self.wait_for_element(finish_button, state='visible', timeout=timeout)
        finish_button.click()
        logger.info("Finish button clicked")

        # -- 4. Wait for navigation back to EWealthManager --------------------
        try:
            self.page.wait_for_url(lambda url: 'docusign' not in url, timeout=30000)
            logger.info(f"Navigated back from DocuSign to: {self.page.url}")
        except Exception:
            logger.info(f"Still on DocuSign: {self.page.url}")
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)

    def fetch_docusign_review_and_continue_dialog_text(self, timeout: int = 10000) -> str:
        """Fetch dialog text from the Review and Continue modal."""
        logger.info("Fetching Review and Continue dialog text...")
        try:
            dialog_el = self.page.locator(docusign_locators.DIALOG_CONTENT_P_TAG).first
            self.wait_for_element(dialog_el, state='visible', timeout=timeout)
            text = dialog_el.inner_text().strip()
            logger.info(f"Dialog text fetched: '{text[:100]}'")
            return text
        except Exception as e:
            logger.warning(f"Review and Continue dialog text element not found: {e}")
            return ""

    def get_stamping_element(self, stamping_text: str):
        """Get locator for a stamping element by text content."""
        logger.info(f"Getting stamping element locator for: '{stamping_text}'")
        return self.page.get_by_text(stamping_text, exact=False)

    def verify_request_submitted_popup(self, timeout: int = 15000) -> None:
        """Verify the Request Submitted confirmation popup with D# link is present."""
        logger.info("Verifying Request Submitted popup...")
        try:
            with open('reports/request_submitted_page.html', 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass
        logger.info(f"Current URL after DocuSign: {self.page.url}")
        link = self.page.locator(docusign_locators.REQUEST_SUBMITTED_LINK).first
        self.wait_for_element(link, state='visible', timeout=timeout)
        logger.info("Request Submitted popup confirmed  D# link is visible")

    def get_d_number_and_click(self, test_context: dict) -> str:
        """Get D# from Request Submitted popup, store in test_context, then click to navigate."""
        logger.info("Getting D# from Request Submitted popup...")
        link = self.page.locator(docusign_locators.REQUEST_SUBMITTED_LINK).first
        self.wait_for_element(link, state='visible', timeout=15000)
        d_number = link.inner_text().strip()
        logger.info(f"D# found: {d_number}")
        test_context['d_number'] = d_number
        link.click()
        logger.info(f"D# link clicked  navigating to Tracking Center")
        return d_number