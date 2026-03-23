"""
Client Accounts Page Object

Page object for client account interactions and verifications.
"""

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

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.logger = logger

    def navigate(self) -> None:
        """Navigate to client accounts page."""
        self.navigate_to(self.PAGE_PATH)

    def _get_esig_iframe(self):
        """
        Get reference to eSignature iframe with safety check.
        
        Returns:
            FrameLocator if found, None otherwise
        """
        iframe_locator = self.page.locator(client_accounts_locators.ESIG_IFRAME)
        if iframe_locator.count() == 0:
            logger.warning("🔧 iframe#esig_iframe not found")
            return None
        return self.page.frame_locator(client_accounts_locators.ESIG_IFRAME)


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

    def provide_authorized_signers_information(self, authorized_signer: str, email_address: str, phone: str) -> None:
        """
        Provide Authorized Signers information on the Signer(s) Information dialog.
        
        Args:
            authorized_signer: Name/value of authorized signer to select (if dropdown is enabled)
            email_address: Email address to enter
            phone: Phone number to enter
        
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
            dropdown = iframe_frame.locator("select[name='authorizedSignersDropdown']")
            
            if dropdown.count() == 0:
                raise AssertionError("Authorized Signers dropdown not found")
            
            # Check if dropdown is enabled
            is_disabled = dropdown.is_disabled()
            logger.info(f"  ✓ Dropdown found. Disabled status: {is_disabled}")
            
            if not is_disabled and authorized_signer and authorized_signer.strip():
                logger.info(f"  Step 3: Dropdown is enabled. Attempting to select '{authorized_signer}'...")
                dropdown.select_option(value=authorized_signer)
                logger.info(f"  ✓ Option '{authorized_signer}' selected")
                self.page.wait_for_load_state("networkidle", timeout=3000)
            else:
                if is_disabled:
                    logger.info("  ✓ Dropdown is disabled, skipping selection as per requirements")
                else:
                    logger.info("  ⚠ Authorized signer value is empty, skipping selection")
            
            # Step 4: Fill Email Address
            if email_address and email_address.strip():
                logger.info("  Step 4: Filling Email Address...")
                email_input = iframe_frame.locator("input[name='emailText']")
                
                if email_input.count() == 0:
                    raise AssertionError("Email Address input not found")
                
                if not email_input.is_visible():
                    raise AssertionError("Email Address input not visible")
                
                # Clear existing value first
                email_input.clear()
                email_input.fill(email_address)
                logger.info(f"  ✓ Email Address filled: {email_address}")
            else:
                logger.info("  ⚠ Email Address value is empty, skipping")
            
            # Step 5: Fill Phone
            if phone and phone.strip():
                logger.info("  Step 5: Filling Phone...")
                phone_input = iframe_frame.locator("input[name='PhoneText']")
                
                if phone_input.count() == 0:
                    raise AssertionError("Phone input not found")
                
                if not phone_input.is_visible():
                    raise AssertionError("Phone input not visible")
                
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

    def select_authorized_signer_esign_method(self, method: str) -> None:
        """
        Select Authorized Signer eSign Method (SMS or Tracking Center).
        
        Args:
            method: The eSign method to select ('SMS' or 'Tracking Center')
        
        Raises:
            AssertionError: If method is invalid or radio button not found/clickable
        """
        valid_methods = ["SMS", "Tracking Center"]
        if method not in valid_methods:
            raise AssertionError(f"Invalid eSign method '{method}'. Must be one of: {valid_methods}")
        
        logger.info(f"Selecting '{method}' eSign method radio button...")
        self._select_authorized_signer_esign_method(method)

    def _select_authorized_signer_esign_method(self, method: str) -> None:
        """
        Internal method to select eSign method radio button.
        
        Args:
            method: The eSign method to select ('SMS' or 'Tracking Center')
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
            radio_button_id = "radiobtnSMS" if method == "SMS" else "radiobtnTC"
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
            self.page.wait_for_load_state("networkidle", timeout=5000)
            
            is_checked = radio_button.is_checked()
            if not is_checked:
                logger.warning(f"  ⚠ '{method}' radio button may not be selected (is_checked returned False)")
            else:
                logger.info(f"  ✓ '{method}' radio button is selected")
            
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

    def verify_authorized_signers_dropdown(self, signers: list) -> None:
        """
        Verify Authorized Signers dropdown state and options based on signer count.
        
        If signers count == 1: Dropdown should be disabled
        If signers count > 1: Dropdown options should match signer Name_ManageLogin values
        
        Args:
            signers: List of signer dicts with 'Name_ManageLogin' and 'Role' keys
                     from test_context["multiple_signers"]
        
        Raises:
            AssertionError: If validation fails
        """
        logger.info(f"Verifying Authorized Signers dropdown with {len(signers)} signer(s)...")
        
        try:
            # Step 1: Access iframe
            logger.info("  Step 1: Accessing iframe...")
            iframe_frame = self._get_esig_iframe()
            if not iframe_frame:
                raise AssertionError("Signer Information dialog iframe (iframe#esig_iframe) not found")
            logger.info("  ✓ Iframe accessed")
            
            # Step 2: Find dropdown
            logger.info("  Step 2: Locating Authorized Signers dropdown...")
            dropdown = iframe_frame.locator("select[name='authorizedSignersDropdown']")
            
            if dropdown.count() == 0:
                raise AssertionError("Authorized Signers dropdown not found")
            
            if not dropdown.is_visible():
                raise AssertionError("Authorized Signers dropdown not visible")
            
            logger.info("  ✓ Dropdown found and visible")
            
            # Step 3: Validate based on signer count
            if len(signers) == 1:
                # Case 1: Only 1 signer - dropdown should be disabled and default option should match signer name
                logger.info("  Step 3: Validating dropdown is disabled (1 signer present)...")
                is_disabled = dropdown.is_disabled()
                
                if not is_disabled:
                    raise AssertionError(
                        f"Dropdown should be disabled when only 1 signer is present, "
                        f"but is_disabled returned: {is_disabled}"
                    )
                
                logger.info("  ✓ Dropdown is correctly disabled (1 signer only)")
                
                # Step 4: Verify the default selected option matches the signer name
                logger.info("  Step 4: Verifying default selected option matches signer name...")
                signer_name = signers[0].get("Name_ManageLogin", "")
                
                if not signer_name:
                    raise AssertionError("Name_ManageLogin not found in signer data")
                
                # Get the selected option text
                selected_option = iframe_frame.locator("select[name='authorizedSignersDropdown'] option[selected]")
                
                if selected_option.count() == 0:
                    raise AssertionError("No selected option found in dropdown")
                
                selected_text = (selected_option.first.text_content() or "").strip()
                logger.info(f"  Selected option text: '{selected_text}'")
                logger.info(f"  Expected signer name: '{signer_name}'")
                
                if selected_text != signer_name:
                    raise AssertionError(
                        f"Selected option mismatch: expected '{signer_name}', "
                        f"but found '{selected_text}'"
                    )
                
                logger.info(f"  ✓ Default selected option matches signer: '{selected_text}'")
                
            elif len(signers) > 1:
                # Case 2: Multiple signers - dropdown should be enabled and options match signers
                logger.info(f"  Step 3: Validating dropdown options match {len(signers)} signers...")
                is_disabled = dropdown.is_disabled()
                
                if is_disabled:
                    raise AssertionError(
                        f"Dropdown should be enabled when {len(signers)} signers are present, "
                        f"but is_disabled returned: {is_disabled}"
                    )
                
                logger.info("  ✓ Dropdown is enabled")
                
                # Step 4: Fetch all options from dropdown
                logger.info("  Step 4: Fetching dropdown options...")
                options = iframe_frame.locator("select[name='authorizedSignersDropdown'] option").all()
                
                if not options:
                    raise AssertionError("No options found in dropdown")
                
                logger.info(f"  ✓ Found {len(options)} option(s) in dropdown")
                
                # Step 5: Extract option texts (skip first option which is "--Select Authorized Signer--")
                logger.info("  Step 5: Extracting and validating option values...")
                option_texts = []
                for idx, option in enumerate(options):
                    option_text = (option.text_content() or "").strip()
                    option_texts.append(option_text)
                    logger.info(f"    Option {idx}: '{option_text}'")
                
                # Skip the first "--Select Authorized Signer--" option
                actual_options = option_texts[1:] if len(option_texts) > 1 else option_texts
                
                # Step 6: Extract expected signer names from test_context signers
                logger.info("  Step 6: Comparing options with signer names...")
                expected_signer_names = [signer.get("Name_ManageLogin", "") for signer in signers]
                
                logger.info(f"  Expected signer names: {expected_signer_names}")
                logger.info(f"  Actual dropdown options: {actual_options}")
                
                # Validate count matches
                if len(actual_options) != len(expected_signer_names):
                    raise AssertionError(
                        f"Option count mismatch: expected {len(expected_signer_names)} options "
                        f"(matching {len(expected_signer_names)} signers), "
                        f"but found {len(actual_options)} options"
                    )
                
                logger.info(f"  ✓ Option count matches signer count: {len(actual_options)}")
                
                # Validate each option matches a signer name
                for idx, (actual, expected) in enumerate(zip(actual_options, expected_signer_names)):
                    if actual != expected:
                        raise AssertionError(
                            f"Option {idx + 1} mismatch: expected '{expected}', "
                            f"but found '{actual}'"
                        )
                    logger.info(f"  ✓ Option {idx + 1} matches: '{actual}'")
                
                logger.info("  ✓ All dropdown options match signer names")
            
            else:
                # Case 3: No signers - log warning
                logger.warning("  ⚠ Warning: No signers provided in test_context['multiple_signers']")
            
            logger.info("✓ Successfully verified Authorized Signers dropdown")
            
        except Exception as e:
            logger.error(f"✗ Failed to verify Authorized Signers dropdown: {e}")
            raise AssertionError(f"Failed to verify Authorized Signers dropdown: {e}") from e

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
            with WaitContext(timeout=10.0, poll_interval=0.2) as wait:
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

                    # Primary strategy: role-based locator (fastest)
                    item = container.get_by_role('listitem', name=type_name)
                    if item.count() > 0:
                        if self._wait_and_click_element(item, f"Type '{type_name}'", timeout_ms=1500):
                            logger.info(f"✓ Type '{type_name}' selected via role locator")
                            retry.success()
                            return
                    else:
                        logger.debug(f"Role-based locator count=0 for '{type_name}'")

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
        dialog_handler.wait_for_dialog(timeout=15000)
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
        dialog = dialog_handler.wait_for_dialog(timeout=10000)
        logger.info("Request Submitted dialog appeared")

        # Get dialog title and content using dialog_handler
        dialog_title = dialog_handler.get_dialog_title(timeout=5000)
        logger.info(f"Dialog Title: {dialog_title}")

        dialog_content = dialog_handler.get_dialog_text(timeout=5000)
        logger.info(f"Dialog Content:\n{dialog_content}")

        # Get the D-link (tracking center link) from the FIRST dialog only
        # Target: <a class="printConfirmationLink" href="...">D003525811</a>
        d_link = self.page.locator('[role="dialog"]').first.locator('a.printConfirmationLink')
        d_link.wait_for(state="visible", timeout=5000)
        d_link_text = (d_link.text_content() or "").strip() if d_link.text_content() else ""
        d_link_href = d_link.get_attribute("href") or ""
        logger.info(f"D-Link Text: {d_link_text}, Href: {d_link_href}")

        # Get the "Print or Download" link from the FIRST dialog only
        # Target: <a href="#" onclick="return btnDownload();">Print or Download</a>
        print_download_link = self.page.locator('[role="dialog"]').first.locator('a[onclick*="btnDownload"]')
        logger.info(f"Print or Download link found: {print_download_link.count() > 0}")

        # Get Close button from the FIRST dialog only
        # Target the visible formButton close button at the bottom (not the hidden titlebar close button)
        # The close button is in the .close-button-container div in the footer
        close_button = self.page.locator('[role="dialog"]').first.locator('.close-button-container button.formButton')
        close_button.wait_for(state="visible", timeout=5000)
        logger.info("Close button found")

        return {
            'title': dialog_title,
            'content': dialog_content,
            'd_link': d_link,
            'd_link_text': d_link_text,
            'd_link_href': d_link_href,
            'print_download_link': print_download_link,
            'close_button': close_button
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
        dialog_text = dialog_handler.get_dialog_text(timeout=10000)
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
            task_name_span.wait_for(state='visible', timeout=10000)
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

    # TODO: Add additional page-specific methods for client account interactions
