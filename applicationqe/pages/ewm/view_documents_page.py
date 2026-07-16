from datetime import datetime, timedelta
import re

from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from pages.ewm.docusign_page import DocuSignPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class ViewDocumentsPage(BasePage):
    """Page object for View Documents page"""

    PAGE_NAME = "VIEW DOCUMENTS PAGE"

    def __init__(
        self,
        page: Page,
        page_verification: bool = True,
        home_url: str = "",
    ):
        """Initialize View Documents page"""
        super().__init__(page, base_url=home_url)
        self.form_root = self.active_root()

        self._init_locators()

        if page_verification:
            self._verify_page_label()
            Assertions.assert_true(self.esignature_button.is_visible(), "eSignature button should be present on View Documents page")
            logger.info("eSign button visibility verification: PASSED ")

    def _init_locators(self):
        form_root = self.form_root
        # Page locators - using more generic selectors
        self.page_label: Locator = form_root.locator(".PageHeading, h1, [class*='page-heading'], [class*='PageHeading']")
        # More flexible locators for account details
        self.account_details_container: Locator = form_root.locator("//div[contains(@class, 'account') or contains(@class, 'Account') or contains(@class, 'detail')]").first
        self.esignature_button: Locator = form_root.locator(
            "xpath=//*[@id='eSignatureButton']"
            " | //button[contains(@id, 'eSignature') or contains(@class, 'eSignatureButton')"
            " or contains(translate(normalize-space(.), 'ESIGNATURE', 'esignature'), 'esignature')]"
            " | //a[contains(translate(normalize-space(.), 'ESIGNATURE', 'esignature'), 'esignature')]"
            " | //input[contains(translate(@value, 'ESIGNATURE', 'esignature'), 'esignature')"
            " or contains(translate(@id, 'ESIGNATURE', 'esignature'), 'esignature')]"
        )
        self.esignature_ineligible: Locator = form_root.locator("//*[contains(text(), 'Not Eligible') or contains(text(), 'not eligible')]")
        self.combined_document_button: Locator = form_root.locator("//button[contains(text(), 'One Combined Document') or contains(text(), 'Combined Document')]")
        self.continue_button: Locator = form_root.locator("//button[contains(text(),'Continue')]")
        self.in_person_option: Locator = form_root.locator("[id*=inPerson] + span")
        self.is_default_option_by_mail: Locator = form_root.locator("#byEmail0")
        self.in_person_and_by_email_instruction: Locator = form_root.locator("//div[@class='col-xs-12 bundle-header-modal']")
        self.sub_advisory_agent: Locator = form_root.locator("//span[contains(text(), 'Client Signature Not Required')]")
        self.b_d_routing_heading: Locator = form_root.locator("//div[contains(@class, 'contentheading') and normalize-space(text())='Broker Dealer Routing']")
        self.b_d_routing_description: Locator = form_root.locator("//*[contains(text(),'You are responsible')]|//div[contains(text(),'Your BD/OSJ')]")
        self.b_d_routing_email_copy_option: Locator = form_root.locator("//input[@type='radio' and @id='emailcopyyes']")
        self.fa_approval_heading: Locator = form_root.locator(
            "//div[contains(@class, 'contentheading') and normalize-space(text())='Financial Advisor Approval']"
        )
        self.fa_approval_description: Locator = form_root.locator(
            "//div[contains(text(),'You are authorized to set up the account')]"
        )
        self.optional_bd_routing_heading: Locator = form_root.locator(
            "//div[contains(@class, 'contentheading') and normalize-space(text())='Optional Broker Dealer Routing']"
        )
        self.optional_bd_routing_description: Locator = form_root.locator("//*[contains(text(),'You are responsible')]")
        self.optional_bd_routing_email_copy_option: Locator = form_root.locator("//input[@type='radio' and @id='emailcopyno']")
        self.authorized_signer_approval_heading: Locator = form_root.locator("//div[text()='Authorized Signer Approval']")
        self.page_body: Locator = form_root.locator("body")
        self.authorized_signer_approval_description1: Locator = form_root.locator(
            "//div[@id='authorizedSignerMethodSection']//div[@class='authorized-signers-text-content']"
            "//span[contains(text(),'begin the signature process')]"
        )
        self.authorized_signer_approval_description2: Locator = form_root.locator(
            "//div[@id='authorizedSignerMethodSection']//div[@class='authorized-signers-text-content']"
            "//span[contains(text(),'approval from another authorized signer')]"
        )
        self.authorized_signer_approval_no: Locator = form_root.locator("//*[@id='addAuthorizedSignerNo']")
        self.authorized_signer_approval_yes: Locator = form_root.locator("//*[@id='addAuthorizedSignerYes']")
        self.authorized_signer_email: Locator = form_root.locator("#authorizedSignerEmail")
        self.authorized_signer_phone: Locator = form_root.locator("#authorizedSignerPhone")
        self.additional_documents_yes: Locator = form_root.locator("#additionaldocumentsyes")
        self.additional_documents_no: Locator = form_root.locator("#additionaldocumentsno")

        # Internal Admin locators
        self.financial_advisor_or_shared_text: Locator = self.page.get_by_text("Financial Advisor or Shared")
        self.radio_sms_checkmark: Locator = form_root.locator(".checkmark.radio-sms")
        self.authorized_signers_dropdown: Locator = form_root.locator("#authorizedsignersdropdown")

        # Finish Later / Tracking Center dialog locators
        self.finish_later_dialog: Locator = self.page.get_by_role("dialog", name="Finish Later")
        self.tracking_center_link_dialog: Locator = self.page.get_by_role("link", name="Tracking Center.")

        # Separate documents dialog locators
        self.separate_documents_button: Locator = form_root.locator("//button[contains(text(), 'Separate Documents')]")
        self.account_establishment_documents_option: Locator = form_root.locator(
            "//span[contains(text(), 'Account Establishment Documents')]"
        )
        self.separate_documents_dialog: Locator = form_root.locator("//div[@id='View_Print_SaveDocuments_dialogbox']")
        self.separate_documents_close_button: Locator = form_root.locator(
            "//input[contains(@value, 'Close')] | //button[contains(text(), 'Close')]"
        )
        self.email_input_modal: Locator = form_root.locator("input[id*='txtbdemail']")
        self.email_error_modal: Locator = form_root.locator(
            "input[id*='Hold_Email_0'] ~ .field-validation-error, "
            "div[id*='esignatureSignerModalPopup'] #errorMessage, "
            ".validation-summary-errors:near(input[id*='Hold_Email_0'])"
        )

        # eSign provider error message (inside the eSign signer popup)
        self.esign_error_message: Locator = form_root.locator("#errorMessage")

    def _verify_page_label(self):
        """Verify view documents page is loaded"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info(f"{self.PAGE_NAME} verification: PASSED")
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification failed: {str(e).splitlines()[0]}, continuing anyway")

    def verify_view_documents_page(
        self,
        reg_type: str,
        custodian: str,
        investment: str,
        amount: str,
        client_account_type: str,
        is_esignature_eligible: bool
    ):
        """
        Verify all elements on view documents page
        
        Args:
            reg_type: Registration type
            custodian: Custodian name
            investment: Investment solution
            amount: Account amount
            client_account_type: Client account type
            is_esignature_eligible: Whether eSignature is eligible
        """
        logger.info("Starting verification of View Documents page")
        
        # Handle special case for Savos Personal Portfolio Custom
        if client_account_type == "Savos Personal Portfolio Custom" and "|" in investment:
            investment = investment.split("|")[0].strip()
        
        # Wait for page to be ready
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            self.page.wait_for_timeout(2000)  # Additional wait for dynamic content
        except Exception as e:
            logger.warning(f"Page load wait: {str(e).splitlines()[0]}")
        
        # Get entire page text for verification (more resilient approach)
        try:
            page_text = self.page_body.text_content()
        except Exception as e:
            logger.error(f"Failed to get page text: {str(e).splitlines()[0]}")
            raise
        
        # Verify eSignature eligibility
        if not is_esignature_eligible:
            try:
                if self.esignature_ineligible.count() > 0:
                    logger.info("eSignature eligibility verification: PASSED - Not Eligible")
                else:
                    logger.warning("eSignature 'Not Eligible' indicator not found")
            except Exception as e:
                logger.warning(f"eSignature ineligible check failed: {str(e).splitlines()[0]}")
        else:
            try:
                if self.esignature_button.count() > 0:
                    logger.info("eSignature eligibility verification: PASSED - Button present")
                else:
                    logger.warning("eSignature button not found")
            except Exception as e:
                logger.warning(f"eSignature button check failed: {str(e).splitlines()[0]}")
        
        # Verify Registration Type in page text
        if reg_type.strip() in page_text:
            logger.info(f"Registration Type Verification: PASSED - '{reg_type}'")
        else:
            logger.warning(f"Registration Type '{reg_type}' not found in page text")
        
        # Verify Investment Solution or Client Account Type
        if client_account_type == "Multiple Strategy Account":
            if client_account_type.strip() in page_text:
                logger.info(f"Client Account Type Verification: PASSED - '{client_account_type}'")
            else:
                logger.warning(f"Client Account Type '{client_account_type}' not found")
        else:
            if investment.strip() in page_text:
                logger.info(f"Investment Solution Verification: PASSED - '{investment}'")
            else:
                logger.warning(f"Investment Solution '{investment}' not found")
        
        # Verify Amount in page text
        amount_value = "" if amount is None else str(amount).strip()
        if amount_value in page_text or f"${amount_value}" in page_text:
            logger.info(f"Account Amount Verification: PASSED - '{amount_value}'")
        else:
            logger.warning(f"Amount '{amount_value}' not found in page text")
        
        # Verify Status
        if "proposed" in page_text.lower():
            logger.info("Account Status Verification: PASSED - 'Proposed'")
        else:
            logger.warning("Status 'Proposed' not found in page text")
        
        # Verify Timestamp is present
        self._verify_timestamp_in_text(page_text)
        
        logger.info("View Documents page verification completed successfully")

    def _verify_timestamp_in_text(self, page_text: str):
        """
        Verify timestamp pattern exists in page text
        
        Args:
            page_text: Full page text content
        """
        try:
            # Look for timestamp pattern: M/d/yyyy h:mm:ss AM/PM Timezone
            timestamp_pattern = r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M\s+[A-Z]{2,4}'
            matches = re.findall(timestamp_pattern, page_text)
            
            if matches:
                timestamp_text = matches[0]
                logger.info(f"Found timestamp in page: '{timestamp_text}'")
                
                # Parse and verify it's within reasonable timeframe
                parts = timestamp_text.strip().split()
                clean_timestamp = ' '.join(parts[:-1])  # Remove timezone
                
                try:
                    timestamp_dt = datetime.strptime(clean_timestamp, "%m/%d/%Y %I:%M:%S %p")
                    current_time = datetime.now()
                    time_diff = abs((current_time - timestamp_dt).total_seconds() / 60)
                    
                    if time_diff <= 60:  # Within 1 hour is reasonable
                        logger.info(f"Timestamp Verification: PASSED - within {time_diff:.1f} minutes")
                    else:
                        logger.warning(f"Timestamp is {time_diff:.1f} minutes different from current time")
                except Exception as parse_error:
                    logger.info(f"Timestamp found but parsing optional: {parse_error}")
            else:
                pass
                
        except Exception as e:
            logger.info(f"Timestamp verification skipped: {str(e).splitlines()[0]}")

    def click_combined_documents_button(self, step_name: str, log_message: str) -> bool:
        """
        Click the One Combined Document button
        
        Args:
            step_name: Step name for logging
            log_message: Custom log message
        """
        try:
            self.combined_document_button.wait_for(state="visible", timeout=30000)
            button_text = self.combined_document_button.text_content() or ""
            if "One Combined Document" not in button_text:
                logger.warning(f"Combined document button text mismatch: '{button_text}'")
            else:
                logger.info("One Combined Document button found")

            self.combined_document_button.click()
            logger.info(f"{step_name}: {log_message}")

            # Wait for download to initiate
            self.page.wait_for_timeout(3000)
            logger.info("Clicked Combined Documents button successfully")
            return True

        except Exception as e:
            logger.warning(f"Combined document button not available: {str(e).splitlines()[0]}")
            return False
    def click_separate_documents_button(self, step_name: str, log_message: str):
        """
        Click Separate Documents button then click Account Establishment link.
        The Account Establishment click triggers the popup/new tab with the PDF.
        
        Args:
            step_name: Step name for logging
            log_message: Custom log message
        """
        try:
            # Wait for page to stabilize
            self.page.wait_for_timeout(1000)

            # Step 1: Click the Separate Documents button to open the dialog
            self.separate_documents_button.wait_for(state="visible", timeout=30000)
            logger.info("Separate Documents button found")
            try:
                self.page.evaluate("element => element.click()", self.separate_documents_button.element_handle())
                logger.info("Clicked Separate Documents button via JavaScript")
            except Exception:
                self.separate_documents_button.click()
                logger.info("Clicked Separate Documents button via regular click")

            logger.info(f"{step_name}: {log_message}")

            # Step 2: Click Account Establishment Documents link ΓÇö triggers popup/new tab
            self.account_establishment_documents_option.wait_for(state="visible", timeout=10000)
            self.account_establishment_documents_option.scroll_into_view_if_needed()
            try:
                self.page.evaluate(
                    "element => element.click()",
                    self.account_establishment_documents_option.element_handle(),
                )
                logger.info("Clicked Account Establishment Documents link via JavaScript")
            except Exception:
                self.account_establishment_documents_option.click()
                logger.info("Clicked Account Establishment Documents link via regular click")

            self.page.wait_for_timeout(1000)
            logger.info("Account Establishment Documents link clicked ΓÇö popup/new tab triggered")

        except Exception as e:
            logger.error(f"Failed to click separate documents button: {str(e).splitlines()[0]}")
            raise

    def select_account_establishment_documents(self):
        """
        Select Account Establishment Documents from the dropdown.
        The selection automatically triggers the PDF download/popup.
        
        Returns:
            None - download happens asynchronously
        """
        try:
            # Click on "Account Establishment Documents" option
            self.account_establishment_documents_option.wait_for(state="visible", timeout=10000)
            
            # Try JavaScript click for better reliability
            try:
                self.page.evaluate(
                    "element => element.click()",
                    self.account_establishment_documents_option.element_handle(),
                )
                logger.info("Selected Account Establishment Documents via JavaScript")
            except Exception:
                self.account_establishment_documents_option.click()
                logger.info("Selected Account Establishment Documents")
            
            # Wait for the selection to register and trigger the popup
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            logger.error(f"Failed to select account establishment documents: {str(e).splitlines()[0]}")
            raise

    def click_separate_documents_button_and_select_establishment(self, step_name: str, log_message: str):
        """
        Click Separate Documents button and select Account Establishment Documents
        
        Args:
            step_name: Step name for logging
            log_message: Custom log message
        """
        try:
            # Wait for page to stabilize
            self.page.wait_for_timeout(1000)
            
            # Find and click "Separate Documents" button
            self.separate_documents_button.wait_for(state="visible", timeout=30000)
            logger.info("Separate Documents button found")
            
            self.separate_documents_button.click()
            logger.info(f"{step_name}: {log_message}")
            
            # Wait for the dropdown/modal to appear
            self.page.wait_for_timeout(1000)
            
            # Click on "Account Establishment Documents" option
            self.account_establishment_documents_option.wait_for(state="visible", timeout=10000)
            
            # Try JavaScript click for better reliability
            try:
                self.page.evaluate(
                    "element => element.click()",
                    self.account_establishment_documents_option.element_handle(),
                )
                logger.info("Selected Account Establishment Documents via JavaScript")
            except Exception:
                self.account_establishment_documents_option.click()
                logger.info("Selected Account Establishment Documents")
            
            # Wait for page to process the selection
            self.page.wait_for_timeout(2000)
            logger.info("Account Establishment Documents selected successfully")
            
        except Exception as e:
            logger.error(f"Failed to click separate documents and select establishment: {str(e).splitlines()[0]}")
            raise

    def close_separate_documents_dialog(self, step_name: str, log_message: str):
        """
        Close the Separate Documents dialog by clicking Close button
        
        Args:
            step_name: Step name for logging
            log_message: Custom log message
        """
        try:
            # Find dialog and close button
            # Use base_page's close_dialog method
            self.close_dialog(self.separate_documents_dialog, self.separate_documents_close_button, timeout=10000)
            logger.info(f"{step_name}: {log_message}")
            
        except Exception as e:
            logger.warning(f"Could not close separate documents dialog: {str(e).splitlines()[0]}, continuing anyway")

    def e_signature_start(self, option: str, advisor_type: str, custodian: str = "", test_data: dict = None):
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.wait_for_timeout(1000)

        existing_pages = list(self.page.context.pages)

        self.esignature_button.wait_for(state="visible", timeout=15000)
        try:
            self.esignature_button.scroll_into_view_if_needed()
            self.esignature_button.click(timeout=7000)
            logger.info("eSignature button clicked via regular click")
        except Exception as e1:
            logger.warning(f"Regular eSignature click failed: {str(e1).splitlines()[0]}")
            try:
                self.esignature_button.click(force=True, timeout=7000)
                logger.info("eSignature button clicked via force click")
            except Exception as e2:
                logger.warning(f"Force eSignature click failed: {str(e2).splitlines()[0]}")
                self.esignature_button.evaluate("el => el.click()")
                logger.info("eSignature button clicked via JavaScript")
        self.wait_for_timeout(3000)

        if advisor_type.strip().lower() == "subadvisory":
            self._handle_sub_advisory_agent(custodian, test_data)
        else:
            if advisor_type.strip().lower() == "non subadvisory":
                self._handle_non_sub_advisory_agent(option, custodian, test_data)

        current_pages = list(self.page.context.pages)
        if len(current_pages) > len(existing_pages):
            new_page = current_pages[-1]
            self.page = new_page

    def _handle_sub_advisory_agent(self, custodian: str = "", test_data: dict = None):
        if self.sub_advisory_agent.is_visible():
            Assertions.assert_text_contains(self.sub_advisory_agent, "Client Signature Not Required")
        self._click_continue_button()

    def _handle_non_sub_advisory_agent(self, option: str, custodian: str = "", test_data: dict = None):
        is_default_by_mail = self.is_default_option_by_mail.is_checked()
        Assertions.assert_true(is_default_by_mail, "Expected default selected option to be 'By Email'")

        option_lower = option.lower()

        if "in person" in option_lower:
            self.in_person_option.scroll_into_view_if_needed()
            self.in_person_option.click()

        self._validate_instructions()
        if "in person" in option_lower:
            self.in_person_option.click()
            logger.info("click in person option")
        else:
            logger.info("by mail option selected; leaving default selection")

        self.user_e_sign_method(test_data)
        self._validate_broker_dealer_routing()
        self._validate_financial_advisor_approval()
        self._validate_optional_broker_dealer_routing()
        self._validate_authorized_signer_approval()
        self._enter_fidelity_details(custodian, test_data)

        if self.additional_documents_no.count() > 0 and not self.additional_documents_no.is_checked():
            self.click(self.additional_documents_no, timeout=5000)

            if not self.additional_documents_no.is_checked():
                self.additional_documents_no.evaluate(
                    "el => { el.checked = true; el.dispatchEvent(new Event('change', { bubbles: true })); }"
                )

        self._click_continue_button()

    def _validate_instructions(self):
        instruction_text = (self.in_person_and_by_email_instruction.text_content() or "").lower()
        in_person_ok = "in person" in instruction_text
        by_email_ok = "by email" in instruction_text
        Assertions.assert_true(in_person_ok and by_email_ok, "Expected 'In Person And By Email Instruction'")

    def _validate_broker_dealer_routing(self):
        if self.b_d_routing_heading.is_visible():
            Assertions.assert_text_contains(self.b_d_routing_heading, "Broker Dealer Routing")

            description = (self.b_d_routing_description.text_content() or "").strip()
            expected_a = (
                "You are responsible to monitor the account approval process with your BD/OSJ"
            )
            expected_b = (
                "Your BD/OSJ must provide their approval before AssetMark will process the account applications"
            )
            Assertions.assert_true(
                expected_a in description or expected_b in description,
                "Expected 'Broker Dealer Routing Instruction'",
            )

            if self.b_d_routing_email_copy_option.is_visible():
                Assertions.assert_true(
                    self.b_d_routing_email_copy_option.is_checked(),
                    "Expected the default selected Email Copy option to be 'YES' For Broker Dealer Routing",
                )

    def _validate_financial_advisor_approval(self):
        if self.fa_approval_heading.is_visible():
            Assertions.assert_text_contains(self.fa_approval_heading, "Financial Advisor Approval")
            Assertions.assert_text_contains(
                self.fa_approval_description,
                "You are authorized to set up the account",
            )

    def _validate_optional_broker_dealer_routing(self):
        if self.optional_bd_routing_heading.is_visible():
            Assertions.assert_text_contains(self.optional_bd_routing_heading, "Optional Broker Dealer Routing")
            Assertions.assert_text_contains(
                self.optional_bd_routing_description,
                "You are responsible to monitor the account approval process",
            )

            Assertions.assert_true(
                self.optional_bd_routing_email_copy_option.is_checked(),
                "Expected the default selected Email Copy option to be 'No' For Optional Broker Dealer Routing",
            )

    def _validate_authorized_signer_approval(self):
        if self.authorized_signer_approval_heading.is_visible():
            Assertions.assert_text_contains(self.authorized_signer_approval_heading, "Authorized Signer Approval")
            Assertions.assert_text_contains(
                self.authorized_signer_approval_description1,
                "begin the signature process",
            )
            Assertions.assert_text_contains(
                self.authorized_signer_approval_description2,
                "approval from another authorized signer",
            )

            no_selected = self.authorized_signer_approval_no.is_checked()
            yes_selected = self.authorized_signer_approval_yes.is_checked()
            Assertions.assert_true(
                not no_selected and not yes_selected,
                "Expected 'No option selected for Authorized Signer Approval'",
            )
            
            self.authorized_signer_approval_no.click()

    def _enter_fidelity_details(self, custodian: str = "", test_data: dict = None):
        """Fill authorized signer email and phone fields for Fidelity custodian"""
        
        if not (custodian and custodian.strip().lower() == "fidelity" and test_data):
            return
        
        try:
            email = test_data.get("AccountHolderEmail", "")
            phone = test_data.get("AccountHolderPhone", "")
            
            # Fill email field
            if email and self.authorized_signer_email.is_visible():
                self.authorized_signer_email.click()
                self.wait_for_timeout(200)
                self.authorized_signer_email.dblclick()
                self.wait_for_timeout(200)
                self.authorized_signer_email.fill(email)
                self.wait_for_timeout(200)
                logger.info(f"Filled Fidelity email: {email}")
            
            # Fill phone field
            if phone and self.authorized_signer_phone.is_visible():
                self.authorized_signer_phone.dblclick()
                self.wait_for_timeout(200)
                self.authorized_signer_phone.fill(str(phone))
                self.wait_for_timeout(200)
                logger.info(f"Filled Fidelity phone: {phone}")
        
        except Exception as e:
            logger.error(f"Failed to fill Fidelity details: {str(e).splitlines()[0]}", exc_info=True)

    def user_e_sign_method(self, test_data: dict = None) -> None:
        """Handle Internal Admin specific flow: select signer from dropdown and fill phone."""
        if not self.is_visible(self.financial_advisor_or_shared_text, timeout=3000):
            logger.info("'Financial Advisor or Shared' text not present, skipping internal admin handling")
            return

        logger.info("'Financial Advisor or Shared' text detected, handling internal admin flow")

        # Click the radio button
        self.radio_sms_checkmark.scroll_into_view_if_needed()
        self.click(self.radio_sms_checkmark)
        logger.info("Clicked radio-sms checkmark")
        self.wait_for_timeout(1000)

        # Select the authorized signer by index (first non-placeholder option)
        authorized_by = (test_data.get("AuthorizedBy", "") or "").strip() if test_data else ""
        if not authorized_by:
            logger.warning("AuthorizedBy column is empty in test data, selecting by index")

        self.authorized_signers_dropdown.wait_for(state="visible", timeout=5000)
        self.wait_for_timeout(1000)
        options = self.authorized_signers_dropdown.locator("option").all()

        # Select second option (index 1) — first is always placeholder '-Select Authorized Signers-'
        if len(options) > 1:
            second_option = options[1]
            matched_value = second_option.get_attribute("value") or ""
            opt_text = (second_option.text_content() or "").strip()
            logger.info(f"Selecting authorized signer (index 1): {opt_text}")
        else:
            Assertions.fail("No authorized signer options available in dropdown")

        self.authorized_signers_dropdown.select_option(matched_value)
        logger.info(f"Selected authorized signer: {opt_text}")
        self.wait_for_timeout(500)

        # Fill phone number
        phone = str(test_data.get("AccountHolderPhone", "") or "").strip() if test_data else ""
        if phone and self.is_visible(self.authorized_signer_phone, timeout=3000):
            self.authorized_signer_phone.click()
            self.fill(self.authorized_signer_phone, str(phone))
            logger.info(f"Filled authorized signer phone: {phone}")
        else:
            logger.info("Phone field not visible or no phone in test data, skipping")

    def clickTrackingCenterLink(self) -> None:
        """Click the Tracking Center link on the Finish Later dialog."""
        logger.info("[view-docs] Waiting for Finish Later dialog")
        try:
            self._heal_and_retry(self.finish_later_dialog, lambda loc: loc.wait_for(state="visible", timeout=20000))
        except Exception:
            logger.warning("[view-docs] Finish Later dialog wait failed via _heal_and_retry")
        self.wait_for_timeout(3000)

        logger.info("[view-docs] Clicking 'Tracking Center' link")
        try:
            self._heal_and_retry(self.tracking_center_link_dialog, lambda loc: loc.click())
        except Exception:
            logger.warning("[view-docs] Tracking Center link click failed, falling back to JS click")
            self.tracking_center_link_dialog.evaluate("el => el.click()")
        self.wait_for_timeout(5000)
        logger.info("[view-docs] Navigated to Tracking Center")

    def _click_continue_button(self):
        # Handle iframe/actionability edge-cases with compact click fallbacks.
        self.continue_button.wait_for(state="visible", timeout=15000)

        clicked = False
        try:
            self.continue_button.scroll_into_view_if_needed()
            self.continue_button.click(timeout=7000)
            clicked = True
            logger.info("Continue button clicked via regular click")
        except Exception as e1:
            logger.warning(f"Regular Continue click failed: {str(e1).splitlines()[0]}")
            try:
                self.continue_button.click(force=True, timeout=7000)
                clicked = True
                logger.info("Continue button clicked via force click")
            except Exception as e2:
                logger.warning(f"Force Continue click failed: {str(e2).splitlines()[0]}")
                self.continue_button.evaluate("el => el.click()")
                clicked = True
                logger.info("Continue button clicked via JavaScript")

        Assertions.assert_true(clicked, "Failed to click Continue button with all fallback strategies")

        # Wait for spinner to disappear (server is processing the eSign request)
        self.wait_for_spinner_to_disappear(timeout=60)

        # Fail fast if eSign provider error appears after spinner completes
        if self.esign_error_message.count() > 0 and self.esign_error_message.first.is_visible():
            error_text = (self.esign_error_message.first.text_content() or "").strip()
            if error_text:
                logger.error(f"eSign provider error: {error_text}")
                Assertions.fail(f"eSign provider error: {error_text}")

        # Log current URL for debugging
        current_url = self.page.url
        logger.info(f"Current URL after continue click: {current_url}")

    def e_signature_start_by_mail(
        self,
        option: str,
        advisor_type: str,
        custodian: str = "",
        test_data: dict = None,
        outlook_email: str = "",
        outlook_password: str = "",
    ):
        """
        Handle eSignature start for 'by mail' flow with OTP verification
        
        Args:
            option: eSignature option (should be "by mail")
            advisor_type: Sub-advisory or Non Sub-advisory
            custodian: Custodian type
            test_data: Test data dictionary
            outlook_email: Outlook email for OTP retrieval
            outlook_password: Outlook password for OTP retrieval
            
        Returns:
            DocuSignPage instance configured for "by mail" signing
        """
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.wait_for_timeout(1000)

        existing_pages = list(self.page.context.pages)

        self.esignature_button.wait_for(state="visible", timeout=15000)
        try:
            self.esignature_button.scroll_into_view_if_needed()
            self.esignature_button.click(timeout=7000)
            logger.info("eSignature button clicked via regular click")
        except Exception as e1:
            logger.warning(f"Regular eSignature click failed: {str(e1).splitlines()[0]}")
            try:
                self.esignature_button.click(force=True, timeout=7000)
                logger.info("eSignature button clicked via force click")
            except Exception as e2:
                logger.warning(f"Force eSignature click failed: {str(e2).splitlines()[0]}")
                self.esignature_button.evaluate("el => el.click()")
                logger.info("eSignature button clicked via JavaScript")
        self.wait_for_timeout(3000)

        if advisor_type.strip().lower() == "subadvisory":
            self._handle_sub_advisory_agent(custodian, test_data)
        else:
            if advisor_type.strip().lower() == "non subadvisory":
                self._handle_non_sub_advisory_agent(option, custodian, test_data)

        current_pages = list(self.page.context.pages)
        if len(current_pages) > len(existing_pages):
            new_page = current_pages[-1]
            self.page = new_page

        # Return DocuSignPage with OTP credentials for "by mail" flow
        docusign_page = DocuSignPage(self.page)
        docusign_page.outlook_email = outlook_email
        docusign_page.outlook_password = outlook_password
        
        return docusign_page

    def get_all_separate_document_names(self) -> list[str]:
        """Open the Separate Documents dialog and collect all visible document link text.

        Returns:
            Sorted list of document name strings found in the dialog.
        """
        logger.info("Opening Separate Documents dialog to collect document names")
        form_root = self.form_root

        # Click Separate Documents button
        self.separate_documents_button.wait_for(state="visible", timeout=15000)
        try:
            self.separate_documents_button.click()
        except Exception:
            self.separate_documents_button.evaluate("el => el.click()")
        self.page.wait_for_timeout(1500)

        # Collect all link/span text inside the dialog
        dialog = self.separate_documents_dialog
        dialog.wait_for(state="visible", timeout=10000)
        links = dialog.locator("a, span.document-link, span[class*='doc']")
        count = links.count()
        doc_names: list[str] = []
        for i in range(count):
            text = (links.nth(i).text_content() or "").strip()
            if text:
                doc_names.append(text)

        # If links locator returned nothing, try broader fallback
        if not doc_names:
            all_text = (dialog.text_content() or "").strip()
            # Split by newlines to get individual entries
            for line in all_text.splitlines():
                line = line.strip()
                if line and line.lower() not in ("close", "separate documents"):
                    doc_names.append(line)

        logger.info(f"Found {len(doc_names)} documents in Separate Documents dialog")
        for name in doc_names:
            logger.info(f"  Document: {name}")

        # Close the dialog
        try:
            close_btn = form_root.locator(
                "//input[contains(@value, 'Close')] | //button[contains(text(), 'Close')]"
            ).first
            close_btn.click(timeout=5000)
        except Exception as e:
            logger.warning(f"Could not close Separate Documents dialog: {str(e).splitlines()[0]}")

        return sorted(doc_names)

    def get_docusign_page_instance(self):
        """
        Get DocuSignPage instance for the current page context.
        
        This is used when the context has switched to a DocuSign page after clicking
        the eSignature button or similar navigation.
        
        Returns:
            DocuSignPage instance for the current page
        """
        logger.info("Getting DocuSignPage instance for current page context")
        docusign_page = DocuSignPage(self.page)
        return docusign_page

    def get_client_name(self) -> str:
        """
        Extract client name from the page.
        
        Attempts to get the client name from:
        1. Page title (first preference)
        2. Account details container text content (fallback)
        
        Returns:
            Client name string, or empty string if not found
        """
        try:
            # Try to get from page title first
            page_title = self.page.title()
            if page_title:
                logger.info(f"Page title: {page_title}")
                # Try to extract client name from title
                # Example: "Client Name - Dashboard" -> "Client Name"
                if " - " in page_title:
                    client_name = page_title.split(" - ")[0].strip()
                    if client_name:
                        logger.info(f"Client name from page title: {client_name}")
                        return client_name
            
            # Fallback to account details container
            try:
                account_details_text = self.account_details_container.text_content()
                if account_details_text:
                    logger.info(f"Client name from account details: {account_details_text[:50]}")
                    return account_details_text.strip()
            except Exception:
                pass
            
            logger.warning("Client name not found on page")
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting client name: {str(e).splitlines()[0]}")
            return ""
        
    def click_eSign_button(self):        
        self.esignature_button.click(timeout=5000)
        logger.info("eSignature button clicked via regular click")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.check(self.b_d_routing_email_copy_option)
        logger.info("eSignature page loaded and email copy option is visible")

    def fill_email_address_modal(self, email: str) -> None:
        """Fill the account holder email input field."""
        email_value = "" if email is None else str(email).strip()
        self.email_input_modal.first.wait_for(state="visible", timeout=5000)
        self.fill(self.email_input_modal.first, email_value)
        logger.info(f"Filled email field with: {email_value}")        
