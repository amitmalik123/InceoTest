from playwright.sync_api import FrameLocator, Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.shared.locators.esign_signer_information_locators import ESignSignerInformationLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ESignSignerInformationPage(BasePage):
    """Page object for the Signer(s) Information iframe page (eSigUserDetails.aspx)."""

    def __init__(self, page: Page, frame: FrameLocator = None):
        super().__init__(page)
        loc = ESignSignerInformationLocators
        self.frame: FrameLocator = frame if frame is not None else page.frame_locator(loc.IFRAME)

        self.page_title: Locator = self.frame.locator(loc.PAGE_TITLE)

        self._first_signer_row: Locator = self.frame.locator(loc.FIRST_SIGNER_ROW).first

        self.first_signer_name_input: Locator = self._first_signer_row.locator(
            loc.TEXT_INPUT
        ).nth(0)
        self.first_signer_email_input: Locator = self._first_signer_row.locator(
            loc.TEXT_INPUT
        ).nth(1)
        self.first_signer_phone_input: Locator = self._first_signer_row.locator(
            loc.TEXT_INPUT
        ).nth(2)

        self.first_signer_in_person_radio: Locator = self._first_signer_row.locator(
            loc.RADIO_INPUT
        ).nth(0)
        self.first_signer_by_email_radio: Locator = self._first_signer_row.locator(
            loc.RADIO_INPUT
        ).nth(1)

        self.continue_button: Locator = self.frame.locator("#btnContinue")

    def verify_signer_information_page(self, timeout: int = 20000) -> None:
        """Assert the Signer(s) Information page is visible inside the iframe."""
        logger.info("Verifying Signer(s) Information page is loaded inside esig_iframe")
        self.page_title.wait_for(state="visible", timeout=timeout)
        title_text = self.page_title.inner_text()
        assert "Signer" in title_text and "Information" in title_text, (
            f"Expected 'Signer(s) Information' title, got: '{title_text}'"
        )
        logger.info(f"[OK] Signer Information page loaded — title: '{title_text.strip()}'")

    def enter_signer_full_name(self, name: str) -> None:
        """Fill the Signer's Full Name field for the first signer row."""
        logger.info(f"Entering signer full name: '{name}'")
        self.first_signer_name_input.wait_for(state="visible", timeout=10000)
        self.first_signer_name_input.clear()
        self.first_signer_name_input.fill(name)
        entered = self.first_signer_name_input.input_value()
        assert entered == name, f"Name field mismatch — expected '{name}', got '{entered}'"
        logger.info(f"[OK] Signer name entered: '{entered}'")

    def enter_signer_email(self, email: str) -> None:
        """Fill the Email Address field for the first signer row."""
        logger.info(f"Entering signer email: '{email}'")
        self.first_signer_email_input.wait_for(state="visible", timeout=10000)
        self.first_signer_email_input.clear()
        self.first_signer_email_input.fill(email)
        entered = self.first_signer_email_input.input_value()
        assert entered == email, f"Email field mismatch — expected '{email}', got '{entered}'"
        logger.info(f"[OK] Signer email entered: '{entered}'")

    def enter_signer_phone(self, phone: str) -> None:
        """Fill the Phone Number field for the first signer row."""
        logger.info(f"Entering signer phone: '{phone}'")
        self.first_signer_phone_input.wait_for(state="visible", timeout=10000)
        self.first_signer_phone_input.clear()
        self.first_signer_phone_input.fill(phone)
        entered = self.first_signer_phone_input.input_value()
        entered_digits = "".join(c for c in entered if c.isdigit())
        expected_digits = "".join(c for c in phone if c.isdigit())
        assert entered_digits == expected_digits, (
            f"Phone field mismatch — expected digits '{expected_digits}', got '{entered}'"
        )
        logger.info(f"[OK] Signer phone entered: '{entered}'")

    def select_email_radio_button(self) -> None:
        """Select the 'By Email' eSign method radio for the first signer row."""
        logger.info("Selecting 'By Email' radio button for first signer")
        self.first_signer_by_email_radio.wait_for(state="visible", timeout=10000)
        self.first_signer_by_email_radio.click()
        assert self.first_signer_by_email_radio.is_checked(), (
            "'By Email' radio button was not selected after click"
        )
        logger.info("[OK] 'By Email' radio button selected")

    def click_continue_button(self) -> None:
        """Click the Continue button and wait for any navigation."""
        logger.info("Clicking Continue button on Signer Information page")
        self.continue_button.wait_for(state="visible", timeout=60000)
        assert self.continue_button.is_enabled(), "Continue button is disabled — cannot proceed"
        self.continue_button.click()
        logger.info("[OK] Continue button clicked")

    def fill_signer_information(
        self,
        name: str,
        email: str,
        phone: str,
    ) -> None:
        """
        Complete the Signer(s) Information form for the first signer row:
          1. Verify page loaded
          2. Enter name, email, phone
          3. Select 'By Email' radio
          4. Click Continue
          5. Click Submit
        """
        logger.info("--- Filling Signer Information (first signer only) ---")
        self.verify_signer_information_page()
        self.enter_signer_full_name(name)
        self.enter_signer_email(email)
        self.enter_signer_phone(phone)
        self.select_email_radio_button()
        self.click_continue_button()
        logger.info("--- Signer Information form submitted ---")
