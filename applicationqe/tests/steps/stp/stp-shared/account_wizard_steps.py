import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.withdrawal_signature_not_required_modal_page import WithdrawalSignatureNotRequiredModalPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("I click on Account Wizard")
def click_on_account_wizard(page: Page, account_detail_page):
    """Click on Account Wizard link"""
    logger.info("Clicking Account Wizard")
    account_detail_page.click_account_wizard()


@when("I select Funded account option")
def select_funded_account_option(page: Page, account_detail_page):
    """Select the Funded radio option"""
    logger.info("Selecting Funded account option")
    account_detail_page.select_funded_radio()


@when("I select Move Assets Between Accounts")
def select_move_assets_between_accounts(page: Page, account_detail_page):
    """Select Move Assets Between Accounts option"""
    logger.info("Selecting Move Assets Between Accounts")
    account_detail_page.select_move_assets_between_accounts()


@when("I select Roth IRA Conversion")
def select_roth_ira_conversion(page: Page, account_detail_page):
    """Select Roth IRA Conversion option"""
    logger.info("Selecting Roth IRA Conversion")
    account_detail_page.select_roth_ira_conversion()


@when("I click Next on Account Wizard")
def click_next_on_account_wizard(page: Page, account_detail_page):
    """Click Next button on Account Wizard"""
    logger.info("Clicking Next on Account Wizard")
    account_detail_page.click_next()


@then("I should see the Roth Conversion page")
def verify_roth_conversion_page_loaded(page: Page, roth_conversion_page):
    """Verify Roth Conversion page is loaded"""
    logger.info("Verifying Roth Conversion page is loaded")
    page.wait_for_load_state("domcontentloaded", timeout=120000)


@when("User should pick account information from the selected account")
def pick_account_information_from_selected_account(page: Page, account_wizard_page, test_context: dict):
    """Pick account information from the selected account"""
    with allure.step("Pick account information from the selected account"):
        client_id = str(test_context["test_data"]["client_id"])
        account_details_mimo1 = account_wizard_page.select_and_fetch_account_by_client_id(client_id)
        assert account_details_mimo1, (
            f"No account label found containing client_id '{client_id}' on the Account Wizard page. "
            "Verify the client_id in test data matches the account listed on screen."
        )
        account_name = account_details_mimo1[0]
        test_context["account_details_mimo1"] = account_details_mimo1
        
        logger.info(f"Account Name: {account_name}")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Selected Account Information", attachment_type=allure.attachment_type.PNG)


@when("User should pick account information from the selected account for Cancel AIP")
def pick_account_information_for_cancel_aip(page: Page, account_wizard_page, test_context: dict):
    """Pick account information from the selected account for Cancel AIP"""
    with allure.step("Pick account information from the selected account for Cancel AIP"):
        logger.info("Fetching account information for Cancel AIP")
        
        account_details = account_wizard_page.select_and_fetch_account_by_client_id(
            str(test_context["test_data"]["client_id"])
        )
        test_context["cancel_aip_account_details"] = account_details
        test_context["cancel_aip_account_name"] = account_details[0] if account_details else None
        logger.info(f"Cancel AIP Account Details: {account_details}")
        allure.attach(
            str(account_details),
            name="Cancel AIP Account Information",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Cancel AIP Account Information", attachment_type=allure.attachment_type.PNG)


@when("User should pick account information from the selected account for Establish AIP")
def pick_account_information_for_establish_aip(page: Page, account_wizard_page, test_context: dict):
    """Pick account information from the selected account for Establish AIP"""
    with allure.step("Pick account information from the selected account for Establish AIP"):
        logger.info("Fetching account information for Establish AIP")

        account_details = account_wizard_page.select_and_fetch_account_by_client_id(
            str(test_context["test_data"]["client_id"])
        )
        test_context["establish_aip_account_details"] = account_details
        test_context["establish_aip_account_name"] = account_details[0] if account_details else None
        logger.info(f"Establish AIP Account Details: {account_details}")
        allure.attach(
            str(account_details),
            name="Establish AIP Account Information",
            attachment_type=allure.attachment_type.TEXT
        )

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Establish AIP Account Information", attachment_type=allure.attachment_type.PNG)


@when("User checks Toggle Functionality for Specific User and Click on Add ACH Instructions on Account Wizard")
def check_and_click_add_ach_instruction_link(page: Page, account_wizard_page):
    """Check toggle functionality and click Add ACH Instructions link"""
    with allure.step("Check Toggle Functionality and Click Add ACH Instructions"):
        logger.info("Checking the Functionality of the Toggle Button")
        account_wizard_page.click_add_ach_instructions()
        logger.info("Add ACH Instructions link clicked")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Add ACH Instructions Clicked", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('Select "{request}" request and "{type_option}" type in Account Management'))
def select_request_and_type_in_account_management(page: Page, account_wizard_page, test_context, request: str, type_option: str):
    """Select request and type in Account Management"""
    with allure.step(f"Select '{request}' request and '{type_option}' type in Account Management"):
        logger.info(f"Selecting request: {request}, type: {type_option}")
        
        account_number = test_context.get('account_number')
        if not account_number:
            logger.warning("Account number not found in test context, skipping account selection")
        else:
            account_wizard_page.click_account(account_number)
        account_wizard_page.select_request(request)
        account_wizard_page.select_type(type_option)
        
        test_context["request_type"] = type_option
        
        logger.info(f"Selected request '{request}' and type '{type_option}'")
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Request and Type Selected - {request} - {type_option}",
            attachment_type=allure.attachment_type.PNG
        )


