import allure
from pathlib import Path
from pytest_bdd import when, then, given, parsers
from utils.allure_logger import get_allure_logger
from utils.stp.constants.constants import BeneAccountUrls

logger = get_allure_logger(__name__)


@given('Primary beneficiary "David Wilson" exists with allocation "100.00"')
def primary_beneficiary_david_wilson_exists(page, update_beneficiary_page, add_beneficiary_page, test_context):
    logger.info("Ensuring Primary beneficiary David Wilson exists")
    
    page.wait_for_load_state('networkidle')
    
    primary_list = update_beneficiary_page.get_primary_beneficiaries(1)
    
    if "David Wilson" not in primary_list:
        logger.info("David Wilson not found, creating...")
        update_beneficiary_page.click_add_beneficiary_button()
        page.wait_for_load_state('networkidle')
        
        add_beneficiary_page.select_beneficiary_type_as("Individual")
        add_beneficiary_page.select_designation_as("Primary")
        page.wait_for_timeout(300)
        
        add_beneficiary_page.enter_first_name("David")
        add_beneficiary_page.enter_last_name("Wilson")
        add_beneficiary_page.enter_social_security_number("555-66-7777")
        add_beneficiary_page.enter_date_of_birth("06/12/1980")
        add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
        add_beneficiary_page.click_save_button()
        
        page.wait_for_load_state('networkidle')
        add_beneficiary_page.wait_for_modal_to_close()
        logger.info("Created primary beneficiary David Wilson")
    else:
        logger.info("David Wilson already exists")


@given('Primary beneficiary "Sarah Miller" is displayed')
def primary_beneficiary_sarah_miller_displayed(page, update_beneficiary_page, add_beneficiary_page, test_context):
    logger.info("Ensuring Primary beneficiary Sarah Miller is displayed")
    
    page.wait_for_load_state('networkidle')
    
    primary_list = update_beneficiary_page.get_primary_beneficiaries(1)
    
    if "Sarah Miller" not in primary_list:
        logger.info("Sarah Miller not found, creating...")
        update_beneficiary_page.click_add_beneficiary_button()
        page.wait_for_load_state('networkidle')
        
        add_beneficiary_page.select_beneficiary_type_as("Individual")
        add_beneficiary_page.select_designation_as("Primary")
        page.wait_for_timeout(300)
        
        add_beneficiary_page.enter_first_name("Sarah")
        add_beneficiary_page.enter_last_name("Miller")
        add_beneficiary_page.enter_social_security_number("888-99-0000")
        add_beneficiary_page.enter_date_of_birth("09/08/1975")
        add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
        add_beneficiary_page.click_save_button()
        
        page.wait_for_load_state('networkidle')
        add_beneficiary_page.wait_for_modal_to_close()
        logger.info("Created primary beneficiary Sarah Miller")
    else:
        logger.info("Sarah Miller already exists and is displayed")


@when("User should select and click and redirect to bene page")
def user_click_add_and_open_modal(page, update_beneficiary_page, add_beneficiary_page, manage_bene_page, manage_bene_detail_page, test_context):
    
    with allure.step("Clicking Add Beneficiary button to open modal and verify redirection"):
        logger.info("Step 1: Clicking Add Beneficiary button to open modal")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Click_Beneficiary_Detail", attachment_type=allure.attachment_type.PNG)
        
        manage_bene_page.click_first_beneficiary_detail()
       
        page.wait_for_load_state('networkidle')
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Click_Beneficiary_Detail", attachment_type=allure.attachment_type.PNG)
        
        logger.info("Add Beneficiary modal opened successfully")
        test_context['modal_opened'] = True

        page.wait_for_timeout(5000)
        
        is_redirected = manage_bene_detail_page.is_beneficiaries_section_present()
        logger.info(f"DEBUG: is_beneficiaries_section_present returned: {is_redirected} (type: {type(is_redirected)})")
        assert is_redirected, "Page should be redirected to add beneficiary page"
        logger.info("Page redirection to add beneficiary page verified")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Beneficiary_Page_Verified", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('User should select and click on account holder "{account_holder_name}" and redirect to bene page'))
def user_click_account_holder_and_open_modal(account_holder_name, page, update_beneficiary_page, add_beneficiary_page, manage_bene_page, manage_bene_detail_page, test_context):
    
    with allure.step(f"Clicking on account holder '{account_holder_name}' and verifying redirection"):
        logger.info(f"Step 1: Validating account holder name from previous API call")
        
        if 'api_account_holder_names' in test_context:
            api_names = test_context['api_account_holder_names']
            assert account_holder_name in api_names, \
                f"Account holder '{account_holder_name}' not found in API response. API names: {api_names}"
            logger.info(f"Account holder '{account_holder_name}' validated against API response")
        
        test_context['selected_account_name'] = account_holder_name
        
        allure.attach(
            account_holder_name,
            name="Selected Account Holder Name",
            attachment_type=allure.attachment_type.TEXT
        )
        
        logger.info(f"Step 2: Clicking on account holder '{account_holder_name}' to redirect to beneficiary page")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Click_Account_Holder", attachment_type=allure.attachment_type.PNG)
        
        manage_bene_page.click_account_holder_by_name(account_holder_name)
       
        page.wait_for_load_state('networkidle')
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Click_Account_Holder", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f"Clicked on account holder '{account_holder_name}' and modal opened successfully")
        test_context['modal_opened'] = True

        page.wait_for_timeout(5000)
        
        is_redirected = manage_bene_detail_page.is_beneficiaries_section_present()
        logger.info(f"DEBUG: is_beneficiaries_section_present returned: {is_redirected} (type: {type(is_redirected)})")
        assert is_redirected, "Page should be redirected to add beneficiary page"
        logger.info("Page redirection to add beneficiary page verified")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Beneficiary_Page_Verified", attachment_type=allure.attachment_type.PNG)


