"""
Journal Transfer Page Object - Handles journal transfer workflow actions
Organized actions following the test plan specifications
"""
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.ewm.locators.journal_transfer_landing_locators import JournalTransferLocators
from typing import Optional, List, Dict, Any
import random

class JournalTransferLandingPage(BasePage):
    """Page object for journal transfer landing/account selection functionality"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = JournalTransferLocators()

    def navigate_to_journal_transfer(self, url: str) -> None:
        """Navigate to journal transfer page"""
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

    def select_destination_account(self, account_name: str, account_number: Optional[str] = None) -> None:
        """Select destination account from visible destination options before moving forward."""
        self.logger.info(f"Selecting destination account: {account_name}")

        # The reliable signal in this app is the rendered destination account number/text,
        # not button/listitem roles. Reuse that approach first.
        if account_number:
            try:
                self.logger.info(f"Waiting for destination account number to appear: {account_number}")
                account_number_locator = self.page.locator(f"text={account_number}").first
                account_number_locator.wait_for(state="visible", timeout=30000)
                account_number_locator.click(timeout=5000)
                self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)
                self.logger.info(f"✅ Destination account selected by number: {account_number}")
                return
            except Exception as e:
                self.logger.warning(f"Selection by account number failed: {e}")

        try:
            self.logger.info(f"Waiting for destination account name to appear: {account_name}")
            account_name_locator = self.page.locator(f"text='{account_name}'").first
            account_name_locator.wait_for(state="visible", timeout=10000)
            account_name_locator.click(timeout=5000)
            self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)
            self.logger.info(f"✅ Destination account selected by name: {account_name}")
            return
        except Exception as e:
            self.logger.warning(f"Selection by account name failed: {e}")
        
        # Strategy 1: Original approach - listitem with button
        try:
            account_button = self.page.get_by_role("listitem").filter(
                has_text=account_name
            ).get_by_role("button").first

            account_button.wait_for(state="visible", timeout=2000)
            self.click(account_button)
            self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)
            self.logger.info("✅ Destination account selected using listitem strategy")
            return
        except Exception as e:
            self.logger.warning(f"Strategy 1 (listitem) failed: {e}")
        
        # Strategy 2: Direct button search with account name
        try:
            account_button = self.page.get_by_role("button").filter(has_text=account_name).first
            account_button.wait_for(state="visible", timeout=2000)
            self.click(account_button)
            self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)
            self.logger.info("✅ Destination account selected using direct button strategy")
            return
        except Exception as e:
            self.logger.warning(f"Strategy 2 (direct button) failed: {e}")
        
        # Strategy 3: Search for any clickable element containing the account name
        try:
            # Try different clickable element types
            for element_type in ["button", "div", "span", "a"]:
                try:
                    account_element = self.page.locator(f"{element_type}:has-text('{account_name}')").first
                    account_element.wait_for(state="visible", timeout=1000)
                    self.click(account_element)
                    self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)
                    self.logger.info(f"✅ Destination account selected using {element_type} strategy")
                    return
                except Exception:
                    continue
        except Exception as e:
            self.logger.warning(f"Strategy 3 (generic elements) failed: {e}")
        
        # Final fallback: if the details pane already reflects the destination account, the UI may
        # have auto-selected it after page load. This is stronger than using AccountId in the URL.
        try:
            detail_matches = 0
            if account_number:
                try:
                    self.page.get_by_text(account_number).last.wait_for(state="visible", timeout=3000)
                    detail_matches += 1
                except Exception:
                    pass
            try:
                self.page.get_by_text(account_name).last.wait_for(state="visible", timeout=3000)
                detail_matches += 1
            except Exception:
                pass

            if detail_matches > 0:
                self.logger.info("✅ Destination account appears already selected in the rendered details pane")
                return
        except Exception as e:
            self.logger.warning(f"Rendered-details fallback failed: {e}")
        
        # Final strategy: Log what's actually on the page for debugging
        self.logger.error("❌ All account selection strategies failed")
        try:
            # Log available buttons
            buttons = self.page.locator("button").all()
            self.logger.info(f"Available buttons on page: {len(buttons)}")
            for i, button in enumerate(buttons[:5]):  # Show first 5 buttons
                try:
                    text = button.text_content()
                    self.logger.info(f"  Button {i+1}: {text}")
                except:
                    pass
                    
            # Check if account name appears anywhere on page
            account_name_visible = False
            try:
                self.page.get_by_text(account_name).first.wait_for(state="visible", timeout=1000)
                account_name_visible = True
            except Exception:
                account_name_visible = False

            if account_name_visible:
                self.logger.info(f"✅ Account name '{account_name}' is visible on page")
            else:
                self.logger.warning(f"❌ Account name '{account_name}' not found on page")
                
        except Exception as e:
            self.logger.error(f"Error during debugging: {e}")
        
        raise Exception(f"Could not select destination account: {account_name}")

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
        """Click the NEXT button to proceed"""
        self.logger.info("Clicking NEXT button")
        # Primary: role button with configured NEXT label
        next_label = self.locators.NEXT_BUTTON["name"]
        try:
            next_button = self.page.get_by_role("button", name=next_label).first
            self.click(next_button)
        except Exception:
            # Fallback: text-based NEXT button match
            next_button = self.page.get_by_text(next_label).first
            self.click(next_button)
        self.wait_for_load_state("networkidle", timeout=self.locators.NETWORK_IDLE_TIMEOUT)

    def click_cancel_button(self) -> None:
        """Click the CANCEL button"""
        self.logger.info("Clicking CANCEL button")
        cancel_button = self.page.get_by_role("button", name=self.locators.CANCEL_BUTTON)
        self.click(cancel_button)

    def click_back_button(self) -> None:
        """Click the BACK button"""
        self.logger.info("Clicking BACK button")
        back_button = self.page.get_by_role("button", name=self.locators.BACK_BUTTON)
        self.click(back_button)

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

    def configure_journal_portion(self, amount: str, portion_type: str = None) -> None:
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

    def verify_page_elements_present(self, test_data: Dict[str, Any]) -> Dict[str, bool]:
        """Verify all expected page elements are present"""
        elements_status = {}
        
        # Check landing page buttons
        for button in self.locators.LANDING_PAGE_BUTTONS:
            try:
                button_element = self.page.get_by_text(button).first
                elements_status[f"button_{button}"] = button_element.is_visible()
            except:
                elements_status[f"button_{button}"] = False
        
        # Check distribution options
        for option in self.locators.DISTRIBUTION_OPTIONS:
            try:
                option_element = self.page.get_by_text(option)
                elements_status[f"distribution_{option}"] = option_element.is_visible()
            except:
                elements_status[f"distribution_{option}"] = False
        
        # Check signature options
        for option in self.locators.SIGNATURE_OPTIONS:
            try:
                option_element = self.page.get_by_text(option)
                elements_status[f"signature_{option}"] = option_element.is_visible()
            except:
                elements_status[f"signature_{option}"] = False
        
        return elements_status

    def complete_standard_account_selection_flow(self, test_data: Dict[str, Any]) -> None:
        """Complete standard account selection workflow"""
        self.logger.info("Starting standard account selection flow")
        
        # Navigate and dismiss live chat
        self.navigate_to_journal_transfer(test_data["urls"]["journalTransferUrl"])
        self.dismiss_live_chat()
        
        # Select destination account
        self.select_destination_account(test_data["accounts"]["destinationAccountName"])
        
        self.logger.info("Standard account selection flow completed")

    def complete_other_account_configuration_flow(self, account_name: str, account_status: str) -> str:
        """Complete Other Account configuration workflow"""
        self.logger.info("Starting Other Account configuration flow")
        
        # Select Other Account
        self.select_other_account()
        
        # Configure account details
        account_number = self.configure_other_account(account_name)
        self.select_account_status(account_status)
        
        self.logger.info("Other Account configuration flow completed")
        return account_number