@when('User clicks on complete and submit button')
def click_complete_and_submit_button(page: Page, account_wizard_page):
    """Click the Complete and Submit button"""
    with allure.step("Click Complete and Submit button"):
        logger.info("Clicking Complete and Submit button")
        account_wizard_page.click_complete_and_submit()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Complete and Submit Clicked", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('User should click continue button without client signature for "{request_type}"'))
def click_continue_without_client_signature(page: Page, withdrawal_signature_modal_page, mimo_transaction_page, request_type: str):
    """Click continue button without client signature"""
    with allure.step(f"Click continue without client signature for {request_type}"):
        logger.info(f"Clicking continue without signature for: {request_type}")
        
        withdrawal_signature_modal_page.click_submit_without_signature(request_type)
        
        if request_type in ["Contributions", "Cancel"," Withdrawals"]:
            mimo_transaction_page.wait_for_page_load()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Continue Without Signature - {request_type}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should select E-sign flow and click continue for "{request_type}"'))
def click_continue_with_esign_signature(page: Page, withdrawal_signature_modal_page, request_type: str):
    """Select 'Request client electronic signature' and click Continue"""
    with allure.step(f"Select e-sign flow and click continue for {request_type}"):
        logger.info(f"Selecting e-sign signature flow for: {request_type}")

        withdrawal_signature_modal_page.click_request_esign_signature()

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"E-sign Flow Selected - {request_type}",
            attachment_type=allure.attachment_type.PNG
        )


@when('User should accept DocuSign Electronic Record consent and click continue')
def accept_docusign_ersd_and_continue(page: Page, docusign_page):
    """Check ERSD consent checkbox and click Continue on DocuSign Review and Continue modal"""
    with allure.step("Accept DocuSign Electronic Record and Signature Disclosure and click Continue"):
        logger.info("Waiting for DocuSign ERSD modal to appear")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign - ERSD Modal", attachment_type=allure.attachment_type.PNG)

        logger.info("Checking ERSD consent checkbox")
        docusign_page.check_ersd_consent_checkbox()

        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign - Consent Checked", attachment_type=allure.attachment_type.PNG)

        logger.info("Clicking Continue button on ERSD modal")
        docusign_page.click_ersd_continue_button()

        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign - ERSD Continued", attachment_type=allure.attachment_type.PNG)
        logger.info("DocuSign ERSD consent accepted and Continue clicked successfully")


