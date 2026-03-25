"""
Client Accounts Step Definitions

Step definitions for client account related interactions in BDD tests.
"""

import allure
from playwright.sync_api import Page
from pytest_bdd import given, when, then, parsers

from pages.client_accounts_page import ClientAccountsPage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions, SoftAssertions
from utils.dialog_utils import DialogHandler
from utils.helpers import find_element_position_in_parent
from utils.wait_utils import WaitContext

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
                raise AssertionError("'Authorized_Signer_Approval_Option' value not found in test data CSV")
            
            valid_options = ["Yes", "No"]
            if option not in valid_options:
                raise AssertionError(
                    f"Invalid 'Authorized_Signer_Approval_Option' value: '{option}'. "
                    f"Expected one of: {valid_options}"
                )
            
            logger.info(f"  ✓ Option fetched from test data: '{option}'")
            
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
            
            logger.info(f"✓ Successfully completed: User selected Authorized Signer Approval option: '{option}'")
            
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
    authenticated_page: Page, test_context
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
            soft_assert = SoftAssertions()
            
            # Step 1: Wait for and detect dialog
            logger.info("Step 1: Waiting for Signer Information dialog...")
            dialog_handler = DialogHandler(authenticated_page)
            dialog = dialog_handler.wait_for_dialog(timeout=15000)
            Assertions.assert_visible(dialog, "[FAIL] ClientAccountsPage: Dialog Detection — Expected: visible=True, Actual: visible=False. Details: Signer(s) Information dialog must be visible after being detected. Locator: [role='dialog'].")
            logger.info("✓ Dialog detected and visible")
            
            # Step 2: Get and parse expected text from CSV
            logger.info("Step 2: Fetching expected text from CSV...")
            test_data = test_context.get("test_data", {})
            expected_signer_text = (test_data.get("Expected_Signer_Information_Text") or "").strip()
            
            if not expected_signer_text:
                raise AssertionError("[FAIL] ClientAccountsPage: CSV Data Validation — Expected: Expected_Signer_Information_Text not empty, Actual: column is empty. Details: Test data CSV must include Expected_Signer_Information_Text column with pipe-separated sections. Locator: test_data['Expected_Signer_Information_Text'].")
            
            parts = [p.strip() for p in expected_signer_text.split("|")] if "|" in expected_signer_text else [expected_signer_text]
            heading_text = parts[0] if len(parts) > 0 and parts[0] else None
            instruction_text = parts[1] if len(parts) > 1 and parts[1] else None
            
            logger.info(f"✓ CSV data parsed: heading='{(heading_text or '')[:50]}...' instruction='{(instruction_text or '')[:50]}...'")
            
            # Step 3: Try iframe first, fallback to main page
            logger.info("Step 3: Validating content...")
            iframe_count = authenticated_page.locator("iframe#esig_iframe").count()
            
            if iframe_count > 0:
                logger.info("  Checking iframe content...")
                iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
                
                if heading_text:
                    signer_header = iframe_frame.locator("div#divSignersInfo")
            soft_assert.assert_count(
                signer_header,
                1,
                "[FAIL] ClientAccountsPage: Signer Information Header — Expected: div#divSignersInfo count=1, Actual: count not 1. Details: Signer(s) Information dialog header must be visible in iframe esig_iframe. Locator: iframe#esig_iframe > div#divSignersInfo."
            )
            soft_assert.assert_visible(
                signer_header,
                "[FAIL] ClientAccountsPage: Signer Information Header Visibility — Expected: visible=True, Actual: visible=False. Details: div#divSignersInfo must be visible to read heading. Locator: div#divSignersInfo."
            )
            
            if heading_text:
                soft_assert.assert_text_contains(signer_header, heading_text, f"[FAIL] ClientAccountsPage: Heading Text — Expected: contains '{heading_text}', Actual: text mismatch. Details: Signer Information heading must match expected value. Locator: div#divSignersInfo.")
                logger.info(f"  ✓ Heading validated in iframe")
            
            if instruction_text:
                details_table = iframe_frame.locator("table#esig_user_details_table")
                soft_assert.assert_count(
                    details_table,
                    1,
                    "[FAIL] ClientAccountsPage: Signer Details Table — Expected: table#esig_user_details_table count=1, Actual: count not 1. Details: Details table must exist in iframe. Locator: iframe#esig_iframe > table#esig_user_details_table."
                )
                soft_assert.assert_visible(details_table, message="[FAIL] ClientAccountsPage: Details Table Visibility — Expected: visible=True, Actual: visible=False. Details: table#esig_user_details_table must be visible. Locator: table#esig_user_details_table.")
                
                first_td = details_table.locator("td").first
                soft_assert.assert_count(first_td, 1, message="[FAIL] ClientAccountsPage: Details TD — Expected: td count=1, Actual: count!=1. Details: First TD must exist in table. Locator: table#esig_user_details_table td.")
                soft_assert.assert_visible(first_td, message="[FAIL] ClientAccountsPage: Details TD Visibility — Expected: visible=True, Actual: visible=False. Details: First TD must be visible. Locator: table#esig_user_details_table td:first.")
                soft_assert.assert_text_contains(first_td, instruction_text[:50], message=f"[FAIL] ClientAccountsPage: Instruction Text — Expected: contains '{instruction_text[:50]}', Actual: text mismatch. Details: Instruction must be in first TD. Locator: table#esig_user_details_table td:first.")
                logger.info(f"  ✓ Instruction validated in iframe")
            else:
                logger.info("  Checking main page content...")
                
                if heading_text:
                    signer_header = authenticated_page.locator("div#divSignersInfo")
                    soft_assert.assert_count(signer_header, 1, "[FAIL] ClientAccountsPage: Signer Information Header (Main Page) — Expected: count=1, Actual: count!=1. Details: div#divSignersInfo must exist on main page if no iframe found. Locator: div#divSignersInfo.")
                    soft_assert.assert_visible(signer_header, "[FAIL] ClientAccountsPage: Signer Information Header Visibility (Main Page) — Expected: visible=True, Actual: visible=False. Details: div#divSignersInfo must be visible to read heading. Locator: div#divSignersInfo.")
                    soft_assert.assert_text_contains(signer_header, heading_text, f"[FAIL] ClientAccountsPage: Heading Text (Main Page) — Expected: contains '{heading_text}', Actual: text mismatch. Details: Heading must match expected value from CSV. Locator: div#divSignersInfo.")
                    logger.info(f"  ✓ Heading validated")
                
                if instruction_text:
                    details_table = authenticated_page.locator("table#esig_user_details_table")
                    soft_assert.assert_count(details_table, 1, "[FAIL] ClientAccountsPage: Signer Details Table (Main Page) — Expected: count=1, Actual: count!=1. Details: table#esig_user_details_table must exist on main page if no iframe. Locator: table#esig_user_details_table.")
                    soft_assert.assert_visible(details_table, "[FAIL] ClientAccountsPage: Details Table Visibility (Main Page) — Expected: visible=True, Actual: visible=False. Details: table#esig_user_details_table must be visible. Locator: table#esig_user_details_table.")
                    
                    first_td = details_table.locator("td").first
                    soft_assert.assert_count(first_td, 1, "[FAIL] ClientAccountsPage: Details TD (Main Page) — Expected: count=1, Actual: count!=1. Details: First TD must exist in table. Locator: table#esig_user_details_table td:first.")
                    soft_assert.assert_visible(first_td, "[FAIL] ClientAccountsPage: Details TD Visibility (Main Page) — Expected: visible=True, Actual: visible=False. Details: First TD must be visible. Locator: table#esig_user_details_table td:first.")
                    soft_assert.assert_text_contains(first_td, instruction_text[:50], "[FAIL] ClientAccountsPage: Instruction Text (Main Page) — Expected: contains '{instruction_text[:50]}', Actual: text mismatch. Details: Instruction must be in first TD. Locator: table#esig_user_details_table td:first.")
                    logger.info(f"  ✓ Instruction validated")
            
            logger.info("✓ All validations collected")
            
            # Step 4: Verify all soft assertions
            logger.info("Step 4: Verifying all soft assertions...")
            try:
                soft_assert.assert_all()
                logger.info("✓ All soft assertions passed")
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
            logger.info("✓ Dialog verification completed successfully")
            
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
            soft_assert = SoftAssertions()
            
            # Step 1: Get and parse expected text from CSV
            logger.info("Step 1: Fetching expected text from CSV...")
            test_data = test_context.get("test_data", {})
            expected_approval_text = (test_data.get("Expected_Authorized_Signer_Approval_Text") or "").strip()
            
            if not expected_approval_text:
                raise AssertionError("Expected_Authorized_Signer_Approval_Text column is empty")
            
            parts = [p.strip() for p in expected_approval_text.split("|")] if "|" in expected_approval_text else [expected_approval_text]
            heading_text = parts[0] if len(parts) > 0 and parts[0] else None
            approval_message = parts[1] if len(parts) > 1 and parts[1] else None
            
            logger.info(f"✓ CSV data parsed: heading='{(heading_text or '')[:50]}...' message='{(approval_message or '')[:50]}...'")
            
            # Step 2: Access iframe (HARD ASSERT)
            logger.info("Step 2: Accessing iframe...")
            Assertions.assert_equal(
                authenticated_page.locator("iframe#esig_iframe").count(),
                1,
                "Iframe not found"
            )
            iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
            logger.info("✓ Iframe accessed")
            
            # Step 3: Locate and validate table (HARD ASSERT)
            logger.info("Step 3: Validating Authorized Signer table...")
            auth_table = iframe_frame.locator("table#tblAuthorizedSigner")
            Assertions.assert_count(auth_table, 1, "[FAIL] AuthorizedSignerApprovalSection: Table Count — Expected: count=1, Actual: count!=1. Details: Authorized Signer approval table must exist in iframe. Locator: table#tblAuthorizedSigner.")
            Assertions.assert_visible(auth_table, "[FAIL] AuthorizedSignerApprovalSection: Table Visibility — Expected: visible=True, Actual: visible=False. Details: Authorized Signer approval table must be visible. Locator: table#tblAuthorizedSigner.")
            logger.info("✓ Table found and visible")
            
            # Step 4: Validate heading in first TR h4 (HARD ASSERT - Requirement 1)
            if heading_text:
                logger.info(f"Step 4: Validating heading '{heading_text[:50]}...' (HARD ASSERT)...")
                h4_locator = auth_table.locator("tr").first.locator("h4").first
                Assertions.assert_count(h4_locator, 1, "[FAIL] AuthorizedSignerApprovalSection: H4 Heading Count — Expected: count=1, Actual: count!=1. Details: H4 heading element must exist in first TR. Locator: table#tblAuthorizedSigner tr h4.")
                Assertions.assert_visible(h4_locator, "[FAIL] AuthorizedSignerApprovalSection: H4 Heading Visibility — Expected: visible=True, Actual: visible=False. Details: H4 heading must be visible. Locator: table#tblAuthorizedSigner tr h4.")
                Assertions.assert_text_contains(h4_locator, heading_text, f"[FAIL] AuthorizedSignerApprovalSection: H4 Heading Text — Expected: contains '{heading_text}', Actual: text mismatch. Details: Heading must match expected value from CSV. Locator: table#tblAuthorizedSigner tr h4.")
                logger.info("✓ Heading validated (HARD ASSERT PASSED)")
            
            # Step 5: Validate approval message in second TR first TD (HARD ASSERT - Requirement 2)
            if approval_message:
                logger.info(f"Step 5: Validating approval message (HARD ASSERT)...")
                all_trs = auth_table.locator("tr").all()
                Assertions.assert_greater(len(all_trs), 1, "[FAIL] AuthorizedSignerApprovalSection: TR Count — Expected: count>1, Actual: count<=1. Details: At least 2 TR elements required. Locator: table#tblAuthorizedSigner tr.")
                
                first_td = all_trs[1].locator("td").first
                Assertions.assert_count(first_td, 1, "[FAIL] AuthorizedSignerApprovalSection: TD Count — Expected: count=1, Actual: count!=1. Details: First TD must exist in second TR. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:first.")
                Assertions.assert_visible(first_td, "[FAIL] AuthorizedSignerApprovalSection: TD Visibility — Expected: visible=True, Actual: visible=False. Details: First TD must be visible. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:first.")
                Assertions.assert_text_contains(first_td, approval_message[:50], f"[FAIL] AuthorizedSignerApprovalSection: Approval Message — Expected: contains '{approval_message[:50]}', Actual: text mismatch. Details: Message must match expected value from CSV. Locator: table#tblAuthorizedSigner tr:nth-child(2) td:first.")
                logger.info("✓ Message validated (HARD ASSERT PASSED)")
            
            # Step 6: Validate radio buttons and inputs
            logger.info("Step 6: Validating radio buttons (labels and inputs)...")
            all_trs = auth_table.locator("tr").all()
            second_td = all_trs[1].locator("td").all()[1]
            Assertions.assert_visible(second_td, "Second TD not visible")
            
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
            logger.info("  ✓ Radio button labels validated (1 No, 1 Yes, both visible, correct order) — HARD ASSERT PASSED")
            
            # SOFT ASSERT - Validate input elements (Requirement 4)
            logger.info("  Step 6b: Validating input elements (SOFT ASSERT)...")
            soft_assert.assert_count(second_td.locator("input[value='radiobtnNo']"), 1, "[FAIL] AuthorizedSignerApprovalSection: radiobtnNo Input Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 'radiobtnNo' input required. Locator: input[value='radiobtnNo'].")
            soft_assert.assert_count(second_td.locator("input[value='radiobtnYes']"), 1, "[FAIL] AuthorizedSignerApprovalSection: radiobtnYes Input Count — Expected: count=1, Actual: count!=1. Details: Exactly 1 'radiobtnYes' input required. Locator: input[value='radiobtnYes'].")
            soft_assert.assert_visible(second_td.locator("input[value='radiobtnNo']").first, "[FAIL] AuthorizedSignerApprovalSection: radiobtnNo Input Visibility — Expected: visible=True, Actual: visible=False. Details: 'radiobtnNo' input must be visible. Locator: input[value='radiobtnNo'].")
            soft_assert.assert_visible(second_td.locator("input[value='radiobtnYes']").first, "[FAIL] AuthorizedSignerApprovalSection: radiobtnYes Input Visibility — Expected: visible=True, Actual: visible=False. Details: 'radiobtnYes' input must be visible. Locator: input[value='radiobtnYes'].")
            logger.info("  ✓ Input elements collected for soft assertion verification (1 radiobtnNo, 1 radiobtnYes, both visible)")
            
            logger.info("✓ All validations completed")
            
            # Step 7: Verify soft assertions
            logger.info("Step 7: Verifying soft assertions...")
            try:
                soft_assert.assert_all()
                logger.info("✓ All soft assertions passed (input elements validated)")
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
            logger.info("✓ Verification completed successfully")
            
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
            
            logger.info(f"  ✓ eSign method fetched from test data: '{esign_method}'")
            
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
            
            logger.info(f"✓ Successfully verified fields for eSign method: '{esign_method}'")
            
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
                "[FAIL] ClientAccountsPage: eSign Iframe Access — Expected: count=1, Actual: count!=1. Details: iframe#esig_iframe must exist on page. Locator: iframe#esig_iframe."
            )
            iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
            logger.info("✓ Signer(s) Information Iframe accessed")
            
            # Step 2: Validate 'Authorized Signer eSign Method' heading
            logger.info("Step 2: Validating 'Authorized Signer eSign Method' heading...")
            heading = iframe_frame.locator("h5:has-text('Authorized Signer eSign Method')")
            Assertions.assert_count(heading, 1, "[FAIL] ClientAccountsPage: eSign Method Heading Count — Expected: count=1, Actual: count!=1. Details: h5 heading with 'Authorized Signer eSign Method' text must exist. Locator: h5:has-text('Authorized Signer eSign Method').")
            Assertions.assert_visible(heading, "[FAIL] ClientAccountsPage: eSign Method Heading Visibility — Expected: visible=True, Actual: visible=False. Details: eSign Method heading must be visible. Locator: h5:has-text('Authorized Signer eSign Method').")
            logger.info("✓ 'Authorized Signer eSign Method' heading validated")
            
            # Step 3: Validate 'SMS' label
            logger.info("Step 3: Validating 'SMS' label...")
            sms_label = iframe_frame.locator("div#eSignMethodDiv span").filter(has_text="SMS").first
            Assertions.assert_count(sms_label, 1, "[FAIL] ClientAccountsPage: SMS Label Count — Expected: count=1, Actual: count!=1. Details: Span with 'SMS' text must exist in eSignMethodDiv. Locator: div#eSignMethodDiv span:has-text('SMS').")
            Assertions.assert_visible(sms_label, "[FAIL] ClientAccountsPage: SMS Label Visibility — Expected: visible=True, Actual: visible=False. Details: SMS label must be visible. Locator: div#eSignMethodDiv span:has-text('SMS').")
            logger.info("✓ 'SMS' label validated")
            
            # Step 4: Validate SMS radio button is displayed
            logger.info("Step 4: Validating SMS radio button...")
            sms_radio = iframe_frame.locator("input#radiobtnSMS")
            Assertions.assert_count(sms_radio, 1, "[FAIL] ClientAccountsPage: SMS Radio Button Count — Expected: count=1, Actual: count!=1. Details: input#radiobtnSMS must exist in eSign Method section. Locator: input#radiobtnSMS.")
            Assertions.assert_visible(sms_radio, "[FAIL] ClientAccountsPage: SMS Radio Button Visibility — Expected: visible=True, Actual: visible=False. Details: SMS radio button must be visible. Locator: input#radiobtnSMS.")
            logger.info("✓ SMS radio button validated")
            
            # Step 5: Validate 'Tracking Center' label
            logger.info("Step 5: Validating 'Tracking Center' label...")
            tracking_center_label = iframe_frame.locator("div#eSignMethodDiv span").filter(has_text="Tracking Center").first
            Assertions.assert_count(tracking_center_label, 1, "[FAIL] ClientAccountsPage: Tracking Center Label Count — Expected: count=1, Actual: count!=1. Details: Span with 'Tracking Center' text must exist in eSignMethodDiv. Locator: div#eSignMethodDiv span:has-text('Tracking Center').")
            Assertions.assert_visible(tracking_center_label, "[FAIL] ClientAccountsPage: Tracking Center Label Visibility — Expected: visible=True, Actual: visible=False. Details: Tracking Center label must be visible. Locator: div#eSignMethodDiv span:has-text('Tracking Center').")
            logger.info("✓ 'Tracking Center' label validated")
            
            # Step 6: Validate 'Tracking Center' radio button is displayed
            logger.info("Step 6: Validating 'Tracking Center' radio button...")
            tracking_center_radio = iframe_frame.locator("input#radiobtnTC")
            Assertions.assert_count(tracking_center_radio, 1, "[FAIL] ClientAccountsPage: Tracking Center Radio Button Count — Expected: count=1, Actual: count!=1. Details: input#radiobtnTC must exist in eSign Method section. Locator: input#radiobtnTC.")
            Assertions.assert_visible(tracking_center_radio, "[FAIL] ClientAccountsPage: Tracking Center Radio Button Visibility — Expected: visible=True, Actual: visible=False. Details: Tracking Center radio button must be visible. Locator: input#radiobtnTC.")
            logger.info("✓ 'Tracking Center' radio button validated")
            
            # Step 7: Verify none of the radio buttons are selected
            logger.info("Step 7: Verifying no radio buttons are selected by default...")
            sms_checked = sms_radio.is_checked()
            tracking_center_checked = tracking_center_radio.is_checked()
            
            assert not sms_checked, "[FAIL] ClientAccountsPage: SMS Radio Default State — Expected: radiobtnSMS.checked=False, Actual: checked=True. Details: SMS radio button should NOT be selected by default in eSign Method section. Locator: input#radiobtnSMS."
            assert not tracking_center_checked, "[FAIL] ClientAccountsPage: Tracking Center Radio Default State — Expected: radiobtnTC.checked=False, Actual: checked=True. Details: Tracking Center radio button should NOT be selected by default in eSign Method section. Locator: input#radiobtnTC."
            logger.info("✓ Verified: No radio buttons are selected by default")
            
            logger.info("✓ All validations passed")
            
            # Step 8: Screenshot
            logger.info("Step 8: Taking screenshot...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Authorized Signer eSign Method Section - Verified",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.info("✓ Verification completed successfully")
            
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


@when("User select Authorized Signer eSign Method")
def user_select_authorized_signer_esign_method(authenticated_page: Page, client_accounts_page, test_context):
    """
    Select Authorized Signer eSign Method (SMS or Tracking Center).
    
    Reads 'Authorized_Signer_eSign_Method' from test data CSV and selects the appropriate radio button.
    Valid values: 'SMS' or 'Tracking Center'
    """
    with allure.step("User select Authorized Signer eSign Method"):
        logger.info(">>> STEP: User select Authorized Signer eSign Method")
        
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
            
            logger.info(f"  ✓ eSign method fetched from test data: '{esign_method}'")
            
            # Step 2: Call page object method to select the radio button
            logger.info(f"  Step 2: Selecting '{esign_method}' radio button...")
            client_accounts_page.select_authorized_signer_esign_method(esign_method)
            
            # Step 3: Take screenshot for Allure reporting
            logger.info("  Step 3: Taking screenshot after selection...")
            allure.attach(
                authenticated_page.screenshot(),
                name=f"Authorized Signer eSign Method - {esign_method} Selected",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info(f"✓ Successfully completed: User selected Authorized Signer eSign Method: '{esign_method}'")
            
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
            
            authorized_signer = test_data.get("Authorized_Signer", "").strip() if test_data.get("Authorized_Signer") else ""
            email_address = test_data.get("Email_Address", "").strip() if test_data.get("Email_Address") else ""
            phone = test_data.get("Phone", "").strip() if test_data.get("Phone") else ""
            
            logger.info(f"  ✓ Data fetched:")
            logger.info(f"    - Authorized_Signer: '{authorized_signer if authorized_signer else 'N/A'}'")
            logger.info(f"    - Email_Address: '{email_address if email_address else 'N/A'}'")
            logger.info(f"    - Phone: '{phone if phone else 'N/A'}'")
            
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
            
            logger.info("✓ Successfully completed: User provided Authorized Signers information")
            
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
    
    Fetches multiple_signers from test_context:
    - If 1 signer: Verifies dropdown is disabled and shows signer name
    - If > 1 signers: Verifies dropdown is enabled and options match Name_ManageLogin values
    - If 0 signers: Skip verification (no authorized signers found in database)
    """
    with allure.step("Verify Authorized Signer dropdown"):
        logger.info(">>> STEP: Verify Authorized Signer dropdown")
        
        try:
            # Step 1: Get multiple signers from test context
            logger.info("  Step 1: Fetching multiple_signers from test_context...")
            
            # Check if key exists in test_context (not just truthy/falsy)
            if "multiple_signers" not in test_context:
                raise AssertionError("multiple_signers not found in test_context. Run 'User fetch signers information from database' step first.")
            
            signers = test_context.get("multiple_signers", [])
            
            # If no signers found in database, skip this verification
            if not signers:
                logger.info("  ℹ No authorized signers found in database - skipping dropdown verification")
                logger.info("  ✓ Step completed: No signers to verify")
                return
            
            logger.info(f"  ✓ Fetched {len(signers)} signer(s) from test_context")
            
            # Step 2: Access iframe
            logger.info("  Step 2: Accessing iframe...")
            from utils.dialog_utils import DialogHandler
            dialog_handler = DialogHandler(authenticated_page)
            dialog = dialog_handler.wait_for_dialog(timeout=10000)
            
            iframe_frame = authenticated_page.frame_locator("iframe#esig_iframe")
            logger.info("  ✓ Iframe accessed")
            
            # Step 3: Find dropdown
            logger.info("  Step 3: Locating Authorized Signers dropdown...")
            dropdown = iframe_frame.locator("select[name='authorizedSignersDropdown']")
            
            Assertions.assert_count(dropdown, 1, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown — Expected: count=1, Actual: count!=1. Details: Dropdown must exist in Signer Information dialog. Locator: select[name='authorizedSignersDropdown'].")
            Assertions.assert_visible(dropdown, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Visibility — Expected: visible=True, Actual: visible=False. Details: Dropdown must be visible. Locator: select[name='authorizedSignersDropdown'].")
            logger.info("  ✓ Dropdown found and visible")
            
            # Step 4: Validate based on signer count
            if len(signers) == 1:
                # Case 1: Only 1 signer - dropdown should be disabled and show signer name
                logger.info("  Step 4: Validating dropdown is disabled (1 signer present)...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_true(is_disabled, "[FAIL] ClientAccountsPage: Authorized Signers Dropdown Disabled State — Expected: is_disabled=True, Actual: is_disabled=False. Details: Dropdown should be disabled when only 1 signer is present. Locator: select[name='authorizedSignersDropdown'].")
                logger.info("  ✓ Dropdown is correctly disabled (1 signer only)")
                
                # Step 5: Verify the default selected option matches the signer name
                logger.info("  Step 5: Verifying default selected option matches signer name...")
                signer_name = signers[0].get("Name_ManageLogin", "")
                
                assert signer_name, "[FAIL] ClientAccountsPage: Signer Name Extraction — Expected: Name_ManageLogin present, Actual: empty or missing. Details: Signer data must include Name_ManageLogin field from database query."
                
                # Get the selected option text
                selected_option = iframe_frame.locator("select[name='authorizedSignersDropdown'] option[selected]")
                Assertions.assert_count(selected_option, 1, "[FAIL] ClientAccountsPage: Dropdown Selected Option — Expected: count=1, Actual: count!=1. Details: Exactly one option should be selected. Locator: select[name='authorizedSignersDropdown'] option[selected].")
                
                selected_text = (selected_option.first.text_content() or "").strip()
                logger.info(f"  Selected option text: '{selected_text}'")
                logger.info(f"  Expected signer name: '{signer_name}'")
                
                Assertions.assert_equal(selected_text, signer_name, f"[FAIL] ClientAccountsPage: Dropdown Selected Value — Expected: '{signer_name}', Actual: '{selected_text}'. Details: Dropdown should show the only available signer's name. Locator: select[name='authorizedSignersDropdown'].")
                logger.info(f"  ✓ Default selected option matches signer: '{selected_text}'")
                
            elif len(signers) > 1:
                # Case 2: Multiple signers - dropdown should be enabled and options match signers
                logger.info(f"  Step 4: Validating dropdown options match {len(signers)} signers...")
                is_disabled = dropdown.is_disabled()
                
                Assertions.assert_false(is_disabled, f"[FAIL] ClientAccountsPage: Authorized Signers Dropdown Enabled State — Expected: is_disabled=False, Actual: is_disabled=True. Details: Dropdown should be enabled when {len(signers)} signers are present. Locator: select[name='authorizedSignersDropdown'].")
                logger.info("  ✓ Dropdown is enabled")
                
                # Step 5: Fetch all options from dropdown
                logger.info("  Step 5: Fetching dropdown options...")
                options = iframe_frame.locator("select[name='authorizedSignersDropdown'] option").all()
                
                Assertions.assert_greater(len(options), 0, "[FAIL] ClientAccountsPage: Dropdown Options Count — Expected: count>0, Actual: count=0. Details: Dropdown must have at least one option. Locator: select[name='authorizedSignersDropdown'] option.")
                logger.info(f"  ✓ Found {len(options)} option(s) in dropdown")
                
                # Step 6: Extract option texts (skip first option which is "--Select Authorized Signer--")
                logger.info("  Step 6: Extracting and validating option values...")
                option_texts = []
                for idx, option in enumerate(options):
                    option_text = (option.text_content() or "").strip()
                    option_texts.append(option_text)
                    logger.info(f"    Option {idx}: '{option_text}'")
                
                # Skip the first "--Select Authorized Signer--" option
                actual_options = option_texts[1:] if len(option_texts) > 1 else option_texts
                
                # Step 7: Extract expected signer names from test_context signers
                logger.info("  Step 7: Comparing options with signer names...")
                expected_signer_names = [signer.get("Name_ManageLogin", "") for signer in signers]
                
                logger.info(f"  Expected signer names: {expected_signer_names}")
                logger.info(f"  Actual dropdown options: {actual_options}")
                
                # Validate count matches
                Assertions.assert_equal(len(actual_options), len(expected_signer_names), f"[FAIL] ClientAccountsPage: Dropdown Options Count — Expected: {len(expected_signer_names)}, Actual: {len(actual_options)}. Details: Number of dropdown options must match number of signers. Locator: select[name='authorizedSignersDropdown'] option.")
                logger.info(f"  ✓ Option count matches signer count: {len(actual_options)}")
                
                # Validate each option matches a signer name
                for idx, (actual, expected) in enumerate(zip(actual_options, expected_signer_names)):
                    Assertions.assert_equal(actual, expected, f"[FAIL] ClientAccountsPage: Dropdown Option Value — Expected: '{expected}' at index {idx}, Actual: '{actual}'. Details: Each dropdown option must match a signer name. Locator: select[name='authorizedSignersDropdown'] option[{idx+1}].")
                    logger.info(f"  ✓ Option {idx + 1} matches: '{actual}'")
                
                logger.info("  ✓ All dropdown options match signer names")
            
            else:
                # Case 3: No signers - log warning
                logger.warning("  ⚠ Warning: No signers provided in test_context['multiple_signers']")
            
            # Step 8: Take screenshot
            logger.info("  Step 8: Taking screenshot...")
            allure.attach(
                authenticated_page.screenshot(),
                name="Authorized Signer Dropdown - Verified",
                attachment_type=allure.attachment_type.PNG,
            )
            
            logger.info("✓ Successfully verified Authorized Signer dropdown")
            
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
            
            logger.info("✓ Successfully completed: Click on Continue button")
            
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
    
    Hard asserts that the account number is present in one of the account labels,
    then checks if the corresponding radio button is selected.
    If not selected, automatically selects it and uses soft assertions to verify the selection.
    
    Reads 'Account_Number' from test_data CSV and validates against the account list labels.
    Uses SoftAssertions utility for non-blocking assertions on radio button state.
    """
    # Read account number from test data
    test_data = test_context.get("test_data", {})
    account_number = test_data.get("Account_Number") or test_data.get("account_number")
    
    if not account_number:
        raise KeyError("Test data must include 'Account_Number' column for this step")
    
    with allure.step(f"Verify Account Number '{account_number}' is displayed and radio is selected"):
        logger.info(f">>> ENTERED STEP: verify_account_number_displayed_and_radio_selected")
        logger.info(f"Account_Number from test data: '{account_number}'")
        
        # STEP 0-1: Fetch the matching account label using page object method
        logger.info("Step 0-1: Fetching account label using page object method...")
        matching_label = client_accounts_page.fetch_selected_account(account_number)
        logger.info(f"✓ HARD ASSERTION PASSED: Account Number '{account_number}' is displayed under Account Management.")
        
        # STEP 2: Get the corresponding radio button using the label's 'for' attribute
        logger.info("Step 2: Finding and validating corresponding radio button...")
        
        # Get the label's for attribute to locate the matching radio input
        label_for_attr = matching_label.get_attribute("for")
        logger.info(f"Label 'for' attribute value: '{label_for_attr}'")
        
        # Locate the radio input with matching id
        radio_button = authenticated_page.locator(f"input#{label_for_attr}")
        
        assert radio_button.count() > 0, \
            f"[FAIL] ClientAccountsPage: Radio Button Lookup — Expected: radio_button count > 0, " \
            f"Actual: count=0 (not found). Details: Radio button with id '{label_for_attr}' for account '{account_number}' should exist. " \
            f"Locator: input#{label_for_attr}."
        
        radio_button = radio_button.first
        logger.info(f"✓ Located radio button for account '{account_number}'")
        
        # STEP 3: Check radio button state and select if needed
        logger.info("Step 3: Checking radio button selection state...")
        
        is_checked = radio_button.is_checked()
        logger.info(f"Radio button current state - checked: {is_checked}")
        
        if not is_checked:
            logger.info(f"Radio button is NOT checked - selecting it now...")
            radio_button.check()
            authenticated_page.wait_for_timeout(500)  # Wait for state update
            is_checked = radio_button.is_checked()
            logger.info(f"Radio button after selection - checked: {is_checked}")
        else:
            logger.info(f"Radio button is already checked")
        
        # STEP 4: Use SoftAssertions utility for radio button verification
        logger.info("Step 4: Validating radio button state with soft assertions...")
        soft_assert = SoftAssertions()
        soft_assert.assert_true(
            is_checked,
            message=f"[FAIL] ClientAccountsPage: Account Selection — Expected: radio_button[id='{label_for_attr}'] checked=True, "
                    f"Actual: checked={is_checked}. Details: Radio button for account '{account_number}' should be selected. "
                    f"Locator: input#{label_for_attr}."
        )
        
        # STEP 5: Take screenshot for audit trail
        logger.info("Step 5: Capturing screenshot for verification...")
        screenshot = authenticated_page.screenshot()
        allure.attach(
            screenshot, 
            name=f"Account {account_number} - Verified and Selected", 
            attachment_type=allure.attachment_type.PNG
        )
        
        # Verify soft assertions - raises SoftAssertionError if any failed
        try:
            soft_assert.assert_all()
            logger.info(f"✓ SOFT ASSERTION PASSED: Radio button is checked for account '{account_number}'")
        except Exception as e:
            logger.error(f"✗ Soft assertion(s) failed: {str(e)}")
            allure.attach(
                str(e),
                name=f"Account {account_number} - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        logger.info(f"✓ Step completed successfully - Account Number verification PASSED")


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
        logger.info("✓ Request/Type table verified as ready")

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
        logger.info("✓ OAM Request and Type selected successfully")


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
    expected_heading = test_data.get("OAM_Type") or test_data.get("OAM_type")
    
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
        soft_assert = SoftAssertions()
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
            logger.info(f"✓ SOFT ASSERTION PASSED: Form heading matches OAM_Type '{expected_heading}'")
        except Exception as e:
            logger.error(f"✗ Soft assertion(s) failed: {str(e)}")
            allure.attach(
                str(e),
                name="Form Heading Verification - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        logger.info(f"✓ Step completed successfully - Form Heading verification PASSED")


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
            logger.info("✓ Dialog detected successfully")
        except Exception as e:
            logger.error(f"✗ Dialog detection failed: {e}")
            
            # Fallback: Try waiting for dialog by role attribute
            try:
                authenticated_page.wait_for_selector('role=dialog', timeout=15000)
                dialog = authenticated_page.locator('role=dialog').first
                logger.info("✓ Dialog found via role attribute fallback")
            except Exception as e2:
                logger.error(f"✗ All dialog detection strategies failed")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="Dialog Detection Failed", attachment_type=allure.attachment_type.PNG)
                raise AssertionError("Client Signature Not Required dialog not found after multiple detection attempts") from e
        
        # STEP 2: Extract title from modal-title-transition div using page object
        logger.info("Step 2: Extracting dialog title using page object...")
        dialog_title = client_accounts_page.get_signature_dialog_title()
        logger.info(f"Dialog title extracted: '{dialog_title}'")
        
        # STEP 3: Use SoftAssertions to verify the dialog title
        logger.info("Step 3: Verifying dialog title matches expected text...")
        expected_title = "Client Signature Not Required"
        
        soft_assert = SoftAssertions()
        soft_assert.assert_equal(
            dialog_title,
            expected_title,
            message=f"[FAIL] ClientAccountsPage: Signature Dialog Title — Expected: title='{expected_title}', Actual: title='{dialog_title}'. Details: Client Signature Not Required dialog should display correct title from 'div.modal-title-transition'. Locator: div.modal-title-transition."
        )
        
        # STEP 3a: Verify that 'Proceed and submit without a client signature' radio button is checked
        logger.info("Step 3a: Verifying 'Proceed and submit without a client signature' radio button is checked...")
        is_rb_submit_checked = client_accounts_page.is_radio_checked('rbSubmit')
        soft_assert.assert_true(
            is_rb_submit_checked,
            message="[FAIL] ClientAccountsPage: Radio Button Default State — Expected: rbSubmit.checked=True, Actual: rbSubmit.checked=False. Details: 'Proceed and submit without a client signature' radio should be checked by default in Client Signature Not Required dialog. Locator: input#rbSubmit."
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
            logger.info(f"✓ SOFT ASSERTION PASSED: Dialog title matches '{expected_title}'")
        except Exception as e:
            logger.error(f"✗ Soft assertion(s) failed: {str(e)}")
            allure.attach(
                str(e),
                name="Client Signature Not Required Dialog - Assertion Failures",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        
        logger.info(f"✓ Step completed successfully - Client Signature Not Required dialog verification PASSED")


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
            logger.info("✓ Dialog detected successfully")
        except Exception as e:
            logger.error(f"✗ Dialog detection failed: {e}")
            
            # Fallback: Try waiting for any visible dialog
            try:
                authenticated_page.wait_for_selector('role=dialog', timeout=15000)
                dialog = authenticated_page.locator('role=dialog').first
                logger.info("✓ Dialog found via role fallback")
            except Exception as e2:
                logger.error(f"✗ All dialog detection strategies failed")
                screenshot = authenticated_page.screenshot()
                allure.attach(screenshot, name="Dialog Detection Failed", attachment_type=allure.attachment_type.PNG)
                raise AssertionError("Request dialog not found after multiple detection attempts") from e
        
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
                    logger.info(f"✓ Section {idx} verified: {section[:60]}...")
                else:
                    missing_sections[idx] = section
                    logger.warning(f"✗ Section {idx} not found in dialog: {section}")
            
            # Assert all expected sections were found
            assert not missing_sections, \
                f"[FAIL] ClientAccountsPage: Request Dialog Content — Expected: all {len(expected_sections)} sections present, " \
                f"Actual: {len(missing_sections)} missing sections {list(missing_sections.keys())}. " \
                f"Details: All expected text sections must be present in Request Submitted dialog. Missing: {missing_sections}. " \
                f"Locator: [role='dialog']."
            
            logger.info(f"✓ Verified: All {len(expected_sections)} sections present in dialog")
        except Exception as e:
            logger.error(f"✗ Dialog content validation failed: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="Dialog Content Validation Failed", attachment_type=allure.attachment_type.PNG)
            raise
        
        # STEP 3: Fetch and validate dialog elements
        logger.info("Step 3: Fetching dialog elements...")
        try:
            # Initialize soft assertions for optional dialog elements
            soft_assert = SoftAssertions()
            
            dialog_data = client_accounts_page.get_request_submitted_dialog_content()
            
            # Validate D-link (tracking center link)
            d_link = dialog_data.get('d_link')
            d_link_text = dialog_data.get('d_link_text')
            
            if d_link:
                assert d_link.is_visible(), "D-link not visible"
                logger.info(f"✓ D-link is visible and enabled")
                
                # Verify D-number text starts with 'D'
                assert d_link_text and d_link_text.startswith('D'), \
                    f"D-link text should start with 'D', but got: '{d_link_text}'"
                logger.info(f"✓ D-link text starts with 'D': {d_link_text}")
            else:
                raise AssertionError("D-link not found in dialog")
            
            # Verify all soft assertions
            logger.info("Verifying soft assertions for optional dialog elements...")
            try:
                soft_assert.assert_all()
                logger.info("✓ All soft assertions passed")
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
        
        logger.info("✓ Request dialog verification completed successfully")


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
            logger.info(f"✓ D-number clicked successfully: {d_number}")
            
            # Store D-number in test_context for later verification
            test_context['d_number'] = d_number
            logger.info(f"✓ D-number stored in test_context: {d_number}")
            
        except Exception as e:
            logger.error(f"✗ Failed to click D-number element: {e}")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="D-Number Click - Failed", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Failed to click D-number: {e}") from e
        
        # STEP 2: Wait for page navigation to Tracking Center
        try:
            authenticated_page.wait_for_load_state("networkidle", timeout=30000)
            logger.info(f"✓ Page navigated to Tracking Center with D-number: {d_number}")
            
        except Exception as e:
            logger.error(f"✗ Timeout waiting for Tracking Center page to load: {e}")
            logger.error(f"   (D-number {d_number} was clicked, but page load timed out)")
            screenshot = authenticated_page.screenshot()
            allure.attach(screenshot, name="D-Number Navigation - Page Load Timeout", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Page failed to load after clicking D-number {d_number}: {e}") from e
        
        # STEP 3: Take screenshot for Allure reporting
        screenshot = authenticated_page.screenshot()
        allure.attach(screenshot, name="D-number Clicked - Navigating to Tracking Center", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f"✓ D-number click step completed successfully for D-number: {d_number}")

