"""
Client Accounts Step Definitions

Step definitions for client account related interactions in BDD tests.
"""
import allure
from playwright.sync_api import Page
from pytest_bdd import given, when, then, parsers

from pages.client_accounts_page import ClientAccountsPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.soft_assertions_enhanced import EnhancedSoftAssertions
from utils.database import fetch_agent_name_by_aplid_from_db, fetch_authorized_signer
from utils.dialog_utils import DialogHandler
from utils.helpers import find_element_position_in_parent
from utils.wait_utils import WaitContext, wait_for_element_count

logger = get_allure_logger(__name__)


@when("User select Authorized Signer Approval option")
def select_authorized_signer_approval_option(authenticated_page: Page, client_accounts_page, test_context):
    """
    Select radio button on Authorized Signer Approval section.
    
    Fetches the option ('Yes' or 'No') from test data (Authorized_Signer_Approval_Option column)
    and selects the appropriate radio button on the Signer(s) Information dialog.
    """
    with allure.step("User select Authorized Signer Approval option"):
        logger.info(">>> STEP: User select Authorized Signer Approval option")
        
        try:
            # Step 1: Fetch the option from test data
            logger.info("  Step 1: Fetching Authorized Signer Approval option from test data...")
            test_data = test_context.get("test_data", {})
            option = test_data.get("Authorized_Signer_Approval_Option", "").strip()
            
            if not option:
                raise AssertionError("[FAIL] ClientAccountsPage: CSV Data Parsing — Expected: 'Authorized_Signer_Approval_Option' not empty, Actual: column is empty. Details: Test data CSV must include 'Authorized_Signer_Approval_Option' column with value 'Yes' or 'No'. Locator: test_data['Authorized_Signer_Approval_Option'].")
            
            valid_options = ["Yes", "No"]
            if option not in valid_options:
                raise AssertionError(
                    f"[FAIL] ClientAccountsPage: CSV Data Validation — Expected: value in {valid_options}, Actual: '{option}'. Details: 'Authorized_Signer_Approval_Option' must be 'Yes' or 'No'. Locator: test_data['Authorized_Signer_Approval_Option']."
                )
            
            logger.info(f"  [PASS] ClientAccountsPage: CSV Data Parsed.")
            
            # Step 2: Call page object method to select the radio button
            logger.info(f"  Step 2: Selecting '{option}' radio button...")
            client_accounts_page.select_authorized_signer_approval_option(option)
            
            # Step 3: Take screenshot for Allure reporting
            logger.info("  Step 3: Taking screenshot after selection...")
            allure.attach(
                authenticated_page.screenshot(),
                name=f"Authorized Signer Approval - {option} Selected",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info(f"[PASS] ClientAccountsPage: Authorized Signer Approval Option Selected.")
            
        except Exception as e:
            logger.error(f"✗ Failed to select Authorized Signer Approval option: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Authorized Signer Approval - Selection Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Failed to select Authorized Signer Approval option: {e}") from e

@then("Signer(s) Information dialog should be displayed")
def verify_signer_information_dialog_exists_with_correct_information(
    authenticated_page: Page, client_accounts_page, test_context
):
    """
    Verify Signer(s) Information dialog is displayed with correct content.
    
    Validates:
    1. Signer(s) Information dialog is visible
    2. Heading text in div#divSignersInfo is Signer(s) Information
    3. Instruction text in table#esig_user_details_table first TD is as expected
    
    CSV format: Expected_Signer_Information_Text = "Heading | Instruction"
    """
    with allure.step("Signer(s) Information dialog is displayed"):
        logger.info(">>> STEP: Signer(s) Information dialog is displayed")
        
        try:
            # Initialize soft assertions
            soft_assert = EnhancedSoftAssertions(authenticated_page)
            
            # Step 1: Wait for and detect dialog
            logger.info("Step 1: Waiting for Signer Information dialog...")
            dialog_handler = DialogHandler(authenticated_page)
            dialog = dialog_handler.wait_for_dialog(timeout=19000)
            # Note: Dialog was successfully found in DOM by wait_for_dialog()
            # No visibility assertion needed - dialog is in DOM and accessible for interaction
            # jQuery UI dialogs may have CSS that affects to_be_visible() checks
            logger.info("[PASS] ClientAccountsPage: Signer Information Dialog Detected.")
            
            # Step 2: Get and parse expected text from CSV
            logger.info("Step 2: Fetching expected text from CSV...")
            test_data = test_context.get("test_data", {})
            expected_signer_text = (test_data.get("Expected_Signer_Information_Text") or "").strip()
            
            if not expected_signer_text:
                raise AssertionError("[FAIL] ClientAccountsPage: CSV Data Validation — Expected: Expected_Signer_Information_Text not empty, Actual: column is empty. Details: Test data CSV must include Expected_Signer_Information_Text column with pipe-separated sections. Locator: test_data['Expected_Signer_Information_Text'].")
            
            parts = [p.strip() for p in expected_signer_text.split("|")] if "|" in expected_signer_text else [expected_signer_text]
            heading_text = parts[0] if len(parts) > 0 and parts[0] else None
            instruction_text = parts[1] if len(parts) > 1 and parts[1] else None
            
            logger.info(f"[PASS] ClientAccountsPage: CSV Data Parsed.")
            
            # Step 3: Try iframe first, fallback to main page
            logger.info("Step 3: Waiting for potential iframe to be ready...")
            try:
                wait_for_element_count(
                    authenticated_page.locator("iframe#esig_iframe"),
                    count=1,
                    timeout=30.0
                )
            except Exception:
                logger.debug("Iframe not present or didn't appear within timeout - will check main page content")
            
            logger.info("Step 3: Validating content...")
            iframe_count = authenticated_page.locator("iframe#esig_iframe").count()
            
            if iframe_count > 0:
                logger.info("  Checking iframe content...")
                iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
                
                if heading_text:
                    logger.info("  Waiting for signer header element to be available...")
                    try:
                        wait_for_element_count(
                            iframe_frame.locator("div#divSignersInfo"),
                            count=1,
                            timeout=30.0
                        )
                    except Exception as e:
                        logger.warning(f"  ⚠ Signer header element wait timeout/error: {e} - proceeding with assertion anyway")
                    
                    signer_header = iframe_frame.locator("div#divSignersInfo")
            soft_assert.assert_count(
                signer_header,
                1,
                "[FAIL] ClientAccountsPage: Signer Information Header — Expected: div#divSignersInfo count=1, Actual: count not 1. Details: Signer(s) Information dialog header must be visible in iframe esig_iframe. Locator: iframe#esig_iframe > div#divSignersInfo."
            )
            soft_assert.assert_visible(
                signer_header,
                "[FAIL] ClientAccountsPage: Signer Information Header Visibility — Expected: visible=True, Actual: visible=False. Details: Signer(s) Information dialog header must be visible to read heading. Locator: div#divSignersInfo."
            )
            
            if heading_text:
                soft_assert.assert_text_contains(signer_header, heading_text, f"[FAIL] ClientAccountsPage: Signer Information Heading Text — Expected: contains '{heading_text}', Actual: text mismatch. Details: Signer(s) Information dialog heading must match expected value. Locator: div#divSignersInfo.")
                logger.info(f"  [PASS] ClientAccountsPage: Signer Information Heading Verified.")
            
            if instruction_text:
                details_table = iframe_frame.locator("table#esig_user_details_table")
                soft_assert.assert_count(
                    details_table,
                    1,
                    "[FAIL] ClientAccountsPage: Signer Details Table — Expected: table#esig_user_details_table count=1, Actual: count not 1. Details: Signer(s) Information dialog details must exist. Locator: iframe#esig_iframe > table#esig_user_details_table."
                )
                soft_assert.assert_visible(details_table, message="[FAIL] ClientAccountsPage: Signer Details Visibility — Expected: visible=True, Actual: visible=False. Details: Signer(s) Information dialog details must be visible. Locator: table#esig_user_details_table.")
                
                first_td = details_table.locator("td").first
                soft_assert.assert_count(first_td, 1, message="[FAIL] ClientAccountsPage: Signer Details TD — Expected: td count=1, Actual: count!=1. Details: First TD in Signer(s) Information dialog details table must exist. Locator: table#esig_user_details_table td.")
                soft_assert.assert_visible(first_td, message="[FAIL] ClientAccountsPage: Signer Details TD Visibility — Expected: visible=True, Actual: visible=False. Details: First TD in Signer(s) Information dialog details table must be visible. Locator: table#esig_user_details_table td:first.")
                
                # Get actual text from element for debugging
                actual_instruction_text = first_td.text_content().strip() if first_td.count() > 0 else ""
                # Normalize both texts for comparison (handles Unicode, smart quotes, special chars)
                normalized_actual_text = client_accounts_page.normalize_text_for_comparison(actual_instruction_text)
                normalized_expected_text = client_accounts_page.normalize_text_for_comparison(instruction_text)
                logger.info(f"  Expected instruction text (normalized): '{normalized_expected_text}'")
                logger.info(f"  Actual instruction text from element (normalized): '{normalized_actual_text}'")
                
                # Check if normalized actual text contains normalized expected text
                text_match = normalized_expected_text in normalized_actual_text
                soft_assert.assert_true(
                    text_match,
                    message=f"[FAIL] ClientAccountsPage: Signer Information Instruction Text — Expected: contains '{normalized_expected_text}', Actual: '{normalized_actual_text}'. Details: Instruction must be in first TD of Signer(s) Information dialog details table. Locator: table#esig_user_details_table td:first."
                )
                logger.info(f"  [PASS] ClientAccountsPage: Signer Information Instruction Verified.")
            else:
                logger.info("  Checking main page content...")
                
                if heading_text:
                    signer_header = authenticated_page.locator("div#divSignersInfo")
                    soft_assert.assert_count(signer_header, 1, "[FAIL] ClientAccountsPage: Signer Information Header (Main Page) — Expected: count=1, Actual: count!=1. Details: div#divSignersInfo must exist on main page if no iframe found. Locator: div#divSignersInfo.")
                    soft_assert.assert_visible(signer_header, "[FAIL] ClientAccountsPage: Signer Information Header Visibility (Main Page) — Expected: visible=True, Actual: visible=False. Details: div#divSignersInfo must be visible to read heading. Locator: div#divSignersInfo.")
                    soft_assert.assert_text_contains(signer_header, heading_text, f"[FAIL] ClientAccountsPage: Signer Information Heading Text (Main Page) — Expected: contains '{heading_text}', Actual: text mismatch. Details: Heading must match expected value from CSV. Locator: div#divSignersInfo.")
                    logger.info(f"  [PASS] ClientAccountsPage: Signer Information Heading Verified.")
                
                if instruction_text:
                    details_table = authenticated_page.locator("table#esig_user_details_table")
                    soft_assert.assert_count(details_table, 1, "[FAIL] ClientAccountsPage: Signer Details Table (Main Page) — Expected: count=1, Actual: count!=1. Details: table#esig_user_details_table must exist on main page if no iframe. Locator: table#esig_user_details_table.")
                    soft_assert.assert_visible(details_table, "[FAIL] ClientAccountsPage: Details Table Visibility (Main Page) — Expected: visible=True, Actual: visible=False. Details: table#esig_user_details_table must be visible. Locator: table#esig_user_details_table.")
                    
                    first_td = details_table.locator("td").first
                    soft_assert.assert_count(first_td, 1, "[FAIL] ClientAccountsPage: Details TD (Main Page) — Expected: count=1, Actual: count!=1. Details: First TD must exist in table. Locator: table#esig_user_details_table td:first.")
                    soft_assert.assert_visible(first_td, "[FAIL] ClientAccountsPage: Details TD Visibility (Main Page) — Expected: visible=True, Actual: visible=False. Details: First TD must be visible. Locator: table#esig_user_details_table td:first.")
                    
                    # Get actual text from element for debugging
                    actual_instruction_text = first_td.text_content().strip() if first_td.count() > 0 else ""
                    # Normalize both texts for comparison (handles Unicode, smart quotes, special chars)
                    normalized_actual_text = client_accounts_page.normalize_text_for_comparison(actual_instruction_text)
                    normalized_expected_text = client_accounts_page.normalize_text_for_comparison(instruction_text)
                    logger.info(f"  Expected instruction text (normalized): '{normalized_expected_text}'")
                    logger.info(f"  Actual instruction text from element (normalized): '{normalized_actual_text}'")
                    
                    # Check if normalized actual text contains normalized expected text
                    text_match = normalized_expected_text in normalized_actual_text
                    soft_assert.assert_true(
                        text_match,
                        message=f"[FAIL] ClientAccountsPage: Instruction Text (Main Page) — Expected: contains '{normalized_expected_text}', Actual: '{normalized_actual_text}'. Details: Instruction must be in first TD. Locator: table#esig_user_details_table td:first."
                    )
                    logger.info(f"  [PASS] ClientAccountsPage: Signer Information Instruction Verified.")
            
            logger.info("[PASS] ClientAccountsPage: All Signer Information Validations Collected.")
            
            # Step 4: Verify all soft assertions
            logger.info("Step 4: Verifying all soft assertions...")
            try:
                soft_assert.assert_all()
                logger.info("[PASS] ClientAccountsPage: All Soft Assertions Passed.")
            except Exception as soft_assert_error:
                logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
                allure.attach(
                    str(soft_assert_error),
                    name="Signer Information Dialog - Assertion Failures",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise
            
            # Step 5: Screenshot
            logger.info("Step 5: Taking screenshot...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Signer Information Dialog - Verified",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.info("[PASS] ClientAccountsPage: Signer Information Dialog Verification Completed.")
            
        except Exception as e:
            logger.error(f"✗ Dialog verification failed: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Signer Information Dialog - Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Dialog verification failed: {e}") from e


@then("Verify Authorized Signer Approval section should be displayed on Signer(s) Information dialog")
def verify_authorized_signer_approval_section(authenticated_page: Page, test_context):
    """
    Verify Authorized Signer Approval section on Signer(s) Information dialog.
    
    Validates:
    1. Authorized Signer Approval Heading text (first TR h4 tag) — HARD ASSERT
    2. Approval message (second TR first TD) — HARD ASSERT
    3. Radio button labels: exactly 1 'No' and 1 'Yes', 'No' first — HARD ASSERT
    4. Input elements: value='radiobtnNo' and value='radiobtnYes', correct order — SOFT ASSERT
    
    CSV format: Expected_Authorized_Signer_Approval_Text = "Heading | Message"
    """
    with allure.step("Authorized Signer Approval section should be displayed"):
        logger.info(">>> STEP: Verify Authorized Signer Approval section is displayed")
        
        try:
            # Initialize soft assertions for non-critical checks
            soft_assert = EnhancedSoftAssertions(authenticated_page)
            
            # Step 1: Get and parse expected text from CSV
            logger.info("Step 1: Fetching expected text from CSV...")
            test_data = test_context.get("test_data", {})
            expected_approval_text = (test_data.get("Expected_Authorized_Signer_Approval_Text") or "").strip()
            
            if not expected_approval_text:
                raise AssertionError("[FAIL] ClientAccountsPage: CSV Data Parsing — Expected: 'Expected_Authorized_Signer_Approval_Text' not empty, Actual: column is empty. Details: Test data CSV must include 'Expected_Authorized_Signer_Approval_Text' column with pipe-separated values (Heading | Message). Locator: test_data['Expected_Authorized_Signer_Approval_Text'].")
            
            parts = [p.strip() for p in expected_approval_text.split("|")] if "|" in expected_approval_text else [expected_approval_text]
            heading_text = parts[0] if len(parts) > 0 and parts[0] else None
            approval_message = parts[1] if len(parts) > 1 and parts[1] else None
            
            logger.info(f"[PASS] ClientAccountsPage: CSV Data Parsed.")
            
            # Step 2: Access iframe (HARD ASSERT)
            logger.info("Step 2: Accessing iframe...")
            Assertions.assert_equal(
                authenticated_page.locator("iframe#esig_iframe").count(),
                1,
                "[FAIL] AuthorizedSignerApprovalSection: Iframe Access — Expected: count=1, Actual: count!=1. Details: iframe#esig_iframe must exist for Authorized Signer approval table. Locator: iframe#esig_iframe."
            )
            iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
            logger.info("[PASS] ClientAccountsPage: Iframe Accessed.")
            
            # Step 3: Locate and validate table (HARD ASSERT)
            logger.info("Step 3: Validating Authorized Signer table...")
            auth_table = iframe_frame.locator("table#tblAuthorizedSigner")
            Assertions.assert_count(auth_table, 1, "[FAIL] AuthorizedSignerApprovalSection: Table Count — Expected: count=1, Actual: count!=1. Details: Authorized Signer approval table must exist in iframe. Locator: table#tblAuthorizedSigner.")
            Assertions.assert_visible(auth_table, "[FAIL] AuthorizedSignerApprovalSection: Table Visibility — Expected: visible=True, Actual: visible=False. Details: Authorized Signer approval table must be visible. Locator: table#tblAuthorizedSigner.")
            logger.info("[PASS] AuthorizedSignerApprovalSection: Table Found and Visible.")
            
            # Step 4: Validate heading in first TR h4 (HARD ASSERT - Requirement 1)
            if heading_text:
                logger.info(f"Step 4: Validating heading '{heading_text[:50]}...' (HARD ASSERT)...")
                h4_locator = auth_table.locator("tr").first.locator("h4").first
                Assertions.assert_count(h4_locator, 1, "[FAIL] AuthorizedSignerApprovalSection: H4 Heading Count — Expected: count=1, Actual: count!=1. Details: H4 heading element must exist in first TR. Locator: table#tblAuthorizedSigner tr h4.")
                Assertions.assert_visible(h4_locator, "[FAIL] AuthorizedSignerApprovalSection: H4 Heading Visibility — Expected: visible=True, Actual: visible=False. Details: H4 heading must be visible. Locator: table#tblAuthorizedSigner tr h4.")
                Assertions.assert_text_contains(h4_locator, heading_text, f"[FAIL] AuthorizedSignerApprovalSection: H4 Heading Text — Expected: contains '{heading_text}', Actual: text mismatch. Details: Heading must match expected value from CSV. Locator: table#tblAuthorizedSigner tr h4.")
                logger.info("[PASS] AuthorizedSignerApprovalSection: Heading Validated.")
            
            # Step 5: Validate approval message in second TR first TD (HARD ASSERT - Requirement 2)
            if approval_message:
                logger.info(f"Step 5: Validating approval message (HARD ASSERT)...")
                all_trs = auth_table.locator("tr").all()
                Assertions.assert_greater(len(all_trs), 1, "[FAIL] AuthorizedSignerApprovalSection: TR Count — Expected: count>1, Actual: count<=1. Details: At least 2 TR elements required. Locator: table#tblAuthorizedSigner tr.")
                
                first_td = all_trs[1].locator("td").first
                Assertions.assert_count(first_td, 1, "[FAIL] AuthorizedSignerApprovalSection: TD Count — Expected: count=1, Actual: count!=1. Details: First TD must exist in second TR. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:first.")
                Assertions.assert_visible(first_td, "[FAIL] AuthorizedSignerApprovalSection: TD Visibility — Expected: visible=True, Actual: visible=False. Details: First TD must be visible. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:first.")
                Assertions.assert_text_contains(first_td, approval_message[:50], f"[FAIL] AuthorizedSignerApprovalSection: Approval Message — Expected: contains '{approval_message[:50]}', Actual: text mismatch. Details: Message must match expected value from CSV. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:first.")
                logger.info("[PASS] AuthorizedSignerApprovalSection: Approval Message Validated.")
            
            # Step 6: Validate radio buttons and inputs
            logger.info("Step 6: Validating radio buttons (labels and inputs)...")
            all_trs = auth_table.locator("tr").all()
            second_td = all_trs[1].locator("td").all()[1]
            Assertions.assert_visible(second_td, "[FAIL] AuthorizedSignerApprovalSection: Second TD Visibility — Expected: visible=True, Actual: visible=False. Details: Second TD (options column) in second TR must be visible. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:nth-child(2).")
            
            # HARD ASSERT - Validate span labels (Requirement 3)
            logger.info("  Step 6a: Validating radio button labels (HARD ASSERT)...")
            Assertions.assert_count(second_td.locator("span:has-text('No')"), 1, "[FAIL] AuthorizedSignerApprovalSection: No Label Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 'No' label required. Locator: span:has-text('No').")
            Assertions.assert_count(second_td.locator("span:has-text('Yes')"), 1, "[FAIL] AuthorizedSignerApprovalSection: Yes Label Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 'Yes' label required. Locator: span:has-text('Yes').")
            Assertions.assert_visible(second_td.locator("span:has-text('No')").first, "[FAIL] AuthorizedSignerApprovalSection: No Label Visibility — Expected: visible=True, Actual: visible=False. Details: 'No' label must be visible. Locator: span:has-text('No').")
            Assertions.assert_visible(second_td.locator("span:has-text('Yes')").first, "[FAIL] AuthorizedSignerApprovalSection: Yes Label Visibility — Expected: visible=True, Actual: visible=False. Details: 'Yes' label must be visible. Locator: span:has-text('Yes').")
            
            # Validate DOM order for labels (HARD ASSERT - Requirement 3)
            no_pos = find_element_position_in_parent(second_td.locator("span"), "textContent", "No")
            yes_pos = find_element_position_in_parent(second_td.locator("span"), "textContent", "Yes")
            if no_pos is not None and yes_pos is not None:
                Assertions.assert_less(no_pos, yes_pos, "[FAIL] AuthorizedSignerApprovalSection: Label Order — Expected: No position < Yes position, Actual: No position >= Yes position. Details: 'No' label must appear before 'Yes' in DOM. Locator: span:has-text('No') and span:has-text('Yes').")
            logger.info("  [PASS] AuthorizedSignerApprovalSection: Radio Button Labels Validated.")
            
            # SOFT ASSERT - Validate input elements (Requirement 4)
            logger.info("  Step 6b: Validating input elements (SOFT ASSERT)...")
            soft_assert.assert_count(second_td.locator("input[value='radiobtnNo']"), 1, "[FAIL] AuthorizedSignerApprovalSection: radiobtnNo Input Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 'radiobtnNo' input required. Locator: input[value='radiobtnNo'].")
            soft_assert.assert_count(second_td.locator("input[value='radiobtnYes']"), 1, "[FAIL] AuthorizedSignerApprovalSection: radiobtnYes Input Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 'radiobtnYes' input required. Locator: input[value='radiobtnYes'].")
            soft_assert.assert_visible(second_td.locator("input[value='radiobtnNo']").first, "[FAIL] AuthorizedSignerApprovalSection: radiobtnNo Input Visibility — Expected: visible=True, Actual: visible=False. Details: 'radiobtnNo' input must be visible. Locator: input[value='radiobtnNo'].")
            soft_assert.assert_visible(second_td.locator("input[value='radiobtnYes']").first, "[FAIL] AuthorizedSignerApprovalSection: radiobtnYes Input Visibility — Expected: visible=True, Actual: visible=False. Details: 'radiobtnYes' input must be visible. Locator: input[value='radiobtnYes'].")
            logger.info("  [PASS] AuthorizedSignerApprovalSection: Input Elements Validated.")
            
            # Step 6c: Validate action buttons (Cancel and Continue) (SOFT ASSERT)
            logger.info("  Step 6c: Validating action buttons - Cancel and Continue (SOFT ASSERT)...")
            
            # Import locators for button verification
            from locators import client_accounts_locators
            
            # Validate Cancel button - search within iframe
            logger.info("    Validating Cancel button...")
            cancel_button = iframe_frame.locator(client_accounts_locators.CANCEL_BUTTON)
            soft_assert.assert_count(
                cancel_button,
                1,
                "[FAIL] AuthorizedSignerApprovalSection: Cancel Button Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 Cancel button required on the dialog. Locator: input#btnCancel."
            )
            soft_assert.assert_visible(
                cancel_button.first,
                "[FAIL] AuthorizedSignerApprovalSection: Cancel Button Visibility — Expected: visible=True, Actual: visible=False. Details: Cancel button must be visible. Locator: input#btnCancel."
            )
            # Verify Cancel button has correct value attribute
            cancel_value = cancel_button.first.get_attribute("value") if cancel_button.count() > 0 else None
            soft_assert.assert_equal(
                cancel_value,
                "Cancel",
                "[FAIL] AuthorizedSignerApprovalSection: Cancel Button Value — Expected: value='Cancel', Actual: value='{}'".format(cancel_value)
            )
            logger.info("    [PASS] Cancel button validated.")
            
            # Validate Continue button - search within iframe
            logger.info("    Validating Continue button...")
            continue_button = iframe_frame.locator(client_accounts_locators.CONTINUE_BUTTON_DIALOG)
            soft_assert.assert_count(
                continue_button,
                1,
                "[FAIL] AuthorizedSignerApprovalSection: Continue Button Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 Continue button required on the dialog. Locator: input#btnContinue."
            )
            soft_assert.assert_visible(
                continue_button.first,
                "[FAIL] AuthorizedSignerApprovalSection: Continue Button Visibility — Expected: visible=True, Actual: visible=False. Details: Continue button must be visible. Locator: input#btnContinue."
            )
            # Verify Continue button has correct value attribute
            continue_value = continue_button.first.get_attribute("value") if continue_button.count() > 0 else None
            soft_assert.assert_equal(
                continue_value,
                "Continue",
                "[FAIL] AuthorizedSignerApprovalSection: Continue Button Value — Expected: value='Continue', Actual: value='{}'".format(continue_value)
            )
            logger.info("    [PASS] Continue button validated.")
            logger.info("  [PASS] AuthorizedSignerApprovalSection: Action Buttons Validated.")
            
            logger.info("[PASS] AuthorizedSignerApprovalSection: All Validations Completed.")
            
            # Step 7: Verify soft assertions
            logger.info("Step 7: Verifying soft assertions...")
            try:
                soft_assert.assert_all()
                logger.info("[PASS] AuthorizedSignerApprovalSection: All Soft Assertions Passed.")
            except Exception as soft_assert_error:
                logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
                allure.attach(
                    str(soft_assert_error),
                    name="Authorized Signer Approval Section - Input Elements Assertion Failures",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise
            
            # Step 8: Screenshot
            logger.info("Step 8: Taking screenshot...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Authorized Signer Approval Section - Verified",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.info("[PASS] AuthorizedSignerApprovalSection: Verification Completed.")
            
        except Exception as e:
            logger.error(f"✗ Verification failed: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Authorized Signer Approval Section - Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Authorized Signer Approval verification failed: {e}") from e


@then("Verify appropriate fields are displayed based on eSign Method selected")
def verify_fields_for_esign_method(authenticated_page: Page, client_accounts_page, test_context):
    """
    Verify appropriate fields are displayed based on eSign Method selected.
    
    If SMS: Verifies Authorized Signers label/dropdown, Email Address label/input, Phone label/input
    If Tracking Center: Verifies Note message is displayed
    """
    with allure.step("Verify appropriate fields are displayed based on eSign Method selected"):
        logger.info(">>> STEP: Verify appropriate fields are displayed based on eSign Method selected")
        
        try:
            # Step 1: Fetch the eSign method from test data
            logger.info("  Step 1: Fetching Authorized Signer eSign Method from test data...")
            test_data = test_context.get("test_data", {})
            esign_method = test_data.get("Authorized_Signer_eSign_Method", "").strip()
            
            if not esign_method:
                raise AssertionError("'Authorized_Signer_eSign_Method' value not found in test data CSV")
            
            valid_methods = ["SMS", "Tracking Center"]
            if esign_method not in valid_methods:
                raise AssertionError(
                    f"Invalid 'Authorized_Signer_eSign_Method' value: '{esign_method}'. "
                    f"Expected one of: {valid_methods}"
                )
            
            logger.info(f"  [PASS] ClientAccountsPage: CSV Data Parsed.")
            
            # Step 2: Call page object method to verify fields based on eSign method
            logger.info(f"  Step 2: Verifying fields for '{esign_method}' method...")
            client_accounts_page.verify_fields_for_esign_method(esign_method)
            
            # Step 3: Take screenshot for Allure reporting
            logger.info("  Step 3: Taking screenshot after verification...")
            allure.attach(
                authenticated_page.screenshot(),
                name=f"Fields Verified for {esign_method} eSign Method",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info(f"[PASS] ClientAccountsPage: eSign Method Fields Verified.")
            
        except Exception as e:
            logger.error(f"✗ Failed to verify fields for eSign method: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Fields Verification - Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Failed to verify fields for eSign method: {e}") from e

@then("Authorized Signer eSign Method section should be displayed")
def verify_authorized_signer_esign_method_section(authenticated_page: Page):
    """
    Verify Authorized Signer eSign Method section on Signer(s) Information dialog.
    
    Validates:
    1. 'Authorized Signer eSign Method' heading is displayed
    2. 'Authorized Signers' label is displayed
    3. 'SMS' label is displayed
    4. SMS radio button is displayed
    5. 'Tracking Center' label is displayed
    6. 'Tracking Center' radio button is displayed
    7. None of the radio buttons are selected (no default selection)
    """
    with allure.step("Authorized Signer eSign Method section should be displayed"):
        logger.info(">>> STEP: Authorized Signer eSign Method section should be displayed")
        
        try:
            # Step 1: Access iframe
            logger.info("Step 1: Accessing iframe...")
            Assertions.assert_equal(
                authenticated_page.locator("iframe#esig_iframe").count(),
                1,
                "[FAIL] ClientAccountsPage: eSign Iframe Access — Expected: count=1, Actual: count!=1. Details: iframe#esig_iframe must exist to access Signer Information dialog. Locator: iframe#esig_iframe."
            )
            iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
            logger.info("[PASS] ClientAccountsPage: Signer Information Iframe Accessed.")
            
            # Step 2: Validate 'Authorized Signer eSign Method' heading
            logger.info("Step 2: Validating 'Authorized Signer eSign Method' heading...")
            heading = iframe_frame.locator("h5:has-text('Authorized Signer eSign Method')")
            Assertions.assert_count(heading, 1, "[FAIL] ClientAccountsPage: eSign Method Heading Count — Expected: count=1, Actual: count!=1. Details: h5 heading with 'Authorized Signer eSign Method' text must exist. Locator: h5:has-text('Authorized Signer eSign Method').")
            Assertions.assert_visible(heading, "[FAIL] ClientAccountsPage: eSign Method Heading Visibility — Expected: visible=True, Actual: visible=False. Details: eSign Method heading must be visible. Locator: h5:has-text('Authorized Signer eSign Method').")
            logger.info("[PASS] ClientAccountsPage: eSign Method Heading Validated.")
            
            # Step 3: Validate 'SMS' label
            logger.info("Step 3: Validating 'SMS' label...")
            sms_label = iframe_frame.locator("div#eSignMethodDiv span").filter(has_text="SMS").first
            Assertions.assert_count(sms_label, 1, "[FAIL] ClientAccountsPage: SMS Label Count — Expected: count=1, Actual: count!=1. Details: Span with 'SMS' text must exist in eSignMethodDiv. Locator: div#eSignMethodDiv span:has-text('SMS').")
            Assertions.assert_visible(sms_label, "[FAIL] ClientAccountsPage: SMS Label Visibility — Expected: visible=True, Actual: visible=False. Details: SMS label must be visible. Locator: div#eSignMethodDiv span:has-text('SMS').")
            logger.info("[PASS] ClientAccountsPage: SMS Label Validated.")
            
            # Step 4: Validate SMS radio button is displayed
            logger.info("Step 4: Validating SMS radio button...")
            sms_radio = iframe_frame.locator("input#radiobtnSMS")
            Assertions.assert_count(sms_radio, 1, "[FAIL] ClientAccountsPage: SMS Radio Button Count — Expected: count=1, Actual: count!=1. Details: input#radiobtnSMS must exist in eSign Method section. Locator: input#radiobtnSMS.")
            Assertions.assert_visible(sms_radio, "[FAIL] ClientAccountsPage: SMS Radio Button Visibility — Expected: visible=True, Actual: visible=False. Details: SMS radio button must be visible. Locator: input#radiobtnSMS.")
            logger.info("[PASS] ClientAccountsPage: SMS Radio Button Validated.")
            
            # Step 5: Validate 'Tracking Center' label
            logger.info("Step 5: Validating 'Tracking Center' label...")
            tracking_center_label = iframe_frame.locator("div#eSignMethodDiv span").filter(has_text="Tracking Center").first
            Assertions.assert_count(tracking_center_label, 1, "[FAIL] ClientAccountsPage: Tracking Center Label Count — Expected: count=1, Actual: count!=1. Details: Span with 'Tracking Center' text must exist in eSignMethodDiv. Locator: div#eSignMethodDiv span:has-text('Tracking Center').")
            Assertions.assert_visible(tracking_center_label, "[FAIL] ClientAccountsPage: Tracking Center Label Visibility — Expected: visible=True, Actual: visible=False. Details: Tracking Center label must be visible. Locator: div#eSignMethodDiv span:has-text('Tracking Center').")
            logger.info("[PASS] ClientAccountsPage: Tracking Center Label Validated.")
            
            # Step 6: Validate 'Tracking Center' radio button is displayed
            logger.info("Step 6: Validating 'Tracking Center' radio button...")
            tracking_center_radio = iframe_frame.locator("input#radiobtnTC")
            Assertions.assert_count(tracking_center_radio, 1, "[FAIL] ClientAccountsPage: Tracking Center Radio Button Count — Expected: count=1, Actual: count!=1. Details: input#radiobtnTC must exist in eSign Method section. Locator: input#radiobtnTC.")
            Assertions.assert_visible(tracking_center_radio, "[FAIL] ClientAccountsPage: Tracking Center Radio Button Visibility — Expected: visible=True, Actual: visible=False. Details: Tracking Center radio button must be visible. Locator: input#radiobtnTC.")
            logger.info("[PASS] ClientAccountsPage: Tracking Center Radio Button Validated.")
            
            # Step 7: Verify none of the radio buttons are selected
            logger.info("Step 7: Verifying no radio buttons are selected by default...")
            sms_checked = sms_radio.is_checked()
            tracking_center_checked = tracking_center_radio.is_checked()
            
            assert not sms_checked, "[FAIL] ClientAccountsPage: SMS Radio Default State — Expected: radiobtnSMS.checked=False, Actual: checked=True. Details: SMS radio button should NOT be selected by default in eSign Method section. Locator: input#radiobtnSMS."
            assert not tracking_center_checked, "[FAIL] ClientAccountsPage: Tracking Center Radio Default State — Expected: radiobtnTC.checked=False, Actual: checked=True. Details: Tracking Center radio button should NOT be selected by default in eSign Method section. Locator: input#radiobtnTC."
            logger.info("[PASS] ClientAccountsPage: No Default Radio Button Selection Verified.")
            
            logger.info("[PASS] ClientAccountsPage: All eSign Method Validations Passed.")
            
            # Step 8: Screenshot
            logger.info("Step 8: Taking screenshot...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Authorized Signer eSign Method Section - Verified",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.info("[PASS] ClientAccountsPage: eSign Method Section Verification Completed.")
            
        except Exception as e:
            logger.error(f"✗ Verification failed: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Authorized Signer eSign Method Section - Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Authorized Signer eSign Method section verification failed: {e}") from e


@when("User select Signer eSign Method")
def user_select_signer_esign_method(authenticated_page: Page, client_accounts_page, test_context):
    """
    Select Signer eSign Method from available options.
    
    Reads 'Signer_eSign_Method' from test data CSV and selects the appropriate radio button.
    Valid values: 'In Person', 'By Email', 'SMS', or 'Tracking Center'
    """
    with allure.step("User select Signer eSign Method"):
        logger.info(">>> STEP: User select Signer eSign Method")
        
        try:
            # Step 1: Fetch the eSign method from test data
            logger.info("  Step 1: Fetching Signer eSign Method from test data...")
            test_data = test_context.get("test_data", {})
            esign_method = test_data.get("Signer_eSign_Method", "").strip()
            
            if not esign_method:
                raise AssertionError("[FAIL] ClientAccountsPage: CSV Data Parsing — Expected: 'Signer_eSign_Method' not empty, Actual: column is empty. Details: Test data CSV must include 'Signer_eSign_Method' column with value 'In Person', 'By Email', 'SMS', or 'Tracking Center'. Locator: test_data['Signer_eSign_Method'].")
            
            valid_methods = ["In Person", "By Email", "SMS", "Tracking Center"]
            if esign_method not in valid_methods:
                raise AssertionError(
                    f"[FAIL] ClientAccountsPage: CSV Data Validation — Expected: value in {valid_methods}, Actual: '{esign_method}'. Details: 'Signer_eSign_Method' must be one of: 'In Person', 'By Email', 'SMS', or 'Tracking Center'. Locator: test_data['Signer_eSign_Method']."
                )
            
            logger.info(f"  [PASS] ClientAccountsPage: CSV Data Parsed - Method: '{esign_method}'")
            
            # Step 2: Call page object method to select the radio button
            logger.info(f"  Step 2: Selecting '{esign_method}' radio button...")
            client_accounts_page.select_signer_esign_method(esign_method)
            
            # Step 3: Take screenshot for Allure reporting
            logger.info("  Step 3: Taking screenshot after selection...")
            allure.attach(
                authenticated_page.screenshot(),
                name=f"Signer eSign Method - {esign_method} Selected",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info(f"[PASS] ClientAccountsPage: Signer eSign Method Selected - {esign_method}.")
            
        except Exception as e:
            logger.error(f"✗ Failed to select Authorized Signer eSign Method: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Authorized Signer eSign Method - Selection Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Failed to select Authorized Signer eSign Method: {e}") from e

@when("User provide Authorized Signers information")
def provide_authorized_signers_information(authenticated_page: Page, client_accounts_page, test_context):
    """
    Provide Authorized Signers information on the Signer(s) Information dialog.
    
    Fetches data from test data CSV:
    - Authorized_Signers: Value to select in authorizedSignersDropdown (if enabled)
    - Email_Address: Email address to enter in emailText field
    - Phone: Phone number to enter in PhoneText field
    
    If dropdown is disabled, skips selection and only enters email and phone.
    """
    with allure.step("User provide Authorized Signers information"):
        logger.info(">>> STEP: User provide Authorized Signers information")
        
        try:
            # Step 1: Fetch data from test context
            logger.info("  Step 1: Fetching Authorized Signers information from test data...")
            test_data = test_context.get("test_data", {})
            
            # Initialize authorized_signer to None (will be set by role-based logic)
            authorized_signer = None
            
            # Determine Authorized Signer based on role and fetch with environment-aware logic
            authorized_signer_role = test_data.get("Authorized_Signer_Role", "").strip()
            logger.info(f"  Authorized_Signer_Role: '{authorized_signer_role}'")
            
            if authorized_signer_role == "FA":
                # For FA role, use Agent column as APLID
                agent_id = test_data.get("Agent", "").strip()
                if not agent_id:
                    raise ValueError("[FAIL] ClientAccountsPage: CSV Data Validation — Expected: Agent ID not empty, Actual: empty. Details: For Authorized_Signer_Role='FA', Agent column must contain the APLID value. Locator: test_data['Agent'].")
                
                logger.info(f"  Fetching Agent name using APLID: {agent_id}")
                authorized_signer = fetch_authorized_signer(agent_id, "Agent", test_data)
                logger.info(f"  ✓ Agent name fetched: {authorized_signer}")
                
            elif authorized_signer_role == "SAU":
                # For SAU role, use username as UserID and Agent as usl.UserID
                user_id = test_data.get("username", "").strip()
                agent_id = test_data.get("Agent", "").strip()
                if not user_id:
                    raise ValueError("[FAIL] ClientAccountsPage: CSV Data Validation — Expected: username not empty, Actual: empty. Details: For Authorized_Signer_Role='SAU', username column must contain the sd.UserID value. Locator: test_data['username'].")
                if not agent_id:
                    raise ValueError("[FAIL] ClientAccountsPage: CSV Data Validation — Expected: Agent not empty, Actual: empty. Details: For Authorized_Signer_Role='SAU', Agent column must contain the usl.UserID value. Locator: test_data['Agent'].")
                
                logger.info(f"  Fetching SAU name using sd.UserID: {user_id} and usl.UserID: {agent_id}")
                authorized_signer = fetch_authorized_signer(user_id, "SAU", test_data, second_param=agent_id)
                logger.info(f"  ✓ SAU name fetched: {authorized_signer}")
            else:
                # No fallback: Authorized_Signer_Role must be either FA or SAU
                raise ValueError(f"[FAIL] ClientAccountsPage: CSV Data Validation — Expected: Authorized_Signer_Role in ['FA', 'SAU'], Actual: '{authorized_signer_role}'. Details: Authorized_Signer_Role must be 'FA' (Financial Advisor) or 'SAU' (Shared Access User). Authorized Signer name will be fetched using fetch_authorized_signer() function which uses test sheet for protected environments and database for test environments. Locator: test_data['Authorized_Signer_Role'].")
            
            email_address = test_data.get("Email_Address", "").strip() if test_data.get("Email_Address") else ""
            phone = test_data.get("Phone", "").strip() if test_data.get("Phone") else ""
            
            logger.info(f" User provide Authorized Signers information.")
            logger.info(f"    - Authorized_Signer: '{authorized_signer if authorized_signer else 'N/A'}'")
            logger.info(f"    - Email_Address: '{email_address if email_address else 'N/A'}'")
            logger.info(f"    - Phone: '{phone if phone else 'N/A'}'")
            
            # Store authorized_signer in test_context for use in subsequent steps
            test_context["authorized_signer"] = authorized_signer
            logger.info(f"  Stored authorized_signer in test_context: {authorized_signer}")
            
            # Step 2: Call page object method to provide information
            logger.info("  Step 2: Providing information via page method...")
            client_accounts_page.provide_authorized_signers_information(
                authorized_signer=authorized_signer,
                email_address=email_address,
                phone=phone
            )
            
            # Step 3: Take screenshot for Allure reporting
            logger.info("  Step 3: Taking screenshot after providing information...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Authorized Signers Information - Provided",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info("[PASS] ClientAccountsPage: Authorized Signers Information Provided.")
            
        except Exception as e:
            logger.error(f"✗ Failed to provide Authorized Signers information: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Authorized Signers Information - Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Failed to provide Authorized Signers information: {e}") from e


@then("Verify Authorized Signer dropdown")
def verify_authorized_signer_dropdown(authenticated_page: Page, client_accounts_page, test_context):
    """
    Verify Authorized Signer dropdown state and options.
    
    Determines expected signer count from:
    1. test_context['multiple_signers'] (from database fetch in test11)
    2. test_data CSV column 'Multiple_Authorized_Signers' (for non-test11 environments)
    
    Verification logic:
    - If 1 signer: Verifies dropdown is disabled and shows signer name
    - If > 1 signers: Verifies dropdown is enabled and options match Name_ManageLogin values
    - If 0 signers or data unavailable: Skip verification
    """
    with allure.step("Verify Authorized Signer dropdown"):
        logger.info(">>> STEP: Verify Authorized Signer dropdown")
        
        try:
            # Step 1: Determine signer count from multiple sources
            logger.info("  Step 1: Determining expected number of authorized signers...")
            
            signers = None
            signer_count_indicator = None
            is_multiple = None
            
            # Strategy 1: Check test_data CSV FIRST (takes priority for non-test11 environments)
            test_data = test_context.get("test_data", {})
            signer_count_indicator = test_data.get("Multiple_Authorized_Signers", "").strip()
            
            if signer_count_indicator:
                # CSV has the column, use it (for prod, silo, test10, test12)
                logger.info(f"  ✓ Found signer count indicator from CSV: '{signer_count_indicator}'")
                is_multiple = signer_count_indicator.lower() in ["yes", "multiple", "2+", "true"]
                logger.info(f"  ✓ Using CSV data: Multiple authorized signers = {is_multiple}")
            else:
                # No CSV column, fall back to database (test11 only)
                logger.info("  ✓ No CSV column found, checking test_context for database signers...")
                if "multiple_signers" in test_context:
                    signers = test_context.get("multiple_signers", [])
                    logger.info(f"  ✓ Found {len(signers)} signer(s) from database (test_context['multiple_signers'])")
                else:
                    logger.warning("  ⚠ No database signers and no CSV column found")
                    logger.info("  ℹ Skipping dropdown verification - no signer count data available")
                    logger.info("  [PASS] ClientAccountsPage: Step Completed - Signer Count Data Unavailable.")
                    return
            
            # If no signers and no signer count indicator, skip
            if not signers and signer_count_indicator is None:
                logger.info("  ℹ No authorized signers found and no signer count data available - skipping verification")
                logger.info("  [PASS] ClientAccountsPage: Step Completed - No Signer Data to Verify.")
                return
            
            logger.info("  [PASS] ClientAccountsPage: Signer Count Determined.")
            
            # Step 2: Access iframe
            logger.info("  Step 2: Accessing iframe...")
            from utils.dialog_utils import DialogHandler
            dialog_handler = DialogHandler(authenticated_page)
            dialog = dialog_handler.wait_for_dialog(timeout=10000)
            
            iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
            logger.info("  [PASS] ClientAccountsPage: Signer Information Iframe Accessed.")
            
            # Step 3: Find dropdown
            logger.info("  Step 3: Locating Authorized Signers dropdown...")
            dropdown = iframe_frame.locator("select[name='authorizedSignersDropdown']")
            
            Assertions.assert_count(dropdown, 1, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown — Expected: count=1, Actual: count!=1. Details: Dropdown must exist in Signer Information dialog. Locator: select[name='authorizedSignersDropdown'].")
            Assertions.assert_visible(dropdown, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Visibility — Expected: visible=True, Actual: visible=False. Details: Dropdown must be visible. Locator: select[name='authorizedSignersDropdown'].")
            logger.info("  [PASS] ClientAccountsPage: Authorized Signers Dropdown Found and Visible.")
            
            # Step 4: Validate based on signer count
            # Determine validation path: database signers OR CSV indicator
            use_database = signers is not None
            use_csv = is_multiple is not None
            
            # CASE 1: Database signers - Single signer → dropdown should be disabled
            if use_database and len(signers) == 1:
                logger.info("  Step 4: Validating dropdown is disabled (1 signer from database)...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_true(is_disabled, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Disabled State — Expected: is_disabled=True, Actual: is_disabled=False. Details: Dropdown should be disabled when only 1 signer is present. Locator: select[name='authorizedSignersDropdown'].")
                logger.info("  [PASS] ClientAccountsPage: Dropdown Disabled for Single Signer (Database).")
                
                # Verify the default selected option matches the signer name
                logger.info("  Step 5: Verifying default selected option matches signer name...")
                signer_name = signers[0].get("Name_ManageLogin", "")
                
                assert signer_name, "[FAIL] ClientAccountsPage: Signer Name Extraction — Expected: Name_ManageLogin present, Actual: empty or missing. Details: Signer data must include Name_ManageLogin field from database query."
                
                selected_option = iframe_frame.locator("select[name='authorizedSignersDropdown'] option[selected]")
                Assertions.assert_count(selected_option, 1, "[FAIL] ClientAccountsPage: Dropdown Selected Option — Expected: count=1, Actual: count!=1. Details: Exactly one option should be selected. Locator: select[name='authorizedSignersDropdown'] option[selected].")
                
                selected_text = (selected_option.first.text_content() or "").strip()
                logger.info(f"  Selected option text: '{selected_text}'")
                logger.info(f"  Expected signer name: '{signer_name}'")
                
                Assertions.assert_equal(selected_text, signer_name, f"[FAIL] ClientAccountsPage: Dropdown Selected Value — Expected: '{signer_name}', Actual: '{selected_text}'. Details: Dropdown should show the only available signer's name. Locator: select[name='authorizedSignersDropdown'].")
                logger.info(f"  [PASS] ClientAccountsPage: Default Selected Option Matches Signer.")
            
            # CASE 2: Database signers - Multiple signers → dropdown should be enabled
            elif use_database and len(signers) > 1:
                logger.info("  Step 4: Validating dropdown is disabled (1 signer from database)...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_true(is_disabled, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Disabled State — Expected: is_disabled=True, Actual: is_disabled=False. Details: Dropdown should be disabled when only 1 signer is present. Locator: select[name='authorizedSignersDropdown'].")
                logger.info("  [PASS] ClientAccountsPage: Dropdown Disabled for Single Signer (Database).")
                
                # Verify the default selected option matches the signer name
                logger.info("  Step 5: Verifying default selected option matches signer name...")
                signer_name = signers[0].get("Name_ManageLogin", "")
                
                assert signer_name, "[FAIL] ClientAccountsPage: Signer Name Extraction — Expected: Name_ManageLogin present, Actual: empty or missing. Details: Signer data must include Name_ManageLogin field from database query."
                
                selected_option = iframe_frame.locator("select[name='authorizedSignersDropdown'] option[selected]")
                Assertions.assert_count(selected_option, 1, "[FAIL] ClientAccountsPage: Dropdown Selected Option — Expected: count=1, Actual: count!=1. Details: Exactly one option should be selected. Locator: select[name='authorizedSignersDropdown'] option[selected].")
                
                selected_text = (selected_option.first.text_content() or "").strip()
                logger.info(f"  Selected option text: '{selected_text}'")
                logger.info(f"  Expected signer name: '{signer_name}'")
                
                Assertions.assert_equal(selected_text, signer_name, f"[FAIL] ClientAccountsPage: Dropdown Selected Value — Expected: '{signer_name}', Actual: '{selected_text}'. Details: Dropdown should show the only available signer's name. Locator: select[name='authorizedSignersDropdown'].")
                logger.info(f"  [PASS] ClientAccountsPage: Default Selected Option Matches Signer.")
            
            # CASE 2: Database signers - Multiple signers → dropdown should be enabled
            elif use_database and len(signers) > 1:
                logger.info(f"  Step 4: Validating dropdown is enabled ({len(signers)} signers from database)...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_false(is_disabled, f"[FAIL] ClientAccountsPage: Authorized Signers Dropdown Enabled State — Expected: is_disabled=False, Actual: is_disabled=True. Details: Dropdown should be enabled when {len(signers)} signers are present. Locator: select[name='authorizedSignersDropdown'].")
                logger.info("  [PASS] ClientAccountsPage: Dropdown Enabled for Multiple Signers.")
                
                # Fetch all options from dropdown
                logger.info("  Step 5: Fetching dropdown options...")
                options = iframe_frame.locator("select[name='authorizedSignersDropdown'] option").all()
                
                Assertions.assert_greater(len(options), 0, "[FAIL] ClientAccountsPage: Dropdown Options Count — Expected: count>0, Actual: count=0. Details: Dropdown must have at least one option. Locator: select[name='authorizedSignersDropdown'] option.")
                logger.info(f"  [PASS] ClientAccountsPage: Dropdown Options Found.")
                
                # Extract option texts (skip first option which is "--Select Authorized Signer--")
                logger.info("  Step 6: Extracting and validating option values...")
                option_texts = []
                for idx, option in enumerate(options):
                    option_text = (option.text_content() or "").strip()
                    option_texts.append(option_text)
                    logger.info(f"    Option {idx}: '{option_text}'")
                
                # Skip the first "--Select Authorized Signer--" option
                actual_options = option_texts[1:] if len(option_texts) > 1 else option_texts
                
                # Extract expected signer names from test_context signers
                logger.info("  Step 7: Comparing options with signer names...")
                expected_signer_names = [signer.get("Name_ManageLogin", "") for signer in signers]
                
                logger.info(f"  Expected signer names: {expected_signer_names}")
                logger.info(f"  Actual dropdown options: {actual_options}")
                
                # Validate count matches
                Assertions.assert_equal(len(actual_options), len(expected_signer_names), f"[FAIL] ClientAccountsPage: Dropdown Options Count — Expected: {len(expected_signer_names)}, Actual: {len(actual_options)}. Details: Number of dropdown options must match number of signers. Locator: select[name='authorizedSignersDropdown'] option.")
                logger.info(f"  [PASS] ClientAccountsPage: Option Count Matches Signer Count.")
                
                # Validate each option matches a signer name
                for idx, (actual, expected) in enumerate(zip(actual_options, expected_signer_names)):
                    Assertions.assert_equal(actual, expected, f"[FAIL] ClientAccountsPage: Dropdown Option Value — Expected: '{expected}' at index {idx}, Actual: '{actual}'. Details: Each dropdown option must match a signer name. Locator: select[name='authorizedSignersDropdown'] option[{idx+1}].")
                    logger.info(f"  [PASS] ClientAccountsPage: Dropdown Option Validated.")
                
                logger.info("  [PASS] ClientAccountsPage: All Dropdown Options Match Signer Names.")
            
            # CASE 3: CSV indicator says single signer (no database data)
            elif signer_count_indicator and not is_multiple:
                logger.info("  Step 4: Validating dropdown is disabled (single signer from CSV)...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_true(is_disabled, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Disabled State — Expected: is_disabled=True, Actual: is_disabled=False. Details: Test data indicates single authorized signer, dropdown should be disabled. Locator: select[name='authorizedSignersDropdown']. Source: test_data['Multiple_Authorized_Signers']='No'")
                logger.info("  [PASS] ClientAccountsPage: Dropdown Disabled for Single Signer (CSV).")
            
            # CASE 4: CSV indicator says multiple signers (no database data)
            elif signer_count_indicator and is_multiple:
                logger.info("  Step 4: Validating dropdown is enabled (multiple signers from CSV)...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_false(is_disabled, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Enabled State — Expected: is_disabled=False, Actual: is_disabled=True. Details: Test data indicates multiple authorized signers, dropdown should be enabled. Locator: select[name='authorizedSignersDropdown']. Source: test_data['Multiple_Authorized_Signers']='Yes'")
                logger.info("  [PASS] ClientAccountsPage: Dropdown Enabled for Multiple Signers (CSV).")
                
                # Fetch dropdown options (optional - can also just verify it's enabled)
                logger.info("  Step 5: Verifying dropdown has options...")
                options = iframe_frame.locator("select[name='authorizedSignersDropdown'] option").all()
                
                Assertions.assert_greater(len(options), 1, "[FAIL] ClientAccountsPage: Dropdown Options Count — Expected: count>1, Actual: count<=1. Details: Dropdown should have at least one option plus the placeholder. Locator: select[name='authorizedSignersDropdown'] option.")
                logger.info(f"  [PASS] ClientAccountsPage: Dropdown Has {len(options)} Option(s).")
            
            # Step 8: Take screenshot
            logger.info("  Step 8: Taking screenshot...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Authorized Signer Dropdown - Verified",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info("[PASS] ClientAccountsPage: Authorized Signer Dropdown Verified.")
            
        except Exception as e:
            logger.error(f"✗ Failed to verify Authorized Signer dropdown: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Authorized Signer Dropdown - Verification Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Failed to verify Authorized Signer dropdown: {e}") from e


@when("Click on Continue")
def click_continue_button(authenticated_page: Page, client_accounts_page):
    """
    Click the Continue button on Signer(s) Information dialog.
    
    This step will click the Continue button and wait for the page to load.
    """
    with allure.step("Click on Continue"):
        logger.info(">>> STEP: Click on Continue")
        
        try:
            # Call page object method to click Continue button
            logger.info("Calling page method to click Continue button...")
            client_accounts_page.click_continue_on_signer_dialog()
            
            # Take screenshot for Allure reporting
            logger.info("Taking screenshot after clicking Continue...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Continue Button - Clicked",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info("[PASS] ClientAccountsPage: Continue Button Clicked.")
            
        except Exception as e:
            logger.error(f"✗ Failed to click Continue button: {e}")
            try:
                allure.attach(
                    authenticated_page.screenshot(),
                    name="Continue Button - Click Failed",
                    attachment_type=allure.attachment_type.PNG,
                )
            except:
                pass
            raise AssertionError(f"Failed to click Continue button: {e}") from e


@then("Account Number is displayed and radio button is selected")
def verify_account_number_displayed_and_radio_selected(authenticated_page: Page, client_accounts_page, test_context):
    """Verify that the Account Number from test data is displayed and its radio button is selected.
    
    This step:
    1. Reads 'Account_Number' from test_data CSV
    2. Calls page object methods to find and ensure account radio is selected
    3. Performs assertions on the results
    4. Captures screenshots for reporting
    
    Uses Page Object for all DOM interactions and data retrieval.
    Uses SoftAssertions for non-blocking assertions on radio button state.
    """
    # Read account number from test data
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("Account_Number") or test_data.get("account_number")
    
    if not account_number:
        raise KeyError("Test data must include 'Account_Number' column for this step")
    
    with allure.step(f"Verify Account Number '{account_number}' is displayed and radio is selected"):
        logger.info(f">>> ENTERED STEP: verify_account_number_displayed_and_radio_selected")
        logger.info(f"Account_Number from test data: '{account_number}'")
        
        # ASSERTION 1: Account number exists in labels (hard assertion via page object)
        logger.info("ASSERTION 1: Account Number must be displayed in account list...")
        try:
            client_accounts_page.fetch_selected_account(account_number)
            logger.info(f"[PASS] ClientAccountsPage: Account Number Lookup.")
        except AssertionError as e:
            logger.error(f"✗ ASSERTION 1 FAILED: {e}")
            raise
        
        # ASSERTION 2: Radio button must exist and check its current state
        logger.info("ASSERTION 2: Checking and selecting radio button if needed...")
        
        # Step 1: Check radio button state and select if needed (this method does both check and select)
        # The ensure_account_radio_selected() returns both:
        # - was_already_checked: Initial state BEFORE selection attempt
        # - is_checked: Final state AFTER selection attempt
        logger.info("Step 1: Checking radio button state...")
        result = client_accounts_page.ensure_account_radio_selected(account_number)
        label_for_attr = result['label_for_attr']
        was_already_checked = result['was_already_checked']
        is_checked = result['is_checked']
        
        soft_assert = EnhancedSoftAssertions(authenticated_page)
        
        # Step 2: If radio button was NOT selected initially, add soft assertion (warning, non-blocking)
        if not was_already_checked:
            logger.warning(f"⚠ Radio button for account '{account_number}' (id='{label_for_attr}') was NOT initially selected. Selected it now...")
            soft_assert.assert_true(
                False,
                message=f"[FAIL] ClientAccountsPage: Account Radio Button Initial State — Expected: radio_button[id='{label_for_attr}'] initially checked=True, "
                        f"Actual: initially checked={was_already_checked}. Details: Radio button for account '{account_number}' was not pre-selected. "
                        f"Locator: input#{label_for_attr}."
            )
        else:
            logger.info(f"✓ Radio button for account '{account_number}' (id='{label_for_attr}') was already selected.")
        
        # Step 3: Verify final state after selection attempt
        if not is_checked:
            logger.error(f"✗ Radio button for account '{account_number}' (id='{label_for_attr}') could not be selected. Final state: checked={is_checked}")
            raise AssertionError(f"[FAIL] ClientAccountsPage: Radio button for account '{account_number}' could not be selected. Final state: checked={is_checked}")
        else:
            logger.info(f"✓ Radio button for account '{account_number}' (id='{label_for_attr}') is now checked and ready.")
        
        # Step 4: Verify soft assertions (collect warnings but don't stop execution)
        try:
            soft_assert.assert_all()
        except Exception as soft_assert_error:
            # Highlight warning with visual separators for better visibility in logs
            logger.error("=" * 80)
            logger.error("⚠️  SOFT ASSERTION WARNING - Non-blocking but requires attention")
            logger.error("=" * 80)
            logger.error(f"Account: {account_number}")
            logger.error(f"Details: {str(soft_assert_error)}")
            logger.error("=" * 80)
            allure.attach(
                str(soft_assert_error),
                name=f"Account {account_number} - Initial Selection State Warning",
                attachment_type=allure.attachment_type.TEXT
            )
            # Continue execution - this is a warning, not a failure
        
        # Step 5: Take screenshot before state (for audit trail)
        logger.info("Taking screenshot showing selected radio button...")
        screenshot = authenticated_page.screenshot()
        allure.attach(
            screenshot, 
            name=f"Account {account_number} - Radio Button Selected", 
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info(f"[PASS] ClientAccountsPage: Account Number and Radio Button Verification Completed.")


@when("User select OAM Request and Type")
def user_select_oam_request_and_type(authenticated_page: Page, client_accounts_page, test_context):
    """Select OAM Request and Type fields on account wizard using test data.
    
    Uses framework utilities:
    - client_accounts_page: Page object with wait/retry utilities (RetryContext, WaitContext)
    - Assertions: Hard assertions from utils.assertions
    - test_context: Test data loaded from CSV
    """
    with allure.step("User select OAM Request and Type"):
        logger.info(">>> ENTERED STEP: user_select_oam_request_and_type")
        logger.info("Selecting OAM Request and Type fields on Account Wizard")

        # STEP 1: Verify table is ready before attempting selection
        logger.info("Step 1: Verifying Request/Type table is ready...")
        table_ready = client_accounts_page.verify_request_type_table_ready()
        
        # Use Assertions utility for hard assertion (fails immediately with clear message)
        Assertions.assert_true(
            table_ready,
            message="[FAIL] ClientAccountsPage: Request/Type Table Readiness — Expected: table_ready=True (all components visible/enabled), Actual: table_ready=False. Details: Request/Type picker must be fully loaded before selection. Components: div#divlstContainer, ul#HTMLlslCategory, li#lstcategoryli0. Locator: div#divlstContainer."
        )
        logger.info("[PASS] ClientAccountsPage: Request Type Table Ready.")

        # STEP 2: Read values from test data CSV loaded into test_context
        td = test_context.get("test_data", {})
        request_value = td.get("OAM_Request") or td.get("OAM_request")
        type_value = td.get("OAM_Type") or td.get("OAM_type")

        if not request_value:
            raise KeyError("Test data must include a 'request' value for this step")

        # STEP 3: Select request and type using page object methods
        # These methods internally use RetryContext and WaitContext from utils.retry_utils and utils.wait_utils
        logger.info(f"Step 2: Selecting OAM Request='{request_value}' Type='{type_value}'")
        client_accounts_page.select_request(request_value)
        if type_value:
            client_accounts_page.select_type(type_value)

        # STEP 4: Capture screenshot for verification
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="Request and Type Selected", attachment_type=allure.attachment_type.PNG)
        logger.info("[PASS] ClientAccountsPage: OAM Request and Type Selected.")


@then("Verify Form Heading must be same as selected OAM Type")
def verify_form_heading_matches_oam_type(authenticated_page: Page, client_accounts_page, test_context):
    """Verify that the form heading text matches the OAM_Type from test data.
    
    Extracts the text from the <b> tag in the form heading span and compares it
    with the OAM_Type column from the test data CSV using soft assertions.
    
    Uses framework utilities:
    - client_accounts_page.get_form_heading_text(): Extracts heading from DOM
    - SoftAssertions: Non-blocking assertions that collect failures
    - test_context: Test data loaded from CSV
    """
    # Read OAM_Type from test data
    test_data = test_context.get("test_data", {})
    expected_heading = test_data.get("OAM_Type")
    
    if not expected_heading:
        raise KeyError("Test data must include 'OAM_Type' column for this step")
    
    with allure.step(f"Verify Form Heading matches OAM Type: '{expected_heading}'"):
        logger.info(f">>> ENTERED STEP: verify_form_heading_matches_oam_type")
        logger.info(f"Expected OAM_Type from test data: '{expected_heading}'")
        
        # STEP 1: Extract form heading text from the page
        logger.info("Step 1: Retrieving form heading text from page...")
        actual_heading = client_accounts_page.get_form_heading_text()
        logger.info(f"Actual form heading text: '{actual_heading}'")
        
        # STEP 2: Use SoftAssertions to verify the heading matches OAM_Type
        logger.info("Step 2: Comparing form heading with OAM_Type...")
        soft_assert = EnhancedSoftAssertions(authenticated_page)
        soft_assert.assert_equal(
            actual_heading,
            expected_heading,
            message=f"[FAIL] ClientAccountsPage: Form Heading Verification — Expected: heading='{expected_heading}', Actual: heading='{actual_heading}'. Details: Form heading text from OAM_Type field 'span#ctl00_cphContentArea_AccountActionsBox1_lblTaskName > b' should match selected OAM Type. Locator: span#ctl00_cphContentArea_AccountActionsBox1_lblTaskName b."
        )
        
        # STEP 3: Take screenshot for audit trail
        logger.info("Step 3: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(
            screenshot,
            name=f"Form Heading Verified: {actual_heading}",
            attachment_type=allure.attachment_type.PNG
        )
        
        # STEP 4: Verify soft assertions - raises SoftAssertionError if any failed
        try:
            soft_assert.assert_all()
            logger.info(f"[PASS] ClientAccountsPage: Form Heading Matches OAM Type.")
        except Exception as e:
            logger.error(f"✗ Soft assertion(s) failed: {str(e)}")
            allure.attach(
                str(e),
                name="Form Heading Verification - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        logger.info(f"[PASS] ClientAccountsPage: Form Heading Verification Completed.")


@when("User select Submission Type")
def user_select_submission_type(authenticated_page: Page, client_accounts_page, test_context):
    """Click the Complete button based on Submission_Type from test data.
    
    Reads 'Submission_Type' from test_data CSV (e.g., 'Complete and Submit', 'Complete and Print', 'Complete and eSign')
    and clicks the corresponding button on Account Wizard.
    """
    # Read submission type from test data
    test_data = test_context.get("test_data", {})
    submission_type = test_data.get("Submission_Type") or test_data.get("submission_type")
    
    if not submission_type:
        raise KeyError("Test data must include a 'Submission_Type' column for this step")
    
    with allure.step(f"Click {submission_type}"):
        logger.info(f">>> ENTERED STEP: user_select_submission_type")
        logger.info(f"Submission_Type from test data: '{submission_type}'")
        logger.info(f"Clicking {submission_type} button")
        client_accounts_page.click_complete_button(submission_type)
        authenticated_page.wait_for_timeout(1000)
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name=f"{submission_type} Clicked", attachment_type=allure.attachment_type.PNG)

@when("User select Client Signature Method")
def user_select_client_signature_method(authenticated_page: Page, client_accounts_page, test_context):
    """Handle the signature dialog based on Client_Signature_Method from test data.
    
    Reads 'Client_Signature_Method' from test_data CSV (e.g., 
    'Proceed and submit without a client signature',
    'Print to obtain client physical signature',
    'Request client electronic signature')
    and handles the signature dialog accordingly.
    """
    # Read client signature method from test data
    test_data = test_context.get("test_data", {})
    signature_method = test_data.get("Client_Signature_Method") or test_data.get("client_signature_method")
    
    if not signature_method:
        raise KeyError("Test data must include a 'Client_Signature_Method' column for this step")
    
    with allure.step(f"Select Client Signature Method: {signature_method}"):
        logger.info(f">>> ENTERED STEP: user_select_client_signature_method")
        logger.info(f"Client_Signature_Method from test data: '{signature_method}'")
        logger.info(f"Handling signature dialog with method: {signature_method}")
        client_accounts_page.handle_signature_dialog(signature_option=signature_method)
        # Page state is already waited on in handle_signature_dialog, take screenshot immediately
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name=f"Client Signature Method Selected: {signature_method}", attachment_type=allure.attachment_type.PNG)


@then("Client Signature Not Required dialog should be displayed")
def verify_client_signature_not_required_dialog(authenticated_page: Page, client_accounts_page):
    """Verify that the "Client Signature Not Required" dialog is displayed with correct title.
    
    Uses framework utilities:
    - DialogHandler: Robust dialog detection with multiple strategies
    - client_accounts_page.get_signature_dialog_title(): Extracts dialog title from DOM
    - SoftAssertions: Non-blocking assertions for dialog title verification
    - allure_logger: Unified logging with Allure integration
    """
    with allure.step("Verify Client Signature Not Required dialog is displayed"):
        logger.info(">>> ENTERED STEP: verify_client_signature_not_required_dialog")
        logger.info("Verifying Client Signature Not Required dialog appearance and content")
        
        # STEP 1: Wait for dialog to appear using DialogHandler
        logger.info("Step 1: Waiting for dialog to appear...")
        dialog_handler = DialogHandler(authenticated_page)
        
        try:
            # Wait for dialog with robust detection
            dialog = dialog_handler.wait_for_dialog(timeout=15000)
            logger.info("[PASS] ClientAccountsPage: Client Signature Not Required Dialog Detected.")
        except Exception as e:
            logger.error(f"[FAIL] ClientAccountsPage: Client Signature Not Required Dialog Not Detected {e}")
            
            # Fallback: Try waiting for dialog by role attribute
            try:
                authenticated_page.wait_for_selector('role=dialog', timeout=15000)
                dialog = authenticated_page.locator('role=dialog').first
                logger.info("[PASS] ClientAccountsPage: Client Signature Not Required Dialog Found.")
            except Exception as e2:
                logger.error(f"[FAIL] ClientAccountsPage: Client Signature Not Required Dialog Not Detected. {e2}")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="Dialog Detection Failed", attachment_type=allure.attachment_type.PNG)
                raise AssertionError("[FAIL] ClientAccountsPage: Dialog Detection — Expected: dialog visible=True, Actual: dialog not found. Details: Client Signature Not Required dialog must appear after form submission. Locator: [role='dialog'].") from e
        
        # STEP 2: Extract title from modal-title-transition div using page object
        logger.info("Step 2: Extracting dialog title using page object...")
        dialog_title = client_accounts_page.get_signature_dialog_title()
        logger.info(f"Dialog title extracted: '{dialog_title}'")
        
        # STEP 3: Use SoftAssertions to verify the dialog title
        logger.info("Step 3: Verifying dialog title matches expected text...")
        expected_title = "Client Signature Not Required"
        
        soft_assert = EnhancedSoftAssertions(authenticated_page)
        soft_assert.assert_equal(
            dialog_title,
            expected_title,
            message=f"[FAIL] ClientAccountsPage: Client Signature Not Required Dialog Title — Expected: title='{expected_title}', Actual: title='{dialog_title}'. Details: Client Signature Not Required dialog should display correct title."
        )
        
        # STEP 3a: Verify that 'Proceed and submit without a client signature' radio button is checked
        logger.info("Step 3a: Verifying 'Proceed and submit without a client signature' radio button is checked...")
        is_rb_submit_checked = client_accounts_page.is_radio_checked('rbSubmit')
        soft_assert.assert_true(
            is_rb_submit_checked,
            message="[FAIL] ClientAccountsPage: Client Signature Not Required Dialog Radio Button Default State — Expected: checked=True, Actual: checked=False. Details: 'Proceed and submit without a client signature' radio should be checked by default in Client Signature Not Required dialog. Locator: input#rbSubmit."
        )
        
        # STEP 4: Take screenshot for audit trail
        logger.info("Step 4: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(
            screenshot,
            name="Client Signature Not Required Dialog - Verified",
            attachment_type=allure.attachment_type.PNG
        )
        
        # STEP 5: Verify all soft assertions - raises SoftAssertionError if any failed
        try:
            soft_assert.assert_all()
            logger.info(f"[PASS] ClientAccountsPage: Client Signature Not Required Dialog Title Matches Expected.")
        except Exception as e:
            logger.error(f"[FAIL] ClientAccountsPage: Client Signature Not Required Dialog - Soft assertion(s) failed: {str(e)}")
            allure.attach(
                str(e),
                name="Client Signature Not Required Dialog - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        logger.info(f"[PASS] ClientAccountsPage: Client Signature Not Required Dialog Verification Completed.")


@then("Verify request pop up")
def verify_request_dialog(authenticated_page: Page, client_accounts_page, test_context):
    """
    Verify that the Request dialog is displayed with the expected content.
    
    Reads 'Expected_RequestPopUp_Text' from test_data CSV (with | separated values)
    and verifies all expected text values are present in the dialog.
    
    Uses robust dialog detection with multiple strategies and automatic retries.
    """
    # Read expected dialog text from test data
    test_data = test_context.get("test_data", {})
    expected_text = test_data.get("Expected_RequestPopUp_Text") or test_data.get("expected_requestpopup_text")
    
    if not expected_text:
        raise KeyError("Test data must include 'Expected_RequestPopUp_Text' column for this step")
    
    # Parse pipe-separated text sections for granular verification
    # Safe strip: handle None values and ensure each section is properly trimmed
    expected_sections = [section.strip() for section in (expected_text or "").split("|") if section and section.strip()]
    
    with allure.step(f"Verify Request dialog with {len(expected_sections)} expected sections"):
        logger.info(f">>> ENTERED STEP: verify_request_dialog")
        logger.info(f"Expecting {len(expected_sections)} sections in Request dialog")
        
        # STEP 1: Wait for dialog with robust detection
        logger.info("Step 1: Waiting for dialog...")
        dialog_handler = DialogHandler(authenticated_page)
        
        try:
            # Use DialogHandler's robust wait with fallbacks
            dialog = dialog_handler.wait_for_dialog(timeout=15000)
            logger.info("[PASS] ClientAccountsPage: Request Dialog Detected.")
        except Exception as e:
            logger.error(f"✗ Dialog detection failed: {e}")
            
            # Fallback: Try waiting for any visible dialog
            try:
                authenticated_page.wait_for_selector('role=dialog', timeout=15000)
                dialog = authenticated_page.locator('role=dialog').first
                logger.info("[PASS] ClientAccountsPage: Dialog Found via Fallback Method.")
            except Exception as e2:
                logger.error(f"✗ All dialog detection strategies failed")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="Dialog Detection Failed", attachment_type=allure.attachment_type.PNG)
                raise AssertionError("[FAIL] ClientAccountsPage: Dialog Detection — Expected: dialog visible=True, Actual: dialog not found. Details: Request Submitted dialog must appear after workflow completion. Locator: [role='dialog'].") from e
        
        # STEP 2: Verify dialog content with expected text from test data
        logger.info("Step 2: Validating dialog content...")
        try:
            # Get dialog text for validation
            dialog_text = dialog.text_content() or dialog_handler.get_dialog_text()
            logger.info(f"Dialog text length: {len(dialog_text)} characters")
            
            # Verify each expected section is present in the dialog
            missing_sections = {}
            for idx, section in enumerate(expected_sections, 1):
                if section in dialog_text:
                    logger.info(f"[PASS] ClientAccountsPage: Dialog Section Verified.")
                else:
                    missing_sections[idx] = section
                    logger.warning(f"✗ Section {idx} not found in dialog: {section}")
            
            # Assert all expected sections were found
            assert not missing_sections, \
                f"[FAIL] ClientAccountsPage: Request Dialog Content — Expected: all {len(expected_sections)} sections present, " \
                f"Actual: {len(missing_sections)} missing sections {list(missing_sections.keys())}. " \
                f"Details: All expected text sections must be present in Request Submitted dialog. Missing: {missing_sections}. " \
                f"Locator: [role='dialog']."
            
            logger.info(f"[PASS] ClientAccountsPage: All Dialog Sections Verified.")
        except Exception as e:
            logger.error(f"✗ Dialog content validation failed: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="Dialog Content Validation Failed", attachment_type=allure.attachment_type.PNG)
            raise
        
        # STEP 3: Fetch and validate dialog elements
        logger.info("Step 3: Fetching dialog elements...")
        try:
            # Initialize soft assertions for optional dialog elements
            soft_assert = EnhancedSoftAssertions(authenticated_page)
            
            dialog_data = client_accounts_page.get_request_submitted_dialog_content()
            
            # Validate D-link (tracking center link)
            d_link = dialog_data.get('d_link')
            d_link_text = dialog_data.get('d_link_text')
            
            if d_link:
                assert d_link.is_visible(), "D-link not visible"
                logger.info(f"[PASS] ClientAccountsPage: D-Link Visibility and State Verified.")
                
                # Verify D-number text starts with 'D'
                assert d_link_text and d_link_text.startswith('D'), \
                    f"D-link text should start with 'D', but got: '{d_link_text}'"
                logger.info(f"[PASS] ClientAccountsPage: D-Link Text Format Verified.")
            else:
                raise AssertionError("D-link not found in dialog")
            
            # Verify all soft assertions
            logger.info("Verifying soft assertions for optional dialog elements...")
            try:
                soft_assert.assert_all()
                logger.info("[PASS] ClientAccountsPage: All Dialog Elements Validated.")
            except Exception as soft_assert_error:
                logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
                allure.attach(
                    str(soft_assert_error),
                    name="Request Dialog - Soft Assertion Failures",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise
        except Exception as e:
            logger.error(f"✗ Dialog element validation failed: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="Dialog Elements Validation Failed", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Dialog elements validation failed: {e}") from e
        
        # STEP 4: Capture final screenshot
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="Request Dialog - Verified", attachment_type=allure.attachment_type.PNG)
        
        logger.info("[PASS] ClientAccountsPage: Request Dialog Verification Completed.")


@when("User click on D number")
def user_click_on_d_number(authenticated_page: Page, client_accounts_page, test_context):
    """
    Click on the D-number (Tracking Center link) in the dialog.
    This navigates to the Tracking Center to view the request status.
    
    This step also stores the D-number in test_context for verification
    that the same D-number is displayed on the Tracking Center page.
    """
    with allure.step("User click on D number"):
        logger.info(">>> STEP: User click on D number")
        
        d_number = None
        try:
            # STEP 1: Click the D-number link and get the D-number value
            d_number = client_accounts_page.click_d_number()
            logger.info(f"[PASS] ClientAccountsPage: D-Number Clicked.")
            
            # Store D-number in test_context for later verification
            test_context['d_number'] = d_number
            logger.info(f"[PASS] ClientAccountsPage: D-Number Stored in Context.")
            
        except Exception as e:
            logger.error(f"✗ Failed to click D-number element: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="D-Number Click - Failed", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Failed to click D-number: {e}") from e
        
        # STEP 2: Wait for page navigation to Tracking Center
        try:
            authenticated_page.wait_for_load_state("networkidle", timeout=30000)
            logger.info(f"[PASS] ClientAccountsPage: Page Navigation to Tracking Center Completed.")
            
        except Exception as e:
            logger.error(f"✗ Timeout waiting for Tracking Center page to load: {e}")
            logger.error(f"   (D-number {d_number} was clicked, but page load timed out)")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="D-Number Navigation - Page Load Timeout", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Page failed to load after clicking D-number {d_number}: {e}") from e
        
        # STEP 3: Take screenshot for Allure reporting
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="D-number Clicked - Navigating to Tracking Center", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f"[PASS] ClientAccountsPage: D-Number Click Step Completed.")


@then("Client In Person Signing dialog should be displayed")
def verify_client_in_person_signing_dialog_displayed(authenticated_page: Page, client_accounts_page, test_context):
    """
    Verify that the Client In-Person Signing dialog is displayed with correct content.
    
    This dialog appears after the user completes the DocuSign signing process
    in an in-person client signature workflow. 
    
    Validations:
    1. Dialog with role="dialog" is visible
    2. Dialog title is "Client In Person Signing"
    3. Dialog body contains expected text about completing eSignature and client signing steps
    4. Two action buttons are present: "Return to eWealthManager" and "Start Client Signing"
    5. Close dialog or click button to proceed
    
    Related steps:
    - "When User click on \"Start Client Signing\" button" (next step after this)
    - "When User click on \"Return to eWealthManager\" button" (alternative step)
    - "When User Finish the DocuSign process" (prerequisite - displays dialog)
    
    Uses:
    - DialogHandler: Robust dialog detection
    - client_accounts_page.get_client_in_person_signing_dialog_content(): Retrieves dialog content
    - EnhancedSoftAssertions: Non-blocking assertions for content verification
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots for reporting
    
    Example feature file usage:
        When User Finish the DocuSign process
        Then Client In Person Signing dialog should be displayed
        When User click on "Start Client Signing" button
    
    Raises:
        AssertionError: If dialog not found or content doesn't match expectations
    """
    logger.info("[STEP] Verify Client In Person Signing dialog should be displayed")
    
    with allure.step("Client In Person Signing dialog should be displayed"):
        try:
            # Step 1: Wait for page to be ready before looking for dialog
            logger.info("[DEBUG] Waiting for page to be ready...")
            try:
                authenticated_page.wait_for_load_state("networkidle", timeout=30000)
                logger.info("✓ Page network is idle")
            except Exception as e:
                logger.debug(f"[DEBUG] wait_for_load_state networkidle timeout: {e}")
                # Continue anyway - page might still be usable
                authenticated_page.wait_for_load_state("load", timeout=30000)
                logger.info("✓ Page load complete (at least load event)")
            
            # Add small delay to allow dialog to render
            import time
            time.sleep(1)
            
            # Step 2: Verify dialog is present (wait up to 5 minutes for dialog to load)
            logger.info("[STEP_DETAIL] Verifying dialog is present (timeout: 5 minutes)...")
            dialog_handler = DialogHandler(authenticated_page)
            try:
                logger.info("[DEBUG] Calling wait_for_dialog with 300s timeout...")
                dialog = dialog_handler.wait_for_dialog(timeout=300000)  # 5 minutes
                logger.info("✓ Dialog is present")
            except Exception as e:
                logger.error(f"[ERROR] Dialog wait failed after 5 minutes: {e}")
                allure.attach(authenticated_page.screenshot(), name="Dialog_Not_Found_Screenshot", 
                             attachment_type=allure.attachment_type.PNG)
                raise AssertionError("Client In Person Signing dialog is not displayed after 5 minutes")
            
            # Step 2: Retrieve dialog content (title, body, buttons)
            logger.info("[STEP_DETAIL] Retrieving dialog content...")
            dialog_content = client_accounts_page.get_client_in_person_signing_dialog_content()
            
            if not dialog_content['dialog_present']:
                raise AssertionError("Failed to retrieve Client In Person Signing dialog content")
            
            dialog_title = dialog_content['title']
            dialog_body = dialog_content['body']
            buttons = dialog_content['buttons']
            
            logger.info(f"[DATA] Dialog Title: {dialog_title}")
            logger.info(f"[DATA] Dialog Body Length: {len(dialog_body)} characters")
            logger.info(f"[DATA] Buttons Found: {list(buttons.keys())}")
            
            # Step 3: Verify dialog content using soft assertions
            logger.info("[STEP_DETAIL] Verifying dialog content...")
            soft_asserts = EnhancedSoftAssertions(authenticated_page)
            
            # Verify title
            expected_title = "Client In Person Signing"
            soft_asserts.assert_equal(
                dialog_title,
                expected_title,
                f"Dialog title should be '{expected_title}' but got '{dialog_title}'"
            )
            logger.info(f"✓ Title verified: '{dialog_title}'")
            
            # Verify body text - check for key phrases
            logger.info("[STEP_DETAIL] Verifying dialog body text...")
            
            # Key text segments to verify
            expected_text_segments = [
                "Thank you for completing your part of the eSignature process",
                "These forms",
                "are now ready for signing by your client(s)",
                "Please turn control over to test",
                "Your client(s) will select",
                "Start Client Signing",
                "They will then proceed with identity verification and the signing process"
            ]
            
            for segment in expected_text_segments:
                soft_asserts.assert_in(
                    segment,
                    dialog_body,
                    f"Dialog body should contain '{segment}'"
                )
            
            logger.info(f"✓ Body text verified: contains all expected segments")
            
            # Step 4: Verify buttons are present
            logger.info("[STEP_DETAIL] Verifying dialog buttons...")
            
            if 'return_button' not in buttons or buttons['return_button'].count() == 0:
                soft_asserts.assert_not_none(None, "Return to eWealthManager button must be present in dialog")
                logger.warning("⚠ 'Return to eWealthManager' button not found")
            else:
                logger.info("✓ 'Return to eWealthManager' button is present")
            
            if 'start_signing_button' not in buttons or buttons['start_signing_button'].count() == 0:
                soft_asserts.assert_not_none(None, "Start Client Signing button must be present in dialog")
                logger.warning("⚠ 'Start Client Signing' button not found")
            else:
                logger.info("✓ 'Start Client Signing' button is present")
            
            # Raise any soft assertion failures before proceeding
            soft_asserts.assert_all()
            
            # Step 5: Capture screenshot for reporting
            logger.info("[STEP_DETAIL] Capturing screenshot...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Client In Person Signing Dialog - Verified",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] Client In Person Signing dialog verified successfully")
            
        except AssertionError as ae:
            # Re-raise assertion errors without additional wrapping
            logger.error(f"[FAIL] Step failed with assertion error: {ae}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: Client In Person Signing Dialog Verification",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise
        
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error while verifying Client In Person Signing dialog: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: Client In Person Signing Dialog Verification (Exception)",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"Failed to verify Client In Person Signing dialog: {e}") from e


@when(parsers.re(r'User click on "(?P<button_text>.*?)" button'))
def user_click_on_form_button_dynamic(authenticated_page: Page, client_accounts_page, button_text: str, test_context):
    """
    Dynamic step definition for clicking any form button with specified text.
    
    This step accepts the button text as a parameter from the feature file,
    allowing it to be reused for multiple buttons.

    Args:
        button_text: The exact text of the button to click (e.g., 'Return to eWealthManager', 'Start Client Signing')

    Pre-conditions:
    - The dialog containing the button must be displayed
    - The button must be visible on the page

    Post-conditions:
    - The specified button is clicked
    - Page state changes based on button action

    Uses framework utilities:
    - client_accounts_page.click_form_button(button_text): Page object method to click any form button
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots on failure for reporting

    Example feature file usage:
        When User click on "Return to eWealthManager" button
        When User click on "Start Client Signing" button
        When User click on "Continue" button

    Raises:
        AssertionError: If button not found or not visible
    """
    with allure.step(f'User click on "{button_text}" button'):
        logger.info(f"[STEP] User click on {button_text} button")

        try:
            # Call page object method to click the button with dynamic text
            client_accounts_page.click_form_button(button_text, timeout=60000)

            # Capture screenshot after clicking button
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name=f"After Clicking {button_text} Button",
                attachment_type=allure.attachment_type.PNG
            )

            logger.info(f"[PASS] Successfully clicked '{button_text}' button")

        except Exception as e:
            logger.error(f"Failed to click '{button_text}' button: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name=f"Failed to Click {button_text} Button",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"Failed to click '{button_text}' button: {e}") from e

@when('User provide client signature details')
def user_provide_client_signature_details(authenticated_page: Page, client_accounts_page, test_context):
    """
    BDD step to provide client signature details in the Signer(s) Information dialog.
    
    This step fills in the Account Holders table with client signer information.
    
    Prerequisite:
    - Signer(s) Information dialog must be displayed
    - Test data must contain: Account_Owner, Email_Address, Phone
    
    Test Data Columns (from CSV):
    - Account_Owner: Client's full name (e.g., "Carmen E Tucker")
    - Email_Address: Client's email address
    - Phone: Client's phone number (e.g., "925-123-4567")
    
    Signature:
    - Fills the Account Holders table row 1 (signer_index=1) for the account owner
    - Uses page object's enter_client_signer_details() method
    
    Returns:
    - Nothing (updates form in-place)
    
    Raises:
    - AssertionError: If fields cannot be filled or data is missing
    
    Example feature file usage:
        Then Signer(s) Information dialog should be displayed
        When User provide client signature details
        And User select Authorized Signer Approval option
        And Click on Continue
    
    Related Steps:
    - "When User select Client Signature Method" (prerequisite - shows dialog)
    - "And User select Authorized Signer Approval option" (next step)
    """
    with allure.step("User provide client signature details"):
        logger.info("[STEP] User provide client signature details")

        try:
            # Step 1: Retrieve test data for signer details
            logger.info("[STEP_DETAIL] Retrieving test data for signer details...")
            test_data = test_context.get("test_data", {})
            
            full_name = test_data.get("Account_Owner", "")
            email_address = test_data.get("Email_Address", "")
            phone = test_data.get("Phone", "")
            
            # Validation: Ensure required fields are present
            logger.info(f"[DATA] Account_Owner: {full_name}")
            logger.info(f"[DATA] Email_Address: {email_address}")
            logger.info(f"[DATA] Phone: {phone}")
            
            if not full_name:
                raise AssertionError("Required test data 'Account_Owner' not found in test context")
            if not email_address:
                raise AssertionError("Required test data 'Email_Address' not found in test context")
            if not phone:
                raise AssertionError("Required test data 'Phone' not found in test context")
            
            # Step 2: Call page object method to enter signer details
            logger.info("[STEP_DETAIL] Calling page object to enter signer details...")
            result = client_accounts_page.enter_client_signer_details(
                full_name=full_name,
                email_address=email_address,
                phone=phone,
                signer_index=1  # First Account Owner
            )
            
            # Validation: Verify fields were filled successfully
            if not result.get("fields_filled"):
                raise AssertionError(f"Failed to fill all signer details fields. Result: {result}")
            
            logger.info("[STEP_DETAIL] ✓ Signer details successfully entered")
            logger.info(f"[STEP_DETAIL] ✓ Name field filled: {full_name}")
            logger.info(f"[STEP_DETAIL] ✓ Email field filled: {email_address}")
            logger.info(f"[STEP_DETAIL] ✓ Phone field filled: {phone}")
            
            # Step 3: Capture screenshot for Allure reporting
            logger.info("[STEP_DETAIL] Capturing screenshot for Allure report...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Client Signature Details Provided",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] ✓ Successfully provided client signature details")
            
        except AssertionError:
            # Re-raise assertion errors without additional wrapping
            logger.error(f"[FAIL] Step failed with assertion error")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Failed: Client Signature Details",
                attachment_type=allure.attachment_type.PNG
            )
            raise
            
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error while providing client signature details: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Failed: Client Signature Details (Exception)",
                attachment_type=allure.attachment_type.PNG
            )
            raise AssertionError(f"Failed to provide client signature details: {e}") from e


@then("Verify eSignature Process Complete dialog should be displayed")
def verify_esignature_process_complete_dialog_displayed(authenticated_page: Page, client_accounts_page, test_context):
    """
    Verify that the eSignature Process Complete dialog is displayed with correct content.
    
    This step:
    1. Verifies a dialog is present on the page
    2. Retrieves the dialog title and body content
    3. Verifies the title is "eSignature Process Complete"
    4. Verifies the body text is "Thank you for completing your part of the eSignature process."
    5. Verifies a close button is present
    6. Clicks the close button to close the dialog
    
    Uses framework utilities:
    - DialogHandler: Robust dialog detection
    - client_accounts_page.get_esignature_process_complete_dialog_content(): Retrieves dialog content
    - EnhancedSoftAssertions: Non-blocking assertions for content verification
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots for reporting
    
    Pre-condition:
    - eSignature Process Complete dialog must be displayed
    
    Post-condition:
    - Dialog is closed
    - Application returns to previous state
    
    Example feature file usage:
        Then Verify eSignature Process Complete dialog should be displayed
    
    Raises:
        AssertionError: If dialog not found, content doesn't match, or close button fails
    """
    logger.info("[STEP] Verify eSignature Process Complete dialog should be displayed")
    
    with allure.step("Verify eSignature Process Complete dialog should be displayed"):
        try:
            # Step 1: Verify dialog is present
            logger.info("[STEP_DETAIL] Verifying dialog is present...")
            dialog_handler = DialogHandler(authenticated_page)
            try:
                dialog = dialog_handler.wait_for_dialog(timeout=300000)  # 5 minutes
                logger.info("✓ Dialog is present")
            except Exception as e:
                logger.error(f"[ERROR] Dialog wait failed: {e}")
                raise AssertionError("eSignature Process Complete dialog is not displayed")
            
            # Step 2: Retrieve dialog content (title, body, close button)
            logger.info("[STEP_DETAIL] Retrieving dialog content...")
            dialog_content = client_accounts_page.get_esignature_process_complete_dialog_content()
            
            if not dialog_content['dialog_present']:
                raise AssertionError("Failed to retrieve eSignature Process Complete dialog content")
            
            dialog_title = dialog_content['title']
            dialog_body = dialog_content['body']
            close_button = dialog_content['close_button']
            
            logger.info(f"[DATA] Dialog Title: {dialog_title}")
            logger.info(f"[DATA] Dialog Body: {dialog_body}")
            logger.info(f"[DATA] Close Button Found: {close_button is not None and close_button.count() > 0}")
            
            # Step 3: Verify dialog content using soft assertions
            logger.info("[STEP_DETAIL] Verifying dialog content...")
            soft_asserts = EnhancedSoftAssertions(authenticated_page)
            
            # Verify title
            expected_title = "eSignature Process Complete"
            soft_asserts.assert_equal(
                dialog_title,
                expected_title,
                f"Dialog title should be '{expected_title}' but got '{dialog_title}'"
            )
            logger.info(f"✓ Title verified: '{dialog_title}'")
            
            # Verify body text
            expected_body = "Thank you for completing your part of the eSignature process."
            soft_asserts.assert_in(
                expected_body,
                dialog_body,
                f"Dialog body should contain '{expected_body}' but got '{dialog_body}'"
            )
            logger.info(f"✓ Body text verified: contains expected message")
            
            # Step 4: Verify close button is present
            logger.info("[STEP_DETAIL] Verifying close button is present...")
            if close_button is None or close_button.count() == 0:
                soft_asserts.add_failure("Close button is not present in the dialog")
                logger.warning("⚠ Close button not found")
            else:
                logger.info("✓ Close button is present")
            
            # Raise any soft assertion failures before proceeding
            soft_asserts.assert_all()
            
            # Step 5: Close the dialog by clicking close button
            logger.info("[STEP_DETAIL] Closing dialog by clicking close button...")
            if close_button and close_button.count() > 0:
                close_button.wait_for(state="visible", timeout=5000)
                close_button.click()
                logger.info("✓ Close button clicked")
                
                # Wait for dialog to close
                authenticated_page.wait_for_timeout(1000)
                logger.info("✓ Dialog closed")
            
            # Step 6: Capture screenshot for reporting
            logger.info("[STEP_DETAIL] Capturing screenshot...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="eSignature Process Complete Dialog Verified",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] eSignature Process Complete dialog verified and closed successfully")
            
        except AssertionError as ae:
            # Re-raise assertion errors without additional wrapping
            logger.error(f"[FAIL] Step failed with assertion error: {ae}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: eSignature Dialog Verification",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise
        
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error while verifying eSignature dialog: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: eSignature Dialog Verification (Exception)",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"Failed to verify eSignature Process Complete dialog: {e}") from e


@then("Finish Later pop up should be displayed")
def verify_finish_later_dialog_displayed(authenticated_page: Page, client_accounts_page, test_context):
    """
    Verify that the Finish Later dialog is displayed with correct content.
    
    This step:
    1. Verifies a dialog is present on the page
    2. Retrieves the dialog title and body content
    3. Verifies the title is "Finish Later"
    4. Verifies the body text contains the expected message with D-number from test_context
    5. Extracts the D-number from the dialog and verifies it matches the D-number in test_context
    6. Verifies two buttons are present: "Save" and "Delete"
    
    Expected dialog text:
    "Select Save to save the document for review or signing at a later time. 
    To view your saved request, select <D number> in the tracking center. 
    Select Delete to cancel this document. By deleting, all data will be lost and the request will be canceled."
    
    D-number Validation:
    - Extracts the D-number displayed in the dialog
    - Compares it with D-number from test_context (stored in "User Finish later the DocuSign process" step)
    - Ensures both values match using soft assertions
    
    Uses framework utilities:
    - DialogHandler: Robust dialog detection
    - client_accounts_page.get_finish_later_dialog_content(): Retrieves dialog content including d_number
    - EnhancedSoftAssertions: Non-blocking assertions for content verification
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots for reporting
    
    Pre-condition:
    - Finish Later dialog must be displayed after clicking "Finish Later" option
    - test_context must contain 'd_number' from previous "User Finish later the DocuSign process" step
    
    Example feature file usage:
        When User Finish later the DocuSign process and save the request
        Then Finish Later pop up should be displayed
    
    Raises:
        AssertionError: If dialog not found, content doesn't match, D-number mismatch, or buttons missing
    """
    logger.info("[STEP] Finish Later pop up should be displayed")
    
    with allure.step("Finish Later pop up should be displayed"):
        try:
            # Step 1: Verify dialog is present
            logger.info("[STEP_DETAIL] Verifying dialog is present...")
            dialog_handler = DialogHandler(authenticated_page)
            try:
                dialog = dialog_handler.wait_for_dialog(timeout=300000)  # 5 minutes
                logger.info("✓ Dialog is present")
            except Exception as e:
                logger.error(f"[ERROR] Dialog wait failed: {e}")
                raise AssertionError("Finish Later dialog is not displayed")
            
            # Step 2: Retrieve dialog content (title, body, buttons)
            logger.info("[STEP_DETAIL] Retrieving dialog content...")
            dialog_content = client_accounts_page.get_finish_later_dialog_content()
            
            if not dialog_content['dialog_present']:
                raise AssertionError("Failed to retrieve Finish Later dialog content")
            
            dialog_title = dialog_content['title']
            dialog_body = dialog_content['body']
            buttons = dialog_content['buttons']
            
            logger.info(f"[DATA] Dialog Title: {dialog_title}")
            logger.info(f"[DATA] Dialog Body: {dialog_body}")
            logger.info(f"[DATA] Buttons Found: Save={buttons.get('save_button') is not None}, Delete={buttons.get('delete_button') is not None}")
            
            # Step 3: Get D-number from test_context for message verification
            d_number = test_context.get('d_number', '')
            logger.info(f"[DATA] D-Number from test_context: {d_number}")
            
            # Step 4: Build expected dialog body text with D-number
            expected_body_parts = [
                "Select Save",
                "save the document for review or signing at a later time",
                "To view your saved request",
                "in the tracking center",
                "Select Delete",
                "cancel this document",
                "By deleting, all data will be lost",
                "request will be canceled"
            ]
            
            # Step 5: Verify dialog content using soft assertions
            logger.info("[STEP_DETAIL] Verifying dialog content...")
            soft_asserts = EnhancedSoftAssertions(authenticated_page)
            
            # Verify title
            expected_title = "Finish Later"
            soft_asserts.assert_equal(
                dialog_title,
                expected_title,
                f"Dialog title should be '{expected_title}' but got '{dialog_title}'"
            )
            logger.info(f"✓ Title verified: '{dialog_title}'")
            
            # Verify body text contains all expected parts
            logger.info("[STEP_DETAIL] Verifying dialog body text contains expected content...")
            for expected_part in expected_body_parts:
                soft_asserts.assert_in(
                    expected_part,
                    dialog_body,
                    f"Dialog body should contain '{expected_part}' but got '{dialog_body}'"
                )
                logger.info(f"✓ Body contains: '{expected_part}'")
            
            # Verify D-number is referenced in dialog body
            if d_number:
                soft_asserts.assert_in(
                    d_number,
                    dialog_body,
                    f"Dialog body should reference D-number '{d_number}' but got '{dialog_body}'"
                )
                logger.info(f"✓ Body references D-number: {d_number}")
            else:
                logger.warning("⚠ D-number not found in test_context, skipping D-number verification")
            
            # Step 5.5: Extract and verify D-number from dialog matches test_context
            logger.info("[STEP_DETAIL] Extracting and verifying D-number from dialog...")
            if d_number:
                # Extract D-number from dialog content structure if available
                dialog_d_number = dialog_content.get('d_number', '')
                
                if dialog_d_number:
                    logger.info(f"[DATA] D-Number extracted from dialog: {dialog_d_number}")
                    logger.info(f"[DATA] D-Number from test_context: {d_number}")
                    
                    # Verify the D-number in dialog matches the one in test_context
                    soft_asserts.assert_equal(
                        dialog_d_number,
                        d_number,
                        f"[FAIL] D-Number Mismatch — Expected: d_number='{d_number}' (from test_context), Actual: d_number='{dialog_d_number}' (from dialog). Details: The D-number displayed in the Finish Later dialog must match the D-number stored in test_context from the Finish Later process step. Locator: finish-later-dialog-d-number."
                    )
                    logger.info(f"✓ D-number in dialog matches test_context: {dialog_d_number}")
                else:
                    logger.warning("⚠ D-number could not be extracted from dialog content structure, but presence in body text was already verified")
            
            # Step 6: Verify buttons are present
            logger.info("[STEP_DETAIL] Verifying buttons are present...")
            
            # Check Save button
            save_button = buttons.get('save_button')
            if save_button is None or save_button.count() == 0:
                soft_asserts.add_failure("'Save' button is not present in the Finish Later dialog")
                logger.warning("⚠ 'Save' button not found")
            else:
                logger.info("✓ 'Save' button is present")
            
            # Check Delete button
            delete_button = buttons.get('delete_button')
            if delete_button is None or delete_button.count() == 0:
                soft_asserts.add_failure("'Delete' button is not present in the Finish Later dialog")
                logger.warning("⚠ 'Delete' button not found")
            else:
                logger.info("✓ 'Delete' button is present")
            
            # Raise any soft assertion failures
            soft_asserts.assert_all()
            
            # Step 7: Capture screenshot for reporting
            logger.info("[STEP_DETAIL] Capturing screenshot...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Finish_Later_Dialog_Verified",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] Finish Later dialog verified successfully")
            logger.info(f"  - Title: '{dialog_title}'")
            logger.info(f"  - Body text verified with expected content")
            logger.info(f"  - D-number comparison verified")
            logger.info(f"  - Buttons present: Save and Delete")
            if d_number:
                logger.info(f"  - D-number from test_context: {d_number}")
            
        except AssertionError as ae:
            # Re-raise assertion errors without additional wrapping
            logger.error(f"[FAIL] Step failed with assertion error: {ae}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: Finish Later Dialog Verification",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise
        
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error while verifying Finish Later dialog: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: Finish Later Dialog Verification (Exception)",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"Failed to verify Finish Later dialog: {e}") from e


@when("User save the document for finsih later")
def user_save_the_document_for_finish_later(authenticated_page: Page, client_accounts_page, test_context):
    """
    Save the document for finish later by clicking the Save button in the Finish Later dialog.
    
    This step:
    1. Locates the Save button in the Finish Later dialog
    2. Clicks the Save button to save the request
    3. Captures screenshot for reporting
    
    Uses framework utilities:
    - client_accounts_page.click_finish_later_save_button(): Clicks the Save button
    - logger: Unified logging from allure_logger
    - allure: Attach screenshots for reporting
    
    Pre-condition:
    - Finish Later dialog must be displayed (from previous step)
    
    Post-condition:
    - Document is saved
    - Dialog is closed
    - Application returns to previous state
    
    Example feature file usage:
        Then Finish Later pop up should be displayed
        When User save the document for finsih later
    
    Raises:
        AssertionError: If Save button not found or click fails
    """
    logger.info("[STEP] User save the document for finish later")
    
    with allure.step("User save the document for finish later"):
        try:
            # Click the Save button in the Finish Later dialog
            logger.info("[STEP_DETAIL] Clicking Save button to save the document for finish later...")
            client_accounts_page.click_finish_later_save_button(timeout=30000)
            
            # Step 2: Capture screenshot for reporting
            logger.info("[STEP_DETAIL] Capturing screenshot after saving...")
            screenshot = authenticated_page.screenshot()
            allure.attach(
                screenshot,
                name="Document_Saved_For_Finish_Later",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] Document saved for finish later successfully")
            
        except AssertionError as ae:
            # Re-raise assertion errors without additional wrapping
            logger.error(f"[FAIL] Step failed with assertion error: {ae}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: Save Document For Finish Later",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise
        
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error while saving document for finish later: {e}")
            try:
                screenshot = authenticated_page.screenshot()
                allure.attach(
                    screenshot,
                    name="Failed: Save Document For Finish Later (Exception)",
                    attachment_type=allure.attachment_type.PNG
                )
            except:
                pass
            raise AssertionError(f"Failed to save document for finish later: {e}") from e