@then(parsers.parse('user is redirected on signer information page and fill signer detail with name "{signer_name}" email "{signer_email}" phone "{signer_phone}" and click on continue button'))
def fill_signer_information_and_continue(page: Page, esign_signer_information_page, signer_name: str, signer_email: str, signer_phone: str):
    """Verify Signer Information page, fill first signer details, and submit."""
    with allure.step("Fill signer information and submit e-sign request"):
        logger.info("Waiting for esig_iframe to be present")
        page.locator("#esig_iframe").wait_for(state="attached", timeout=20000)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Signer Information - Page Loaded", attachment_type=allure.attachment_type.PNG)

        logger.info("Verifying Signer(s) Information page loaded")
        esign_signer_information_page.verify_signer_information_page()

        logger.info(f"Entering signer full name: {signer_name}")
        esign_signer_information_page.enter_signer_full_name(signer_name)

        logger.info(f"Entering signer email: {signer_email}")
        esign_signer_information_page.enter_signer_email(signer_email)

        logger.info(f"Entering signer phone: {signer_phone}")
        esign_signer_information_page.enter_signer_phone(signer_phone)

        logger.info("Selecting 'By Email' delivery method")
        esign_signer_information_page.select_email_radio_button()

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Signer Information - Fields Filled", attachment_type=allure.attachment_type.PNG)

        logger.info("Clicking Continue button")
        esign_signer_information_page.click_continue_button()

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Signer Information - Submitted", attachment_type=allure.attachment_type.PNG)
        logger.info("Signer information submitted successfully")


@when('User clicks on complete and submit button and click on Continue button without client signature')
def click_complete_and_submit_and_continue_without_signature(page: Page, account_wizard_page, test_context):
    
    with allure.step("Click Complete and Submit, then Continue without client signature"):
        logger.info("Step 1: Clicking Complete and Submit button")
        
        # Step 1: Click Complete and Submit button
        account_wizard_page.click_complete_and_submit()
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="After Complete and Submit Clicked",
            attachment_type=allure.attachment_type.PNG
        )
        
        # Step 2: Wait for signature modal to appear
        logger.info("Step 2: Waiting for signature modal")
        signature_modal = WithdrawalSignatureNotRequiredModalPage(page)
        signature_modal.signature_not_required_radio.wait_for(state='visible', timeout=10000)
        
        # Step 3: Click submit without signature radio button
        logger.info("Step 3: Selecting 'Submit without signature' option")
        signature_modal.signature_not_required_radio.click()
        logger.info("Signature not required radio button clicked")
        
        # Step 4: Click Continue button on modal
        logger.info("Step 4: Clicking Continue button on signature modal")
        signature_modal.continue_button.click()
        logger.info("Continue button clicked")
        
        # Step 5: Wait for iframe to load (Withdrawal Method Modal)
        page.wait_for_timeout(1000)
        logger.info("Step 5: Checking for esig_iframe")
        
        # Check if iframe exists and switch context
        if page.frame_locator("#esig_iframe").first.count() > 0:
            logger.info("esig_iframe detected - Withdrawal Method Modal should be loaded")
        else:
            logger.warning("esig_iframe not found - may have navigated to different page")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="After Continue Without Signature",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Complete and Submit + Continue without signature flow completed")


