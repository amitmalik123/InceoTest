"""
Transfer Request Page Object - Handles transaction configuration phase
Focused on transaction details, amounts, and distribution types
"""
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.ewm.locators.transaction_details_locators import TransactionDetailsLocators
from typing import Optional, List, Dict, Any

class TransactionDetailsPage(BasePage):
    """Page object for transaction details configuration phase"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = TransferRequestPageLocators()

    def select_distribution_type(self, distribution_type: str) -> None:
        """Select distribution type radio button"""
        self.logger.info(f"Selecting distribution type: {distribution_type}")
        radio_button = self.page.get_by_role("radio", name=distribution_type)
        self.click(radio_button)

    def select_journal_portion_type(self, portion_type: str) -> None:
        """Select journal portion type: $ Amount or % Percentage"""
        self.logger.info(f"Selecting portion type: {portion_type}")
        portion_button = self.page.get_by_text(portion_type)
        self.click(portion_button)

    def enter_transfer_amount(self, amount: str) -> None:
        """Enter transfer amount in the amount field"""
        self.logger.info(f"Entering transfer amount: {amount}")
        amount_field = self.page.get_by_role(self.locators.AMOUNT_TEXTBOX_ROLE)
        self.fill(amount_field, amount)

    def configure_journal_portion(self, amount: str, portion_type: Optional[str] = None) -> None:
        """Configure journal portion transfer with amount and type"""
        self.logger.info("Configuring journal portion transfer")
        
        if portion_type:
            self.select_journal_portion_type(portion_type)
        
        self.enter_transfer_amount(amount)

    def select_all_securities(self, count: int = 2) -> List[bool]:
        """Select securities using All buttons"""
        self.logger.info(f"Selecting securities using All buttons (first {count})")
        
        all_buttons = self.page.get_by_role("button", name=self.locators.ALL_BUTTON_NAME).all()
        results = []
        
        for i, button in enumerate(all_buttons[:count]):
            try:
                self.click(button)
                results.append(True)
                self.logger.info(f"Successfully clicked All button {i+1}")
            except Exception as e:
                results.append(False)
                self.logger.warning(f"Could not click All button {i+1}: {str(e)}")
        
        return results

    def select_signature_option(self, signature_option: str) -> None:
        """Select signature option radio button"""
        self.logger.info(f"Selecting signature option: {signature_option}")
        radio_button = self.page.get_by_role("radio", name=signature_option)
        self.click(radio_button)

    def get_available_cash_amount(self) -> Optional[str]:
        """Get available cash amount from the page"""
        try:
            cash_element = self.page.locator("//div[span[text()='Cash Available:']]/following-sibling::div/span").first
            cash_text = cash_element.inner_text()
            self.logger.info(f"Available cash found: {cash_text}")
            return cash_text
        except Exception:
            self.logger.warning("Could not retrieve available cash amount")
            return None

    def calculate_amount_with_excess(self, available_cash: str, additional_amount: str) -> str:
        """Calculate total amount including excess for warning scenarios"""
        try:
            cash_value = float(available_cash.replace("$", "").replace(",", ""))
            extra_value = float(additional_amount.replace("$", "").replace(",", ""))
            total = cash_value + extra_value
            calculated_amount = f"{total:.2f}"
            self.logger.info(f"Calculated amount with excess: ${calculated_amount}")
            return calculated_amount
        except Exception as e:
            self.logger.error(f"Error calculating amount: {e}")
            return additional_amount

    def click_next_button(self) -> None:
        """Click the NEXT button to proceed to review page"""
        self.logger.info("Clicking NEXT button to proceed to review")
        next_button = self.page.get_by_role("button", name=self.locators.NEXT_BUTTON).first
        self.click(next_button)
        self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)

    def click_back_button(self) -> None:
        """Click the BACK button to return to landing page"""
        self.logger.info("Clicking BACK button")
        back_button = self.page.get_by_role("button", name=self.locators.BACK_BUTTON)
        self.click(back_button)

    def click_cancel_button(self) -> None:
        """Click the CANCEL button"""
        self.logger.info("Clicking CANCEL button")
        cancel_button = self.page.get_by_role("button", name=self.locators.CANCEL_BUTTON)
        self.click(cancel_button)

    def verify_distribution_options(self) -> Dict[str, bool]:
        """Verify all distribution options are present"""
        elements_status = {}
        
        for option in self.locators.DISTRIBUTION_OPTIONS:
            try:
                option_element = self.page.get_by_text(option)
                elements_status[f"distribution_{option}"] = option_element.is_visible()
            except:
                elements_status[f"distribution_{option}"] = False
        
        return elements_status

    def verify_signature_options(self) -> Dict[str, bool]:
        """Verify all signature options are present"""
        elements_status = {}
        
        for option in self.locators.SIGNATURE_OPTIONS:
            try:
                option_element = self.page.get_by_text(option)
                elements_status[f"signature_{option}"] = option_element.is_visible()
            except:
                elements_status[f"signature_{option}"] = False
        
        return elements_status

    def verify_transaction_page_elements(self) -> Dict[str, bool]:
        """Verify transaction page elements are present"""
        elements_status = {}
        
        # Check transaction page buttons
        for button in self.locators.TRANSACTION_PAGE_BUTTONS:
            try:
                button_element = self.page.get_by_text(button).first
                elements_status[f"button_{button}"] = button_element.is_visible()
            except:
                elements_status[f"button_{button}"] = False
        
        # Combine with other verification methods
        elements_status.update(self.verify_distribution_options())
        elements_status.update(self.verify_signature_options())
        
        return elements_status

    def is_amount_field_visible(self) -> bool:
        """Check if amount input field is visible"""
        try:
            amount_field = self.page.get_by_role(self.locators.AMOUNT_TEXTBOX_ROLE)
            return amount_field.is_visible()
        except:
            return False

    def get_approximate_percentage(self) -> Optional[str]:
        """Get the approximate percentage text if visible"""
        try:
            approx_element = self.page.get_by_text(self.locators.APPROX_TEXT)
            if approx_element.is_visible():
                return approx_element.inner_text()
            return None
        except:
            return None

    def is_warning_message_visible(self) -> bool:
        """Check if warning message is visible"""
        try:
            warning_element = self.page.locator(self.locators.JOURNAL_PORTION_WARNING_SELECTOR)
            return warning_element.is_visible()
        except:
            return False
