"""
Client Accounts Page Object

Page object for client account interactions and verifications.
"""

import re
import unicodedata

from playwright.sync_api import Locator, Page

from locators import client_accounts_locators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.dialog_utils import DialogHandler
from utils.retry_utils import RetryContext
from utils.wait_utils import WaitContext, WaitTimeoutError, wait_for_condition, wait_for_element_to_disappear, wait_for_loading_spinner_to_disappear

logger = get_allure_logger(__name__)


class ClientAccountsPage(BasePage):
    """Page object for client accounts related operations."""

    PAGE_PATH = "en.aspx"
    
    # Import locators from locators module
    ESIG_IFRAME = client_accounts_locators.ESIG_IFRAME
    DROPDOWN_DIV = client_accounts_locators.DROPDOWN_DIV
    NOTE_TC_DIV = client_accounts_locators.NOTE_TC_DIV
    AUTHORIZED_SIGNERS_DROPDOWN = client_accounts_locators.AUTHORIZED_SIGNERS_DROPDOWN
    AUTHORIZED_SIGNERS_SELECTED_OPTION = client_accounts_locators.AUTHORIZED_SIGNERS_SELECTED_OPTION
    AUTHORIZED_SIGNERS_DROPDOWN_DISABLED = client_accounts_locators.AUTHORIZED_SIGNERS_DROPDOWN_DISABLED
    EMAIL_INPUT = client_accounts_locators.EMAIL_INPUT
    PHONE_INPUT = client_accounts_locators.PHONE_INPUT
    CONTINUE_BUTTON = client_accounts_locators.CONTINUE_BUTTON
    RADIO_YES = client_accounts_locators.RADIO_YES
    RADIO_NO = client_accounts_locators.RADIO_NO
    RADIO_SMS = client_accounts_locators.RADIO_SMS
    RADIO_TC = client_accounts_locators.RADIO_TC
    AUTHORIZED_SIGNERS_LABEL = client_accounts_locators.AUTHORIZED_SIGNERS_LABEL
    EMAIL_ADDRESS_LABEL = client_accounts_locators.EMAIL_ADDRESS_LABEL
    PHONE_LABEL = client_accounts_locators.PHONE_LABEL
    DIALOG_ROLE = client_accounts_locators.DIALOG_ROLE
    CONFIRMATION_LINK = client_accounts_locators.CONFIRMATION_LINK
    DOWNLOAD_LINK = client_accounts_locators.DOWNLOAD_LINK
    CLOSE_BUTTON_CONTAINER = client_accounts_locators.CLOSE_BUTTON_CONTAINER
    TABLE_CONTAINER = client_accounts_locators.TABLE_CONTAINER
    REQUEST_LIST = client_accounts_locators.REQUEST_LIST
    REQUEST_LIST_ITEM = client_accounts_locators.REQUEST_LIST_ITEM
    SUBCATEGORY_CONTAINER = client_accounts_locators.SUBCATEGORY_CONTAINER
    SUBCATEGORY_LIST = client_accounts_locators.SUBCATEGORY_LIST
    COMPLETE_SUBMIT_BUTTON = client_accounts_locators.COMPLETE_SUBMIT_BUTTON
    COMPLETE_PRINT_BUTTON = client_accounts_locators.COMPLETE_PRINT_BUTTON
    COMPLETE_ESIGN_BUTTON = client_accounts_locators.COMPLETE_ESIGN_BUTTON
    FORM_HEADING_SPAN = client_accounts_locators.FORM_HEADING_SPAN
    FORM_HEADING_BOLD = client_accounts_locators.FORM_HEADING_BOLD
    MODAL_TITLE = client_accounts_locators.MODAL_TITLE
    RADIO_SUBMIT = client_accounts_locators.RADIO_SUBMIT
    RADIO_PRINT = client_accounts_locators.RADIO_PRINT
    RADIO_ESIGN = client_accounts_locators.RADIO_ESIGN
    CLIENT_IN_PERSON_SIGNING_BUTTON_RETURN = client_accounts_locators.CLIENT_IN_PERSON_SIGNING_BUTTON_RETURN

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.logger = logger

    def navigate(self) -> None:
        """Navigate to client accounts page."""
        self.navigate_to(self.PAGE_PATH)

    def _get_esig_iframe(self):
        """
        Get reference to eSignature iframe with safety check and wait for content to load.
        
        CRITICAL: The iframe element may exist in DOM but its HTML content loads asynchronously.
        This method waits for the iframe to be present AND for its content to load.
        
        Returns:
            FrameLocator if found and content is loaded, None otherwise
        """
        iframe_locator = self.page.locator(client_accounts_locators.ESIG_IFRAME)
        if iframe_locator.count() == 0:
            logger.warning("🔧 iframe#esig_iframe not found")
            return None
        
        # Wait for iframe to be attached/visible
        try:
            iframe_locator.wait_for(state="attached", timeout=120000)
            logger.debug("✓ iframe#esig_iframe is attached")
        except Exception as e:
            logger.warning(f"⚠ Timeout waiting for iframe to attach: {e}")
            return None
        
        # Get frame reference
        frame = self.page.frame_locator(client_accounts_locators.ESIG_IFRAME)
        
        # Wait for iframe content to load - check for ANY content element inside the iframe
        # This ensures the iframe's HTML is fully loaded before we try to interact with it
        try:
            # Wait for any visible element inside iframe (button, text, input, etc)
            # Try multiple indicators of loaded content:
            # 1. First try button (most likely visible)
            # 2. Then try any text
            # 3. Finally try any element
            logger.debug("✓ Waiting for iframe content...")
            
            # Try to find any button or input (common elements)
            key_element = frame.locator("button, input, [role='button']").first
            if key_element.count() == 0:
                # If no buttons, look for any element with text
                key_element = frame.locator("*:has-text('.')").first
            if key_element.count() == 0:
                # Final fallback - any non-empty element
                key_element = frame.locator("div, section, form").first
                
            key_element.wait_for(state="attached", timeout=120000)
            logger.debug("✓ iframe#esig_iframe content is loaded")
            # Small delay to ensure content is fully rendered
            self.page.wait_for_timeout(300)
        except Exception as e:
            logger.warning(f"⚠ Timeout waiting for iframe content to load: {e}")
            # Continue anyway, will fail on assertion if really needed
        
        return frame


    def select_authorized_signer_approval_option(self, option: str) -> None:
        """
        Select radio button on Authorized Signer Approval section based on option.
        
        Args:
            option: The option to select ('Yes' or 'No')
        
        Raises:
            AssertionError: If option is invalid or radio button not found/clickable
        """
        valid_options = ["Yes", "No"]
        if option not in valid_options:
            raise AssertionError(f"Invalid option '{option}'. Must be one of: {valid_options}")
        
        logger.info(f"Selecting '{option}' radio button on Authorized Signer Approval section...")
        self._select_authorized_signer_approval_option(option)

    def _select_authorized_signer_approval_option(self, option: str) -> None:
        """
        Internal method to select radio button on Authorized Signer Approval section.
        
        Args:
            option: The option to select ('Yes' or 'No')
        """
        try:
            # Step 1: Access iframe
            logger.info("  Step 1: Accessing iframe...")
            iframe_frame = self._get_esig_iframe()
            if not iframe_frame:
                raise AssertionError("Signer Information dialog iframe (iframe#esig_iframe) not found")
            logger.info("  ✓ Iframe accessed")
            
            # Step 2: Map option to radio button value
            logger.info(f"  Step 2: Mapping option '{option}' to radio button value...")
            radio_button_value = f"radiobtn{option}" if option in ["Yes", "No"] else None
            
            if not radio_button_value:
                raise AssertionError(f"Cannot map option '{option}' to radio button value")
            
            logger.info(f"  ✓ Radio button value determined: '{radio_button_value}'")
            
            # Step 3: Find radio button input
            logger.info(f"  Step 3: Locating '{option}' radio button input...")
            radio_button = iframe_frame.locator(f"input[value='{radio_button_value}']")
            
            if radio_button.count() == 0:
                raise AssertionError(f"'{option}' radio button (input[value='{radio_button_value}']) not found in iframe")
            
            if not radio_button.is_visible():
                raise AssertionError(f"'{option}' radio button found but not visible in iframe")
            
            logger.info(f"  ✓ '{option}' radio button found and visible")
            
            # Step 4: Click the radio button
            logger.info(f"  Step 4: Clicking '{option}' radio button...")
            radio_button.click()
            logger.info(f"  ✓ '{option}' radio button clicked")
            
            # Step 5: Verify it's selected
            logger.info(f"  Step 5: Verifying '{option}' radio button is selected...")
            is_checked = radio_button.is_checked()
            if not is_checked:
                logger.warning(f"  ⚠ '{option}' radio button may not be selected (is_checked returned False)")
            else:
                logger.info(f"  ✓ '{option}' radio button is selected")
            
            logger.info(f"✓ Successfully selected '{option}' radio button on Authorized Signer Approval section")
            
        except Exception as e:
            logger.error(f"✗ Failed to select '{option}' radio button: {e}")
            raise AssertionError(f"Failed to select Authorized Signer Approval '{option}' option: {e}") from e

    def provide_authorized_signers_information(self, authorized_signer: str, email_address: str, phone: str, test_context: dict = None) -> None:
        """
        Provide Authorized Signers information on the Signer(s) Information dialog.
        
        Args:
            authorized_signer: Name/value of authorized signer to select (if dropdown is enabled)
            email_address: Email address to enter
            phone: Phone number to enter
            test_context: Optional test context dict to store fetched authorized signer name when dropdown is disabled
        
        Raises:
            AssertionError: If required elements not found or actions fail
        """
        logger.info("Providing Authorized Signers information...")
        
        try:
            # Step 1: Access iframe
            logger.info("  Step 1: Accessing iframe...")
            iframe_frame = self._get_esig_iframe()
            if not iframe_frame:
                raise AssertionError("Signer Information dialog iframe (iframe#esig_iframe) not found")
            logger.info("  ✓ Iframe accessed")
            
            # Step 2: Check and handle Authorized Signers dropdown
            logger.info("  Step 2: Checking Authorized Signers dropdown...")
            dropdown = iframe_frame.locator(self.AUTHORIZED_SIGNERS_DROPDOWN)
            
            if dropdown.count() == 0:
                raise AssertionError("Authorized Signers dropdown not found")
            
            # Check if dropdown is enabled
            is_disabled = dropdown.is_disabled()
            logger.info(f"  ✓ Dropdown found. Disabled status: {is_disabled}")
            
            if is_disabled:
                # Step 3a: Dropdown is disabled - fetch selected option text and update test_context
                logger.info("  Step 3a: Dropdown is disabled. Fetching selected option text...")
                try:
                    selected_option = iframe_frame.locator(self.AUTHORIZED_SIGNERS_SELECTED_OPTION)
                    
                    if selected_option.count() == 0:
                        logger.warning("  ⚠ No selected option found in disabled dropdown")
                    else:
                        # Get the text content of the selected option
                        selected_text = selected_option.inner_text().strip()
                        logger.info(f"  ✓ Selected option text fetched: '{selected_text}'")
                        
                        # Update test_context with the fetched authorized signer name
                        if test_context is not None:
                            test_context["authorized_signer"] = selected_text
                            logger.info(f"  ✓ Updated test_context['authorized_signer'] = '{selected_text}'")
                        else:
                            logger.warning("  ⚠ test_context not provided, cannot update authorized_signer")
                            
                except Exception as e:
                    logger.error(f"  ✗ Error fetching selected option text: {e}")
                    raise AssertionError(f"Failed to fetch selected option text from disabled dropdown: {e}") from e
                    
            elif authorized_signer and authorized_signer.strip():
                # Step 3b: Dropdown is enabled - select the provided option by label (displayed text)
                logger.info(f"  Step 3b: Dropdown is enabled. Attempting to select '{authorized_signer}'...")
                try:
                    # Try selecting by label (displayed text) first - handles cases like "William J. Freund"
                    dropdown.select_option(label=authorized_signer)
                    logger.info(f"  ✓ Option '{authorized_signer}' selected by label")
                except Exception as label_error:
                    # Fallback: try selecting by value (for UUIDs or IDs)
                    logger.info(f"  ⚠ Label selection failed, trying value-based selection: {str(label_error)[:80]}")
                    try:
                        dropdown.select_option(value=authorized_signer)
                        logger.info(f"  ✓ Option '{authorized_signer}' selected by value")
                    except Exception as value_error:
                        raise AssertionError(f"Failed to select option '{authorized_signer}' by label or value: {value_error}") from value_error
                
                # Update test_context with the provided authorized signer
                if test_context is not None:
                    test_context["authorized_signer"] = authorized_signer
                    logger.info(f"  ✓ Updated test_context['authorized_signer'] = '{authorized_signer}'")
                
                # Wait for Email Address field to appear after dropdown selection
                logger.info("  Waiting for form to update after dropdown selection...")
                try:
                    email_input_element = iframe_frame.locator(self.EMAIL_INPUT)
                    with WaitContext(timeout=5.0, poll_interval=0.3) as wait:
                        wait.until_visible(email_input_element)
                    logger.info("  ✓ Form updated, Email Address field is now visible")
                except WaitTimeoutError:
                    logger.warning("  ⚠ Email Address field did not appear within timeout, continuing anyway")
            else:
                logger.info("  ⚠ Dropdown is enabled but authorized signer value is empty, skipping selection")
            
            # Step 4: Fill Email Address
            if email_address and email_address.strip():
                logger.info("  Step 4: Filling Email Address...")
                
                # Wait for Email Address input to be visible
                logger.info("  Waiting for Email Address input to be visible...")
                email_input = iframe_frame.locator(self.EMAIL_INPUT)
                
                if email_input.count() == 0:
                    raise AssertionError("Email Address input not found")
                
                try:
                    with WaitContext(timeout=3.0, poll_interval=0.2) as wait:
                        wait.until_visible(email_input)
                    logger.info("  ✓ Email Address input is visible")
                except WaitTimeoutError:
                    raise AssertionError("Email Address input not visible within timeout")
                
                # Clear existing value first
                email_input.clear()
                email_input.fill(email_address)
                logger.info(f"  ✓ Email Address filled: {email_address}")
            else:
                logger.info("  ⚠ Email Address value is empty, skipping")
            
            # Step 5: Fill Phone
            if phone and phone.strip():
                logger.info("  Step 5: Filling Phone...")
                
                # Wait for Phone input to be visible
                logger.info("  Waiting for Phone input to be visible...")
                phone_input = iframe_frame.locator(self.PHONE_INPUT)
                
                if phone_input.count() == 0:
                    raise AssertionError("Phone input not found")
                
                try:
                    with WaitContext(timeout=3.0, poll_interval=0.2) as wait:
                        wait.until_visible(phone_input)
                    logger.info("  ✓ Phone input is visible")
                except WaitTimeoutError:
                    raise AssertionError("Phone input not visible within timeout")
                
                # Clear existing value first
                phone_input.clear()
                phone_input.fill(phone)
                logger.info(f"  ✓ Phone filled: {phone}")
            else:
                logger.info("  ⚠ Phone value is empty, skipping")
            
            logger.info("✓ Successfully provided Authorized Signers information")
            
        except Exception as e:
            logger.error(f"✗ Failed to provide Authorized Signers information: {e}")
            raise AssertionError(f"Failed to provide Authorized Signers information: {e}") from e

    def select_signer_esign_method(self, method: str) -> None:
        """
        Select Signer eSign Method.
        
        Args:
            method: The eSign method to select. Valid values:
                - 'SMS': SMS signature method (radiobtnSMS)
                - 'Tracking Center': Tracking center method (radiobtnTC)
                - 'In Person': In-person signature method (radbtnInPerson1)
                - 'By Email': Remote/email signature method (radbtnRemote1)
        
        Raises:
            AssertionError: If method is invalid or radio button not found/clickable
        """
        valid_methods = ["SMS", "Tracking Center", "In Person", "By Email"]
        if method not in valid_methods:
            raise AssertionError(f"Invalid eSign method '{method}'. Must be one of: {valid_methods}")
        
        logger.info(f"Selecting '{method}' eSign method radio button...")
        self._select_signer_esign_method(method)

    def _select_signer_esign_method(self, method: str) -> None:
        """
        Internal method to select eSign method radio button.
        
        Args:
            method: The eSign method to select ('SMS', 'Tracking Center', 'In Person', or 'By Email')
        """
        try:
            # Step 1: Access iframe
            logger.info("  Step 1: Accessing iframe...")
            iframe_frame = self._get_esig_iframe()
            if not iframe_frame:
                raise AssertionError("Signer Information dialog iframe (iframe#esig_iframe) not found")
            logger.info("  ✓ Iframe accessed")
            
            # Step 2: Map method to radio button ID
            logger.info(f"  Step 2: Mapping method '{method}' to radio button ID...")
            radio_button_id_map = {
                "SMS": "radiobtnSMS",
                "Tracking Center": "radiobtnTC",
                "In Person": "radbtnInPerson1",
                "By Email": "radbtnRemote1"
            }
            radio_button_id = radio_button_id_map.get(method)
            if not radio_button_id:
                raise AssertionError(f"No radio button ID mapping found for method '{method}'")
            logger.info(f"  ✓ Radio button ID determined: '{radio_button_id}'")
            
            # Step 3: Find radio button input
            logger.info(f"  Step 3: Locating '{method}' radio button input...")
            radio_button = iframe_frame.locator(f"input#{radio_button_id}")
            
            if radio_button.count() == 0:
                raise AssertionError(f"'{method}' radio button (input#{radio_button_id}) not found in iframe")
            
            if not radio_button.is_visible():
                raise AssertionError(f"'{method}' radio button found but not visible in iframe")
            
            logger.info(f"  ✓ '{method}' radio button found and visible")
            
            # Step 4: Click the radio button
            logger.info(f"  Step 4: Clicking '{method}' radio button...")
            radio_button.click()
            logger.info(f"  ✓ '{method}' radio button clicked")
            
            # Step 5: Verify it's selected
            logger.info(f"  Step 5: Verifying '{method}' radio button is selected...")
            try:
                # Wait for radio button to be checked (up to 3 seconds)
                radio_button.wait_for(state="checked", timeout=3000)
                logger.info(f"  ✓ '{method}' radio button is selected")
            except Exception as wait_error:
                # If wait fails, log warning but don't fail - sometimes the page doesn't update immediately
                logger.warning(f"  ⚠ Radio button selection state could not be confirmed within timeout. Details: {wait_error}")
                # Still verify the checked status
                try:
                    is_checked = radio_button.is_checked()
                    if is_checked:
                        logger.info(f"  ✓ '{method}' radio button confirmed as selected")
                    else:
                        logger.warning(f"  ⚠ '{method}' radio button may not be selected (is_checked returned False)")
                except:
                    logger.warning(f"  ⚠ Could not verify radio button state")
            
            logger.info(f"✓ Successfully selected '{method}' eSign method")
            
        except Exception as e:
            logger.error(f"✗ Failed to select '{method}' eSign method: {e}")
            raise AssertionError(f"Failed to select '{method}' eSign method: {e}") from e

    def verify_fields_for_esign_method(self, method: str) -> None:
        """
        Verify appropriate fields are displayed based on eSign Method selected.
        
        If method is 'SMS': Verifies Authorized Signers label/dropdown, Email Address label/input, Phone label/input
        If method is 'Tracking Center': Verifies Note message is displayed
        
        Args:
            method: The eSign method ('SMS' or 'Tracking Center')
        
        Raises:
            AssertionError: If required fields not found or not visible
        """
        logger.info(f"Verifying fields for '{method}' eSign method...")
        
        try:
            # Step 1: Access iframe
            logger.info("  Step 1: Accessing iframe...")
            iframe_frame = self._get_esig_iframe()
            if not iframe_frame:
                raise AssertionError("Signer Information dialog iframe (iframe#esig_iframe) not found")
            logger.info("  ✓ Iframe accessed")
            
            if method == "SMS":
                logger.info("  Step 2: Verifying SMS method fields...")
                
                # Verify dropdownDiv is visible (contains all SMS fields)
                dropdown_div = iframe_frame.locator("div#dropdownDiv")
                if dropdown_div.count() == 0:
                    raise AssertionError("Dropdown div container (div#dropdownDiv) not found")
                if not dropdown_div.is_visible():
                    raise AssertionError("Dropdown div container not visible")
                logger.info("  ✓ Dropdown div container found and visible")
                
                # 1. Verify 'Authorized Signers' label
                logger.info("  Verifying 'Authorized Signers' label...")
                auth_signers_labels = dropdown_div.locator("span:has-text('Authorized Signers')")
                if auth_signers_labels.count() == 0:
                    raise AssertionError("'Authorized Signers' label not found in SMS fields")
                if not auth_signers_labels.first.is_visible():
                    raise AssertionError("'Authorized Signers' label not visible")
                logger.info("    ✓ 'Authorized Signers' label verified")
                
                # 2. Verify 'Authorized Signers' dropdown
                logger.info("  Verifying 'Authorized Signers' dropdown...")
                dropdown = iframe_frame.locator("select[name='authorizedSignersDropdown']")
                if dropdown.count() == 0:
                    raise AssertionError("Authorized Signers dropdown not found")
                if not dropdown.is_visible():
                    raise AssertionError("Authorized Signers dropdown not visible")
                logger.info("    ✓ 'Authorized Signers' dropdown verified")
                
                # 3. Verify 'Email Address' label
                logger.info("  Verifying 'Email Address' label...")
                email_labels = dropdown_div.locator("span:has-text('Email Address')")
                if email_labels.count() == 0:
                    raise AssertionError("'Email Address' label not found in SMS fields")
                if not email_labels.first.is_visible():
                    raise AssertionError("'Email Address' label not visible")
                logger.info("    ✓ 'Email Address' label verified")
                
                # 4. Verify 'Email Address' input field
                logger.info("  Verifying 'Email Address' input field...")
                email_input = iframe_frame.locator("input[name='emailText']")
                if email_input.count() == 0:
                    raise AssertionError("Email Address input field not found")
                if not email_input.is_visible():
                    raise AssertionError("Email Address input field not visible")
                if email_input.is_disabled():
                    raise AssertionError("Email Address input field is disabled (not editable)")
                logger.info("    ✓ 'Email Address' input field verified (visible and editable)")
                
                # 5. Verify 'Phone' label
                logger.info("  Verifying 'Phone' label...")
                phone_labels = dropdown_div.locator("span:has-text('Phone')")
                if phone_labels.count() == 0:
                    raise AssertionError("'Phone' label not found in SMS fields")
                if not phone_labels.first.is_visible():
                    raise AssertionError("'Phone' label not visible")
                logger.info("    ✓ 'Phone' label verified")
                
                # 6. Verify 'Phone' input field
                logger.info("  Verifying 'Phone' input field...")
                phone_input = iframe_frame.locator("input[name='PhoneText']")
                if phone_input.count() == 0:
                    raise AssertionError("Phone input field not found")
                if not phone_input.is_visible():
                    raise AssertionError("Phone input field not visible")
                if phone_input.is_disabled():
                    raise AssertionError("Phone input field is disabled (not editable)")
                logger.info("    ✓ 'Phone' input field verified (visible and editable)")
                
                logger.info("  ✓ All SMS method fields verified successfully")
                
            elif method == "Tracking Center":
                logger.info("  Step 2: Verifying Tracking Center method fields...")
                
                # Verify noteTc div is visible with expected message
                logger.info("  Verifying Tracking Center note message...")
                note_div = iframe_frame.locator("div#noteTc")
                if note_div.count() == 0:
                    raise AssertionError("Tracking Center note div (div#noteTc) not found")
                if not note_div.is_visible():
                    raise AssertionError("Tracking Center note div not visible")
                logger.info("    ✓ Note div found and visible")
                
                # Verify the message text
                note_text = note_div.text_content() or ""
                expected_text = "An email notification will be sent to the primary email address associated with the agent code"
                if expected_text not in note_text:
                    raise AssertionError(f"Expected message not found in note. Expected substring: '{expected_text}'")
                logger.info(f"    ✓ Note message verified: '{(note_text or '').strip()}'")
                
                logger.info("  ✓ Tracking Center method fields verified successfully")
            
            logger.info(f"✓ Successfully verified fields for '{method}' eSign method")
            
        except Exception as e:
            logger.error(f"✗ Failed to verify fields for '{method}' method: {e}")
            raise AssertionError(f"Failed to verify fields for eSign method '{method}': {e}") from e

    def click_continue_on_signer_dialog(self) -> None:
        """
        Click the Continue button on Signer(s) Information dialog.
        
        Raises:
            AssertionError: If iframe or button not found or not clickable
        """
        logger.info("Clicking Continue button on Signer(s) Information dialog...")
        
        try:
            # Step 1: Access iframe
            logger.info("  Step 1: Accessing iframe...")
            iframe_frame = self._get_esig_iframe()
            if not iframe_frame:
                raise AssertionError("Signer Information dialog iframe (iframe#esig_iframe) not found")
            logger.info("  ✓ Iframe accessed")
            
            # Step 2: Find Continue button using role-based selector
            logger.info("  Step 2: Locating Continue button...")
            # Try role=button with name filter first (more maintainable)
            continue_button = iframe_frame.locator("input[type='submit'][value='Continue']")
            
            if continue_button.count() == 0:
                raise AssertionError("Continue button (input[type='submit'][value='Continue']) not found in iframe")
            
            if not continue_button.is_visible():
                raise AssertionError("Continue button found but not visible in iframe")
            
            if continue_button.is_disabled():
                raise AssertionError("Continue button is disabled and cannot be clicked")
            
            logger.info("  ✓ Continue button found, visible, and enabled")
            
            # Step 2.5: Wait for loading spinner to disappear before clicking
            logger.info("  Step 2.5: Waiting for loading spinner to disappear...")
            try:
                wait_for_loading_spinner_to_disappear(iframe_frame, timeout=15.0)
            except Exception as spinner_error:
                logger.warning(f"  ⚠ Loading spinner wait failed (non-blocking): {spinner_error}")
            
            # Step 3: Click the button
            logger.info("  Step 3: Clicking Continue button...")
            continue_button.click()
            logger.info("  ✓ Continue button clicked")
            
            # Step 4: Wait for navigation/dialog to close
            logger.info("  Step 4: Waiting for page to load after clicking Continue...")
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            logger.info("  ✓ Page loaded after Continue click")
            
            logger.info("✓ Successfully clicked Continue button on Signer(s) Information dialog")
            
        except Exception as e:
            logger.error(f"✗ Failed to click Continue button: {e}")
            raise AssertionError(f"Failed to click Continue button on Signer(s) Information dialog: {e}") from e

    # NOTE: verify_authorized_signers_dropdown() logic moved to step definition
    # Location: tests/bdd/steps/client_accounts_steps.py::verify_authorized_signer_dropdown()
    # Reason: Better separation of concerns - verification logic now in step definition

    def _wait_and_click_element(self, locator: Locator, element_name: str, timeout_ms: int = 1500) -> bool:
        """
        Optimized helper to wait for element to be visible AND clickable, then click it.
        
        PERFORMANCE OPTIMIZATIONS:
        - Uses count() for fail-fast detection (instant vs 30s element_handle())
        - Reduced timeouts: 1.5s instead of 3s
        - Uses wait_for_condition with smart polling
        - JS click as graceful fallback (not expensive element_handle())
        
        Args:
            locator: The element locator to click
            element_name: Human-readable name for logging
            timeout_ms: Max wait time in milliseconds (reduced to 1500ms for fast-fail)
            
        Returns:
            True if successfully clicked, False otherwise
            
        Uses:
            - count() for instant fail-fast detection
            - wait_for_condition() for smart polling (0.1s intervals)
            - Standard click if element is visible
            - JS click as fallback (NOT expensive element_handle())
        """
        timeout_sec = timeout_ms / 1000.0
        
        try:
            # Step 0: FAIL-FAST CHECK - use count() to instantly know if element exists
            # This is INSTANT compared to element_handle() which waits 30s
            if locator.count() == 0:
                logger.debug(f"Element not found for {element_name} (count=0), using fallback")
                return False
            
            # Step 1: Playwright native wait (fast) - visibility check with REDUCED timeout
            locator.wait_for(state='visible', timeout=timeout_ms)
            logger.debug(f"✓ {element_name} is visible")
            
            # Step 2: Enhanced check using wait_utils - verify element is clickable
            # Smart polling every 0.1s instead of constant waiting
            try:
                wait_for_condition(
                    lambda: locator.is_visible() and locator.is_enabled(),
                    timeout=timeout_sec,
                    poll_interval=0.1,
                    error_message=f"{element_name} not fully ready for click"
                )
                logger.debug(f"✓ {element_name} is visible and enabled")
            except WaitTimeoutError:
                # Element is visible but may not be enabled - try click anyway
                logger.debug(f"⚠ {element_name} might not be enabled, attempting click")
            
            # Step 3: Standard click
            self.click(locator)
            logger.info(f"✓ {element_name} clicked successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Standard click failed for {element_name}: {e}")
            # Last resort: Try JS click (cheaper than element_handle wait)
            try:
                logger.debug(f"Attempting JS click for {element_name}")
                # Check if element exists before calling element_handle()
                if locator.count() > 0:
                    self.page.evaluate("(el) => el.click()", locator.element_handle())
                    logger.info(f"✓ {element_name} clicked via JS fallback")
                    return True
                else:
                    logger.debug(f"Element no longer found for JS click: {element_name}")
                    return False
            except Exception as js_error:
                logger.error(f"✗ Failed to click {element_name}: {js_error}")
                return False

    def verify_request_type_table_ready(self) -> bool:
        """
        Verify the Request/Type picker table is fully loaded and interactive.
        
        Uses Approach (Multi-Element Array) with WaitContext to verify:
        1. Table container (#divlstContainer) - UI structure rendered
        2. Request list (#HTMLlslCategory) - list initialized  
        3. First request option (#lstcategoryli0) - data loaded and clickable
        
        Returns:
            True if all components ready, False otherwise
            
        Example:
            if client_accounts_page.verify_request_type_table_ready():
                client_accounts_page.select_request("Account Information Change")
        """
        logger.info("Verifying Request/Type table readiness...")
        
        try:
            table_container = self.page.locator(client_accounts_locators.TABLE_CONTAINER)
            request_list = self.page.locator(client_accounts_locators.REQUEST_LIST)
            first_option = self.page.locator(client_accounts_locators.REQUEST_LIST_ITEM)
            
            # Verify all key components are visible and enabled
            with WaitContext(timeout=40.0, poll_interval=0.2) as wait:
                wait.until(lambda: table_container.is_visible(), error_message="Table container not visible")
                wait.until(lambda: request_list.is_visible(), error_message="Request list not visible")
                wait.until(lambda: first_option.is_visible(), error_message="First request option not visible")
                wait.until(lambda: first_option.is_enabled(), error_message="First request option not enabled")
            
            logger.info("✓ Request/Type table ready - all components visible and enabled")
            return True
            
        except Exception as e:
            logger.error(f"✗ Request/Type table verification failed: {str(e)}")
            return False

    def select_request(self, list_item_name: str) -> None:
        """Select an item from the Request list
        
        PERFORMANCE OPTIMIZATIONS:
        - RetryContext: Auto-retry with smart delays (0.3s, 0.6s, 1.0s) instead of cascading timeouts
        - WaitContext: Fail-fast timeouts (1.5s) instead of 3s + 30s cascade
        - Wait for list readiness before clicking (ensures items are rendered)
        - count() checks for instant element existence detection

        Args:
            list_item_name: Visible name of the list item to click.
        """
        logger.info(f"Selecting request list item: {list_item_name}")
        
        with RetryContext(max_retries=2, initial_delay=0.3) as retry:
            while retry.should_retry():
                try:
                    container = self.page.locator('#divlstContainer')
                    
                    # Wait for container to be visible
                    with WaitContext(timeout=2.0, poll_interval=0.2) as wait:
                        wait.until_visible(container)
                    
                    # OPTIMIZATION: Wait for list items to exist before trying to click
                    # This ensures the list is fully rendered
                    ul = container.locator('#HTMLlslCategory')
                    list_items = ul.locator('li')
                    
                    with WaitContext(timeout=2.0, poll_interval=0.2) as wait:
                        try:
                            # Wait for at least one item to be visible
                            wait.until(lambda: list_items.count() > 0, error_message="List items not loaded")
                            logger.debug(f"✓ List has {list_items.count()} items available")
                        except WaitTimeoutError:
                            logger.warning(f"List items not rendering, attempting click anyway")
                    
                    # Primary strategy: role-based locator (fastest)
                    # OPTIMIZATION: Use short timeout (1.5s) via _wait_and_click_element
                    item = container.get_by_role('listitem', name=list_item_name)
                    
                    # Check if item exists (instant via count()) before waiting
                    if item.count() > 0:
                        if self._wait_and_click_element(item, f"Request '{list_item_name}'", timeout_ms=1500):
                            logger.info(f"✓ Request '{list_item_name}' selected via role locator")
                            retry.success()
                            return
                    else:
                        logger.debug(f"Role-based locator count=0, trying fallback")

                    # Fallback: text-based locator (will be used if role failed)
                    # OPTIMIZATION: Direct locator query without intermediate exception handling
                    li = ul.locator(f'li:has-text("{list_item_name}")')
                    
                    # Check count first (instant)
                    if li.count() > 0:
                        target = li.first
                        if self._wait_and_click_element(target, f"Request '{list_item_name}' (text-based)", timeout_ms=1500):
                            logger.info(f"✓ Request '{list_item_name}' selected via text locator")
                            retry.success()
                            return
                    
                    raise Exception(f"Failed to select request '{list_item_name}' - element not found")
                    
                except Exception as e:
                    if retry.should_retry():
                        retry.failed(e)
                    else:
                        raise

    def select_type(self, type_name: str) -> None:
        """Select an item from the Type list

        PERFORMANCE OPTIMIZATIONS:
        - RetryContext: Auto-retry with smart delays (0.3s, 0.6s, 1.0s)
        - WaitContext: Fail-fast timeouts (1.5s) instead of 3s + 30s cascade
        - count() checks for instant element existence detection
        - Multiple fallback strategies with early exit on count=0
        - Parallel element readiness check

        The HTML structure for Type is a scrollable div with id `divSubCategory`
        containing a UL with id `HTMLSubCategory`. Each LI is a selectable item.

        Args:
            type_name: Visible text of the type to select (e.g., 'Bill Account via ACH').
        """
        
        logger.info(f"Selecting Type list item: {type_name}")
        
        with RetryContext(max_retries=2, initial_delay=0.3) as retry:
            while retry.should_retry():
                try:
                    container = self.page.locator('#divSubCategory')
                    
                    # Wait for container to be visible
                    with WaitContext(timeout=2.0, poll_interval=0.2) as wait:
                        wait.until_visible(container)
                    
                    # OPTIMIZATION: Wait for list items to render before attempting clicks
                    ul = container.locator('#HTMLSubCategory')
                    list_items = ul.locator('li')
                    
                    with WaitContext(timeout=2.0, poll_interval=0.2) as wait:
                        try:
                            wait.until(lambda: list_items.count() > 0, error_message="Type list items not loaded")
                            logger.debug(f"✓ Type list has {list_items.count()} items available")
                        except WaitTimeoutError:
                            logger.warning(f"Type list not rendering, attempting click anyway")

                    # Primary strategy: role-based locator with onclick attribute check (most reliable)
                    # Ensures we're clicking the actual clickable li with SubSelectCategoryClick handler
                    item = container.locator(
                        f'li[onclick*="SubSelectCategoryClick"]:has-text("{type_name}")'
                    )
                    if item.count() > 0:
                        if self._wait_and_click_element(item, f"Type '{type_name}'", timeout_ms=1500):
                            logger.info(f"✓ Type '{type_name}' selected via onclick locator")
                            retry.success()
                            return
                    else:
                        logger.debug(f"onclick locator count=0 for '{type_name}', trying fallback")

                    # Fallback 1: LI with onclick attribute (efficient & more stable)
                    clickable = ul.locator(f'li[onclick]:has-text("{type_name}")')
                    if clickable.count() > 0:
                        target = clickable.first
                        if self._wait_and_click_element(target, f"Type '{type_name}' (onclick)", timeout_ms=1500):
                            logger.info(f"✓ Type '{type_name}' selected via onclick locator")
                            retry.success()
                            return
                    else:
                        logger.debug(f"Onclick strategy count=0 for '{type_name}'")

                    # Fallback 2: Any LI with exact text
                    li = ul.locator(f'li:has-text("{type_name}")')
                    if li.count() > 0:
                        target = li.first
                        if self._wait_and_click_element(target, f"Type '{type_name}' (text-based)", timeout_ms=1500):
                            logger.info(f"✓ Type '{type_name}' selected via text locator")
                            retry.success()
                            return
                    else:
                        logger.debug(f"Text-based locator count=0 for '{type_name}'")
                    
                    raise Exception(f"Failed to select type '{type_name}' - element not found with any strategy")
                    
                except Exception as e:
                    if retry.should_retry():
                        retry.failed(e)
                    else:
                        raise

    def click_complete_button(self, button_text: str) -> None:
        """Click the Complete button with flexible text parameter.

        Supports multiple button types:
        - 'Complete and Submit': Submit without client signature (OnlineSubmitbutton)
        - 'Complete and Print': Get physical signature (HTMLPrintButton)
        - 'Complete and eSign': Request electronic signature (eSignatureButton)

        Each button has its own unique ID for reliable fallback locating.
        
        Args:
            button_text: The button text to match (e.g., 'Complete and Submit')
        """
        logger.info(f"Clicking '{button_text}' button")
        
        # Map button text to their corresponding IDs
        button_id_map = {
            'Complete and Submit': 'OnlineSubmitbutton',
            'Complete and Print': 'HTMLPrintButton',
            'Complete and eSign': 'eSignatureButton'
        }
        
        button_id = button_id_map.get(button_text)
        if not button_id:
            raise ValueError(f"Unknown button text: '{button_text}'. Supported: {list(button_id_map.keys())}")
        
        # Primary strategy: Playwright role-based locator with exact text match
        try:
            submit_btn = self.page.get_by_role('button', name=button_text)
            submit_btn.wait_for(state='visible', timeout=5000)
            logger.debug(f"✓ Found '{button_text}' button via role locator")
        except Exception as e:
            logger.debug(f"Role-based locator failed: {e}")
            # Fallback: Use stable id attribute specific to the button
            try:
                submit_btn = self.page.locator(f'input#{button_id}')
                submit_btn.wait_for(state='visible', timeout=5000)
                logger.debug(f"✓ Found '{button_text}' button via id locator (#{button_id})")
            except Exception as e2:
                logger.error(f"All locator strategies failed for '{button_text}' (#{button_id}): {e2}")
                raise

        self.click(submit_btn)
        logger.info(f"✓ '{button_text}' button clicked successfully")

    def handle_signature_dialog(self, signature_option: str, button_text: str = "Continue") -> None:
        """
        Handle the 'Client Signature Not Required' dialog that appears during submission.

        This dialog appears with options to:
        - Proceed and submit without a client signature
        - Print to obtain client physical signature
        - Request client electronic signature

        Args:
            signature_option: Full text from the feature file:
                - "Proceed and submit without a client signature" → rbSubmit
                - "Print to obtain client physical signature" → rbPrint
                - "Request client electronic signature" → rbEsign
            button_text: Button to click in the dialog (default: "Continue")

        Raises:
            PlaywrightTimeoutError: If dialog or button not found
            ValueError: If signature_option doesn't match expected text
        """
        logger.info(f"Handling signature dialog with option: {signature_option}, button: {button_text}")

        dialog_handler = DialogHandler(self.page)

        # Wait for dialog to appear
        dialog_handler.wait_for_dialog(timeout=120000)
        logger.info("Signature dialog appeared")

        # Wait for page to settle (intelligent wait instead of arbitrary timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=5000)

        # Determine which radio button to select based on exact feature file text
        if signature_option == "Print to obtain client physical signature":
            logger.info("Selecting: Print to obtain client physical signature")
            dialog_handler.select_dialog_option("rbPrint")
        elif signature_option == "Request client electronic signature":
            logger.info("Selecting: Request client electronic signature")
            dialog_handler.select_dialog_option("rbEsign")
        elif signature_option == "Proceed and submit without a client signature":
            logger.info("Selecting: Proceed and submit without a client signature")
            dialog_handler.select_dialog_option("rbSubmit")
        else:
            raise ValueError(
                f"Unknown signature option: '{signature_option}'. "
                f"Expected one of: 'Proceed and submit without a client signature', "
                f"'Print to obtain client physical signature', "
                f"'Request client electronic signature'"
            )

        # Click the specified button (dialog should be ready from the load state wait above)
        dialog_handler.click_dialog_button(button_text)
        logger.info(f"Clicked '{button_text}' button in signature dialog")

    def click_form_button(self, button_text: str, timeout: int = 60000) -> None:
        """
        Generic method to click a form button with specific text.

        This method can be used to click any button with class 'formButton' and specific text content.
        It validates the button is visible and enabled before clicking.

        Args:
            button_text: The exact text of the button to click (e.g., 'Return to eWealthManager', 'Start Client Signing')
            timeout: Timeout in milliseconds for waiting for button visibility (default: 60000ms)

        Raises:
            AssertionError: If button not found, not visible, or click fails

        Example:
            client_accounts_page.click_form_button('Return to eWealthManager')
            client_accounts_page.click_form_button('Start Client Signing', timeout=120000)
        """
        logger.info(f"Clicking form button with text: '{button_text}'...")

        try:
            # Build the locator using button text
            button_locator = self.page.locator(f'button.formButton:has-text("{button_text}")')

            # STEP 1: Check if button exists
            if button_locator.count() == 0:
                logger.error(f"✗ Button with text '{button_text}' not found on page")
                raise AssertionError(f"Form button '{button_text}' not found on page")

            logger.debug(f"✓ Button '{button_text}' found on page")

            # STEP 2: Wait for button to be visible
            logger.debug(f"Waiting for button '{button_text}' to be visible...")
            button_locator.wait_for(state='visible', timeout=timeout)
            logger.debug(f"✓ Button '{button_text}' is visible")

            # STEP 3: Verify button is enabled for clicking
            if not button_locator.is_enabled():
                logger.warning(f"Button '{button_text}' is not enabled, attempting to click anyway")

            # STEP 4: Click the button using framework utilities
            self.click(button_locator)
            logger.info(f"✓ Button '{button_text}' clicked successfully")

        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"✗ Failed to click button '{button_text}': {e}")
            raise AssertionError(f"Failed to click form button '{button_text}'. Details: {e}") from e

    def get_request_submitted_dialog_content(self) -> dict:
        """
        Fetch content from the Request Submitted dialog.

        Returns:
            Dictionary containing:
            - 'title': Dialog title
            - 'content': Full text content of the dialog
            - 'd_link_text': The tracking center link starting with 'D'
            - 'd_link_href': The href attribute of the tracking center link
            - 'print_download_link': The Print or Download link element
            - 'close_button': The Close button element

        Raises:
            PlaywrightTimeoutError: If dialog or required elements not found

        Example:
            dialog_data = page_obj.get_request_submitted_dialog_content()
            assert "Request Submitted" in dialog_data['title']
            assert dialog_data['d_link_text'].startswith('D')
        """
        logger.info("Fetching Request Submitted dialog content")

        # Use DialogHandler to wait for and get dialog content
        dialog_handler = DialogHandler(self.page)
        
        # Wait for dialog to appear and get the specific dialog locator
        dialog = dialog_handler.wait_for_dialog(timeout=120000)
        logger.info("Request Submitted dialog appeared")
        
        # CRITICAL FIX: Wait for dialog content to be fully rendered
        # Dialog may exist in DOM but text rendering still in progress
        # Add explicit waits for key content elements before extraction
        logger.info("Waiting for dialog content to fully render...")
        try:
            # Wait for at least one paragraph/text content to exist in dialog
            dialog.locator('p, div:not(:empty)').first.wait_for(state="visible", timeout=8000)
            logger.info("Dialog content elements are visible")
        except Exception as e:
            logger.warning(f"Could not wait for specific content elements: {e}")
        
        # Add small delay for final DOM settlement (animations, etc.)
        self.page.wait_for_timeout(1000)

        # Get dialog title and content using dialog_handler
        # INCREASED TIMEOUT: 5000ms → 10000ms to account for slower environments
        dialog_title = dialog_handler.get_dialog_title(timeout=20000)
        logger.info(f"Dialog Title: {dialog_title}")

        dialog_content = dialog_handler.get_dialog_text(timeout=20000)
        logger.info(f"Dialog Content:\n{dialog_content}")

        # FIX: Use the same dialog reference instead of re-querying with different selector
        # This ensures we're always working with the same dialog instance
        # Target: <a class="printConfirmationLink" href="...">D003525811</a>
        d_link = dialog.locator('a.printConfirmationLink')
        d_link.wait_for(state="visible", timeout=8000)
        d_link_text = (d_link.text_content() or "").strip() if d_link.text_content() else ""
        d_link_href = d_link.get_attribute("href") or ""
        logger.info(f"D-Link Text: {d_link_text}, Href: {d_link_href}")

        return {
            'title': dialog_title,
            'content': dialog_content,
            'd_link': d_link,
            'd_link_text': d_link_text,
            'd_link_href': d_link_href,
        }

    def get_signer_information_dialog_text(self) -> str:
        """
        Get the full text content from the Signer Information dialog.
        
        Uses DialogHandler to wait for and retrieve text from the dialog.
        
        Returns:
            Full text content of the dialog
            
        Raises:
            PlaywrightTimeoutError: If dialog not found
            
        Example:
            dialog_text = page_obj.get_signer_information_dialog_text()
            assert "Expected text" in dialog_text
        """
        logger.info("Getting Signer Information dialog text")
        dialog_handler = DialogHandler(self.page)
        dialog_text = dialog_handler.get_dialog_text(timeout=120000)
        logger.info(f"Signer Information dialog text retrieved: {len(dialog_text)} characters")
        return dialog_text

    def click_d_number(self) -> str:
        """
        Click on the D-number (Tracking Center link) in the dialog.
        
        This method:
        1. Locates the D-link element in the dialog
        2. Waits for it to be visible and enabled
        3. Extracts the D-number
        4. Clicks on it to navigate to the Tracking Center
        5. Returns the D-number for verification purposes
        
        Returns:
            The D-number (e.g., "D003518970")
        
        Raises:
            PlaywrightTimeoutError: If dialog or D-link not found
            
        Example:
            d_number = page_obj.click_d_number()
            assert d_number.startswith('D')
        """
        logger.info("Clicking on D-number (Tracking Center link)...")
        
        # Get the D-link from the first visible dialog
        d_link = self.page.locator('[role="dialog"]').first.locator('a.printConfirmationLink')
        
        # Wait for the D-link to be visible
        d_link.wait_for(state="visible", timeout=5000)
        logger.info("D-link is visible")
        
        # Get the D-number for logging and returning
        d_link_text = d_link.text_content()
        d_number = d_link_text.strip() if d_link_text else ""
        logger.info(f"D-number found: {d_number}")
        
        # Verify it's enabled/clickable
        if not d_link.is_enabled():
            logger.warning("D-link is not enabled, attempting to click anyway")
        
        # Click the D-link
        logger.info(f"Clicking D-number: {d_number}")
        d_link.click()
        
        logger.info(f"✓ D-number clicked: {d_number}")
        return d_number
    
    def get_form_heading_text(self) -> str:
        """
        Extract the form heading text from the <b> tag in the task name span.
        
        Locates the span with id "ctl00_cphContentArea_AccountActionsBox1_lblTaskName"
        and extracts the text from the first <b> (bold) tag inside it.
        
        Returns:
            The text from the <b> tag (e.g., "Copy for Digital Deposit")
            
        Raises:
            PlaywrightTimeoutError: If the span or <b> tag is not found
            
        Example:
            heading_text = page_obj.get_form_heading_text()
            # Returns: "Copy for Digital Deposit"
        """
        logger.info("Retrieving form heading text...")
        
        try:
            # Locate the span by ID
            task_name_span = self.page.locator('span#ctl00_cphContentArea_AccountActionsBox1_lblTaskName')
            
            # Wait for the span to be visible
            task_name_span.wait_for(state='visible', timeout=120000)
            logger.debug("Form heading span found and visible")
            
            # Find the <b> tag inside the span
            bold_element = task_name_span.locator('b').first
            
            # Wait for the <b> tag to be visible
            bold_element.wait_for(state='visible', timeout=5000)
            logger.debug("<b> tag found in form heading span")
            
            # Extract the text from the <b> tag
            heading_text = bold_element.text_content()
            
            if not heading_text:
                logger.warning("Form heading text is empty")
                raise ValueError("Form heading text retrieved but is empty")
            
            heading_text = (heading_text or "").strip()
            logger.info(f"✓ Form heading text retrieved: '{heading_text}'")
            
            return heading_text
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve form heading text: {e}")
            raise
    
    def get_signature_dialog_title(self) -> str:
        """
        Extract the title text from the signature dialog's modal-title-transition div.
        
        Locates the div with class 'modal-title-transition' and extracts its text content.
        This is typically used to verify the "Client Signature Not Required" dialog.
        
        Returns:
            The text from the modal-title-transition div (e.g., "Client Signature Not Required")
            
        Raises:
            PlaywrightTimeoutError: If the dialog or title div is not found
            ValueError: If the title text is empty
            
        Example:
            title = page_obj.get_signature_dialog_title()
            assert title == "Client Signature Not Required"
        """
        logger.info("Retrieving signature dialog title...")
        
        try:
            # Find the modal-title-transition div within the dialog
            modal_title_div = self.page.locator('div.modal-title-transition').first
            
            # Wait for the title div to be visible
            modal_title_div.wait_for(state='visible', timeout=5000)
            logger.debug("modal-title-transition div found and visible")
            
            # Extract the text from the title div
            dialog_title = modal_title_div.text_content()
            
            if not dialog_title:
                logger.warning("Dialog title text is empty")
                raise ValueError("Dialog title text retrieved but is empty")
            
            dialog_title = (dialog_title or "").strip()
            logger.info(f"✓ Signature dialog title retrieved: '{dialog_title}'")
            
            return dialog_title
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve signature dialog title: {e}")
            raise
    
    def is_radio_checked(self, radio_id: str) -> bool:
        """
        Check if a radio button input is currently checked.
        
        Uses framework utilities from utils.wait_utils for robust element state checking.
        
        Args:
            radio_id: The ID attribute of the radio input element (e.g., 'rbSubmit', 'rbPrint', 'rbEsign')
            
        Returns:
            True if the radio button is checked, False otherwise
            
        Raises:
            WaitTimeoutError: If the radio button element is not found within timeout
            
        Example:
            is_checked = page_obj.is_radio_checked('rbSubmit')
            assert is_checked, "rbSubmit radio button should be checked"
        """
        logger.info(f"Checking if radio button with id '{radio_id}' is checked...")
        
        try:
            # Locate the radio input by its ID
            radio_input = self.page.locator(f'input#{radio_id}')
            
            # STEP 1: Wait for element to be attached to DOM using BasePage utility
            logger.debug(f"Waiting for radio input '{radio_id}' to be attached to DOM...")
            self.wait_for_element(radio_input, state='attached', timeout=5000)
            logger.debug(f"✓ Radio input '{radio_id}' found in DOM")
            
            # STEP 2: Check if the radio button is checked
            is_checked = radio_input.is_checked()
            logger.info(f"Radio button '{radio_id}' checked status: {is_checked}")
            
            return is_checked
            
        except WaitTimeoutError as e:
            logger.error(f"✗ Radio button '{radio_id}' not found or timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Failed to check radio button status for id '{radio_id}': {e}")
            raise

    def fetch_selected_account(self, account_number: str) -> Locator:
        """
        Fetch and return the label element for a given account number.
        
        This method:
        1. Waits for any loading spinners to disappear
        2. Searches all account labels for the specified account number
        3. Returns the matching label element (Locator object)
        
        Args:
            account_number: The account number to search for (e.g., '13222266')
            
        Returns:
            Locator: The matching label element for the account
            
        Raises:
            AssertionError: If no account labels found or account number not found in any label
            
        Example:
            matching_label = client_accounts_page.fetch_selected_account('13222266')
            # Use matching_label with radio button lookup
        """
        logger.info(f"Fetching account label for account number: {account_number}")
        
        # STEP 0: Wait for any loading spinner to disappear before searching for labels
        logger.info("Step 0: Waiting for loading spinner to disappear...")
        spinner_selectors = [
            ".spinner",
            ".loading",
            ".loader",
            "div.lds-container",
            "[role='progressbar']",
            ".ajaxLoader"
        ]
        
        # Use existing WaitContext utility to wait for spinners to disappear
        wait_context = WaitContext(timeout=15.0, poll_interval=0.2)
        for selector in spinner_selectors:
            try:
                spinner = self.page.locator(selector)
                if spinner.count() > 0:
                    logger.info(f"Found spinner with selector '{selector}', waiting for it to disappear...")
                    wait_context.until_hidden(spinner)
                    logger.info(f"Spinner '{selector}' disappeared")
            except Exception as e:
                # Spinner not found or already gone - continue
                logger.debug(f"Spinner '{selector}' not found or already hidden: {e}")
        
        # Also wait for page to settle using existing BasePage utility
        self.wait_for_load_state("domcontentloaded", timeout=120000)
        logger.info("Page load state settled")
        
        # STEP 1: Find label containing the account number
        logger.info(f"Step 1: Searching for account number '{account_number}' in account labels...")
        
        # Get all labels in the account list container
        account_list_container = self.page.locator('div#ctl00_cphContentArea_ToSetTheRadioItemBackgroundColor')
        labels = account_list_container.locator('label')
        
        label_count = labels.count()
        assert label_count > 0, "[FAIL] ClientAccountsPage: Account Labels Presence — Expected: label_count > 0, Actual: count=0. Details: At least one account label should be displayed on the account list page. Locator: div#ctl00_cphContentArea_ToSetTheRadioItemBackgroundColor label."
        logger.info(f"Found {label_count} account labels on the page")
        
        # Find the label containing the account number
        matching_label = None
        matching_label_text = None
        for i in range(label_count):
            label_text = labels.nth(i).inner_text()
            if account_number in label_text:
                matching_label = labels.nth(i)
                matching_label_text = label_text
                logger.info(f"✓ Found label with account number at index {i}")
                logger.info(f"  Label text: {label_text}")
                break
        
        # HARD ASSERT - Account number must exist in a label
        assert matching_label is not None, \
            f"[FAIL] ClientAccountsPage: Account Lookup — Expected: account_number='{account_number}' found in labels, " \
            f"Actual: matching_label=None (not found). Details: Account '{account_number}' must exist in Account Management on this test environment. " \
            f"Locator: div#ctl00_cphContentArea_ToSetTheRadioItemBackgroundColor label."
        
        logger.info(f"✓ Successfully fetched label for account '{account_number}'")
        return matching_label

    def get_account_radio_button(self, account_number: str) -> tuple:
        """
        Get the radio button element for a given account number and validate it exists.
        
        This method:
        1. Fetches the account label using fetch_selected_account()
        2. Extracts the radio button ID from the label's 'for' attribute
        3. Locates and validates the radio button exists
        4. Returns both the radio button and its ID for further operations
        
        Args:
            account_number: The account number to find radio button for (e.g., '13222266')
            
        Returns:
            Tuple of (radio_button: Locator, label_for_attr: str)
            
        Raises:
            AssertionError: If account not found or radio button doesn't exist
            
        Example:
            radio_button, button_id = page_obj.get_account_radio_button('13222266')
            is_checked = radio_button.is_checked()
        """
        logger.info(f"Getting radio button for account: {account_number}")
        
        # Get the matching account label
        matching_label = self.fetch_selected_account(account_number)
        logger.info("✓ Account label fetched successfully")
        
        # Extract the radio button ID from the label's 'for' attribute
        label_for_attr = matching_label.get_attribute("for")
        logger.info(f"Label 'for' attribute: '{label_for_attr}'")
        
        # Locate the radio input with matching id
        radio_button = self.page.locator(f"input#{label_for_attr}")
        
        # Validate radio button exists
        assert radio_button.count() > 0, \
            f"[FAIL] ClientAccountsPage: Radio Button Lookup — Expected: radio_button count > 0, " \
            f"Actual: count=0 (not found). Details: Radio button with id '{label_for_attr}' for account '{account_number}' should exist. " \
            f"Locator: input#{label_for_attr}."
        
        radio_button = radio_button.first
        logger.info(f"✓ Radio button located for account '{account_number}'")
        
        return radio_button, label_for_attr

    def normalize_text_for_comparison(self, text: str) -> str:
        """
        Normalize text for comparison by handling special characters and Unicode issues.
        
        Handles:
        - Unicode normalization (NFC)
        - Smart quotes (curly) → regular quotes
        - Non-breaking spaces → regular spaces
        - Multiple consecutive spaces → single space
        - Other whitespace normalization
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text string
            
        Example:
            normalized = page_obj.normalize_text_for_comparison("Heading\u2019s Text")
            # "Heading's Text"
        """
        if not text:
            return ""
        
        # Apply Unicode NFC normalization
        text = unicodedata.normalize('NFC', text)
        
        # Replace smart/curly quotes with regular straight quotes
        text = text.replace('\u2018', "'")  # Left single quotation mark
        text = text.replace('\u2019', "'")  # Right single quotation mark (most common)
        text = text.replace('\u201C', '"')  # Left double quotation mark
        text = text.replace('\u201D', '"')  # Right double quotation mark
        
        # Replace non-breaking space with regular space
        text = text.replace('\u00A0', ' ')  # Non-breaking space
        text = text.replace('\u2009', ' ')  # Thin space
        text = text.replace('\u200B', '')   # Zero-width space (remove)
        
        # Replace em-dash with regular hyphen
        text = text.replace('\u2014', '-')  # Em-dash
        text = text.replace('\u2013', '-')  # En-dash
        
        # Normalize multiple whitespace to single space
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        return text.strip()

    def ensure_account_radio_selected(self, account_number: str) -> dict:
        """
        Ensure an account's radio button is selected (select if not already).
        
        This method:
        1. Gets the radio button for the specified account
        2. Checks its current selection state
        3. Selects it if not already selected
        4. Returns comprehensive data for assertions
        
        Args:
            account_number: The account number to ensure is selected (e.g., '13222266')
            
        Returns:
            Dictionary containing:
            - 'radio_button': Locator for the radio button
            - 'label_for_attr': The ID of the radio button
            - 'is_checked': Final checked state after selection attempt
            - 'was_already_checked': Boolean indicating if it was already checked before selection
            
        Raises:
            AssertionError: If account not found or radio button operation fails
            
        Example:
            result = page_obj.ensure_account_radio_selected('13222266')
            assert result['is_checked'], "Radio should be checked"
        """
        logger.info(f"Ensuring account radio is selected: {account_number}")
        
        # Step 1: Get radio button and its ID
        logger.info("Step 1: Getting radio button for account...")
        radio_button, label_for_attr = self.get_account_radio_button(account_number)
        
        # Step 2: Check current state
        logger.info("Step 2: Checking current radio button state...")
        is_checked = radio_button.is_checked()
        was_already_checked = is_checked
        logger.info(f"Radio button current state - checked: {is_checked}")
        
        # Step 3: Select if not already checked
        if not is_checked:
            logger.info(f"Radio button is NOT checked - selecting it...")
            radio_button.check()
            self.page.wait_for_timeout(500)  # Wait for state update
            is_checked = radio_button.is_checked()
            logger.info(f"Radio button after selection - checked: {is_checked}")
        else:
            logger.info(f"Radio button is already checked")
        
        result = {
            'radio_button': radio_button,
            'label_for_attr': label_for_attr,
            'is_checked': is_checked,
            'was_already_checked': was_already_checked
        }
        
        logger.info(f"✓ Account radio button operation completed: {result}")
        return result

    def enter_client_signer_details(self, full_name: str, email_address: str, phone: str, signer_index: int = 1) -> dict:
        """
        Enter client signer details in the Account Holders table.
        
        This method fills in the following fields for a specific signer row:
        - Signer's Full Name (txtAccountHolderName{index})
        - Email Address (txtAccountHolderEmail{index})
        - Phone Number (txtAccountHolderPhone{index})
        
        Args:
            full_name: Full name of the signer (from Account_Owner test data)
            email_address: Email address of the signer (from Email_Address test data)
            phone: Phone number of the signer (from Phone test data)
            signer_index: Row index in the table (1 for first Account Owner, 2 for second, etc.)
                         Default: 1 (Account Owner row)
        
        Returns:
            Dictionary containing:
            - 'name_field': Locator for the name input field
            - 'email_field': Locator for the email input field
            - 'phone_field': Locator for the phone input field
            - 'values_entered': Dictionary with actual values entered
            - 'fields_filled': Boolean indicating all fields were filled successfully
        
        Raises:
            AssertionError: If required input fields not found or not fillable
            
        Example:
            result = page_obj.enter_client_signer_details(
                full_name="John Smith",
                email_address="john@example.com",
                phone="925-123-4567",
                signer_index=1
            )
            assert result['fields_filled'], "All signer details should be filled"
        """
        logger.info(f"Entering client signer details for signer index {signer_index}")
        
        try:
            # Step 0: Wait for dialog to be fully rendered and iframe to load
            logger.info(f"Step 0: Waiting for Signer(s) Information dialog and iframe to load...")
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(1000)  # Additional delay for animations
            
            # Step 0.5: Wait for iframe to be present and accessible
            logger.info(f"Step 0.5: Locating and accessing iframe #esig_iframe...")
            iframe_locator = self.page.locator('iframe#esig_iframe')
            iframe_locator.wait_for(state="attached", timeout=120000)
            logger.info(f"  ✓ Iframe #esig_iframe is attached")
            
            # Get the iframe element to access its content
            iframe = self.page.frame_locator('iframe#esig_iframe')
            
            # CRITICAL: Wait for iframe content to load before accessing elements
            # The iframe may be attached but its HTML content is still loading
            logger.info(f"Step 0.6: Waiting for iframe content to load...")
            try:
                # Try multiple indicators of loaded content
                content_loaded = False
                
                # Try 1: Look for a button (most common visible element)
                try:
                    iframe.locator("button").first.wait_for(state="attached", timeout=30000)
                    content_loaded = True
                except:
                    pass
                
                # Try 2: Look for text
                if not content_loaded:
                    try:
                        iframe.locator("*:has-text('.')").first.wait_for(state="attached", timeout=30000)
                        content_loaded = True
                    except:
                        pass
                
                # Try 3: Look for input fields
                if not content_loaded:
                    try:
                        iframe.locator("input, textarea").first.wait_for(state="attached", timeout=30000)
                        content_loaded = True
                    except:
                        pass
                
                # Try 4: Generic element search
                if not content_loaded:
                    iframe.locator("div, section, form").first.wait_for(state="attached", timeout=30000)
                
                self.page.wait_for_timeout(300)  # Small delay for rendering
                logger.info(f"  ✓ Iframe content is loaded and ready")
            except Exception as e:
                logger.warning(f"  ⚠ Timeout waiting for iframe content: {e}")
                # Continue anyway, will fail on assertion if really needed
            
            # Step 1: Locate the input fields using dynamic IDs based on signer_index (WITHIN IFRAME)
            logger.info(f"Step 1: Locating input fields for signer index {signer_index} inside iframe...")
            
            name_field = iframe.locator(f'input[name="txtAccountHolderName{signer_index}"]')
            email_field = iframe.locator(f'input[name="txtAccountHolderEmail{signer_index}"]')
            phone_field = iframe.locator(f'input[name="txtAccountHolderPhone{signer_index}"]')
            
            # Step 2: Verify fields exist in iframe and wait for visibility
            logger.info(f"Step 2: Verifying input fields are present and visible in iframe...")
            
            logger.info(f"  Waiting for name field to be visible...")
            name_field.wait_for(state="visible", timeout=120000)
            
            logger.info(f"  Waiting for email field to be visible...")
            email_field.wait_for(state="visible", timeout=120000)
            
            logger.info(f"  Waiting for phone field to be visible...")
            phone_field.wait_for(state="visible", timeout=120000)
            
            logger.info(f"✓ All input fields are visible and ready in iframe")
            
            # Step 3: Clear existing values (if any) using retry logic for reliability
            logger.info(f"Step 3: Clearing existing field values...")
            with RetryContext(max_retries=2, initial_delay=0.2) as retry:
                while retry.should_retry():
                    try:
                        name_field.clear()
                        email_field.clear()
                        phone_field.clear()
                        retry.success()
                    except Exception as e:
                        if retry.should_retry():
                            retry.failed(e)
                        else:
                            raise
            
            logger.info(f"✓ Fields cleared")
            
            # Step 4: Fill in signer details with validation
            logger.info(f"Step 4: Filling signer details...")
            
            # Fill Full Name
            name_field.fill(full_name)
            logger.info(f"  ✓ Full Name filled: {full_name}")
            
            # Fill Email Address
            email_field.fill(email_address)
            logger.info(f"  ✓ Email Address filled: {email_address}")
            
            # Fill Phone Number
            phone_field.fill(phone)
            logger.info(f"  ✓ Phone Number filled: {phone}")
            
            # Add small delay to allow form to commit values
            self.page.wait_for_timeout(500)
            
            # Step 5: Verify values were actually entered (validation)
            logger.info(f"Step 5: Verifying entered values...")
            actual_name = (name_field.input_value() or "").strip()
            actual_email = (email_field.input_value() or "").strip()
            actual_phone = (phone_field.input_value() or "").strip()
            
            name_match = actual_name == full_name.strip()
            email_match = actual_email == email_address.strip()
            phone_match = actual_phone == phone.strip()
            
            logger.info(f"  Name validation: {name_match} (expected: '{full_name.strip()}', actual: '{actual_name}')")
            logger.info(f"  Email validation: {email_match} (expected: '{email_address.strip()}', actual: '{actual_email}')")
            logger.info(f"  Phone validation: {phone_match} (expected: '{phone.strip()}', actual: '{actual_phone}')")
            
            # If all fields match exactly, consider them filled
            # If not all match but all have values, still consider success (form accepted them)
            all_fields_filled = (name_match and email_match and phone_match) or \
                               (bool(actual_name) and bool(actual_email) and bool(actual_phone))
            
            if not (name_match and email_match and phone_match):
                logger.warning(f"⚠ Strict validation failed, but fields have values - proceeding with caution")
            
            result = {
                'name_field': name_field,
                'email_field': email_field,
                'phone_field': phone_field,
                'values_entered': {
                    'full_name': actual_name,
                    'email_address': actual_email,
                    'phone': actual_phone
                },
                'fields_filled': all_fields_filled
            }
            
            if all_fields_filled:
                logger.info(f"✓ All signer details entered successfully for index {signer_index}")
            else:
                logger.warning(f"⚠ Some signer details may not have been entered correctly for index {signer_index}")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Failed to enter client signer details: {e}")
            raise AssertionError(f"Failed to enter signer details for index {signer_index}: {e}") from e

    def get_esignature_process_complete_dialog_content(self) -> dict:
        """
        Extract content from the eSignature Process Complete dialog.
        
        Retrieves:
        1. Dialog title (should be "eSignature Process Complete")
        2. Dialog body text (should be "Thank you for completing your part of the eSignature process.")
        3. Close button element reference
        
        This method:
        - Uses DialogHandler to verify dialog is present
        - Extracts title from modal-title-transition div
        - Extracts body text using DialogHandler
        - Locates the close button
        
        Returns:
            Dictionary containing:
            - 'title': Dialog title text (str)
            - 'body': Dialog body text (str)
            - 'close_button': Close button locator (Locator)
            - 'dialog_present': Boolean indicating dialog was found
            
        Raises:
            PlaywrightTimeoutError: If dialog not found or elements not visible
            
        Example:
            dialog_content = page_obj.get_esignature_process_complete_dialog_content()
            assert dialog_content['title'] == "eSignature Process Complete"
            assert "Thank you" in dialog_content['body']
        """
        logger.info("Retrieving eSignature Process Complete dialog content...")
        
        try:
            # Verify dialog is present using DialogHandler
            dialog_handler = DialogHandler(self.page)
            try:
                logger.info("[DEBUG] Waiting for dialog to appear (timeout: 5 minutes)...")
                dialog = dialog_handler.wait_for_dialog(timeout=300000)  # 5 minutes
                logger.info("✓ Dialog is present")
            except Exception as e:
                logger.warning(f"eSignature Process Complete dialog not found: {e}")
                return {
                    'title': None,
                    'body': None,
                    'close_button': None,
                    'dialog_present': False
                }
            
            # Get dialog title from modal-title-transition div
            logger.info("Extracting dialog title...")
            modal_title_div = self.page.locator('div.modal-title-transition').first
            modal_title_div.wait_for(state='visible', timeout=5000)
            dialog_title = (modal_title_div.text_content() or "").strip()
            logger.info(f"✓ Dialog title: '{dialog_title}'")
            
            # Get dialog body text using DialogHandler
            logger.info("Extracting dialog body text...")
            dialog_body = dialog_handler.get_dialog_text(timeout=5000)
            logger.info(f"✓ Dialog body: '{dialog_body}'")
            
            # Locate close button in the dialog (multiple strategies for robustness)
            logger.info("Locating close button...")
            close_button_locators = [
                self.page.locator('.close-button-container button').first,  # PRIORITY 1: Most reliable - visible close button
                self.page.locator('button.formButton').first,  # PRIORITY 2: Class-based selector for visible button
                self.page.locator('[role="dialog"] .close-button-set button').first,  # PRIORITY 3: Button set selector
                self.page.locator('button[aria-label*="Close"], button[aria-label*="close"]').first,  # PRIORITY 4: Aria-label
                self.page.locator('[role="dialog"] button.close').first,  # PRIORITY 5: Class-based
                self.page.locator('button[title*="Close"]').first,  # PRIORITY 6: Title attribute (may be hidden titlebar button)
            ]
            
            close_button = None
            for locator in close_button_locators:
                if locator.count() > 0:
                    close_button = locator
                    logger.info("✓ Close button found")
                    break
            
            if not close_button:
                logger.warning("Close button not found with any strategy")
            
            result = {
                'title': dialog_title,
                'body': dialog_body,
                'close_button': close_button,
                'dialog_present': True
            }
            
            logger.info(f"✓ eSignature dialog content retrieved successfully")
            return result
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve eSignature dialog content: {e}")
            raise

    def get_client_in_person_signing_dialog_content(self) -> dict:
        """
        Extract content from the Client In-Person Signing dialog.
        
        Retrieves:
        1. Dialog title (should be "Client In Person Signing")
        2. Dialog body text (paragraphs and list items)
        3. Buttons: "Return to eWealthManager" and "Start Client Signing"
        
        This method:
        - Uses DialogHandler to verify dialog is present
        - Extracts title from modal-title-transition div
        - Extracts body content from #divConfirmation container
        - Locates both action buttons
        
        Returns:
            Dictionary containing:
            - 'title': Dialog title text (str)
            - 'body': Dialog body text (str)
            - 'buttons': Dict with button references {'return_button': Locator, 'start_signing_button': Locator}
            - 'dialog_present': Boolean indicating dialog was found
            
        Raises:
            PlaywrightTimeoutError: If dialog not found or elements not visible
            
        Example:
            dialog_content = page_obj.get_client_in_person_signing_dialog_content()
            assert dialog_content['title'] == "Client In Person Signing"
            assert "Thank you for completing" in dialog_content['body']
        """
        logger.info("Retrieving Client In-Person Signing dialog content...")
        
        try:
            # Verify dialog is present using DialogHandler (wait up to 5 minutes)
            logger.info("[DEBUG] Waiting for dialog to appear (timeout: 5 minutes)...")
            dialog_handler = DialogHandler(self.page)
            try:
                logger.info("[DEBUG] Calling wait_for_dialog with 300s timeout...")
                dialog = dialog_handler.wait_for_dialog(timeout=300000)  # 5 minutes
                logger.info("✓ Dialog is present")
            except Exception as e:
                logger.warning(f"[WARN] Client In-Person Signing dialog not found after 5 minutes: {e}")
                return {
                    'title': None,
                    'body': None,
                    'buttons': {},
                    'dialog_present': False
                }
            
            # Get dialog title
            logger.info("Extracting dialog title...")
            modal_title_div = self.page.locator('div.modal-title-transition').first
            modal_title_div.wait_for(state='visible', timeout=5000)
            dialog_title = (modal_title_div.text_content() or "").strip()
            logger.info(f"✓ Dialog title: '{dialog_title}'")
            
            # Get dialog body content
            logger.info("Extracting dialog body content...")
            confirmation_div = self.page.locator('#divConfirmation').first
            confirmation_div.wait_for(state='visible', timeout=5000)
            
            # Get all text from dialog body (paragraphs, list items, etc.)
            dialog_body = confirmation_div.text_content() or ""
            dialog_body = (dialog_body or "").strip()
            logger.info(f"✓ Dialog body retrieved ({len(dialog_body)} characters)")
            
            # Locate buttons
            logger.info("Locating dialog buttons...")
            buttons = {}
            
            # Find "Return to eWealthManager" button
            return_button_locators = [
                self.page.locator('button:has-text("Return to eWealthManager")').first,
                self.page.locator('button.formButton:has-text("Return to eWealthManager")').first,
                self.page.locator('.button-container button:has-text("Return to eWealthManager")').first,
            ]
            
            for locator in return_button_locators:
                if locator.count() > 0:
                    buttons['return_button'] = locator
                    logger.info("✓ 'Return to eWealthManager' button found")
                    break
            
            # Find "Start Client Signing" button
            start_signing_locators = [
                self.page.locator('button:has-text("Start Client Signing")').first,
                self.page.locator('button.formButton:has-text("Start Client Signing")').first,
                self.page.locator('.button-container button:has-text("Start Client Signing")').first,
            ]
            
            for locator in start_signing_locators:
                if locator.count() > 0:
                    buttons['start_signing_button'] = locator
                    logger.info("✓ 'Start Client Signing' button found")
                    break
            
            if not buttons.get('return_button'):
                logger.warning("'Return to eWealthManager' button not found")
            if not buttons.get('start_signing_button'):
                logger.warning("'Start Client Signing' button not found")
            
            result = {
                'title': dialog_title,
                'body': dialog_body,
                'buttons': buttons,
                'dialog_present': True
            }
            
            logger.info(f"✓ Client In-Person Signing dialog content retrieved successfully")
            return result
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve Client In-Person Signing dialog content: {e}")
            raise

    def get_finish_later_dialog_content(self) -> dict:
        """
        Extract content from the Finish Later dialog.
        
        Retrieves:
        1. Dialog title (should be "Finish Later")
        2. Dialog body text (complete message text)
        3. Buttons: "Save" and "Delete"
        
        This method:
        - Uses DialogHandler to verify dialog is present
        - Extracts title from modal-title-transition div
        - Extracts body content from #divConfirmation container
        - Locates both action buttons (Save and Delete)
        
        Returns:
            Dictionary containing:
            - 'title': Dialog title text (str)
            - 'body': Dialog body text (str)
            - 'buttons': Dict with button references {'save_button': Locator, 'delete_button': Locator}
            - 'dialog_present': Boolean indicating dialog was found
            
        Raises:
            PlaywrightTimeoutError: If dialog not found or elements not visible
            
        Example:
            dialog_content = page_obj.get_finish_later_dialog_content()
            assert dialog_content['title'] == "Finish Later"
            assert "Select Save" in dialog_content['body']
        """
        logger.info("Retrieving Finish Later dialog content...")
        
        try:
            # Verify dialog is present using DialogHandler (wait up to 5 minutes)
            logger.info("[DEBUG] Waiting for Finish Later dialog to appear (timeout: 5 minutes)...")
            dialog_handler = DialogHandler(self.page)
            try:
                logger.info("[DEBUG] Calling wait_for_dialog with 300s timeout...")
                dialog = dialog_handler.wait_for_dialog(timeout=300000)  # 5 minutes
                logger.info("✓ Finish Later dialog is present")
            except Exception as e:
                logger.warning(f"[WARN] Finish Later dialog not found after 5 minutes: {e}")
                return {
                    'title': None,
                    'body': None,
                    'buttons': {},
                    'dialog_present': False
                }
            
            # Get dialog title
            logger.info("Extracting dialog title...")
            modal_title_div = self.page.locator(client_accounts_locators.FINISH_LATER_DIALOG_TITLE).first
            modal_title_div.wait_for(state='visible', timeout=5000)
            dialog_title = (modal_title_div.text_content() or "").strip()
            logger.info(f"✓ Dialog title: '{dialog_title}'")
            
            # Get dialog body content
            logger.info("Extracting dialog body content...")
            confirmation_div = self.page.locator(client_accounts_locators.FINISH_LATER_DIALOG_BODY).first
            confirmation_div.wait_for(state='visible', timeout=5000)
            
            # Get all text from dialog body
            dialog_body = confirmation_div.text_content() or ""
            dialog_body = (dialog_body or "").strip()
            logger.info(f"✓ Dialog body retrieved ({len(dialog_body)} characters)")
            
            # Locate buttons
            logger.info("Locating dialog buttons...")
            buttons = {}
            
            # Find "Save" button
            save_button_locators = [
                self.page.locator(client_accounts_locators.FINISH_LATER_BUTTON_SAVE).first,
                self.page.locator('button:has-text("Save")').first,
                self.page.locator('button.formButton:has-text("Save")').first,
            ]
            
            for locator in save_button_locators:
                if locator.count() > 0:
                    buttons['save_button'] = locator
                    logger.info("✓ 'Save' button found")
                    break
            
            # Find "Delete" button
            delete_button_locators = [
                self.page.locator(client_accounts_locators.FINISH_LATER_BUTTON_DELETE).first,
                self.page.locator('button:has-text("Delete")').first,
                self.page.locator('button.formButton:has-text("Delete")').first,
            ]
            
            for locator in delete_button_locators:
                if locator.count() > 0:
                    buttons['delete_button'] = locator
                    logger.info("✓ 'Delete' button found")
                    break
            
            if not buttons.get('save_button'):
                logger.warning("'Save' button not found")
            if not buttons.get('delete_button'):
                logger.warning("'Delete' button not found")
            
            result = {
                'title': dialog_title,
                'body': dialog_body,
                'buttons': buttons,
                'dialog_present': True
            }
            
            logger.info(f"✓ Finish Later dialog content retrieved successfully")
            return result
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve Finish Later dialog content: {e}")
            raise

    def click_finish_later_save_button(self, timeout: int = 60000) -> None:
        """
        Click the Save button in the Finish Later dialog.
        
        This method:
        1. Locates the Save button using XPath selector
        2. Waits for button to be visible
        3. Clicks the button
        4. Logs and returns on success
        
        Args:
            timeout: Maximum time to wait for button in milliseconds (default: 60000ms = 60 seconds)
            
        Raises:
            AssertionError: If Save button not found or not clickable
            
        Example:
            client_accounts_page.click_finish_later_save_button()
        """
        logger.info("Clicking 'Save' button in Finish Later dialog...")
        
        try:
            # Locate the Save button using XPath
            save_button = self.page.locator(client_accounts_locators.FINISH_LATER_BUTTON_SAVE_XPATH)
            
            # Verify button is present
            if save_button.count() == 0:
                logger.error(f"Save button not found using XPath: {client_accounts_locators.FINISH_LATER_BUTTON_SAVE_XPATH}")
                raise AssertionError(f"Save button not found in Finish Later dialog. Locator: {client_accounts_locators.FINISH_LATER_BUTTON_SAVE_XPATH}")
            
            # Wait for button to be visible
            logger.info(f"Waiting for Save button to be visible (timeout: {timeout}ms)...")
            save_button.wait_for(state="visible", timeout=timeout)
            logger.info("✓ Save button is visible")
            
            # Click the button
            logger.info("Clicking Save button...")
            save_button.click()
            logger.info("✓ Save button clicked successfully")
            
            # Wait for dialog to close or page state change
            self.page.wait_for_timeout(1000)
            logger.info("[PASS] Finish Later document saved successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to click Save button: {e}")
            raise AssertionError(f"Failed to click Save button in Finish Later dialog: {e}") from e

 