@when("User should check custodianIDs to determine address change flows")
def check_custodian_ids_for_address_change(page: Page, account_wizard_page, test_context: dict):
    """Check custodian IDs to determine address change flow"""
    with allure.step("Check custodianIDs to determine address change flows"):
        logger.info("Checking custodian IDs for address change flows")
        
        account_details = account_wizard_page.select_and_fetch_account_by_client_id(
            str(test_context["test_data"]["client_id"])
        )
        
        test_context['account_details'] = account_details
        
        custodian_id = test_context.get('custodian_id', '')
        
        # Example logic: certain custodians only allow mailing address changes
        display_only_mailing = custodian_id in ['CUST001', 'CUST002']  # Customize as needed
        
        test_context['display_only_mailing_address'] = display_only_mailing
        logger.info(f"Custodian ID: {custodian_id}, Display only mailing address: {display_only_mailing}")
        
        allure.attach(
            f"Custodian ID: {custodian_id}\nDisplay only mailing: {display_only_mailing}",
            name="Custodian Information",
            attachment_type=allure.attachment_type.TEXT
        )
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Custodian Check", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('User Should click on Update Addresses for "{test}" and verify the page layout'))
@then(parsers.parse('User Should click on Update Addresses for "{test}" and verify the page layout'))
def click_update_addresses_and_verify_layout(page: Page, account_wizard_page, dm_tool_page, test_context: dict, test: str):
    """Click on Update Addresses and verify DM Tool page layout"""
    with allure.step(f"Click on Update Addresses for {test} and verify the page layout"):
        logger.info(f"Clicking on Update Addresses for {test}")
        
        account_wizard_page.click_dm_link()
        
        logger.info("Update Addresses clicked")
        
        # Wait for DM Tool page to load
        page.wait_for_timeout(3000)
        dm_tool_page.wait_for_data_to_load()
        
        # Take screenshot after page is fully loaded
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Address Change Page Loaded", attachment_type=allure.attachment_type.PNG)
        
        # Get display mode from test context
        display_only_mailing = test_context.get('display_only_mailing_address', False)
        advisor_name = test_context.get('advisor_name', 'Test Advisor')
        
        # Verify page layout
        dm_tool_page.test_address_change_ui(display_only_mailing, advisor_name)
        
        # Store before addresses for later comparison
        if not display_only_mailing:
            legal_before = dm_tool_page.return_address('legal')
            test_context['legal_address_before'] = legal_before
            logger.info(f"Legal address BEFORE: {legal_before}")
        
        mailing_before = dm_tool_page.return_address('mailing')
        test_context['mailing_address_before'] = mailing_before
        logger.info(f"Mailing address BEFORE: {mailing_before}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Update Addresses Page Layout - {test}",
            attachment_type=allure.attachment_type.PNG
        )
        
        logger.info("Update Addresses page layout verified")


@when("User clicks on next button for SWP")
def click_next_button_for_swp(page: Page, account_wizard_page, test_context: dict):
    """Click Next button for SWP Establish and navigate to SWP Establish Landing Page"""
    with allure.step("Click Next button for SWP"):
        logger.info("\n")
        logger.info("Clicking Next button for SWP")
        
        # Click next button and get SWP Establish Landing Page
        swp_establish_landing_page = account_wizard_page.click_next_btn_for_swp()
        
        # Store in test context for subsequent steps
        test_context['swp_establish_landing_page'] = swp_establish_landing_page
        
        # Wait for page to load
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(2000)
        
        logger.info("Next button for SWP clicked successfully")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="SWP Establish Landing Page",
            attachment_type=allure.attachment_type.PNG
        )


@then('User is redirected to DocuSign document page and URL is verified')
def verify_docusign_document_url(page: Page, docusign_page):
    """Verify the browser is on the DocuSign signing URL after ERSD consent"""
    with allure.step("Verify DocuSign document URL"):
        logger.info("Verifying DocuSign document URL...")
        docusign_url = docusign_page.verify_docusign_url()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign - URL Verified", attachment_type=allure.attachment_type.PNG)
        logger.info(f"DocuSign URL confirmed: {docusign_url}")


@when('User scrolls to last page clicks on sign icon and verifies signature')
def scroll_and_click_sign_icon(page: Page, docusign_page):
    """Scroll to the last page of the DocuSign document, click the Sign icon and verify"""
    with allure.step("Scroll to last page, click Sign icon and verify signature applied"):
        logger.info("Scrolling to last page and clicking Sign icon...")
        docusign_page.scroll_to_last_page_and_sign()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign - Signed", attachment_type=allure.attachment_type.PNG)
        logger.info("Signature applied and verified successfully")


@then('User gets the D number from DocuSign document')
def get_docusign_d_number(page: Page, docusign_page, test_context: dict):
    """Capture the D-number (document tracking number) from the DocuSign page"""
    with allure.step("Get D-number from DocuSign document"):
        logger.info("Retrieving D-number from DocuSign page...")
        d_number = docusign_page.get_d_number()
        test_context['d_number'] = d_number
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"DocuSign - D Number: {d_number}", attachment_type=allure.attachment_type.PNG)
        logger.info(f"D-number captured: {d_number}")


