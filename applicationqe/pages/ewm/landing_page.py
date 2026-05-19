"""
Landing Page Object - Handles journal transfer account selection phase
Focused on account selection and navigation to transfer request
"""
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.ewm.locators.landing_page_locators import LandingPageLocators
from typing import Optional, Dict, Any
import random

class LandingPage(BasePage):
    """Page object for journal transfer landing page - account selection phase"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = LandingPageLocators()

    def navigate_to_journal_transfer(self, url: str) -> None:
        """Navigate to journal transfer landing page"""
        self.logger.info(f"Navigating to journal transfer page: {url}")
        self.navigate_to(url)
        self.wait_for_load_state("domcontentloaded")

    def dismiss_live_chat(self) -> bool:
        """Dismiss live chat popup if present"""
        self.logger.info("Attempting to dismiss live chat popup")
        try:
            close_button = self.page.locator(self.locators.LIVE_CHAT_CLOSE)
            close_button.wait_for(state="visible", timeout=self.locators.LIVE_CHAT_TIMEOUT)
            self.click(close_button)
            self.logger.info("Live chat popup dismissed")
            return True
        except Exception:
            self.logger.info("Live chat popup not present")
            return False

    def select_destination_account(self, account_name: str) -> None:
        """Select destination account from the available list"""
        self.logger.info(f"Selecting destination account: {account_name}")
        
        account_button = self.page.get_by_role(self.locators.DESTINATION_ACCOUNT_LISTITEM_ROLE).filter(
            has_text=account_name
        ).get_by_role(self.locators.DESTINATION_ACCOUNT_BUTTON_ROLE).first
        
        self.click(account_button)
        self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)
        self.logger.info("Destination account selected and page updated")

    def select_other_account(self) -> None:
        """Select 'Other Account' option"""
        self.logger.info("Selecting Other Account option")
        other_account_option = self.page.get_by_text("Other Account")
        self.click(other_account_option)

    def configure_other_account(self, account_name: str, account_number: Optional[str] = None) -> str:
        """Configure Other Account details"""
        self.logger.info(f"Configuring Other Account: {account_name}")
        
        # Fill account name
        name_field = self.page.get_by_test_id(self.locators.OTHER_ACCOUNT_NAME_INPUT)
        self.fill(name_field, account_name)
        
        # Generate or use provided account number
        if account_number is None:
            digit = str(random.randint(1, 8))
            account_number = digit * 8
            self.logger.info(f"Generated account number: {account_number}")
        
        # Fill account number
        number_field = self.page.get_by_test_id(self.locators.OTHER_ACCOUNT_NUMBER_INPUT)
        self.fill(number_field, account_number)
        
        # Confirm account number
        confirm_field = self.page.get_by_test_id(self.locators.OTHER_ACCOUNT_CONFIRM_INPUT)
        self.fill(confirm_field, account_number)
        
        # Check qualified checkbox
        qualified_checkbox = self.page.get_by_test_id(self.locators.QUALIFIED_CHECKBOX)
        qualified_checkbox.check()
        
        self.logger.info("Other Account configuration completed")
        return account_number

    def select_account_status(self, status: str) -> None:
        """Select account status radio button"""
        self.logger.info(f"Selecting account status: {status}")
        status_radio = self.page.get_by_role(self.locators.ACCOUNT_STATUS_RADIO, name=status)
        self.click(status_radio)

    def click_next_button(self) -> None:
        """Click the NEXT button to proceed to transfer request page"""
        self.logger.info("Clicking NEXT button to proceed to transfer request")
        next_button = self.page.get_by_role("button", name=self.locators.NEXT_BUTTON).first
        self.click(next_button)
        self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)

    def click_cancel_button(self) -> None:
        """Click the CANCEL button"""
        self.logger.info("Clicking CANCEL button")
        cancel_button = self.page.get_by_role("button", name=self.locators.CANCEL_BUTTON)
        self.click(cancel_button)

    def verify_landing_page_elements(self) -> Dict[str, bool]:
        """Verify landing page elements are present"""
        elements_status = {}
        
        # Check landing page buttons
        for button in self.locators.LANDING_PAGE_BUTTONS:
            try:
                button_element = self.page.get_by_text(button).first
                elements_status[f"button_{button}"] = button_element.is_visible()
            except:
                elements_status[f"button_{button}"] = False
        
        return elements_status

    def get_page_title(self) -> str:
        """Get the current page title"""
        return self.page.title()

    def is_transfer_heading_visible(self) -> bool:
        """Check if transfer heading is visible"""
        try:
            heading = self.page.get_by_text(self.locators.TRANSFER_HEADING)
            return heading.is_visible()
        except:
            return False

    def is_journal_text_visible(self) -> bool:
        """Check if journal text is visible"""
        try:
            journal_text = self.page.get_by_text(self.locators.JOURNAL_TEXT)
            return journal_text.is_visible()
        except:
            return False