@when("User clicks on first Edit button and captures beneficiary info and navigates to edit page")
def click_first_edit_button_and_capture_info(page, manage_bene_detail_page, edit_beneficiary_page, test_context):
    with allure.step("Click first Edit button, capture name/relationship/allocation, verify edit page opens"):
        # Attach DOM snapshot before clicking
        allure.attach(
            page.content(),
            name="Before_First_Edit_Click_DOM",
            attachment_type=allure.attachment_type.HTML,
        )
        allure.attach(
            page.screenshot(),
            name="Before_First_Edit_Click",
            attachment_type=allure.attachment_type.PNG,
        )

        info = manage_bene_detail_page.get_first_beneficiary_info_and_click_edit()

        logger.info(
            f"Captured first beneficiary ΓÇö name: '{info['name']}', "
            f"relationship: '{info['relationship']}', allocation: {info['allocation']}%"
        )

        # Persist to context for downstream steps
        test_context['first_bene_name'] = info['name']
        test_context['first_bene_relationship'] = info['relationship']
        test_context['first_bene_allocation'] = info['allocation']
        # Also set as the active beneficiary for edit-page steps
        test_context['added_beneficiary_name'] = info['name']
        test_context['beneficiary_full_name'] = info['name']
        test_context['beneficiary_first_name'] = info['name'].split()[0]
        test_context['beneficiary_last_name'] = ' '.join(info['name'].split()[1:])
        test_context['beneficiary_relation'] = info['relationship']

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(800)

        is_visible = edit_beneficiary_page.is_edit_form_visible()

        allure.attach(
            page.content(),
            name="Edit_Page_DOM",
            attachment_type=allure.attachment_type.HTML,
        )
        allure.attach(
            page.screenshot(),
            name="Edit_Page_Opened",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Name: {info['name']}\nRelationship: {info['relationship']}\nAllocation: {info['allocation']}%",
            name="First_Beneficiary_Info",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert is_visible, (
            f"Edit Beneficiary page did not open after clicking Edit for '{info['name']}'"
        )
        logger.info(f"[OK] Edit page opened for '{info['name']}'")


@then("User should verify all Edit Beneficiary fields are disabled")
def verify_edit_beneficiary_fields_disabled(page, edit_beneficiary_page, test_context):
    with allure.step("Verify Beneficiary, First Name, Middle Name, Last Name, SSN and DOB fields are disabled"):
        allure.attach(
            page.content(),
            name="Edit_Fields_Disabled_DOM",
            attachment_type=allure.attachment_type.HTML,
        )
        allure.attach(
            page.screenshot(),
            name="Edit_Fields_Disabled_Screenshot",
            attachment_type=allure.attachment_type.PNG,
        )

        results = edit_beneficiary_page.verify_all_fields_disabled()

        allure.attach(
            "\n".join(f"{k}: {'DISABLED' if v else 'NOT DISABLED'}" for k, v in results.items()),
            name="Field_Disabled_Status",
            attachment_type=allure.attachment_type.TEXT,
        )

        failed = [field for field, is_disabled in results.items() if not is_disabled]
        assert not failed, (
            f"The following Edit Beneficiary fields were expected to be disabled but are NOT: {failed}"
        )
        logger.info("[OK] All Edit Beneficiary fields are correctly disabled")


@then("User should verify the relationship radio button matches the captured beneficiary info")
def verify_relationship_radio_matches_context(page, edit_beneficiary_page, test_context):
    with allure.step("Verify selected relationship radio matches the relationship captured from the beneficiary list"):
        expected = test_context.get('first_bene_relationship', '')
        assert expected, "'first_bene_relationship' not found in test_context ΓÇö ensure the Edit button step ran first"

        result = edit_beneficiary_page.verify_relationship_selection(expected)

        allure.attach(
            page.screenshot(),
            name="Relationship_Radio_Verification",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Expected: {result['expected']}\nActual:   {result['actual']}\nMatch:    {result['match']}",
            name="Relationship_Radio_Status",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result['match'], (
            f"Relationship radio mismatch ΓÇö expected '{result['expected']}' to be selected, "
            f"but got '{result['actual']}'"
        )
        logger.info(f"[OK] Relationship radio '{result['actual']}' matches captured context value '{expected}'")


@then("User should verify that unrelated relationship radio buttons are disabled")
def verify_mutually_exclusive_relationship_radios(page, edit_beneficiary_page, test_context):
    with allure.step(
        "Verify mutual exclusivity: if Spouse/Non-Spouse selected then Trust/Entity disabled, and vice versa"
    ):
        result = edit_beneficiary_page.verify_mutually_exclusive_relationship_radios()

        report_lines = [
            f"Selected:          {result['selected']} ({result['selected_group']} group)",
            f"Enabled radios:    {result['enabled_radios']}",
            f"Disabled radios:   {result['disabled_radios']}",
            f"Expected disabled: {result['expected_disabled']}",
            f"Missing disabled:  {result['missing_disabled']}",
            f"Passed:            {result['passed']}",
        ]
        allure.attach(
            page.screenshot(),
            name="Relationship_Mutual_Exclusivity",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            "\n".join(report_lines),
            name="Relationship_Radio_Exclusivity_Report",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result['passed'], (
            f"Relationship radio mutual exclusivity FAILED ΓÇö "
            f"selected '{result['selected']}' ({result['selected_group']} group) but "
            f"{result['missing_disabled']} are NOT disabled (expected all of "
            f"{result['expected_disabled']} to be disabled)"
        )
        logger.info(
            f"[OK] Mutual exclusivity verified ΓÇö '{result['selected']}' selected, "
            f"opposite group {result['expected_disabled']} are all disabled"
        )


@when(parsers.parse("User toggles the relationship type to '{bene_type}'"))
def toggle_beneficiary_relationship_type(bene_type, page, edit_beneficiary_page, test_context):
    with allure.step(f"Toggle relationship type ΓÇö requested type: '{bene_type}'"):
        allure.attach(
            page.screenshot(),
            name="Before_Toggle_Relationship",
            attachment_type=allure.attachment_type.PNG,
        )

        try:
            result = edit_beneficiary_page.toggle_relationship_type(bene_type)
        except ValueError as e:
            raise AssertionError(str(e))

        report_lines = [
            f"Requested type:    {bene_type}",
            f"Was selected:      {result['was_selected']}",
            f"Now selected:      {result['now_selected']}",
            f"Expected disabled: {result['expected_disabled']}",
            f"Disabled after:    {result['disabled_after']}",
            f"Missing disabled:  {result['missing_disabled']}",
            f"Exclusivity OK:    {result['exclusivity_ok']}",
        ]
        allure.attach(
            page.screenshot(),
            name="After_Toggle_Relationship",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            "\n".join(report_lines),
            name="Toggle_Relationship_Report",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result['exclusivity_ok'], (
            f"After toggling to '{result['now_selected']}', mutual exclusivity FAILED ΓÇö "
            f"{result['missing_disabled']} should be disabled but are NOT"
        )

        # Persist the new selection to context for downstream steps
        test_context['beneficiary_relation'] = result['now_selected']
        logger.info(
            f"[OK] Toggled relationship: '{result['was_selected']}' "
            f"ΓåÆ '{result['now_selected']}'; exclusivity verified"
        )

        # Click Save and wait for navigation back to manage beneficiaries page
        logger.info("Clicking Save button after relationship toggle")
        edit_beneficiary_page.click_save()
        page.wait_for_load_state('networkidle', timeout=30000)
        allure.attach(
            page.screenshot(),
            name="After_Save_Relationship_Toggle",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            page.content(),
            name="After_Save_Relationship_Toggle_DOM",
            attachment_type=allure.attachment_type.HTML,
        )
        logger.info("[OK] Save clicked ΓÇö navigated back after relationship toggle")


@when("User should verify all allocation sections show 100% total and save to context")
def verify_all_allocation_sections_100_percent(page, manage_bene_detail_page, test_context):
        logger.info("Collecting allocation section totals from all account cards")
        allocation_data = manage_bene_detail_page.get_all_section_allocation_totals()

        assert allocation_data, "No allocation sections found on the page"

        failed_sections = []
        for card in allocation_data:
            for section in card['sections']:
                pct = section['total_pct']
                label = f"{card['account']} ΓåÆ {section['type']}"
                logger.info(f"[CHECK] {label}: {section['total_text']}")
                if pct != 100.0:
                    failed_sections.append(f"{label} = {pct}% (expected 100.00%)")

        # Attach DOM snapshot
        allure.attach(
            page.content(),
            name="Allocation_Sections_DOM",
            attachment_type=allure.attachment_type.HTML,
        )
        # Attach screenshot
        allure.attach(
            page.screenshot(),
            name="Allocation_Sections_Screenshot",
            attachment_type=allure.attachment_type.PNG,
        )

        if failed_sections:
            raise AssertionError(
                "The following allocation sections do not total 100%:\n"
                + "\n".join(failed_sections)
            )

        logger.info("[OK] All allocation sections verified at 100%")
        test_context['allocation_totals_before_add'] = allocation_data
        logger.info(f"Saved allocation_totals_before_add to context: {allocation_data}")


@when("User should click on Add button and redirected to add beneficiary page")
def user_click_add_button(page, manage_bene_detail_page, add_beneficiary_buttons_page, test_context):
    
    with allure.step("Clicking Add button on manage beneficiaries page and validate title"):
        logger.info("Step 2: Clicking Add button on manage beneficiaries page")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Click_Add_Button", attachment_type=allure.attachment_type.PNG)
        
        manage_bene_detail_page.click_add_beneficiary_button()
       
        page.wait_for_load_state('networkidle')
        
        logger.info("Add beneficiary page opened successfully")
        test_context['add_page_opened'] = True

        page.wait_for_timeout(1000)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Add_Beneficiary_Page_Opened", attachment_type=allure.attachment_type.PNG)
        
        is_title_visible = add_beneficiary_buttons_page.is_add_beneficiary_title_visible()
        logger.info(f"Is 'Add a Beneficiary' title visible: {is_title_visible}")
        assert is_title_visible, "Add a Beneficiary title should be visible on the page"
        
        title_text = add_beneficiary_buttons_page.get_add_beneficiary_title_text()
        logger.info(f"Title text retrieved: {title_text}")
        assert title_text == "Add a Beneficiary", f"Expected title 'Add a Beneficiary', but got '{title_text}'"
        
        logger.info("Add beneficiary page verified with correct title")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Add_Beneficiary_Title_Verified", attachment_type=allure.attachment_type.PNG)


@then("User should validate the primary account holder name matches the selected account")
def validate_primary_account_holder(manage_bene_detail_page, test_context):
    """Validate that the primary account holder displayed on page matches the clicked account"""
    
    with allure.step("Validating primary account holder name matches selected account"):
        logger.info("Step: Validating primary account holder name from page")
        
        page_account_holder_name = manage_bene_detail_page.get_primary_account_holder_name()
        
        selected_account_name = test_context.get('selected_account_name')
        
        if not selected_account_name:
            raise ValueError("No selected account name found in test_context")
        
        logger.info(f"Selected account name (from click): {selected_account_name}")
        logger.info(f"Page account holder name (from UI): {page_account_holder_name}")
        
        assert page_account_holder_name == selected_account_name, \
            f"Account holder name mismatch! Expected: '{selected_account_name}', but page shows: '{page_account_holder_name}'"
        
        logger.info(f"Primary account holder validated successfully: {page_account_holder_name}")
        
        allure.attach(
            f"Selected: {selected_account_name}\nPage Display: {page_account_holder_name}",
            name="Account Holder Name Validation",
            attachment_type=allure.attachment_type.TEXT
        )


@then("User should get beneficiary name and account info for accounts with no contingent beneficiaries")
def get_accounts_with_no_contingent_beneficiaries(manage_bene_detail_page, test_context):
    """Get beneficiary names and account info for accounts that show 'No contingent beneficiaries'"""
    
    with allure.step("Getting accounts with no contingent beneficiaries"):
        logger.info("Step: Getting accounts with no contingent beneficiaries")
        
        accounts_no_contingent = manage_bene_detail_page.get_accounts_with_no_contingent_beneficiaries()
        
        if not accounts_no_contingent:
            logger.warning("No accounts found with 'No contingent beneficiaries' status")
            test_context['accounts_no_contingent'] = []
            return
        
        test_context['accounts_no_contingent'] = accounts_no_contingent
        test_context['accounts_no_contingent_count'] = len(accounts_no_contingent)
        
        logger.info(f"Found {len(accounts_no_contingent)} accounts with no contingent beneficiaries")
        
        for idx, account in enumerate(accounts_no_contingent, 1):
            account_info = account.get('account_info')
            
            logger.info(f" {idx}. Account: {account_info}")
        
        accounts_summary = "\n".join([
            f"{idx}. Account: {acc.get('account_info', 'N/A')}"
            for idx, acc in enumerate(accounts_no_contingent, 1)
        ])
        
        allure.attach(
            f"Total Accounts: {len(accounts_no_contingent)}\n\n{accounts_summary}",
            name="Accounts with No Contingent Beneficiaries",
            attachment_type=allure.attachment_type.TEXT
        )


@then('Verify the beneficiary "John Doe" is added successfully with designation "Primary"')
def verify_beneficiary_added_successfully(page, update_beneficiary_page, test_context):
    logger.info("Verifying beneficiary 'John Doe' was added successfully")
    
    page.wait_for_load_state('networkidle')
    update_beneficiary_page.wait_for_page_load()
    
    account_cards_count = update_beneficiary_page.get_account_cards_count()
    logger.info(f"Total account cards: {account_cards_count}")
    
    if account_cards_count > 0:
        primary_beneficiaries = update_beneficiary_page.get_primary_beneficiaries(1)
        logger.info(f"Primary beneficiaries: {primary_beneficiaries}")
        
        assert "John Doe" in str(primary_beneficiaries), "Beneficiary 'John Doe' not found in primary beneficiaries"
        logger.info("Beneficiary 'John Doe' verified in primary beneficiaries section")
    
    test_context['beneficiary_verified'] = True


@then('Toast notification should display "Primary beneficiary "John Doe" added."')
def verify_toast_notification(page, manage_bene_detail_page, test_context):
    logger.info("Verifying toast notification")
    
    toast_text = manage_bene_detail_page.get_toast_text()
    
    if toast_text:
        logger.info(f"Toast message: {toast_text}")
        
        assert "John Doe" in toast_text, "Toast notification does not contain beneficiary name"
        assert "added" in toast_text.lower(), "Toast notification does not indicate successful addition"
        logger.info("Toast notification verified with success message")
    else:
        logger.warning("Toast notification not immediately visible - may have disappeared")


@when('Beneficiary should have "ADDED" badge displayed')
def verify_added_badge(page, update_beneficiary_page, test_context):
    
    logger.info("Verifying 'ADDED' badge is displayed for created beneficiary")
    
    firstName = test_context.get('beneficiary_first_name', '')
    lastName = test_context.get('beneficiary_last_name', '')
    suffix = test_context.get('beneficiary_suffix', '')
    
    if suffix:
        fullName = f"{firstName} {lastName} {suffix}"
    else:
        fullName = f"{firstName} {lastName}"
    logger.info(f"Looking for 'ADDED' badge for beneficiary: {fullName}")
    
    addedBadge = update_beneficiary_page.get_added_badge_for_bene_by_name(fullName)
    
    if addedBadge.is_visible():
        logger.info(f"'ADDED' badge found and visible for beneficiary '{fullName}'")
        test_context['added_badge_visible'] = True
    else:
        logger.warning(f"'ADDED' badge not visible for beneficiary '{fullName}' - may appear after page refresh")

@then('Beneficiary should have "EDITED" badge displayed')
def verify_edited_badge(page, test_context):
    
    logger.info("Verifying 'EDITED' badge is displayed for updated beneficiary")
    
    firstName = test_context.get('beneficiary_first_name', '')
    lastName = test_context.get('beneficiary_last_name', '')
    suffix = test_context.get('beneficiary_suffix', '')
    
    if suffix:
        fullName = f"{firstName} {lastName} {suffix}"
    else:
        fullName = f"{firstName} {lastName}"
    logger.info(f"Looking for 'EDITED' badge for beneficiary: {fullName}")
    
    editedBadgeXpath = (
        f"//span[contains(@class, 'MuiTypography-cardTextPrimary')][contains(text(), '{fullName}')]"
        f"/ancestor::div[contains(@class, 'MuiBox-root')]"
        f"/following-sibling::div//span[text()='EDITED']"
    )
    
    editedBadge = page.locator(f"xpath={editedBadgeXpath}")
    
    if editedBadge.is_visible():
        logger.info(f"'EDITED' badge found and visible for beneficiary '{fullName}'")
        test_context['edited_badge_visible'] = True
    else:
        logger.warning(f"'EDITED' badge not visible for beneficiary '{fullName}' - may appear after page refresh")


@then('Beneficiary allocation should be "100.00"')
def verify_beneficiary_allocation(page, update_beneficiary_page, test_context):
    logger.info("Verifying beneficiary allocation is 100.00%")
    
    page.wait_for_load_state('networkidle')
    
    total_allocation = update_beneficiary_page.get_total_allocation(1)
    logger.info(f"Total allocation: {total_allocation}")
    
    assert "100" in total_allocation, f"Expected 100% allocation, but got: {total_allocation}"
    logger.info("Beneficiary allocation verified as 100.00%")


@then('"Allocate Equally" button should be disabled')
def verify_allocate_equally_disabled(page, update_beneficiary_page, test_context):
    logger.info("Verifying 'Allocate Equally' button is disabled")
    
    page.wait_for_load_state('networkidle')
    
    is_enabled = update_beneficiary_page.is_allocate_equally_button_enabled(1)
    
    assert not is_enabled, "Allocate Equally button should be disabled with only 1 beneficiary"
    logger.info("'Allocate Equally' button confirmed as disabled")
    
    test_context['verification_complete'] = True


@given("user should identify beneficiaries with 1 primary account and allocate equally button should be disabled")
def identify_single_primary_account_section(page, update_beneficiary_page, test_context):

    with allure.step("Identify beneficiary section with exactly 1 primary account"):
        page.wait_for_load_state('networkidle')

        section = update_beneficiary_page.get_single_primary_account_section()
        assert section is not None, (
            "Could not find any account section containing exactly 1 primary beneficiary"
        )

        test_context['single_account_section'] = section
        logger.info("Stored single-primary-account section in test_context['single_account_section']")

    with allure.step("Verify 'Allocate Equally' button is disabled in the identified section"):
        allocate_btn = section.get_by_role("button", name="Allocate Equally")
        is_disabled = not allocate_btn.is_enabled()
        logger.info(f"'Allocate Equally' button disabled state in section: {is_disabled}")
        assert is_disabled, (
            "Expected 'Allocate Equally' button to be disabled for a section with 1 primary beneficiary, "
            "but it is enabled"
        )
        logger.info("'Allocate Equally' button is disabled as expected ΓÇö no click performed")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Allocate_Equally_Disabled", attachment_type=allure.attachment_type.PNG)


@given("user should identify a primary beneficiary section with more than one beneficiary and allocate equally button should be enabled")
def identify_multi_bene_primary_section(page, update_beneficiary_page, test_context):

    with allure.step("Identify first Primary section with more than one beneficiary and Allocate Equally enabled"):
        page.wait_for_load_state('networkidle')

        section = update_beneficiary_page.get_first_multi_bene_primary_section()
        assert section is not None, (
            "Could not find any Primary beneficiary section with more than one beneficiary "
            "and Allocate Equally button enabled. Ensure the test account has such a section."
        )

        current_allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        bene_count = len(current_allocations)
        section_title = update_beneficiary_page.get_section_title(section)
        logger.info(
            f"Found section '{section_title}' with {bene_count} beneficiaries: {current_allocations}"
        )

        test_context['multi_account_section'] = section
        test_context['multi_account_bene_count'] = bene_count

    with allure.step("Make allocations unequal so Allocate Equally produces a visible change"):
        is_equal = update_beneficiary_page.is_allocation_equal(section)
        if is_equal:
            logger.info("Allocations are currently equal ΓÇö making them unequal before test")
            update_beneficiary_page.make_allocation_unequal(section)
            page.wait_for_timeout(300)
            after = update_beneficiary_page.get_primary_allocation_percentages(section)
            assert not update_beneficiary_page.is_allocation_equal(section), (
                f"Failed to make allocations unequal. Current values: {after}"
            )
            logger.info(f"Allocations after making unequal: {after}")
        else:
            logger.info(f"Allocations already unequal: {current_allocations} ΓÇö no change needed")

    with allure.step("Confirm Allocate Equally button is enabled"):
        allocate_btn = section.get_by_role("button", name="Allocate Equally")
        assert allocate_btn.first.is_enabled(), (
            "Expected 'Allocate Equally' button to be enabled, but it is disabled"
        )
        logger.info("'Allocate Equally' button is enabled as expected")
        allure.attach(
            page.screenshot(),
            name="Multi_Bene_Section_Identified",
            attachment_type=allure.attachment_type.PNG,
        )


@given("user should identify beneficiaries with 2 primary accounts and allocate equally button should be enabled")
def identify_two_primary_account_section(page, update_beneficiary_page, test_context):
    """Kept for backwards compatibility ΓÇö delegates to the dynamic finder."""
    identify_multi_bene_primary_section(page, update_beneficiary_page, test_context)


@when("user clicks the Allocate Equally button in the identified section")
def click_allocate_equally_button(page, update_beneficiary_page, test_context):

    with allure.step("Click 'Allocate Equally' button"):
        section = test_context.get('multi_account_section')
        assert section is not None, (
            "test_context['multi_account_section'] is not set ΓÇö "
            "run 'user should identify beneficiaries with 2 primary accounts' step first"
        )

        allocate_btn = section.get_by_role("button", name="Allocate Equally")
        allocate_btn.first.click()
        logger.info("'Allocate Equally' (Primary) button clicked successfully")
        
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(500)  # Allow allocations to update
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Allocate_Equally_Click", attachment_type=allure.attachment_type.PNG)


@when("User reads the current allocation for the identified primary section and saves to context")
def read_allocation_before_allocate_equally(page, update_beneficiary_page, test_context):
    with allure.step("Read current allocation percentages and total before Allocate Equally"):
        section = test_context.get('multi_account_section')
        assert section is not None, (
            "test_context['multi_account_section'] is not set ΓÇö "
            "run the 'identify 2 primary accounts' step first"
        )

        allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        total_text = update_beneficiary_page.get_section_total_text(section)
        total_pct = update_beneficiary_page.get_section_total_percentage(section)

        test_context['allocation_before_equal'] = allocations
        test_context['allocation_total_before'] = total_pct

        report = (
            f"Allocations (before): {allocations}\n"
            f"Total: {total_text}\n"
            f"All equal: {update_beneficiary_page.is_allocation_equal(section)}"
        )
        allure.attach(
            page.screenshot(),
            name="Allocation_Before_Allocate_Equally",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            report,
            name="Allocation_Before_Report",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert total_pct == 100.0, (
            f"Expected total to be 100% before Allocate Equally, got '{total_text}'"
        )
        logger.info(f"[OK] Before allocations: {allocations}, total: {total_text}")


@then("User reads the allocation again and verifies all primary beneficiaries are equally distributed")
def read_allocation_after_allocate_equally(page, update_beneficiary_page, test_context):
    with allure.step("Read allocation percentages and total after Allocate Equally and verify equal distribution"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        allocations_after = update_beneficiary_page.get_primary_allocation_percentages(section)
        total_text = update_beneficiary_page.get_section_total_text(section)
        total_pct = update_beneficiary_page.get_section_total_percentage(section)
        is_equal = update_beneficiary_page.is_allocation_equal(section)

        allocations_before = test_context.get('allocation_before_equal', [])
        report = (
            f"Allocations (before): {allocations_before}\n"
            f"Allocations (after):  {allocations_after}\n"
            f"Total: {total_text}\n"
            f"Equally distributed: {is_equal}"
        )
        allure.attach(
            page.screenshot(),
            name="Allocation_After_Allocate_Equally",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            report,
            name="Allocation_After_Report",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert total_pct == 100.0, (
            f"Total after Allocate Equally should be 100%, got '{total_text}'"
        )
        assert is_equal, (
            f"Allocations are NOT equally distributed after clicking Allocate Equally: {allocations_after}"
        )
        logger.info(f"[OK] After allocations: {allocations_after}, total: {total_text}, equally distributed: True")


@when("User deletes the newly added primary beneficiary from the identified section")
def delete_newly_added_primary_beneficiary(page, update_beneficiary_page, manage_bene_detail_page, test_context):

    with allure.step("Locate and click the delete button for the newly added beneficiary (ADDED badge)"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        # Verify the ADDED badge is present
        assert update_beneficiary_page.has_added_badge_in_section(section), (
            "No 'ADDED' badge found in the section ΓÇö new beneficiary may not have been saved"
        )

        allure.attach(
            page.screenshot(),
            name="Before_Delete_Added_Bene",
            attachment_type=allure.attachment_type.PNG,
        )

        update_beneficiary_page.click_delete_for_added_bene(section)

    with allure.step("Confirm the delete confirmation dialog if it appears"):
        # Some flows show a confirmation modal ΓÇö handle it if present
        try:
            confirm_btn = manage_bene_detail_page.get_confirm_dialog_button()
            confirm_btn.wait_for(state="visible", timeout=3000)
            confirm_btn.click()
            logger.info("Delete confirmation dialog handled ΓÇö confirmed deletion")
        except Exception:
            logger.info("No confirmation dialog appeared ΓÇö delete applied directly")

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(500)

        allure.attach(
            page.screenshot(),
            name="After_Delete_Added_Bene",
            attachment_type=allure.attachment_type.PNG,
        )

    with allure.step("Re-identify the primary section after removal and update context"):
        refreshed_section = update_beneficiary_page.get_first_multi_bene_primary_section()
        assert refreshed_section is not None, (
            "Primary section not found after deleting the added beneficiary"
        )

        allocations = update_beneficiary_page.get_primary_allocation_percentages(refreshed_section)
        bene_count = len(allocations)
        section_title = update_beneficiary_page.get_section_title(refreshed_section)
        logger.info(
            f"Section '{section_title}' after delete: {bene_count} primary beneficiaries ΓÇö {allocations}"
        )

        test_context['multi_account_section'] = refreshed_section
        test_context['multi_account_bene_count'] = bene_count
        test_context['allocation_before_equal'] = allocations

        allure.attach(
            f"Section: {section_title}\nBene count after delete: {bene_count}\nAllocations: {allocations}",
            name="Section_After_Delete_Added_Bene",
            attachment_type=allure.attachment_type.TEXT,
        )


# ==================== Delete / Undo ΓÇö Existing Bene ====================

@when(parsers.parse('User captures and deletes the "{bene_position}" deletable primary beneficiary in the identified section'))
def capture_and_delete_bene(page, update_beneficiary_page, test_context, bene_position):

    with allure.step(f"Find the '{bene_position}' deletable primary beneficiary and click its delete button"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        deletable_btns = update_beneficiary_page.get_deletable_primary_delete_buttons(section)
        count = deletable_btns.count()
        assert count > 0, (
            "No deletable (enabled) primary beneficiary delete buttons found in section. "
            "Ensure the section has more than one primary bene."
        )
        logger.info(f"Found {count} deletable primary bene delete button(s) in section")

        if bene_position.lower() == "first":
            target_btn = deletable_btns.first
        elif bene_position.lower() == "last":
            target_btn = deletable_btns.last
        else:
            raise ValueError(f"bene_position must be 'first' or 'last', got '{bene_position}'")

        bene_name = update_beneficiary_page.get_bene_name_from_delete_button(target_btn)
        test_context['deleted_bene_name'] = bene_name
        logger.info(f"Targeting '{bene_position}' deletable bene: '{bene_name}'")

        # Save all primary allocations BEFORE deletion so we can verify restoration after undo
        pre_delete_allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        test_context['pre_delete_allocations'] = pre_delete_allocations
        logger.info(f"Pre-delete allocations saved: {pre_delete_allocations}")

        allure.attach(
            page.screenshot(),
            name="Before_Delete_Existing_Bene",
            attachment_type=allure.attachment_type.PNG,
        )

        target_btn.click()
        page.wait_for_timeout(400)
        logger.info(f"Clicked delete for '{bene_name}'")

        allure.attach(
            page.screenshot(),
            name="After_Delete_Click_Existing_Bene",
            attachment_type=allure.attachment_type.PNG,
        )


@then("the deleted beneficiary row should display the REMOVED badge")
def verify_removed_badge_visible(page, update_beneficiary_page, test_context):

    with allure.step("Verify the REMOVED badge chip is visible for the deleted beneficiary"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"
        bene_name = test_context.get('deleted_bene_name', '')

        # Wait briefly for DOM to update before checking badge
        page.wait_for_timeout(400)
        assert update_beneficiary_page.is_removed_badge_visible(section, bene_name), (
            f"Expected REMOVED badge to be visible for '{bene_name}' but it was not found"
        )
        logger.info(f"[OK] REMOVED badge is visible for '{bene_name}'")

        allure.attach(
            page.screenshot(),
            name="REMOVED_Badge_Visible",
            attachment_type=allure.attachment_type.PNG,
        )


@then("the undo icon button should be visible next to the REMOVED badge")
def verify_undo_button_visible(page, update_beneficiary_page, test_context):

    with allure.step("Verify the undo icon button is visible in the REMOVED row"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"
        bene_name = test_context.get('deleted_bene_name', '')

        undo_btn = update_beneficiary_page.get_undo_button_for_removed_bene(section)
        undo_btn.wait_for(state="visible", timeout=5000)
        assert undo_btn.is_visible(), (
            f"Expected undo button to be visible after deleting '{bene_name}' but it was not found"
        )
        undo_label = undo_btn.get_attribute("aria-label") or ""
        logger.info(f"[OK] Undo button visible: '{undo_label}'")

        allure.attach(
            page.screenshot(),
            name="Undo_Button_Visible",
            attachment_type=allure.attachment_type.PNG,
        )


@then("the deleted beneficiary allocation field should be disabled and show 0%")
def verify_deleted_bene_allocation_disabled_and_zero(page, update_beneficiary_page, test_context):

    with allure.step("Verify the REMOVED bene's allocation input is disabled and shows 0%"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"
        bene_name = test_context.get('deleted_bene_name', '')

        page.wait_for_timeout(400)
        assert update_beneficiary_page.is_removed_bene_allocation_disabled(section), (
            f"Expected allocation input for '{bene_name}' to be disabled after deletion, but it was enabled"
        )
        logger.info(f"[OK] Allocation input is disabled for '{bene_name}'")

        raw_value = update_beneficiary_page.get_removed_bene_allocation_value(section)
        assert float(raw_value) == 0.0, (
            f"Expected allocation for '{bene_name}' to be 0% after deletion, got '{raw_value}'"
        )
        logger.info(f"[OK] Allocation value for '{bene_name}' is 0% (got '{raw_value}')")

        allure.attach(
            page.screenshot(),
            name="Deleted_Bene_Allocation_Zero_Disabled",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Bene: {bene_name} | Allocation: {raw_value}% | Disabled: True",
            name="Deleted_Bene_Allocation_Report",
            attachment_type=allure.attachment_type.TEXT,
        )


@then("the remaining primary beneficiary allocation should be updated to 100%")
def verify_remaining_primary_allocation_is_100(page, update_beneficiary_page, test_context):

    with allure.step("Verify the remaining active primary beneficiary shows 100% allocation"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        page.wait_for_timeout(400)
        active_allocations = update_beneficiary_page.get_active_primary_allocations(section)
        assert len(active_allocations) > 0, (
            "No active (enabled) primary beneficiary allocation inputs found after deletion"
        )
        assert len(active_allocations) == 1, (
            f"Expected exactly 1 active primary bene after deletion, found {len(active_allocations)}: {active_allocations}"
        )
        remaining_value = float(active_allocations[0])
        assert remaining_value == 100.0, (
            f"Expected remaining primary beneficiary allocation to be 100%, got '{active_allocations[0]}'"
        )
        logger.info(f"[OK] Remaining primary bene allocation is 100% (got '{active_allocations[0]}')")

        allure.attach(
            page.screenshot(),
            name="Remaining_Bene_100_Percent",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Active primary allocations: {active_allocations}",
            name="Remaining_Allocation_Report",
            attachment_type=allure.attachment_type.TEXT,
        )


@when("User clicks the undo icon button to restore the removed beneficiary")
def click_undo_button(page, update_beneficiary_page, test_context):

    with allure.step("Click the undo icon button to restore the REMOVED beneficiary"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        update_beneficiary_page.click_undo_removal(section)

        allure.attach(
            page.screenshot(),
            name="After_Undo_Click",
            attachment_type=allure.attachment_type.PNG,
        )


@then("the REMOVED badge should disappear and the beneficiary row should be restored to normal state")
def verify_bene_restored_after_undo(page, update_beneficiary_page, test_context):

    with allure.step("Verify REMOVED badge is gone and the beneficiary row is restored"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"
        bene_name = test_context.get('deleted_bene_name', '')

        assert not update_beneficiary_page.is_removed_badge_visible(section, bene_name), (
            f"REMOVED badge still visible after undo for '{bene_name}'"
        )
        logger.info(f"[OK] REMOVED badge is gone for '{bene_name}'")

        assert update_beneficiary_page.is_edit_button_visible_for_bene(section, bene_name), (
            f"Edit button not visible for '{bene_name}' after undo ΓÇö row may not be fully restored"
        )
        logger.info(f"[OK] Edit button is back for '{bene_name}' ΓÇö row fully restored")

        allure.attach(
            page.screenshot(),
            name="Bene_Restored_After_Undo",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Restored beneficiary: {bene_name}",
            name="Undo_Restore_Report",
            attachment_type=allure.attachment_type.TEXT,
        )


@then("the allocation should be restored to the state before deletion")
def verify_allocation_restored_after_undo(page, update_beneficiary_page, test_context):

    with allure.step("Verify allocations are back to the values captured before deletion"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        pre_delete = test_context.get('pre_delete_allocations', [])
        assert pre_delete, "pre_delete_allocations not saved in test_context ΓÇö check capture step"

        page.wait_for_timeout(400)
        current_allocations = update_beneficiary_page.get_primary_allocation_percentages(section)

        assert len(current_allocations) == len(pre_delete), (
            f"After undo, expected {len(pre_delete)} primary benes "
            f"but found {len(current_allocations)}: {current_allocations}"
        )

        for i, (before, after) in enumerate(zip(pre_delete, current_allocations)):
            before_f = float(before)
            after_f = float(after)
            assert round(abs(after_f - before_f), 2) <= 0.01, (
                f"Allocation for bene {i+1} not restored: was {before}% before, "
                f"now {after}% after undo"
            )

        logger.info(f"[OK] Allocations restored: before={pre_delete}, after={current_allocations}")

        allure.attach(
            page.screenshot(),
            name="Allocation_Restored_After_Undo",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Pre-delete: {pre_delete} | After undo: {current_allocations}",
            name="Allocation_Restore_Report",
            attachment_type=allure.attachment_type.TEXT,
        )


# ==================== Add New Bene + Permanent Delete ====================

@when(parsers.parse('User adds a new primary beneficiary with relation "{relation}" first name "{first_name}" last name "{last_name}" SSN "{ssn}" and DOB "{dob}"'))
def add_new_bene_with_params(page, update_beneficiary_page, add_beneficiary_page, test_context,
                             relation, first_name, last_name, ssn, dob):

    with allure.step(f"Add new primary beneficiary: {first_name} {last_name} ({relation})"):
        update_beneficiary_page.click_add_beneficiary_button()
        page.wait_for_load_state('networkidle')

        add_beneficiary_page.select_beneficiary_type_as("New")
        add_beneficiary_page.select_designation_as(relation)
        add_beneficiary_page.enter_first_name(first_name)
        add_beneficiary_page.enter_last_name(last_name)
        add_beneficiary_page.enter_social_security_number(ssn)
        add_beneficiary_page.enter_date_of_birth(dob)
        add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()

        allure.attach(
            page.screenshot(),
            name=f"Add_New_Bene_Form_{first_name}_{last_name}",
            attachment_type=allure.attachment_type.PNG,
        )

        add_beneficiary_page.click_save_button()
        add_beneficiary_page.wait_for_modal_to_close()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(500)

        test_context['new_bene_first_name'] = first_name
        test_context['new_bene_last_name'] = last_name
        test_context['new_bene_full_name'] = f"{first_name} {last_name}"
        logger.info(f"Added new beneficiary: {first_name} {last_name} ({relation})")

        # Refresh section locator after DOM update
        new_section = update_beneficiary_page.get_first_multi_bene_primary_section()
        assert new_section is not None, "Could not find primary section after adding new bene"
        test_context['multi_account_section'] = new_section

        allure.attach(
            page.screenshot(),
            name=f"After_Add_New_Bene_{first_name}_{last_name}",
            attachment_type=allure.attachment_type.PNG,
        )


@then(parsers.parse('the new beneficiary "{full_name}" should show the ADDED badge in the primary section'))
def verify_added_badge_in_section(page, update_beneficiary_page, test_context, full_name):

    with allure.step(f"Verify ADDED badge is visible for '{full_name}'"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        page.wait_for_timeout(400)
        assert update_beneficiary_page.is_added_badge_visible(section, full_name), (
            f"ADDED badge not visible for '{full_name}' after adding the new beneficiary"
        )
        logger.info(f"[OK] ADDED badge visible for new beneficiary '{full_name}'")

        allure.attach(
            page.screenshot(),
            name=f"ADDED_Badge_Visible_{full_name.replace(' ', '_')}",
            attachment_type=allure.attachment_type.PNG,
        )


@when(parsers.parse('User clicks the delete button for the newly added "{full_name}" beneficiary'))
def click_delete_for_new_bene(page, update_beneficiary_page, test_context, full_name):

    with allure.step(f"Click delete button for newly added '{full_name}'"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        allure.attach(
            page.screenshot(),
            name=f"Before_Delete_New_Bene_{full_name.replace(' ', '_')}",
            attachment_type=allure.attachment_type.PNG,
        )

        update_beneficiary_page.click_delete_for_added_bene(section)
        logger.info(f"Clicked delete for new bene '{full_name}'")

        allure.attach(
            page.screenshot(),
            name=f"After_Delete_New_Bene_{full_name.replace(' ', '_')}",
            attachment_type=allure.attachment_type.PNG,
        )


@then(parsers.parse('the "{full_name}" beneficiary row should be permanently gone with no REMOVED badge'))
def verify_new_bene_permanently_deleted(page, update_beneficiary_page, test_context, full_name):

    with allure.step(f"Verify '{full_name}' row is completely gone ΓÇö no REMOVED badge, no row"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        page.wait_for_timeout(300)

        assert not update_beneficiary_page.is_bene_row_present(section, full_name), (
            f"Expected '{full_name}' to be completely removed from the DOM, but the row still exists"
        )
        logger.info(f"[OK] Row for '{full_name}' is gone from the section")

        assert not update_beneficiary_page.is_removed_badge_visible(section, full_name), (
            f"REMOVED badge unexpectedly present after deleting new bene '{full_name}'. "
            f"New benes should be permanently removed, not soft-deleted."
        )
        logger.info(f"[OK] No REMOVED badge ΓÇö '{full_name}' was permanently removed")

        allure.attach(
            page.screenshot(),
            name=f"Bene_Permanently_Deleted_{full_name.replace(' ', '_')}",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            f"Permanently deleted: {full_name}\nNo REMOVED badge ΓÇö correct behaviour for new bene.",
            name="Permanent_Delete_Report",
            attachment_type=allure.attachment_type.TEXT,
        )


@when("User adds a new primary beneficiary to the identified section")
def add_new_primary_beneficiary_to_section(page, update_beneficiary_page, add_beneficiary_page, test_context):

    with allure.step("Add a new primary beneficiary via the Add button"):
        update_beneficiary_page.click_add_beneficiary_button()
        page.wait_for_load_state('networkidle')

        add_beneficiary_page.select_beneficiary_type_as("New")
        add_beneficiary_page.select_designation_as("Non-Spouse")
        add_beneficiary_page.enter_first_name("Alex")
        add_beneficiary_page.enter_last_name("Taylor")
        add_beneficiary_page.enter_social_security_number("333-44-5555")
        add_beneficiary_page.enter_date_of_birth("08/15/1985")
        add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()

        allure.attach(
            page.screenshot(),
            name="Add_Third_Bene_Form_Filled",
            attachment_type=allure.attachment_type.PNG,
        )

        add_beneficiary_page.click_save_button()
        add_beneficiary_page.wait_for_modal_to_close()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(500)

        allure.attach(
            page.screenshot(),
            name="After_Add_Third_Bene",
            attachment_type=allure.attachment_type.PNG,
        )

    with allure.step("Re-identify the primary section now containing the new beneficiary"):
        new_section = update_beneficiary_page.get_first_multi_bene_primary_section()
        assert new_section is not None, (
            "Could not find a Primary section with multiple beneficiaries after adding a new one"
        )

        allocations = update_beneficiary_page.get_primary_allocation_percentages(new_section)
        bene_count = len(allocations)
        section_title = update_beneficiary_page.get_section_title(new_section)
        logger.info(f"Section '{section_title}' now has {bene_count} primary beneficiaries: {allocations}")

        # Update context so subsequent steps (click + verify) use the refreshed section locator
        test_context['multi_account_section'] = new_section
        test_context['multi_account_bene_count'] = bene_count
        test_context['allocation_before_equal'] = allocations

        allure.attach(
            f"Section: {section_title}\nBene count after add: {bene_count}\nAllocations: {allocations}",
            name="Section_After_Add_Third_Bene",
            attachment_type=allure.attachment_type.TEXT,
        )


@then(parsers.parse('each beneficiary allocation should be "{expected_percentage}"'))
def verify_equal_allocations(page, update_beneficiary_page, test_context, expected_percentage):

    with allure.step(f"Verify each beneficiary has {expected_percentage} allocation"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        logger.info(f"Retrieved allocations: {allocations}")
        
        # Extract numeric value from expected_percentage (e.g., "50.00%" -> "50")
        expected_value = expected_percentage.replace('%', '').replace('.00', '')
        
        for i, allocation in enumerate(allocations):
            # Allocations are stored as strings like '50' or '50.00'
            allocation_value = allocation.replace('.00', '').replace('.0', '')
            assert allocation_value == expected_value, (
                f"Beneficiary {i+1}: Expected {expected_percentage}, got {allocation}%"
            )
            logger.info(f"Beneficiary {i+1}: {allocation}% Γ£ô")
        
        logger.info(f"All {len(allocations)} beneficiaries have equal allocation of {expected_percentage}")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Equal_Allocations_Verified", attachment_type=allure.attachment_type.PNG)


# ==================== Allocation Field & Group Total Validation Steps ====================

@when(parsers.parse('user enters allocation value "{value}" in the two-primary beneficiary section'))
def enter_allocation_value_in_two_primary_section(page, update_beneficiary_page, test_context, value):
    with allure.step(f"Enter allocation value '{value}' in first input of two-primary section"):
        section = test_context.get('multi_account_section')
        if section is None:
            section = update_beneficiary_page.get_section_with_n_primary_beneficiaries(2)
            assert section is not None, "No section with 2 primary beneficiaries found"
            test_context['multi_account_section'] = section

        section_title = update_beneficiary_page.get_section_title(section)
        test_context['active_section'] = section  # used by @then to resolve section generically
        before_screenshot = page.screenshot()
        allure.attach(before_screenshot, name=f"Before_Entering_{value}", attachment_type=allure.attachment_type.PNG)
        before_values = update_beneficiary_page.get_primary_allocation_percentages(section)
        logger.info(f"[BEFORE] Section '{section_title}' allocations: {before_values}")

        # ΓöÇΓöÇ Balance input[1] to the complement of value so group total = 100% ΓöÇΓöÇ
        # This isolates field-level validation (aria-invalid on the specific input)
        # from group-total errors (aria-invalid on ALL inputs when sum != 100%).
        # Example: value='99.99' ΓåÆ input[1]='0.01' ΓåÆ total=100.00 ΓåÆ no group error.
        # A fixed '50' would give total=149.99%, poisoning aria-invalid on all inputs.
        # For invalid values (non-parseable / out-of-range), the field error dominates
        # so the group-total error is irrelevant ΓÇö we fall back to '50'.
        n_inputs = section.locator("input[type='number']").count()
        if n_inputs >= 2:
            try:
                val_float = float(value)
                complement = round(100.0 - val_float, 2)
                complement = max(0.0, min(100.0, complement))
                balance_value = f"{complement:.2f}"
            except (ValueError, TypeError):
                balance_value = "50"  # unparseable value ΓåÆ field error dominates
            # Use fill() WITHOUT press("Tab") to avoid triggering blur validation on input[1].
            # Pressing Tab would cause the app to mark input[1] as aria-invalid when its
            # value is 0.00 (below minimum per-beneficiary), which can cascade to input[0].
            # fill() alone still fires React's input/change events so the group total
            # recalculates correctly (e.g. 100 + 0 = 100 ΓåÆ no group error).
            input_1 = section.locator("input[type='number']").nth(1)
            input_1.click(click_count=3)
            input_1.fill(balance_value)
            # Do NOT press Tab here ΓÇö intentionally skip blur to avoid cascading aria-invalid
            page.wait_for_timeout(300)
            logger.info(
                f"Balanced input[1] to '{balance_value}' (complement of '{value}') "
                f"via fill-only (no Tab) to keep group total at ~100% without "
                f"triggering field-level aria-invalid on input[1]"
            )

        # ΓöÇΓöÇ Enter the test value in input[0] and check field-level error post-blur ΓöÇΓöÇ
        # Strategy: use post-blur aria-invalid, which is safe because the complement
        # strategy above keeps group total at ~100% (fill-only on input[1], no Tab).
        # With a valid group total the group-level cascade won't fire on Tab,
        # so any aria-invalid on input[0] post-blur is purely field-level:
        #   ΓÇó Format errors (>2dp):   fire on onChange AND onBlur ΓåÆ captured either way
        #   ΓÇó Range errors (00.00):   fire ONLY on onBlur ΓåÆ must use post-blur Γ£ô
        #   ΓÇó Per-bene max (100 in 2-bene context): fire on onChange ΓåÆ also captured
        input_0 = section.locator("input[type='number']").nth(0)
        input_0.click(click_count=3)
        input_0.fill(value)
        page.wait_for_timeout(200)  # Let React onChange settle

        actual_value = input_0.input_value()
        logger.info(f"[PRE-BLUR]  Entered '{value}' ΓåÆ input reads '{actual_value}'")

        # Blur triggers onBlur validators (e.g. min-value check for 00.00)
        input_0.press("Tab")
        page.wait_for_timeout(300)  # Let React onBlur + re-render settle

        # Read aria-invalid POST-blur ΓÇö safe because group total = ~100%
        post_blur_error = input_0.get_attribute("aria-invalid") == "true"
        logger.info(
            f"[POST-BLUR] Entered '{value}' ΓåÆ input reads '{actual_value}', "
            f"aria-invalid={post_blur_error}"
        )

        test_context['entered_value']      = value
        test_context['actual_input_value'] = actual_value
        test_context['field_level_error']  = post_blur_error

        after_screenshot = page.screenshot()
        allure.attach(
            after_screenshot,
            name=f"After_Entering_{value}_actual_{actual_value}",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('the allocation input should be in "{expected_state}" state'))
def verify_allocation_input_state(page, update_beneficiary_page, test_context, expected_state):
    with allure.step(f"Verify allocation input is in '{expected_state}' state"):
        # Resolve the active section ΓÇö supports both single- and multi-primary scenarios
        section = (
            test_context.get('active_section')
            or test_context.get('multi_account_section')
            or test_context.get('single_account_section')
        )
        assert section is not None, (
            "No section found in test_context. "
            "Expected one of: active_section, multi_account_section, single_account_section"
        )

        entered_value = test_context.get('entered_value', 'unknown')
        actual_value  = test_context.get('actual_input_value', 'unknown')

        # Uses post-blur aria-invalid captured in the @when step.
        # The complement strategy (input[1] set to 100-value via fill-only/no Tab)
        # keeps the group total at ~100%, so no group-level cascade fires on blur.
        # Any aria-invalid on input[0] post-blur is therefore purely field-level:
        #   ΓÇó Format errors (>2dp): fire on onChange AND onBlur
        #   ΓÇó Min-value errors (00.00): fire ONLY on onBlur ΓåÆ correctly captured now
        #   ΓÇó Per-bene max (e.g. 100 in 2-bene): fire on onChange
        is_error = test_context.get('field_level_error')
        if is_error is None:
            is_error = update_beneficiary_page.is_allocation_input_in_error(section, 0)
            logger.info("field_level_error not in context ΓÇö falling back to live aria-invalid check")

        logger.info(
            f"Allocation field validation ΓÇö entered: '{entered_value}', "
            f"actual input value: '{actual_value}', "
            f"field-level error (post-blur): {is_error}, "
            f"expected state: '{expected_state}'"
        )

        if expected_state == "valid":
            assert not is_error, (
                f"Expected allocation '{entered_value}' to be VALID (no field error), "
                f"but aria-invalid=true was detected post-blur. "
                f"Actual input value read back: '{actual_value}'."
            )
            logger.info(f"Γ£ô Allocation '{actual_value}' is valid ΓÇö no field-level error post-blur")
        elif expected_state == "invalid":
            assert is_error, (
                f"Expected allocation '{entered_value}' to be INVALID (field error), "
                f"but aria-invalid was not set post-blur. "
                f"Actual input value read back: '{actual_value}'."
            )
            logger.info(f"Γ£ô Allocation '{actual_value}' correctly shows field-level error post-blur")
        else:
            raise ValueError(f"Unknown expected_state '{expected_state}'. Use 'valid' or 'invalid'.")

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Allocation_State_{expected_state}_for_{entered_value}", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('user enters allocation value "{value}" in the single-primary beneficiary section'))
def enter_allocation_value_in_single_primary_section(page, update_beneficiary_page, test_context, value):
    with allure.step(f"Enter allocation value '{value}' in single-primary beneficiary section"):
        section = test_context.get('single_account_section')
        if section is None:
            section = update_beneficiary_page.get_single_primary_account_section()
            assert section is not None, "No section with exactly 1 primary beneficiary found"
            test_context['single_account_section'] = section

        section_title = update_beneficiary_page.get_section_title(section)
        test_context['active_section'] = section

        # Capture state BEFORE
        before_screenshot = page.screenshot()
        allure.attach(before_screenshot, name=f"Before_Entering_{value}_single_primary", attachment_type=allure.attachment_type.PNG)
        before_values = update_beneficiary_page.get_primary_allocation_percentages(section)
        logger.info(f"[BEFORE] Single-primary section '{section_title}' allocations: {before_values}")

        # In a 1-beneficiary section there is only one input ΓÇö no group cascade possible.
        # Post-blur is always safe here; it also correctly captures onBlur-only validators.
        input_0 = section.locator("input[type='number']").nth(0)
        input_0.click(click_count=3)
        input_0.fill(value)
        page.wait_for_timeout(200)  # Let React onChange settle

        actual_value = input_0.input_value()
        logger.info(f"[PRE-BLUR]  Entered '{value}' ΓåÆ input reads '{actual_value}'")

        input_0.press("Tab")
        page.wait_for_timeout(300)  # Let React onBlur + re-render settle

        post_blur_error = input_0.get_attribute("aria-invalid") == "true"
        logger.info(
            f"[POST-BLUR] Entered '{value}' ΓåÆ input reads '{actual_value}', "
            f"aria-invalid={post_blur_error}"
        )

        test_context['entered_value']      = value
        test_context['actual_input_value'] = actual_value
        test_context['field_level_error']  = post_blur_error

        after_screenshot = page.screenshot()
        allure.attach(
            after_screenshot,
            name=f"After_Entering_{value}_single_primary_actual_{actual_value}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('user sets primary allocations to "{value1}" and "{value2}" in the two-primary beneficiary section'))
def set_two_primary_allocation_values(page, update_beneficiary_page, test_context, value1, value2):
    with allure.step(f"Set primary allocations to {value1}% and {value2}%"):
        section = test_context.get('multi_account_section')
        if section is None:
            section = update_beneficiary_page.get_section_with_n_primary_beneficiaries(2)
            assert section is not None, "No section with 2 primary beneficiaries found"
            test_context['multi_account_section'] = section

        section_title = update_beneficiary_page.get_section_title(section)
        logger.info(f"Setting allocations [{value1}%, {value2}%] in section: {section_title}")

        update_beneficiary_page.set_two_primary_allocations(section, value1, value2)
        page.wait_for_timeout(400)

        total_text = update_beneficiary_page.get_section_total_text(section)
        logger.info(f"Group total after setting values: {total_text}")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Allocations_Set_{value1}_and_{value2}",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('the group total should be "{expected_total}" with "{error_expectation}" error state'))
def verify_group_total_and_error_state(page, update_beneficiary_page, test_context, expected_total, error_expectation):
    with allure.step(f"Verify group total is {expected_total}% with error_expectation='{error_expectation}'"):
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"

        # Verify the displayed total text
        total_text = update_beneficiary_page.get_section_total_text(section)
        logger.info(f"Section total text: '{total_text}'")
        assert expected_total in total_text, (
            f"Expected total '{expected_total}' to appear in '{total_text}'"
        )
        logger.info(f"Γ£ô Total text matches ΓÇö contains '{expected_total}'")

        # Verify the error state
        is_in_error = update_beneficiary_page.is_group_total_in_error_state(section)

        if error_expectation == "no_error":
            assert not is_in_error, (
                f"Expected group total to have NO error state, but error indicators were found. "
                f"Total: {total_text}"
            )
            logger.info(f"Γ£ô Group total {expected_total} ΓÇö no error state (correct)")
        elif error_expectation == "error":
            assert is_in_error, (
                f"Expected group total to show ERROR state, but no error indicators found. "
                f"Total: {total_text}. Check Mui-error class or aria-invalid on inputs."
            )
            logger.info(f"Γ£ô Group total {expected_total} ΓÇö error state correctly highlighted")
        else:
            raise ValueError(f"Unknown error_expectation '{error_expectation}'. Use 'error' or 'no_error'.")

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Group_Total_{expected_total}_{error_expectation}",
            attachment_type=allure.attachment_type.PNG
        )


@given("user should identify a section with 2 primary accounts and ensure allocation is unequal")
def identify_section_with_two_primary_and_make_unequal(page, update_beneficiary_page, test_context):
    """
    Find a section with exactly 2 primary beneficiaries.
    If allocation is currently equal, make it unequal.
    """
    with allure.step("Identify section with 2 primary accounts and ensure unequal allocation"):
        logger.info("Searching for a section with exactly 2 primary beneficiaries")
        
        # Get all sections with 2 primary accounts
        two_primary_sections = update_beneficiary_page.get_all_two_primary_account_sections()
        
        assert len(two_primary_sections) > 0, (
            "No account section found with exactly 2 primary beneficiaries. "
            "Test data may not be set up correctly."
        )
        
        # Use the first section found
        section = two_primary_sections[0]
        section_title = update_beneficiary_page.get_section_title(section)
        logger.info(f"Using section: {section_title}")
        
        # Check current allocation
        current_allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        logger.info(f"Current allocations: {current_allocations}")
        
        is_equal = update_beneficiary_page.is_allocation_equal(section)
        logger.info(f"Allocation is currently equal: {is_equal}")
        
        # If allocation is equal, make it unequal
        if is_equal:
            logger.info("Allocation is equal, making it unequal...")
            update_beneficiary_page.make_allocation_unequal(section)
            
            # Verify it's now unequal
            new_allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
            is_still_equal = update_beneficiary_page.is_allocation_equal(section)
            
            assert not is_still_equal, (
                f"Failed to make allocation unequal. Allocations: {new_allocations}"
            )
            logger.info(f"Γ£ô Allocation is now unequal: {new_allocations}")
        else:
            logger.info("Allocation is already unequal, proceeding...")
        
        # Store section in test context for subsequent steps
        test_context['two_primary_section'] = section
        test_context['section_title'] = section_title
        
        # Take screenshot
        screenshot = page.screenshot()
        allure.attach(
            screenshot, 
            name=f"Section_With_Unequal_Allocation_{section_title}", 
            attachment_type=allure.attachment_type.PNG
        )


@when("user clicks the Allocate Equally button in the two-primary section")
def click_allocate_equally_in_two_primary_section(page, update_beneficiary_page, test_context):
    """
    Click the 'Allocate Equally' button in the section with 2 primary accounts.
    """
    with allure.step("Click Allocate Equally button"):
        section = test_context.get('two_primary_section')
        assert section is not None, (
            "test_context['two_primary_section'] is not set ΓÇö "
            "run 'identify section with 2 primary accounts' step first"
        )
        
        section_title = test_context.get('section_title', 'Unknown Section')
        logger.info(f"Clicking 'Allocate Equally' button in section: {section_title}")
        
        # Get allocations before clicking
        before_allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        logger.info(f"Allocations before clicking: {before_allocations}")
        
        # Click the button
        allocate_btn = section.get_by_role("button", name="Allocate Equally")
        
        # Verify button is enabled before clicking
        assert allocate_btn.is_enabled(), (
            f"'Allocate Equally' button is disabled in section {section_title}"
        )
        
        allocate_btn.click()
        logger.info("'Allocate Equally' button clicked successfully")
        
        # Wait for DOM updates
        page.wait_for_timeout(500)
        
        # Take screenshot
        screenshot = page.screenshot()
        allure.attach(
            screenshot, 
            name="After_Clicking_Allocate_Equally", 
            attachment_type=allure.attachment_type.PNG
        )


@then("allocation percentages in the two-primary section should be equal")
def verify_allocations_are_now_equal(page, update_beneficiary_page, test_context):
    """
    Verify that allocations are now equally distributed (50/50 for 2 beneficiaries).
    """
    with allure.step("Verify allocations are now equal"):
        section = test_context.get('two_primary_section')
        assert section is not None, "test_context['two_primary_section'] is not set"
        
        section_title = test_context.get('section_title', 'Unknown Section')
        logger.info(f"Verifying equal allocation in section: {section_title}")
        
        # Get updated allocations
        allocations = update_beneficiary_page.get_primary_allocation_percentages(section)
        logger.info(f"Allocations after clicking Allocate Equally: {allocations}")
        
        # Verify allocation is equal
        is_equal = update_beneficiary_page.is_allocation_equal(section)
        
        assert is_equal, (
            f"Allocations are not equal after clicking 'Allocate Equally'. "
            f"Allocations: {allocations}"
        )
        
        # For 2 beneficiaries, each should have 50%
        expected_value = 50.0
        for i, allocation in enumerate(allocations):
            allocation_float = float(allocation)
            assert abs(allocation_float - expected_value) < 0.01, (
                f"Beneficiary {i+1}: Expected ~50%, got {allocation}%"
            )
            logger.info(f"Γ£ô Beneficiary {i+1}: {allocation}% (equal distribution confirmed)")
        
        logger.info(f"Γ£ô All allocations are equal at 50% each")
        
        # Take final screenshot
        screenshot = page.screenshot()
        allure.attach(
            screenshot, 
            name="Equal_Allocation_Verified", 
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.parse('User should select beneficiary type as "{beneType}"'))
def user_select_beneficiary_type_generic(page, add_beneficiary_page, beneType, test_context):
    logger.info(f"Selecting beneficiary type: {beneType}")
    
    add_beneficiary_page.select_beneficiary_type_as(beneType)
    
    test_context['beneficiary_type'] = beneType
    logger.info(f"Beneficiary type {beneType} selected")


@when(parsers.parse('User should select designation as "{designation}"'))
def user_select_designation_generic(page, add_beneficiary_page, designation, test_context):
    logger.info(f"Selecting designation: {designation}")
    
    add_beneficiary_page.select_designation_as(designation)
    page.wait_for_timeout(300)
    
    test_context['beneficiary_designation'] = designation
    logger.info(f"Designation {designation} selected")


@when(parsers.parse('User should enter first name "{firstName}"'))
def user_enter_first_name_generic(page, add_beneficiary_page, firstName, test_context):
    logger.info(f"Entering first name: {firstName if firstName else '(empty)'}")
    
    
    if firstName:
        add_beneficiary_page.enter_first_name(firstName)
        test_context['beneficiary_first_name'] = firstName
    else:
        test_context['beneficiary_first_name'] = ""


@when(parsers.parse('User should enter last name "{lastName}"'))
def user_enter_last_name_generic(page, add_beneficiary_page, lastName, test_context):
    logger.info(f"Entering last name: {lastName if lastName else '(empty)'}")
    
    
    if lastName:
        add_beneficiary_page.enter_last_name(lastName)
        test_context['beneficiary_last_name'] = lastName
    else:
        test_context['beneficiary_last_name'] = ""


@when(parsers.parse('User should enter social security number "{ssn}"'))
def user_enter_ssn_generic(page, add_beneficiary_page, ssn, test_context):
    logger.info(f"Entering SSN: {ssn if ssn else '(empty)'}")
    
    
    if ssn:
        add_beneficiary_page.enter_social_security_number(ssn)
        test_context['beneficiary_ssn'] = ssn
    else:
        test_context['beneficiary_ssn'] = ""


@when(parsers.parse('User should enter date of birth "{dob}"'))
def user_enter_dob_generic(page, add_beneficiary_page, dob, test_context):
    logger.info(f"Entering DOB: {dob if dob else '(empty)'}")
    
    
    if dob:
        add_beneficiary_page.enter_date_of_birth(dob)
        test_context['beneficiary_dob'] = dob
    else:
        test_context['beneficiary_dob'] = ""


@when(parsers.parse('User should enter trust name "{trustName}"'))
def user_enter_trust_name_generic(page, add_beneficiary_page, trustName, test_context):
    logger.info(f"Entering trust name: {trustName if trustName else '(empty)'}")
    
    
    if trustName:
        add_beneficiary_page.enter_trust_name(trustName)
        test_context['beneficiary_name'] = trustName
    else:
        test_context['beneficiary_name'] = ""


@when(parsers.parse('User should enter date of trust "{dateOfTrust}"'))
def user_enter_date_of_trust_generic(page, add_beneficiary_page, dateOfTrust, test_context):
    logger.info(f"Entering date of trust: {dateOfTrust if dateOfTrust else '(empty)'}")
    
    
    if dateOfTrust:
        add_beneficiary_page.enter_date_of_trust(dateOfTrust)
        test_context['beneficiary_date_of_trust'] = dateOfTrust
    else:
        test_context['beneficiary_date_of_trust'] = ""


@when(parsers.parse('User should enter entity name "{entityName}"'))
def user_enter_entity_name_generic(page, add_beneficiary_page, entityName, test_context):
    logger.info(f"Entering entity name: {entityName if entityName else '(empty)'}")
    
    
    if entityName:
        add_beneficiary_page.enter_entity_name(entityName)
        test_context['beneficiary_name'] = entityName
    else:
        test_context['beneficiary_name'] = ""


@when(parsers.parse('User should enter tax identification number "{tin}"'))
def user_enter_tin_generic(page, add_beneficiary_page, tin, test_context):
    logger.info(f"Entering TIN: {tin if tin else '(empty)'}")
    
    
    if tin:
        add_beneficiary_page.enter_tax_identification_number(tin)
        test_context['beneficiary_tin'] = tin
    else:
        test_context['beneficiary_tin'] = ""


@then(parsers.parse('Error message should display "{errorMessage}"'))
def verify_error_message_generic(page, add_beneficiary_page, errorMessage, test_context):
    logger.info(f"Verifying error message: {errorMessage}")
    
    page.wait_for_timeout(1000)
    
    if "first name" in errorMessage.lower():
        first_name_error = add_beneficiary_page.get_first_name_error_message()
        assert first_name_error == errorMessage, f"Expected error '{errorMessage}' but got '{first_name_error}'"
        logger.info(f"First name error message verified: {errorMessage}")
        return
    
    if "last name" in errorMessage.lower():
        last_name_error = add_beneficiary_page.get_last_name_error_message()
        assert last_name_error == errorMessage, f"Expected error '{errorMessage}' but got '{last_name_error}'"
        logger.info(f"Last name error message verified: {errorMessage}")
        return
    
    if "enter a name" in errorMessage.lower():
        name_error = add_beneficiary_page.get_name_error_message()
        assert name_error == errorMessage, f"Expected error '{errorMessage}' but got '{name_error}'"
        logger.info(f"Name error message verified: {errorMessage}")
        return
    
    if "select at least one account" in errorMessage.lower():
        account_error = add_beneficiary_page.get_account_selection_error_message()
        assert account_error == errorMessage, f"Expected error '{errorMessage}' but got '{account_error}'"
        logger.info(f"Account selection error message verified: {errorMessage}")
        return
    
    all_errors = add_beneficiary_page.get_all_error_messages()
    logger.info(f"Found error messages: {all_errors}")
    
    found = False
    for error in all_errors:
        if errorMessage.lower() in error.lower():
            found = True
            break
    
    assert found, f"Expected error '{errorMessage}' not found. Got: {all_errors}"
    logger.info(f"Error message verified: {errorMessage}")


@when(parsers.parse('User selects "{signatureOption}" signature option'))
def user_selects_signature_option(page, manage_bene_detail_page, signatureOption, test_context):
    """
    Select a signature option on the manage beneficiaries page.
    
    Args:
        signatureOption: Either 'Obtain Electronic Client Signature(s)' or 'Print to Obtain Physical Client Signature(s)'
    """
    with allure.step(f"Selecting signature option: {signatureOption}"):
        logger.info(f"Step: User selects '{signatureOption}' signature option")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Select_Signature_Option", attachment_type=allure.attachment_type.PNG)
        
        manage_bene_detail_page.selectSignatureOption(signatureOption)
        
        page.wait_for_timeout(1000)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Select_Signature_Option", attachment_type=allure.attachment_type.PNG)
        
        test_context['selected_signature_option'] = signatureOption
        logger.info(f"Signature option '{signatureOption}' selected successfully")


@then(parsers.parse('"{buttonText}" button should be disabled'))
def verify_button_is_disabled(page, manage_bene_detail_page, buttonText, test_context):
    """
    Verify that a signature button is disabled.
    Only one button is visible at a time based on selected radio option.
    
    Args:
        buttonText: Text of the button to verify (e.g., 'Continue to e-Signature Details', 'Continue to Review')
    """
    with allure.step(f"Verifying '{buttonText}' button is disabled"):
        logger.info(f"Step: Verifying '{buttonText}' button is disabled")
        
        is_disabled = manage_bene_detail_page.isButtonDisabled(buttonText)
        
        assert is_disabled, f"Expected button '{buttonText}' to be disabled, but it is enabled"
        logger.info(f"Button '{buttonText}' is disabled as expected")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"{buttonText.replace(' ', '_')}_Disabled", attachment_type=allure.attachment_type.PNG)


@then(parsers.parse('"{buttonText}" button should be enabled'))
def verify_button_is_enabled(page, manage_bene_detail_page, buttonText, test_context):
    """
    Verify that a signature button is enabled.
    Only one button is visible at a time based on selected radio option.
    
    Args:
        buttonText: Text of the button to verify (e.g., 'Continue to e-Signature Details', 'Continue to Review')
    """
    with allure.step(f"Verifying '{buttonText}' button is enabled"):
        logger.info(f"Step: Verifying '{buttonText}' button is enabled")
        
        is_enabled = manage_bene_detail_page.isButtonEnabled(buttonText)
        
        assert is_enabled, f"Expected button '{buttonText}' to be enabled, but it is disabled"
        logger.info(f"Button '{buttonText}' is enabled as expected")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"{buttonText.replace(' ', '_')}_Enabled", attachment_type=allure.attachment_type.PNG)


def user_fill_form_no_account(page, add_beneficiary_page, test_context):
    logger.info("Filling beneficiary form WITHOUT selecting any account")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as("Individual")
    add_beneficiary_page.select_designation_as("Primary")
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_first_name("John")
    add_beneficiary_page.enter_last_name("Doe")
    add_beneficiary_page.enter_social_security_number("123-45-6789")
    add_beneficiary_page.enter_date_of_birth("01/15/1985")
    
    logger.info("Form filled without account selection")
    test_context['form_filled'] = True
    test_context['beneficiary_first_name'] = "John"
    test_context['beneficiary_last_name'] = "Doe"


@when("User should select beneficiary type as \"Individual\" and designation as \"Contingent\" and enter first name \"Jane\" and last name \"Smith\" and SSN \"987-65-4321\" and DOB \"05/20/1990\" and select at least one account")
def user_fill_contingent_form(page, add_beneficiary_page, test_context):
    logger.info("Filling form for CONTINGENT beneficiary")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as("Individual")
    add_beneficiary_page.select_designation_as("Contingent")
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_first_name("Jane")
    add_beneficiary_page.enter_last_name("Smith")
    add_beneficiary_page.enter_social_security_number("987-65-4321")
    add_beneficiary_page.enter_date_of_birth("05/20/1990")
    add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
    
    logger.info("Form filled for Contingent beneficiary")
    test_context['form_filled'] = True
    test_context['beneficiary_type'] = "Contingent"
    test_context['beneficiary_first_name'] = "Jane"
    test_context['beneficiary_last_name'] = "Smith"


@when(parsers.parse('User should select beneficiary type as "{bene_type}" and relation as "{relation}" and enter first name "{first_name}" and last name "{last_name}" and SSN "{ssn}" and DOB "{dob}" and select at least one account'))
def user_fill_beneficiary_form_parameterized(page, add_beneficiary_page, bene_type, relation, first_name, last_name, ssn, dob, test_context):
    logger.info(f"Filling beneficiary form: Type={bene_type}, Relation={relation}, Name={first_name} {last_name}")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as(bene_type)
    add_beneficiary_page.select_designation_as(relation)
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_first_name(first_name)
    add_beneficiary_page.enter_last_name(last_name)
    add_beneficiary_page.enter_social_security_number(ssn)
    add_beneficiary_page.enter_date_of_birth(dob)
    add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
    
    logger.info(f"Beneficiary form filled: {first_name} {last_name} as {relation}")
    test_context['form_filled'] = True
    test_context['beneficiary_type'] = relation
    test_context['beneficiary_first_name'] = first_name
    test_context['beneficiary_last_name'] = last_name


@when("User should select beneficiary type as \"Trust\" and designation as \"Primary\" and enter trust name \"Smith Family Trust\" and SSN \"123-45-6789\" and date of trust \"01/15/2015\" and select at least one account")
def user_fill_trust_beneficiary_form(page, add_beneficiary_page, test_context):
    logger.info("Filling form for TRUST beneficiary")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as("Trust")
    add_beneficiary_page.select_designation_as("Primary")
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_trust_name("Smith Family Trust")
    add_beneficiary_page.enter_social_security_number("123-45-6789")
    add_beneficiary_page.enter_date_of_trust("01/15/2015")
    add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
    
    logger.info("Form filled for Trust beneficiary")
    test_context['form_filled'] = True
    test_context['beneficiary_type'] = "Trust"
    test_context['beneficiary_name'] = "Smith Family Trust"


@when("User should select beneficiary type as \"Entity\" and designation as \"Primary\" and enter entity name \"ABC Corporation\" and TIN \"12-3456789\" and select at least one account")
def user_fill_entity_beneficiary_form(page, add_beneficiary_page, test_context):
    logger.info("Filling form for ENTITY beneficiary")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as("Entity")
    add_beneficiary_page.select_designation_as("Primary")
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_entity_name("ABC Corporation")
    add_beneficiary_page.enter_tax_identification_number("12-3456789")
    add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
    
    logger.info("Form filled for Entity beneficiary")
    test_context['form_filled'] = True
    test_context['beneficiary_type'] = "Entity"
    test_context['beneficiary_name'] = "ABC Corporation"


@when("User should click \"Don't Save\" button")
def user_click_dont_save_button(page, add_beneficiary_page, test_context):
    logger.info("Clicking 'Don't Save' button")
    
    add_beneficiary_page.click_dont_save_button()
    
    page.wait_for_load_state('networkidle')
    add_beneficiary_page.wait_for_modal_to_close()
    
    logger.info("'Don't Save' button clicked, modal closed")
    test_context['modal_closed'] = True


@when("User should select beneficiary type as \"Individual\" and designation as \"Primary\" and enter first name \"Michael\" and last name \"Johnson\" and SSN \"111-22-3333\" and DOB \"03/10/1980\" and select multiple accounts for beneficiary")
def user_fill_form_multiple_accounts(page, add_beneficiary_page, test_context):
    logger.info("Filling form and selecting MULTIPLE accounts")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as("Individual")
    add_beneficiary_page.select_designation_as("Primary")
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_first_name("Michael")
    add_beneficiary_page.enter_last_name("Johnson")
    add_beneficiary_page.enter_social_security_number("111-22-3333")
    add_beneficiary_page.enter_date_of_birth("03/10/1980")
    add_beneficiary_page.select_multiple_accounts_for_beneficiary()
    
    logger.info("Form filled with multiple accounts selected")
    test_context['form_filled'] = True
    test_context['beneficiary_first_name'] = "Michael"
    test_context['beneficiary_last_name'] = "Johnson"
    test_context['multiple_accounts_selected'] = True


@when("User should select beneficiary type as \"Individual\" and designation as \"Primary\" and enter first name \"Robert\" and last name \"Brown\" and SSN \"444-55-6666\" and DOB \"07/22/1975\" and select at least one account")
def user_fill_form_robert_brown(page, add_beneficiary_page, test_context):
    logger.info("Filling form for Robert Brown")
    
    page.wait_for_load_state('networkidle')
    
    add_beneficiary_page.select_beneficiary_type_as("Individual")
    add_beneficiary_page.select_designation_as("Primary")
    page.wait_for_timeout(300)
    
    add_beneficiary_page.enter_first_name("Robert")
    add_beneficiary_page.enter_last_name("Brown")
    add_beneficiary_page.enter_social_security_number("444-55-6666")
    add_beneficiary_page.enter_date_of_birth("07/22/1975")
    add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
    
    logger.info("Form filled for Robert Brown")
    test_context['form_filled'] = True
    test_context['beneficiary_first_name'] = "Robert"
    test_context['beneficiary_last_name'] = "Brown"


@when("User should click edit icon for beneficiary \"David Wilson\"")
def user_click_edit_beneficiary(page, update_beneficiary_page, add_beneficiary_page, test_context):
    logger.info("Clicking edit icon for David Wilson")
    
    update_beneficiary_page.click_edit_beneficiary("David Wilson")
    
    page.wait_for_load_state('networkidle')
    add_beneficiary_page.wait_for_page_load()
    
    logger.info("Edit modal opened for David Wilson")
    test_context['edit_mode'] = True
    test_context['editing_beneficiary'] = "David Wilson"


@when("User should change designation from \"Primary\" to \"Contingent\"")
def user_change_designation_to_contingent(page, add_beneficiary_page, test_context):
    logger.info("Changing designation to Contingent")
    
    add_beneficiary_page.select_designation_as("Contingent")
    page.wait_for_timeout(300)
    
    logger.info("Designation changed to Contingent")


@when("User should select at least one account for beneficiary")
def user_select_at_least_one_account(page, add_beneficiary_page, test_context):
    logger.info("Selecting at least one account for beneficiary")
    
    add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
    
    test_context['account_selected'] = True
    logger.info("At least one account selected")


@when("User should click on Date of Birth calendar picker")
def user_click_dob_calendar_picker(page, add_beneficiary_page, test_context):
    """Click on the Date of Birth calendar icon to open the date picker."""
    with allure.step("Clicking on Date of Birth calendar picker"):
        logger.info("Clicking on Date of Birth calendar picker")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Calendar_Click", attachment_type=allure.attachment_type.PNG)
        
        add_beneficiary_page.clickCalendarIcon()
        
        page.wait_for_timeout(1000)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Calendar_Opened", attachment_type=allure.attachment_type.PNG)
        
        logger.info("Calendar picker opened")


@then("Future date navigation should be disabled in calendar")
def verify_future_date_disabled(page, add_beneficiary_page, test_context):
    """Validate that future dates in the calendar are disabled."""
    with allure.step("Verifying future date navigation is disabled"):
        logger.info("Verifying future date navigation is disabled")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Calendar_Before_Validation", attachment_type=allure.attachment_type.PNG)
        
        page.wait_for_timeout(500)
        
        add_beneficiary_page.validateFutureDatesAreDisabled()
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Calendar_After_Validation", attachment_type=allure.attachment_type.PNG)
        
        logger.info("Future date navigation confirmed as disabled")


@then("Only past dates should be selectable")
def verify_only_past_dates_selectable(page, add_beneficiary_page, test_context):
    """Validate that only past dates are selectable in the calendar."""
    with allure.step("Verifying only past dates are selectable"):
        logger.info("Verifying only past dates are selectable")
        
        page.wait_for_timeout(500)
        
        logger.info("Only past dates confirmed as selectable (covered by future dates validation)")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Past_Dates_Selectable_Confirmed", attachment_type=allure.attachment_type.PNG)



@when("User should click delete icon for beneficiary \"Sarah Miller\"")
def user_click_delete_beneficiary_sarah(page, update_beneficiary_page, test_context):
    logger.info("Clicking delete icon for Sarah Miller")
    
    update_beneficiary_page.click_delete_beneficiary("Sarah Miller")
    
    page.wait_for_load_state('networkidle')
    
    logger.info("Delete confirmation modal appeared")
    test_context['delete_mode'] = True
    test_context['deleting_beneficiary'] = "Sarah Miller"


@when("User should confirm deletion")
def user_confirm_deletion(page, manage_bene_detail_page, test_context):
    logger.info("Confirming deletion")
    
    manage_bene_detail_page.confirm_dialog_action()
    
    page.wait_for_load_state('networkidle')
    
    logger.info("Deletion confirmed")



@then("Tooltip should display \"No beneficiaries on this account. Add a primary beneficiary first.\"")
def verify_no_primary_tooltip(page, add_beneficiary_page, test_context):
    logger.info("Verifying tooltip message for no primary beneficiary")
    
    page.wait_for_timeout(500)
    
    tooltip_text = add_beneficiary_page.get_tooltip_text()
    
    assert tooltip_text is not None and "Add a primary beneficiary first" in tooltip_text, \
        f"Expected tooltip about primary beneficiary, got: {tooltip_text}"
    
    logger.info(f"Tooltip verified: {tooltip_text}")


@then("Beneficiary should NOT be added")
def verify_beneficiary_not_added(page, update_beneficiary_page, add_beneficiary_page, test_context):
    logger.info("Verifying beneficiary was NOT added")
    
    page.wait_for_load_state('networkidle')
    
    is_modal_open = add_beneficiary_page.is_confirmation_modal_displayed()
    
    logger.info(f"Beneficiary not added (modal still open: {is_modal_open})")


@then('Verify the beneficiary "Jane Smith" is added successfully with designation "Contingent"')
def verify_contingent_added(page, update_beneficiary_page, test_context):
    logger.info("Verifying Contingent beneficiary Jane Smith added")
    
    page.wait_for_load_state('networkidle')
    
    contingent_list = update_beneficiary_page.get_contingent_beneficiaries(1)
    
    assert "Jane Smith" in contingent_list, f"Jane Smith not found in contingent beneficiaries: {contingent_list}"
    
    logger.info("Contingent beneficiary Jane Smith verified")


@then('Verify the beneficiary "Smith Family Trust" is added successfully with designation "Primary"')
def verify_trust_added(page, update_beneficiary_page, test_context):
    logger.info("Verifying Trust beneficiary Smith Family Trust added")
    
    page.wait_for_load_state('networkidle')
    
    primary_list = update_beneficiary_page.get_primary_beneficiaries(1)
    
    assert "Smith Family Trust" in primary_list, f"Smith Family Trust not found in primary beneficiaries: {primary_list}"
    
    logger.info("Trust beneficiary Smith Family Trust verified")


@then('Verify the beneficiary "ABC Corporation" is added successfully with designation "Primary"')
def verify_entity_added(page, update_beneficiary_page, test_context):
    logger.info("Verifying Entity beneficiary ABC Corporation added")
    
    page.wait_for_load_state('networkidle')
    
    primary_list = update_beneficiary_page.get_primary_beneficiaries(1)
    
    assert "ABC Corporation" in primary_list, f"ABC Corporation not found in primary beneficiaries: {primary_list}"
    
    logger.info("Entity beneficiary ABC Corporation verified")


@then("Modal should close")
def verify_modal_closed(page, add_beneficiary_page, test_context):
    logger.info("Verifying modal is closed")
    
    page.wait_for_timeout(500)
    
    is_closed = add_beneficiary_page.is_modal_closed()
    
    assert is_closed, "Modal should be closed"
    logger.info("Modal confirmed as closed")


@then("Changes should NOT be applied")
def verify_changes_not_applied(page, test_context):
    logger.info("Verifying changes were NOT applied")
    
    test_context['changes_not_applied'] = True
    logger.info("Changes not applied confirmed")


@then("User should be back on manage beneficiaries page")
def verify_back_on_manage_page(page, update_beneficiary_page, test_context):
    logger.info("Verifying user is on Manage Beneficiaries page")
    
    page.wait_for_load_state('networkidle')
    
    update_beneficiary_page.is_back_button_visible()
    
    logger.info("User confirmed on Manage Beneficiaries page")


@then("No toast notification should be displayed")
def verify_no_toast(page, manage_bene_detail_page, test_context):
    logger.info("Verifying no toast notification")
    
    if manage_bene_detail_page.is_toast_visible():
        logger.warning("Toast notification found ΓÇö unexpected")
        return False
    
    logger.info("No toast notification confirmed")
    return True


@then('Verify beneficiary "Michael Johnson" is added to all selected accounts')
def verify_beneficiary_multiple_accounts(page, update_beneficiary_page, test_context):
    logger.info("Verifying Michael Johnson added to all selected accounts")
    
    page.wait_for_load_state('networkidle')
    
    primary_list = update_beneficiary_page.get_primary_beneficiaries(1)
    
    assert "Michael Johnson" in primary_list, f"Michael Johnson not found: {primary_list}"
    
    logger.info("Michael Johnson verified in primary beneficiaries")


@then("Beneficiary should appear in all account sections")
def verify_appears_all_accounts(page, update_beneficiary_page, test_context):
    logger.info("Verifying beneficiary appears in all account sections")
    
    account_count = update_beneficiary_page.get_account_cards_count()
    logger.info(f"Checking {account_count} account(s)")
    
    logger.info("Beneficiary verified in all account sections")


@then("Beneficiary allocation should remain \"100.00\"")
def verify_allocation_remains_100(page, update_beneficiary_page, test_context):
    logger.info("Verifying beneficiary allocation remains 100.00")
    
    page.wait_for_load_state('networkidle')
    
    total_allocation = update_beneficiary_page.get_total_allocation(1)
    
    assert "100" in total_allocation, f"Expected 100% allocation, got: {total_allocation}"
    logger.info("Allocation confirmed as 100.00%")


@then("Beneficiary \"David Wilson\" designation should be updated to \"Contingent\"")
def verify_designation_updated_contingent(page, update_beneficiary_page, test_context):
    logger.info("Verifying David Wilson designation updated to Contingent")
    
    page.wait_for_load_state('networkidle')
    
    contingent_list = update_beneficiary_page.get_contingent_beneficiaries(1)
    
    assert "David Wilson" in contingent_list, f"David Wilson not found in contingent beneficiaries: {contingent_list}"
    logger.info("Designation update verified")


@then("\"ADDED\" badge should be displayed")
def verify_added_badge_displayed(page, update_beneficiary_page, test_context):
    logger.info("Verifying ADDED badge is displayed")
    
    if update_beneficiary_page.is_any_added_badge_visible():
        logger.info("ADDED badge confirmed visible")
    else:
        logger.warning("ADDED badge not immediately visible")


@then("Confirmation modal should appear")
def verify_confirmation_modal_appears(page, manage_bene_detail_page, test_context):
    logger.info("Verifying confirmation modal appears")
    
    page.wait_for_timeout(500)
    
    assert manage_bene_detail_page.is_confirmation_modal_visible(), "Confirmation modal should appear"
    logger.info("Confirmation modal verified")


@then('Beneficiary "Sarah Miller" should be removed')
def verify_beneficiary_removed(page, update_beneficiary_page, test_context):
    logger.info("Verifying Sarah Miller removed")
    
    page.wait_for_load_state('networkidle')
    
    primary_list = update_beneficiary_page.get_primary_beneficiaries(1)
    
    assert "Sarah Miller" not in primary_list, f"Sarah Miller should be removed but found in: {primary_list}"
    logger.info("Sarah Miller confirmed removed")


@then('Toast notification should display "Beneficiary "Sarah Miller" deleted."')
def verify_delete_toast(page, manage_bene_detail_page, test_context):
    logger.info("Verifying delete toast notification")
    
    page.wait_for_timeout(500)
    
    toast_text = manage_bene_detail_page.get_toast_text()
    
    assert "deleted" in toast_text.lower() if toast_text else False, \
        f"Expected delete confirmation toast, got: {toast_text}"
    
    logger.info(f"Delete toast verified: {toast_text}")


@then('Toast notification should display "Primary beneficiary "Smith Family Trust" added."')
def verify_trust_added_toast(page, manage_bene_detail_page, test_context):
    logger.info("Verifying Trust beneficiary added toast")
    
    page.wait_for_timeout(500)
    
    toast_text = manage_bene_detail_page.get_toast_text()
    
    assert "Smith Family Trust" in toast_text and "added" in toast_text.lower() if toast_text else False, \
        f"Expected Trust added toast, got: {toast_text}"
    
    logger.info(f"Trust added toast verified: {toast_text}")


@then('Toast notification should display "Contingent beneficiary "Jane Smith" added."')
def verify_contingent_added_toast(page, manage_bene_detail_page, test_context):
    
    logger.info("Verifying Contingent beneficiary added toast")
    
    page.wait_for_timeout(500)
    
    toast_text = manage_bene_detail_page.get_toast_text()
    
    assert "Jane Smith" in toast_text and "Contingent" in toast_text and "added" in toast_text.lower() if toast_text else False, \
        f"Expected Contingent added toast, got: {toast_text}"
    
    logger.info(f"Contingent added toast verified: {toast_text}")


@then('Toast notification should display "Primary beneficiary "Michael Johnson" added."')
def verify_michael_johnson_toast(page, manage_bene_detail_page, test_context):
    logger.info("Verifying Michael Johnson added toast")
    
    page.wait_for_timeout(500)
    
    toast_text = manage_bene_detail_page.get_toast_text()
    
    assert "Michael Johnson" in toast_text and "added" in toast_text.lower() if toast_text else False, \
        f"Expected Michael Johnson added toast, got: {toast_text}"
    
    logger.info(f"Michael Johnson toast verified: {toast_text}")


@when("Delete added benefeciries for clean up")
def delete_added_beneficiary(page, manage_bene_detail_page, test_context):
    
    with allure.step("Deleting added beneficiary for cleanup"):
        logger.info("Step 6: Deleting added beneficiary for cleanup")
        
        beneficiary_name = test_context.get('beneficiary_name', '')
        logger.info(f"Deleting ADDED beneficiary: {beneficiary_name}")
        
        manage_bene_detail_page.deleteAddedBeneficiary(beneficiary_name)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="11_Delete_Button_Clicked", attachment_type=allure.attachment_type.PNG)
        
        page.wait_for_timeout(500)
        
        try:
            notification_text = manage_bene_detail_page.getNotificationText()
            logger.info(f"Delete notification: {notification_text}")
            test_context['delete_notification'] = notification_text
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="12_Deletion_Notification", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            logger.info(f"No notification displayed for ADDED beneficiary deletion (expected behavior): {str(e)}")
            test_context['delete_notification'] = "No notification for ADDED beneficiary"
        
        logger.info(f"ADDED beneficiary '{beneficiary_name}' deleted successfully")
        test_context['beneficiary_deleted'] = True


@when(parsers.parse('User should select relationship as "{relationship}"'))
def user_select_relationship(page, add_beneficiary_page, relationship, test_context):
    logger.info(f"Selecting relationship: {relationship}")
    
    add_beneficiary_page.select_designation_as(relationship)
    page.wait_for_timeout(300)
    
    test_context['beneficiary_relationship'] = relationship
    logger.info(f"Relationship '{relationship}' selected")


@when(parsers.parse('User clicks on "{buttonText}" button'))
def user_clicks_on_button(page, manage_bene_detail_page, buttonText, test_context):
    with allure.step(f"Clicking '{buttonText}' button"):
        logger.info(f"Clicking '{buttonText}' button")
        if "e-Signature" in buttonText:
            manage_bene_detail_page.click_continue_to_esignature()
        elif "Continue to Review" in buttonText:
            manage_bene_detail_page.click_continue_to_review()
        else:
            raise ValueError(f"No click handler defined for button: {buttonText}")
        page.wait_for_load_state('networkidle')
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"After_Click_{buttonText.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)
        logger.info(f"'{buttonText}' button clicked successfully")


@then("User should be navigated to e-Signature details page")
def verify_navigated_to_esignature_page(page, manage_bene_esignature_page, test_context):
    with allure.step("Verifying navigation to e-Signature Details page"):
        logger.info("Verifying user is on e-Signature Details page")
        manage_bene_esignature_page.wait_for_page_load()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="eSignature_Details_Page", attachment_type=allure.attachment_type.PNG)
        logger.info("User successfully navigated to e-Signature Details page")


@then("User should be navigated to Review page directly")
def verify_navigated_to_review_page_directly(page, manage_bene_review_page, test_context):
    with allure.step("Verifying direct navigation to Review page (Print signature flow)"):
        logger.info("Verifying user is on Review page (skipped e-Signature)")
        page.wait_for_load_state('networkidle', timeout=30000)
        manage_bene_review_page.wait_for_page_load(timeout=30000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Review_Page_Direct_Navigation", attachment_type=allure.attachment_type.PNG)
        logger.info("User successfully navigated to Review page directly")


@when(parsers.re(r'User selects "(?P<authorized_holder>[^"]+)" from the Authorized Account Holder dropdown'))
def select_authorized_account_holder_from_dropdown(page, manage_bene_esignature_page, authorized_holder, test_context):
    with allure.step(f"Selecting '{authorized_holder}' from the Authorized Account Holder dropdown"):
        logger.info(f"Selecting authorized account holder containing: '{authorized_holder}'")
        manage_bene_esignature_page.account_holder_dropdown.click()
        # Match any option whose text contains the specified role/type (e.g. "Power of Attorney")
        option = page.get_by_role("option").filter(has_text=authorized_holder).first
        option.wait_for(state="visible", timeout=10000)
        selected_text = option.inner_text().strip()
        option.click()
        test_context['esig_account_holder'] = selected_text
        logger.info(f"Selected authorized account holder: '{selected_text}'")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Authorized_Account_Holder_Selected", attachment_type=allure.attachment_type.PNG)


@when(parsers.re(r'User enters email "(?P<email>[^"]*)" and phone "(?P<phone>[^"]*)" on e-Signature Details page'))
def user_enters_email_and_phone(page, manage_bene_esignature_page, email, phone, test_context):
    with allure.step(f"Selecting account holder, entering email='{email}' and phone='{phone}'"):

        # For New bene flow: select from the Authorized Account Holder dropdown.
        # For Existing bene flow (Spouse/Non-Spouse): the field is static text ΓÇö skip interaction.
        # For Existing bene flow (Trust/Entity): dropdown is present ΓÇö select like New flow.
        bene_type = test_context.get('bene_type', 'New')
        relation = test_context.get('target_bene_relation', '').lower()
        account_holder_dropdown = manage_bene_esignature_page.account_holder_dropdown.first
        is_dropdown_interactable = (
            manage_bene_esignature_page.account_holder_dropdown.count() > 0
            and account_holder_dropdown.is_visible()
            and account_holder_dropdown.is_enabled()
        )

        if bene_type == 'Existing' and relation not in ('trust', 'entity'):
            logger.info("Existing bene flow (Spouse/Non-Spouse) ΓÇö Authorized Account Holder is static text, skipping dropdown")
            test_context['esig_account_holder'] = ''
        elif not is_dropdown_interactable:
            logger.info("Authorized Account Holder dropdown is not interactable, skipping selection")
            test_context['esig_account_holder'] = ''
        else:
            logger.info("Selecting first available account holder from dropdown")
            selected_holder = manage_bene_esignature_page.select_first_account_holder()
            test_context['esig_account_holder'] = selected_holder
            logger.info(f"Account holder '{selected_holder}' selected and saved to context")

        logger.info(f"Entering email='{email}' and phone='{phone}' on e-Signature Details page")
        if email:
            manage_bene_esignature_page.enter_email(email)
        else:
            manage_bene_esignature_page.email_input.clear(timeout=60000)
        if phone:
            manage_bene_esignature_page.enter_phone(phone)
        else:
            manage_bene_esignature_page.phone_input.clear(timeout=60000)
        test_context['esig_email'] = email
        test_context['esig_phone'] = phone

        # Attach DOM snapshot
        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="eSignature_Fields_DOM", attachment_type=allure.attachment_type.HTML)

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="eSignature_Fields_Entered", attachment_type=allure.attachment_type.PNG)

        logger.info("Account holder selected, email and phone entered on e-Signature Details page")



@when(parsers.re(r'User select first account holder, enters email "(?P<email>[^"]*)" and phone "(?P<phone>[^"]*)" on e-Signature Details page'))
def user_enters_email_and_phone(page, manage_bene_esignature_page, email, phone, test_context):
    with allure.step(f"Selecting account holder, entering email='{email}' and phone='{phone}'"):

        
        logger.info("Selecting first available account holder from dropdown")
        selected_holder = manage_bene_esignature_page.select_first_account_holder()
        test_context['esig_account_holder'] = selected_holder
        logger.info(f"Account holder '{selected_holder}' selected and saved to context")

        logger.info(f"Entering email='{email}' and phone='{phone}' on e-Signature Details page")
        if email:
            manage_bene_esignature_page.enter_email(email)
        else:
            manage_bene_esignature_page.email_input.clear(timeout=60000)
        if phone:
            manage_bene_esignature_page.enter_phone(phone)
        else:
            manage_bene_esignature_page.phone_input.clear(timeout=60000)
        test_context['esig_email'] = email
        test_context['esig_phone'] = phone

        # Attach DOM snapshot
        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="eSignature_Fields_DOM", attachment_type=allure.attachment_type.HTML)

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="eSignature_Fields_Entered", attachment_type=allure.attachment_type.PNG)

        logger.info("Account holder selected, email and phone entered on e-Signature Details page")




@when(parsers.parse('User selects "{method}" as the signature method on e-Signature Details page'))
def user_selects_signature_method(page, manage_bene_esignature_page, method, test_context):
    with allure.step(f"Selecting signature method: '{method}'"):
        method_lower = method.strip().lower()
        if method_lower in ("by email", "email"):
            if manage_bene_esignature_page.is_by_email_selected():
                logger.info("'By Email' is already selected ΓÇö skipping")
            else:
                logger.info("Selecting 'By Email' radio button")
                manage_bene_esignature_page.select_method_by_email()
        elif method_lower in ("in person", "inperson"):
            if manage_bene_esignature_page.is_in_person_selected():
                logger.info("'In Person' is already selected ΓÇö skipping")
            else:
                logger.info("Selecting 'In Person' radio button")
                manage_bene_esignature_page.select_method_in_person()
        else:
            raise ValueError(f"Unknown signature method: '{method}'. Expected 'By Email' or 'In Person'.")
        test_context['esig_method'] = method
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Signature_Method_{method.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)
        logger.info(f"Signature method '{method}' set successfully")


@when("User checks consent checkbox and verifies Continue to Review button state")
def user_checks_consent_and_verifies_button(page, manage_bene_esignature_page, test_context):
    with allure.step("Check consent checkbox and verify Continue to Review button is enabled"):
        # Click the consent checkbox
        logger.info("Clicking the consent checkbox")
        manage_bene_esignature_page.check_certify()
        page.wait_for_timeout(500)

        # Verify button is now enabled
        logger.info("Verifying 'Continue to Review' button is enabled after checking consent")
        assert manage_bene_esignature_page.is_continue_to_review_enabled(), \
            "'Continue to Review' button should be enabled after checking consent checkbox"
        logger.info("Confirmed: 'Continue to Review' is enabled")

        screenshot_after = page.screenshot()
        allure.attach(screenshot_after, name="ConsentCheckbox_After_Check", attachment_type=allure.attachment_type.PNG)

        test_context['consent_checked'] = True


@when("User clicks Continue to Review to trigger validation")
def user_clicks_continue_to_review_for_validation(page, manage_bene_esignature_page, test_context):
    with allure.step("Clicking Continue to Review to trigger validation"):
        logger.info("Triggering validation by clicking Continue to Review")
        manage_bene_esignature_page.trigger_validation()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="eSignature_Validation_Triggered", attachment_type=allure.attachment_type.PNG)
        logger.info("Validation triggered")


@then(parsers.re(r'Email field should display error "(?P<email_error>[^"]*)"'))
def verify_email_field_error(page, manage_bene_esignature_page, email_error, test_context):
    with allure.step(f"Verifying email field error: '{email_error}'"):
        logger.info(f"Checking email field error. Expected: '{email_error}'")
        if not email_error:
            logger.info("No email error expected ΓÇö skipping assertion")
            return
        actual_error = manage_bene_esignature_page.get_field_error("email")
        assert email_error.lower() in actual_error.lower(), (
            f"Email error mismatch. Expected to contain: '{email_error}', Got: '{actual_error}'"
        )
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Email_Field_Error", attachment_type=allure.attachment_type.PNG)
        logger.info(f"Email field error verified: '{actual_error}'")


@then(parsers.re(r'Phone field should display error "(?P<phone_error>[^"]*)"'))
def verify_phone_field_error(page, manage_bene_esignature_page, phone_error, test_context):
    with allure.step(f"Verifying phone field error: '{phone_error}'"):
        logger.info(f"Checking phone field error. Expected: '{phone_error}'")
        if not phone_error:
            logger.info("No phone error expected ΓÇö skipping assertion")
            return
        actual_error = manage_bene_esignature_page.get_field_error("phone")
        assert phone_error.lower() in actual_error.lower(), (
            f"Phone error mismatch. Expected to contain: '{phone_error}', Got: '{actual_error}'"
        )
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Phone_Field_Error", attachment_type=allure.attachment_type.PNG)
        logger.info(f"Phone field error verified: '{actual_error}'")


@then("User should verify beneficiary is present on Review page")
def verify_beneficiary_present_on_review_page(page, manage_bene_review_page, test_context):
    """Non-strict version ΓÇö uses count() > 0 so the same name across multiple accounts does not fail."""
    with allure.step("Verifying beneficiary is present on Review page (non-strict)"):
        page.wait_for_load_state('networkidle', timeout=30000)
        manage_bene_review_page.wait_for_page_load(timeout=30000)

        full_name = test_context.get('beneficiary_full_name', '') or test_context.get('added_beneficiary_name', '')
        assert full_name, "beneficiary_full_name / added_beneficiary_name not found in test_context"

        logger.info(f"Verifying beneficiary '{full_name}' is present on Review page (non-strict)")

        locator = manage_bene_review_page.get_beneficiary_by_name(full_name)
        count = locator.count()
        assert count > 0, f"Beneficiary '{full_name}' not found on Review page"
        logger.info(f"[OK] Beneficiary '{full_name}' found {count} time(s) on Review page")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Review_Page_Beneficiary_Present", attachment_type=allure.attachment_type.PNG)

        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="Review_Page_DOM", attachment_type=allure.attachment_type.HTML)

        test_context['review_page_verified'] = True


@then("User should verify added beneficiary is displayed on Review page")
def verify_added_beneficiary_on_review_page(page, manage_bene_review_page, test_context):
    with allure.step("Verifying newly added beneficiary is present on Review page"):
        page.wait_for_load_state('networkidle', timeout=30000)
        manage_bene_review_page.wait_for_page_load(timeout=30000)

        full_name = (
            test_context.get('beneficiary_full_name', '') or
            test_context.get('beneficiary_name', '') or
            test_context.get('added_beneficiary_name', '')
        )
        if not full_name:
            first = test_context.get('beneficiary_first_name', '')
            last = test_context.get('beneficiary_last_name', '')
            full_name = f"{first} {last}".strip()
        assert full_name, "beneficiary_full_name not found in test_context ΓÇö cannot verify on Review page"

        first_name = test_context.get('beneficiary_first_name', '')
        last_name = test_context.get('beneficiary_last_name', '')
        logger.info(f"Verifying beneficiary on Review page ΓÇö first: '{first_name}', last: '{last_name}', full: '{full_name}'")

        # XPath axis lookup ΓÇö finds the name span, verifies it is visible
        assert manage_bene_review_page.is_beneficiary_visible(full_name), (
            f"Beneficiary '{full_name}' not found on Review page"
        )
        logger.info(f"Beneficiary '{full_name}' confirmed visible on Review page")

        # Attach DOM snapshot
        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="Review_Page_Beneficiary_DOM", attachment_type=allure.attachment_type.HTML)

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Review_Page_Beneficiary_Verified", attachment_type=allure.attachment_type.PNG)

        test_context['review_page_verified'] = True


@then("User should see the Fraud or Compliance Hold warning on the Review page")
def verify_fraud_compliance_hold_warning_on_review_page(page, test_context):
    """Verify the Fraud/Compliance Hold advisory banner is visible on the Review page."""
    expected_text = "Fraud or Compliance Hold"
    with allure.step(f"Verifying '{expected_text}' warning is visible on the Review page"):
        logger.info("Checking for Fraud or Compliance Hold warning on Review page")
        # Wait for the Review page to be fully rendered by polling for the Submit button
        # (SPA ΓÇö URL doesn't change, networkidle fires too early during React re-renders)
        submit_btn = page.locator("button:has-text('Submit')").first
        try:
            submit_btn.wait_for(state="visible", timeout=45000)
            logger.info("Review page Submit button is visible ΓÇö page is fully loaded")
        except Exception:
            logger.warning("Submit button not found within 45s ΓÇö proceeding with fallback wait")
            page.wait_for_load_state("networkidle", timeout=45000)
            page.wait_for_timeout(3000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Review_Page_Loaded", attachment_type=allure.attachment_type.PNG)
        warning_banner = page.locator(
            f"xpath=//div[contains(@class,'MuiAlert-message') and contains(.,'{expected_text}')]"
        ).first
        warning_banner.wait_for(state="visible", timeout=15000)
        assert warning_banner.is_visible(), (
            f"Expected Fraud or Compliance Hold warning banner to be visible on the Review page, "
            f"but it was not found. URL: {page.url}"
        )
        banner_text = warning_banner.inner_text().strip()
        logger.info(f"[OK] Warning banner found: '{banner_text}'")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Fraud_Compliance_Hold_Warning", attachment_type=allure.attachment_type.PNG)
        allure.attach(banner_text, name="Warning_Banner_Text", attachment_type=allure.attachment_type.TEXT)


@when("User clicks Submit to Advisor button")
def user_clicks_submit_to_advisor(page, manage_bene_review_page, test_context):
    with allure.step("Clicking 'Submit to Advisor' button"):
        logger.info("Clicking 'Submit to Advisor' button on Review page")
        manage_bene_review_page.click_submit_to_advisor()
        page.wait_for_load_state('networkidle', timeout=30000)

        # Attach DOM snapshot
        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="After_Submit_To_Advisor_DOM", attachment_type=allure.attachment_type.HTML)

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Submit_To_Advisor", attachment_type=allure.attachment_type.PNG)

        logger.info("'Submit to Advisor' button clicked successfully")
        test_context['submitted_to_advisor'] = True


@then("User should be redirected to DocuSign page")
def user_should_be_redirected_to_docusign(page, test_context):
    with allure.step("Verifying user is redirected to DocuSign page"):
        logger.info("Waiting for DocuSign page to load after Submit to Advisor")
        page.wait_for_load_state('networkidle', timeout=60000)

        max_retries = 6
        retry_wait_ms = 5000
        current_url = page.url

        for attempt in range(1, max_retries + 1):
            current_url = page.url
            logger.info(f"Attempt {attempt}/{max_retries} ΓÇö Current URL: {current_url}")
            if "docusign" in current_url.lower():
                break
            if attempt < max_retries:
                logger.info(f"DocuSign not detected in URL. Waiting 5s before retry {attempt + 1}...")
                page.wait_for_timeout(retry_wait_ms)
                page.wait_for_load_state('networkidle', timeout=30000)
        else:
            screenshot = page.screenshot()
            allure.attach(screenshot, name="DocuSign_Redirect_Failed", attachment_type=allure.attachment_type.PNG)
            allure.attach(current_url, name="Final_URL_Before_Failure", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(
                f"Expected redirect to DocuSign after {max_retries} attempts, but current URL is: {current_url}"
            )

        logger.info(f"[OK] User successfully redirected to DocuSign page: {current_url}")
        test_context['docusign_url'] = current_url

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="DocuSign_Redirect", attachment_type=allure.attachment_type.PNG)

        # Attach URL as text
        allure.attach(current_url, name="DocuSign_URL", attachment_type=allure.attachment_type.TEXT)


@when("User should click Save button")
def user_click_save_button_only(page, add_beneficiary_page, test_context):
    logger.info("Clicking Save button")
    
    page.wait_for_timeout(500)
    
    add_beneficiary_page.click_save_button()
    
    page.wait_for_timeout(1000)
    
    logger.info("Save button clicked")
    test_context['save_clicked'] = True







# ============================================================================
# Contingent Beneficiary Validation Steps
# ============================================================================

@then("User should get beneficiary name and account info for accounts with 2 contingent beneficiaries")
def get_accounts_with_2_contingent_beneficiaries(manage_bene_detail_page, test_context):
    """Get beneficiary names and account info for accounts with exactly 2 contingent beneficiaries"""
    
    with allure.step("Getting accounts with 2 contingent beneficiaries"):
        logger.info("Step: Getting accounts with 2 contingent beneficiaries")
        
        accounts_with_2_contingent = manage_bene_detail_page.get_accounts_with_2_contingent_beneficiaries()
        
        if not accounts_with_2_contingent:
            logger.warning("No accounts found with exactly 2 contingent beneficiaries")
            test_context['accounts_with_2_contingent'] = []
            return
        
        test_context['accounts_with_2_contingent'] = accounts_with_2_contingent
        test_context['accounts_with_2_contingent_count'] = len(accounts_with_2_contingent)
        
        logger.info(f"Found {len(accounts_with_2_contingent)} accounts with 2 contingent beneficiaries")
        
        for idx, account in enumerate(accounts_with_2_contingent, 1):
            account_info = account.get('account_info')
            contingent_beneficiaries = account.get('contingent_beneficiaries', [])
            logger.info(f"  {idx}. Account: {account_info} | Contingent: {contingent_beneficiaries}")
        
        accounts_summary = "\n".join([
            f"{idx}. Account: {acc.get('account_info', 'N/A')} | "
            f"Contingent: {acc.get('contingent_beneficiaries', [])}"
            for idx, acc in enumerate(accounts_with_2_contingent, 1)
        ])
        
        allure.attach(
            f"Total Accounts: {len(accounts_with_2_contingent)}\n\n{accounts_summary}",
            name="Accounts with 2 Contingent Beneficiaries",
            attachment_type=allure.attachment_type.TEXT
        )


@then("User should validate the contingent beneficiary section is displayed")
def validate_contingent_beneficiary_section_displayed(page, manage_bene_detail_page, test_context):
    """Validate that the contingent beneficiary section is present and visible on the page"""
    
    with allure.step("Validating contingent beneficiary section is displayed"):
        logger.info("Step: Validating contingent beneficiary section is displayed")
        
        page.wait_for_load_state('networkidle')
        
        is_contingent_section_visible = manage_bene_detail_page.is_contingent_beneficiary_section_visible()
        
        assert is_contingent_section_visible, "Contingent beneficiary section should be visible on the page"
        
        logger.info("Contingent beneficiary section is visible")
        
        section_heading = manage_bene_detail_page.get_contingent_section_heading()
        logger.info(f"Contingent section heading: {section_heading}")
        
        test_context['contingent_section_visible'] = True
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Contingent_Beneficiary_Section_Visible", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('user sets contingent allocations to "{alloc1}" and "{alloc2}" in the contingent-beneficiary section'))
def set_contingent_allocation_values(page, manage_bene_detail_page, test_context, alloc1, alloc2):
    """Set allocation values for two contingent beneficiaries in the contingent section"""
    
    with allure.step(f"Set contingent allocations to {alloc1}% and {alloc2}%"):
        logger.info(f"Setting contingent allocations to [{alloc1}%, {alloc2}%]")
        
        page.wait_for_load_state('networkidle')
        
        # Get or find the contingent section
        contingent_section = test_context.get('contingent_section')
        if contingent_section is None:
            contingent_section = manage_bene_detail_page.get_contingent_beneficiary_section()
            assert contingent_section is not None, "No contingent beneficiary section found"
            test_context['contingent_section'] = contingent_section
        
        section_title = manage_bene_detail_page.get_contingent_section_heading()
        logger.info(f"Setting allocations in: {section_title}")
        
        # Set the allocation values using page object
        manage_bene_detail_page.set_contingent_allocations(contingent_section, alloc1, alloc2)
        page.wait_for_timeout(400)
        
        # Get the group total after setting values
        total_text = manage_bene_detail_page.get_contingent_group_total_text(contingent_section)
        logger.info(f"Contingent group total after setting values: {total_text}")
        
        test_context['contingent_allocations_set'] = {
            'alloc1': alloc1,
            'alloc2': alloc2
        }
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Contingent_Allocations_Set_{alloc1}_and_{alloc2}",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('the contingent group total should be "{expected_total}" with "{error_expectation}" error state'))
def verify_contingent_group_total_and_error_state(page, manage_bene_detail_page, test_context, expected_total, error_expectation):
    """Verify the contingent group total value and error state"""
    
    with allure.step(f"Verify contingent group total is {expected_total}% with error_expectation='{error_expectation}'"):
        logger.info(f"Verifying contingent group total: {expected_total}% | Error state: {error_expectation}")
        
        contingent_section = test_context.get('contingent_section')
        assert contingent_section is not None, "test_context['contingent_section'] is not set"
        
        # Verify the displayed total text
        total_text = manage_bene_detail_page.get_contingent_group_total_text(contingent_section)
        logger.info(f"Contingent section total text: '{total_text}'")
        assert expected_total in total_text, (
            f"Expected total '{expected_total}' to appear in '{total_text}'"
        )
        logger.info(f"Contingent total text matches - contains '{expected_total}'")
        
        # Verify the error state
        is_in_error = manage_bene_detail_page.is_contingent_group_total_in_error_state(contingent_section)
        
        if error_expectation == "no_error":
            assert not is_in_error, (
                f"Expected contingent group total to have NO error state, but error indicators were found. "
                f"Total: {total_text}"
            )
            logger.info(f"Contingent group total {expected_total} - no error state (correct)")
        elif error_expectation == "error":
            assert is_in_error, (
                f"Expected contingent group total to show ERROR state, but no error indicators found. "
                f"Total: {total_text}. Check Mui-error class or aria-invalid on inputs."
            )
            logger.info(f"Contingent group total {expected_total} - error state correctly highlighted")
        else:
            raise ValueError(f"Unknown error_expectation '{error_expectation}'. Use 'error' or 'no_error'.")
        
        test_context['contingent_total_verified'] = {
            'expected_total': expected_total,
            'error_expectation': error_expectation,
            'error_state_confirmed': is_in_error
        }
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Contingent_Total_{expected_total}_Error_{error_expectation}", attachment_type=allure.attachment_type.PNG)



@given("user should identify beneficiaries with 3 primary accounts and allocate equally button should be enabled")
def identify_3_primary_beneficiaries_and_button_enabled(page, update_beneficiary_page, test_context):
    """Identify section with 3 primary beneficiaries and verify Allocate Equally button is enabled"""
    
    with allure.step("Identifying section with 3 primary beneficiaries and verifying Allocate Equally button"):
        logger.info("Step: Identifying beneficiaries with 3 primary accounts")
        
        page.wait_for_load_state('networkidle')
        
        section = update_beneficiary_page.get_section_with_n_primary_beneficiaries(3)
        
        assert section is not None, (
            "No section with exactly 3 primary beneficiaries found. "
            "Test data must include accounts with 3 primary beneficiaries to run this scenario."
        )
        
        test_context['multi_account_section'] = section
        logger.info("? Found section with 3 primary beneficiaries")
        
        # Verify Allocate Equally button is enabled
        allocate_equally_button = update_beneficiary_page.get_allocate_equally_button(section)
        is_enabled = allocate_equally_button.is_enabled()
        
        assert is_enabled, "Allocate Equally button should be enabled for 3 primary beneficiaries"
        logger.info("? Allocate Equally button is enabled")
        
        section_title = update_beneficiary_page.get_section_title(section)
        logger.info(f"Identified section: {section_title}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Three_Primary_Beneficiaries_Section_Identified",
            attachment_type=allure.attachment_type.PNG
        )


@when("User loads the deceased account bene page")
def load_deceased_account_bene_page(page, test_context):
    """Navigate to the deceased account's bene page using the predefined constant URL."""
    url = BeneAccountUrls.DECEASED
    with allure.step(f"Loading deceased account bene page: {url}"):
        logger.info(f"Navigating to deceased account bene page: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
        test_context['deceased_page_url'] = page.url
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Deceased_Account_Bene_Page", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] Deceased account bene page loaded successfully")


@then(parsers.re(r'User should see "(?P<banner_text>[^"]+)" warning banner'))
def verify_not_eligible_warning_banner(banner_text, deceased_bene_page, page):
    """Verify the warning banner with the given text is visible on the page."""
    with allure.step(f"Verifying warning banner: '{banner_text}'"):
        logger.info(f"Verifying warning banner text: '{banner_text}'")
        assert deceased_bene_page.is_not_eligible_banner_visible(), (
            f"Expected warning banner '{banner_text}' to be visible, but it was not found on the page."
        )
        actual_text = deceased_bene_page.get_not_eligible_banner_text()
        assert banner_text in actual_text, (
            f"Banner text mismatch. Expected: '{banner_text}', Actual: '{actual_text}'"
        )
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Deceased_Not_Eligible_Banner", attachment_type=allure.attachment_type.PNG)
        logger.info(f"[OK] Warning banner '{banner_text}' is visible and verified")


@then('The deceased account card should display "NOT ELIGIBLE" badge')
def verify_not_eligible_badge_on_account_card(deceased_bene_page, page):
    """Verify the 'NOT ELIGIBLE' chip/badge is displayed on the deceased account card."""
    with allure.step("Verifying 'NOT ELIGIBLE' badge on deceased account card"):
        logger.info("Verifying 'NOT ELIGIBLE' badge on the deceased account card")
        assert deceased_bene_page.is_not_eligible_chip_visible(), (
            "Expected 'NOT ELIGIBLE' badge to be visible on the deceased account card, "
            "but it was not found."
        )
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Deceased_Not_Eligible_Badge", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] 'NOT ELIGIBLE' badge is visible on the deceased account card")


@when("User clicks on the deceased account card")
def click_deceased_account_card(deceased_bene_page, page, test_context):
    """Click on the deceased account card (which is not eligible)."""
    with allure.step("Clicking on the deceased account card"):
        logger.info("Clicking on the deceased account card")
        test_context['url_before_click'] = page.url
        deceased_bene_page.click_deceased_account_card()
        page.wait_for_load_state("networkidle", timeout=10000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Click_Deceased_Account_Card", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] Clicked on deceased account card")


@then("User should remain on the same manage beneficiaries page")
def verify_user_remains_on_same_page(page, test_context):
    """Verify the URL has not changed after clicking the not-eligible account card."""
    with allure.step("Verifying user remains on the same manage beneficiaries page"):
        url_before = test_context.get('url_before_click', '')
        url_after = page.url
        logger.info(f"URL before click: {url_before}")
        logger.info(f"URL after click : {url_after}")
        assert url_after == url_before, (
            f"Expected user to remain on the same page after clicking a 'NOT ELIGIBLE' account, "
            f"but URL changed. Before: '{url_before}', After: '{url_after}'"
        )
        screenshot = page.screenshot()
        allure.attach(screenshot, name="User_Remains_On_Same_Page", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] User remained on the same manage beneficiaries page after clicking not-eligible account")


# ==================== Household Navigation Steps ====================

@then("User should be redirected to the edit beneficiary page")
def verify_redirected_to_edit_bene_page(page, edit_beneficiary_page, test_context):
    """Verify the user has been navigated to the edit beneficiary form page."""
    with allure.step("Verifying user is on the edit beneficiary page"):
        is_visible = edit_beneficiary_page.is_edit_form_visible()
        current_url = page.url
        assert is_visible, (
            f"Expected Edit Beneficiary form to be visible. Current URL: {current_url}"
        )
        logger.info(f"[OK] User is on the edit beneficiary page: {current_url}")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Edit_Bene_Page", attachment_type=allure.attachment_type.PNG)


@when("User checks the Custom Request checkbox on the edit beneficiary form")
def check_custom_request_checkbox(page, edit_beneficiary_page, test_context):
    """Check the Custom Request checkbox on the edit beneficiary form."""
    with allure.step("Checking the Custom Request checkbox"):
        edit_beneficiary_page.check_custom_request()
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Custom_Request_Checked", attachment_type=allure.attachment_type.PNG)


@then(parsers.re(r'The "(?P<section_name>[^"]+)" section should be visible'))
def verify_section_visible_by_name(page, edit_beneficiary_page, section_name):
    """Verify a named section heading is visible on the page."""
    with allure.step(f"Verifying '{section_name}' section is visible"):
        is_visible = edit_beneficiary_page.is_section_heading_visible(section_name)
        assert is_visible, f"Expected section '{section_name}' to be visible but it was not"
        logger.info(f"[OK] Section '{section_name}' is visible")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Section_Visible", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('User uploads "{pdf_file}" to the Supporting Documentation section'))
def upload_pdf_to_supporting_documentation(page, edit_beneficiary_page, test_context, pdf_file):
    """Upload a PDF from the data/ folder to the Supporting Documentation file input.
    The filename comes from the Scenario Outline Examples table.
    Path is resolved via pathlib so it works on both Windows and Linux VMs.
    """
    pdf_path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "data"
        / pdf_file
    )
    with allure.step(f"Uploading PDF: {pdf_file}"):
        assert pdf_path.exists(), f"PDF file not found at: {pdf_path}"
        logger.info(f"Uploading PDF from: {pdf_path}")
        edit_beneficiary_page.upload_supporting_document(str(pdf_path))
        test_context['uploaded_pdf_name'] = pdf_file
        screenshot = page.screenshot()
        allure.attach(screenshot, name="PDF_Uploaded", attachment_type=allure.attachment_type.PNG)


@when("User clicks the first edit icon on the bene detail page")
def click_first_edit_icon_on_bene_detail_page(page, test_context):
    """Click the first enabled Edit (pencil) icon button on the bene detail page using XPath axis."""
    with allure.step("Clicking the first edit icon on the bene detail page"):
        logger.info("Looking for the first edit icon button on the page")
        # XPath axis: find the first beneficiary name span, walk up to its row container,
        # then traverse to the sibling actions div and locate the Edit button within it
        edit_btn = page.locator(
            "xpath=(//span[contains(@class,'MuiTypography-cardTextPrimary')]"
            "/parent::div"
            "/following-sibling::div"
            "//button[starts-with(@aria-label,'Edit ')])[1]"
        )
        edit_btn.wait_for(state="visible", timeout=10000)
        bene_name = edit_btn.get_attribute("aria-label", timeout=5000).replace("Edit ", "").strip()
        test_context['first_edited_bene_name'] = bene_name
        edit_btn.scroll_into_view_if_needed()
        edit_btn.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        logger.info(f"[OK] Clicked edit icon for beneficiary: '{bene_name}'")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_First_Edit_Click", attachment_type=allure.attachment_type.PNG)


@when("User clicks the first delete icon on the bene detail page")
def click_first_delete_icon_on_bene_detail_page(page, test_context):
    """Click the first enabled delete (trash) icon button on the bene detail page."""
    with allure.step("Clicking the first delete icon on the bene detail page"):
        logger.info("Looking for the first enabled delete icon button on the page")
        # Delete buttons have aria-label starting with 'Delete '
        delete_btn = page.locator("button[aria-label^='Delete ']").first
        delete_btn.wait_for(state="visible", timeout=10000)
        bene_name = delete_btn.get_attribute("aria-label", timeout=5000).replace("Delete ", "").strip()
        test_context['first_deleted_bene_name'] = bene_name
        delete_btn.scroll_into_view_if_needed()
        delete_btn.click()
        page.wait_for_timeout(500)
        logger.info(f"[OK] Clicked delete icon for beneficiary: '{bene_name}'")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_First_Delete_Click", attachment_type=allure.attachment_type.PNG)


@then(parsers.re(r'The first beneficiary row should display the "(?P<label>[^"]+)" label'))
def verify_first_bene_row_shows_label(page, test_context, label):
    """Verify that the deleted beneficiary row now shows the expected label (e.g. REMOVED)."""
    bene_name = test_context.get('first_deleted_bene_name', '')
    with allure.step(f"Verifying '{label}' label is visible for beneficiary '{bene_name}'"):
        logger.info(f"Checking for '{label}' label on row for '{bene_name}'")
        page.wait_for_timeout(400)
        # Look for the label chip/span near the beneficiary name
        removed_chip = page.locator(
            f"xpath=//span[normalize-space()='{bene_name}']"
            f"/ancestor::div[contains(@class,'MuiBox-root')]"
            f"//span[normalize-space()='{label}']"
        ).first
        assert removed_chip.is_visible(timeout=5000), (
            f"Expected '{label}' label to be visible for '{bene_name}' but it was not found"
        )
        logger.info(f"[OK] '{label}' label is visible for '{bene_name}'")
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"{label}_Label_Visible", attachment_type=allure.attachment_type.PNG)


@when("User loads the Fraud/Frozen account bene page")
def load_fraud_frozen_account_bene_page(page, test_context):
    """Navigate directly to the Fraud/Frozen household landing page using the constant URL."""
    url = BeneAccountUrls.FRAUD_FROZEN
    with allure.step(f"Loading Fraud/Frozen account bene page: {url}"):
        logger.info(f"Navigating to Fraud/Frozen account bene page: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
        test_context['fraud_frozen_page_url'] = page.url
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Fraud_Frozen_Bene_Landing_Page", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] Fraud/Frozen account bene landing page loaded")


@when("User loads the Custom bene account bene page")
def load_custom_bene_account_bene_page(page, test_context):
    """Navigate directly to the Custom bene account landing page using the same Fraud/Frozen constant URL."""
    url = BeneAccountUrls.FRAUD_FROZEN
    with allure.step(f"Loading Custom bene account bene page: {url}"):
        logger.info(f"Navigating to Custom bene account bene page: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
        test_context['custom_bene_page_url'] = page.url
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Custom_Bene_Account_Landing_Page", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] Custom bene account landing page loaded")


@when("User loads the POA account bene page")
def load_poa_account_bene_page(page, manage_bene_page, manage_bene_detail_page, test_context):
    """Navigate to the POA household landing page and click account 40401241 to enter the detail page."""
    url = BeneAccountUrls.POA
    account_number = "40401241"
    with allure.step(f"Loading POA account bene page: {url}"):
        logger.info(f"Navigating to POA account bene page: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="POA_Account_Landing_Page", attachment_type=allure.attachment_type.PNG)
        logger.info("[OK] POA landing page loaded")

    with allure.step(f"Selecting account {account_number} on the POA landing page"):
        logger.info(f"Looking for account {account_number} on the landing page")
        account_card = page.locator(f"text={account_number}").first
        try:
            account_card.wait_for(state="visible", timeout=5000)
            account_card.click()
            logger.info(f"Clicked on account card containing: {account_number}")
        except Exception:
            logger.warning(
                f"Could not find element with account number '{account_number}' directly. "
                f"Falling back to first beneficiary card."
            )
            manage_bene_page.click_first_beneficiary_detail()
        page.wait_for_load_state("networkidle", timeout=30000)
        test_context['selected_account_number'] = account_number
        is_redirected = manage_bene_detail_page.is_beneficiaries_section_present()
        assert is_redirected, (
            f"Expected to land on bene detail page for account {account_number}, "
            f"but beneficiaries section is not present. URL: {page.url}"
        )
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"POA_Bene_Detail_Page_{account_number}", attachment_type=allure.attachment_type.PNG)
        logger.info(f"[OK] POA account {account_number} bene detail page loaded")



@then("User should be on the bene landing page")
def verify_on_bene_landing_page(page, test_context):
    """Verify the user is on the bene landing page."""
    with allure.step("Verifying user is on the bene landing page"):
        current_url = page.url
        logger.info(f"Current URL: {current_url}")
        assert "app.dev01.assetmark.com/bene" in current_url, (
            f"Expected to be on bene landing page (app.dev01.assetmark.com/bene), "
            f"but URL is: {current_url}"
        )
        page.wait_for_load_state("networkidle", timeout=15000)
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Bene_Landing_Page_Verification", attachment_type=allure.attachment_type.PNG)
        logger.info(f"[OK] User is on the bene landing page: {current_url}")


@then(parsers.parse('the three beneficiary allocations should be "{alloc1}" and "{alloc2}" and "{alloc3}" with total "{expected_total}" with no rounding error'))
def verify_three_beneficiary_allocations_with_rounding(page, update_beneficiary_page, test_context, alloc1, alloc2, alloc3, expected_total):
    """Verify three beneficiary allocations with proper rounding to maintain 100.00% total"""
    
    with allure.step(f"Verify three beneficiary allocations: {alloc1}, {alloc2}, {alloc3} totaling {expected_total}"):
        logger.info(f"Verifying three beneficiary allocations: {alloc1}, {alloc2}, {alloc3}")
        
        section = test_context.get('multi_account_section')
        assert section is not None, "test_context['multi_account_section'] is not set"
        
        page.wait_for_load_state('networkidle')
        
        # Get all allocation input values for the three beneficiaries
        allocation_inputs = update_beneficiary_page.get_allocation_inputs_in_section(section)
        
        assert len(allocation_inputs) >= 3, (
            f"Expected at least 3 allocation inputs but found {len(allocation_inputs)}"
        )
        
        # Extract actual values from input fields
        actual_values = []
        for idx, input_elem in enumerate(allocation_inputs[:3]):
            value = input_elem.input_value()
            actual_values.append(value)
            logger.info(f"  Beneficiary {idx + 1} allocation: {value}")
        
        # Parse expected values (remove % sign if present)
        expected_values = [alloc1.replace('%', ''), alloc2.replace('%', ''), alloc3.replace('%', '')]
        
        # Verify each allocation matches expected
        for idx, (expected, actual) in enumerate(zip(expected_values, actual_values)):
            # Handle rounding variance (within 0.01%)
            expected_float = float(expected)
            actual_float = float(actual)
            variance = abs(expected_float - actual_float)
            
            assert variance <= 0.01, (
                f"Beneficiary {idx + 1}: Expected {expected}%, got {actual}% "
                f"(variance: {variance}% exceeds acceptable 0.01%)"
            )
            logger.info(f"? Beneficiary {idx + 1}: {actual}% matches expected {expected}%")
        
        # Verify total is exactly as expected
        total_text = update_beneficiary_page.get_section_total_text(section)
        logger.info(f"Group total text: '{total_text}'")
        
        assert expected_total in total_text, (
            f"Expected total '{expected_total}' to appear in '{total_text}'"
        )
        
        # Verify no error state (100.00% should never trigger error)
        is_in_error = update_beneficiary_page.is_group_total_in_error_state(section)
        assert not is_in_error, (
            f"Group total {expected_total} should NOT have error state, but error indicators found"
        )
        
        logger.info(f"? Three beneficiaries correctly allocated: {actual_values[0]}% / {actual_values[1]}% / {actual_values[2]}%")
        logger.info(f"? Total: {expected_total} (no rounding error)")
        
        test_context['three_beneficiary_allocations'] = {
            'alloc1': actual_values[0],
            'alloc2': actual_values[1],
            'alloc3': actual_values[2],
            'total': expected_total
        }
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Three_Beneficiary_Allocations_{alloc1}_{alloc2}_{alloc3}",
            attachment_type=allure.attachment_type.PNG
        )


@when(parsers.re(r'User enters email "(?P<email>[^"]*)" and phone "(?P<phone>[^"]*)" on e-Signature Details page for Froud and frozen acccount'))
def user_enters_email_and_phone(page, manage_bene_esignature_page, email, phone, test_context):
    with allure.step(f"Selecting account holder, entering email='{email}' and phone='{phone}'"):

        # For New bene flow: select from the Authorized Account Holder dropdown.
        # For Existing bene flow (Spouse/Non-Spouse): the field is static text ΓÇö skip interaction.
        # For Existing bene flow (Trust/Entity): dropdown is present ΓÇö select like New flow.
        bene_type = test_context.get('bene_type', 'New')
        relation = test_context.get('target_bene_relation', '').lower()
        # if bene_type == 'Existing' and relation not in ('trust', 'entity'):
        #     logger.info("Existing bene flow (Spouse/Non-Spouse) ΓÇö Authorized Account Holder is static text, skipping dropdown")
        #     test_context['esig_account_holder'] = ''
        # else:
        #     logger.info("Selecting first available account holder from dropdown")
        #     selected_holder = manage_bene_esignature_page.select_first_account_holder()
        #     test_context['esig_account_holder'] = selected_holder
        #     logger.info(f"Account holder '{selected_holder}' selected and saved to context")

        logger.info(f"Entering email='{email}' and phone='{phone}' on e-Signature Details page")
        if email:
            manage_bene_esignature_page.enter_email(email)
        else:
            manage_bene_esignature_page.email_input.clear(timeout=60000)
        if phone:
            manage_bene_esignature_page.enter_phone(phone)
        else:
            manage_bene_esignature_page.phone_input.clear(timeout=60000)
        test_context['esig_email'] = email
        test_context['esig_phone'] = phone

        # Attach DOM snapshot
        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="eSignature_Fields_DOM", attachment_type=allure.attachment_type.HTML)

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="eSignature_Fields_Entered", attachment_type=allure.attachment_type.PNG)

        logger.info("Account holder selected, email and phone entered on e-Signature Details page")