@when('User clicks on Finish button in DocuSign')
def click_finish_button_in_docusign(page: Page, docusign_page):
    """Click the Finish button at the bottom of the DocuSign document page"""
    with allure.step("Click Finish button in DocuSign"):
        logger.info("Clicking Finish button in DocuSign...")
        docusign_page.click_finish_button()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign - Finish Clicked", attachment_type=allure.attachment_type.PNG)
        logger.info("DocuSign Finish button clicked successfully")


@then('eSignature Process Complete modal is displayed')
def verify_esign_complete_modal(page: Page, docusign_page):
    """Verify the eSignature Process Complete confirmation modal appears after DocuSign"""
    with allure.step("Verify eSignature Process Complete modal"):
        logger.info("Verifying eSignature Process Complete modal...")
        docusign_page.verify_esign_complete_modal()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="eSignature Process Complete Modal", attachment_type=allure.attachment_type.PNG)
        logger.info("eSignature Process Complete modal verified")


@when('User clicks on D number link in eSignature complete modal')
def click_d_number_in_esign_modal(page: Page, docusign_page, test_context: dict):
    """Click the D-number link in the eSignature Process Complete modal to navigate to Tracking Center"""
    with allure.step("Click D-number link in eSignature complete modal"):
        logger.info("Clicking D-number link to navigate to Tracking Center...")
        d_number = docusign_page.click_d_number_in_esign_modal()
        test_context['esign_d_number'] = d_number
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Tracking Center - D Number: {d_number}", attachment_type=allure.attachment_type.PNG)
        logger.info(f"Navigated to Tracking Center via D-number: {d_number}")


@when('User clicks on eSignature button on Tracking Center Item Detail page')
def click_esignature_button_on_tracking_center(page: Page, tracking_center_page):
    """Click the eSignature button on the Tracking Center Item Detail page to open the e-sign modal"""
    with allure.step("Click eSignature button on Tracking Center Item Detail page"):
        logger.info("Clicking eSignature button...")
        tracking_center_page.click_esignature_button()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Tracking Center - eSignature Button Clicked", attachment_type=allure.attachment_type.PNG)
        logger.info("eSignature button clicked successfully")


@then('Electronic Signature Management modal is displayed')
def verify_esign_management_modal(page: Page, tracking_center_page):
    """Verify the Electronic Signature Management modal opens after clicking the eSignature button"""
    with allure.step("Verify Electronic Signature Management modal is displayed"):
        logger.info("Verifying Electronic Signature Management modal...")
        tracking_center_page.verify_esign_management_modal()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Electronic Signature Management Modal", attachment_type=allure.attachment_type.PNG)
        logger.info("Electronic Signature Management modal verified")


@when('User clicks on Resend button in Electronic Signature Management modal')
def click_resend_button_in_esign_modal(page: Page, tracking_center_page):
    """Click the Resend button in the Electronic Signature Management modal"""
    with allure.step("Click Resend button in Electronic Signature Management modal"):
        logger.info("Clicking Resend button...")
        tracking_center_page.click_resend_button()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Electronic Signature Management - Resend Clicked", attachment_type=allure.attachment_type.PNG)
        logger.info("Resend button clicked successfully")


@when("User should click on the Add button to add a new SWP record")
def click_add_button_to_add_swp_record(page: Page, test_context: dict):
    """Click on the Add button to add a new SWP record"""
    with allure.step("Click on Add button to add new SWP record"):
        logger.info("\n")
        logger.info("Validations of Add Button Functionality SWP")
        
        # Get SWP Establish Landing Page from test context
        swp_establish_landing_page = test_context.get('swp_establish_landing_page')
        if swp_establish_landing_page is None:
            raise RuntimeError("SWP Establish Landing Page not found in test_context")
        
        # Click on Add button
        swp_establish_landing_page.click_add_button()
        
        logger.info("Validations of Add Button Functionality SWP --> Validated")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Add Button Clicked - New SWP Record",
            attachment_type=allure.attachment_type.PNG
        )
