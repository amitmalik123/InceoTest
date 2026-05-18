"""
Step definitions for Add Beneficiary feature.
Handles all user interactions on the Add Beneficiary form and modal.
"""

import allure
from pytest_bdd import then, when, parsers
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('User should select beneficiary type as "{bene_type}" and relationship type' \
' as "{relation}" and enter first name "{first_name}" and last name "{last_name}" and enter' \
' SSN "{ssn}" and DOB "{dob}" and select at least one account'))
def user_fill_beneficiary_form(page, add_beneficiary_page, bene_type, relation, first_name, last_name, ssn, dob, test_context):
   
    with allure.step("Filling beneficiary form with provided parameters"):
        logger.info("Step 3: Filling beneficiary form with provided parameters")
        
        # Validate Beneficiary heading is present
        logger.info(" - Validating Beneficiary heading")
        is_heading_valid = add_beneficiary_page.validate_beneficiary_heading("Beneficiary")
        assert is_heading_valid, "Beneficiary heading not found or invalid"
        heading_text = add_beneficiary_page.get_beneficiary_heading_text()
        logger.info(f"Beneficiary heading validated: {heading_text}")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="01_Beneficiary_Heading_Validated", attachment_type=allure.attachment_type.PNG)
        
        # Select beneficiary type
        logger.info(f" - Selecting beneficiary type: {bene_type}")
        add_beneficiary_page.select_beneficiary_type_as(bene_type)
        page.wait_for_timeout(300)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="02_Beneficiary_Type_Selected", attachment_type=allure.attachment_type.PNG)
        
        # Select relationship type
        logger.info(f" - Selecting relationship type: {relation}")
        add_beneficiary_page.select_designation_as(relation)
        page.wait_for_timeout(300)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="03_Relationship_Type_Selected", attachment_type=allure.attachment_type.PNG)
        
        if relation.lower() in ['spouse', 'non-spouse']:
            logger.info(f" - Entering first name: {first_name}")
            add_beneficiary_page.enter_first_name(first_name)
            
            logger.info(f" - Entering last name: {last_name}")
            add_beneficiary_page.enter_last_name(last_name)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="04_Name_Fields_Entered", attachment_type=allure.attachment_type.PNG)
            
            logger.info(f" - Entering SSN: {ssn[:3]}-**-{ssn[-4:]}")
            add_beneficiary_page.enter_social_security_number(ssn)
            
            logger.info(f" - Entering Date of Birth: {dob}")
            add_beneficiary_page.enter_date_of_birth(dob)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="05_SSN_DOB_Entered", attachment_type=allure.attachment_type.PNG)
            
        elif relation.lower() == 'trust':
            full_name = f"{first_name} {last_name}"
            logger.info(f" - Entering Trust name: {full_name}")
            add_beneficiary_page.enter_name(full_name)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="04_Trust_Name_Entered", attachment_type=allure.attachment_type.PNG)
            
            logger.info(" - Selecting Tax ID type: Social Security Number (SSN)")
            add_beneficiary_page.selectTaxIdType("Social Security Number (SSN)")
            page.wait_for_timeout(300)
            
            logger.info(f" - Entering Tax ID (SSN): {ssn[:3]}-**-{ssn[-4:]}")
            add_beneficiary_page.enterTaxIdValue(ssn)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="05_Trust_TaxID_Entered", attachment_type=allure.attachment_type.PNG)
            
            logger.info(f" - Entering Date of Trust: {dob}")
            add_beneficiary_page.enter_date_of_trust(dob)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="06_Trust_Date_Entered", attachment_type=allure.attachment_type.PNG)
            
        elif relation.lower() == 'entity':
            full_name = f"{first_name} {last_name}"
            logger.info(f" - Entering Entity name: {full_name}")
            add_beneficiary_page.enter_name(full_name)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="04_Entity_Name_Entered", attachment_type=allure.attachment_type.PNG)
            
            logger.info(f" - Entering TIN: {ssn[:2]}-**-{ssn[-4:]}")
            add_beneficiary_page.enterTinValue(ssn)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="05_Entity_TIN_Entered", attachment_type=allure.attachment_type.PNG)
        
        logger.info(" - Selecting at least one account")
        add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="07_Account_Selected_Form_Complete", attachment_type=allure.attachment_type.PNG)
        
        test_context['beneficiary_first_name'] = first_name
        test_context['beneficiary_last_name'] = last_name
        test_context['beneficiary_ssn'] = ssn
        test_context['beneficiary_dob'] = dob
        test_context['beneficiary_type'] = bene_type
        test_context['beneficiary_relation'] = relation
        test_context['form_filled'] = True
        
        test_context['beneficiary_name'] = f"{first_name} {last_name}"
        logger.info(f"Beneficiary form filled successfully with {bene_type} - {relation} ({first_name} {last_name})")


@when(parsers.parse('User should select beneficiary type as "{bene_type}" and relationship type' \
' as "{relation}" and enter first name "{first_name}" and last name "{last_name}" and enter' \
' SSN "{ssn}" and DOB "{dob}" and select account "{account_number}" as "{designation}"'))
def user_fill_beneficiary_form_with_account_designation(page, add_beneficiary_page, bene_type, relation, first_name, last_name, ssn, dob, account_number, designation, test_context):
   
    with allure.step(f"Filling beneficiary form and selecting account {account_number} as {designation}"):
        logger.info(f"Step: Filling beneficiary form with account {account_number} as {designation}")
        
        logger.info(" - Validating Beneficiary heading")
        is_heading_valid = add_beneficiary_page.validate_beneficiary_heading("Beneficiary")
        assert is_heading_valid, "Beneficiary heading not found or invalid"
        heading_text = add_beneficiary_page.get_beneficiary_heading_text()
        logger.info(f"Beneficiary heading validated: {heading_text}")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="01_Beneficiary_Heading_Validated", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f" - Selecting beneficiary type: {bene_type}")
        add_beneficiary_page.select_beneficiary_type_as(bene_type)
        page.wait_for_timeout(300)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="02_Beneficiary_Type_Selected", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f" - Selecting relationship type: {relation}")
        add_beneficiary_page.select_designation_as(relation)
        page.wait_for_timeout(300)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="03_Relationship_Type_Selected", attachment_type=allure.attachment_type.PNG)
        
        if relation.lower() in ['spouse', 'non-spouse']:
            logger.info(f" - Entering first name: {first_name}")
            add_beneficiary_page.enter_first_name(first_name)
            
            logger.info(f" - Entering last name: {last_name}")
            add_beneficiary_page.enter_last_name(last_name)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="04_Name_Fields_Entered", attachment_type=allure.attachment_type.PNG)
            
            logger.info(f" - Entering SSN: {ssn[:3]}-**-{ssn[-4:]}")
            add_beneficiary_page.enter_social_security_number(ssn)
            
            logger.info(f" - Entering Date of Birth: {dob}")
            add_beneficiary_page.enter_date_of_birth(dob)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="05_SSN_DOB_Entered", attachment_type=allure.attachment_type.PNG)
            
        elif relation.lower() == 'trust':
            full_name = f"{first_name} {last_name}"
            logger.info(f" - Entering Trust name: {full_name}")
            add_beneficiary_page.enter_trust_name(full_name)
            
            logger.info(f" - Entering SSN for Trust: {ssn[:3]}-**-{ssn[-4:]}")
            add_beneficiary_page.enter_social_security_number(ssn)
            
            logger.info(f" - Entering Date of Trust: {dob}")
            add_beneficiary_page.enter_date_of_trust(dob)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="06_Trust_Info_Entered", attachment_type=allure.attachment_type.PNG)
            
        elif relation.lower() == 'entity':
            full_name = f"{first_name} {last_name}"
            logger.info(f" - Entering Entity name: {full_name}")
            add_beneficiary_page.enter_entity_name(full_name)
            
            logger.info(f" - Entering TIN for Entity: {ssn}")
            add_beneficiary_page.enter_tax_identification_number(ssn)
            
            screenshot = page.screenshot()
            allure.attach(screenshot, name="06_Entity_Info_Entered", attachment_type=allure.attachment_type.PNG)
        
        accounts_no_contingent = test_context.get('accounts_no_contingent', [])
        
        if accounts_no_contingent:
            logger.info(f" - Using account from 'no contingent' list at position {account_number}")
            account_index = int(account_number) - 1
            
            if account_index < 0 or account_index >= len(accounts_no_contingent):
                raise ValueError(f"Invalid account number {account_number}. Only {len(accounts_no_contingent)} accounts available in list.")
            
            account_info = accounts_no_contingent[account_index].get('account_info')
            if not account_info:
                raise ValueError(f"Account info not found at position {account_number}")
            
            logger.info(f" - Selecting account '{account_info}' as {designation}")
            add_beneficiary_page.select_account_by_name_with_designation(account_info, designation)
            test_context['selected_account_info'] = account_info
        else:
            logger.info(f" - Selecting account {account_number} as {designation} (index-based)")
            account_index = int(account_number)
            add_beneficiary_page.select_accounts_with_designation(account_index, designation)
        
        page.wait_for_timeout(500)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"07_Account_{account_number}_Selected_As_{designation}", attachment_type=allure.attachment_type.PNG)
        
        test_context['beneficiary_first_name'] = first_name
        test_context['beneficiary_last_name'] = last_name
        test_context['beneficiary_ssn'] = ssn
        test_context['beneficiary_dob'] = dob
        test_context['beneficiary_type'] = bene_type
        test_context['beneficiary_relation'] = relation
        test_context['beneficiary_account_number'] = account_number
        test_context['beneficiary_designation'] = designation
        test_context['form_filled'] = True
        
        test_context['added_beneficiary_name'] = f"{first_name} {last_name}"
        test_context['added_designation'] = designation
        
        test_context['beneficiary_name'] = f"{first_name} {last_name}"
        logger.info(f"Beneficiary form filled successfully: {first_name} {last_name} - Account {account_number} as {designation}")


@when(parsers.parse('User should select account "{account_number}" as "{designation}"'))
def user_select_account_with_designation(page, add_beneficiary_page, account_number, designation, test_context):
   
    with allure.step(f"Selecting account {account_number} as {designation}"):
        logger.info(f"Step: Selecting account {account_number} with designation type {designation}")
        
        account_index = int(account_number)
        add_beneficiary_page.select_accounts_with_designation(account_index, designation)
        page.wait_for_timeout(500)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Account_{account_number}_Selected_As_{designation}", attachment_type=allure.attachment_type.PNG)
        
        test_context['selected_account_number'] = account_number
        test_context['selected_account_designation'] = designation
        
        logger.info(f"Account {account_number} selected as {designation}")


@when("User toggles the Per Stirpes checkbox")
def user_toggles_per_stirpes_checkbox(page, add_beneficiary_page, test_context):

    with allure.step("Checking current Per Stirpes checkbox state and toggling it"):
        logger.info("Step: Checking whether the Per Stirpes checkbox is checked or unchecked, then changing its state")

        initial_state = add_beneficiary_page.is_per_stirpes_checkbox_checked()
        logger.info(f"Initial Per Stirpes checkbox state: {'checked' if initial_state else 'unchecked'}")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Per_Stirpes_Before_Toggle", attachment_type=allure.attachment_type.PNG)

        new_state = add_beneficiary_page.toggle_per_stirpes_checkbox()

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Per_Stirpes_After_Toggle", attachment_type=allure.attachment_type.PNG)

        allure.attach(
            f"Initial state: {'checked' if initial_state else 'unchecked'}\n"
            f"New state: {'checked' if new_state else 'unchecked'}",
            name="Per_Stirpes_Checkbox_State_Change",
            attachment_type=allure.attachment_type.TEXT
        )

        assert initial_state != new_state, "Per Stirpes checkbox state did not change after toggle"

        test_context['per_stirpes_initial_state'] = initial_state
        test_context['per_stirpes_checked'] = new_state

        logger.info(
            f"[OK] Per Stirpes checkbox toggled successfully from "
            f"{'checked' if initial_state else 'unchecked'} to {'checked' if new_state else 'unchecked'}"
        )


@when("User should click Save button and user is redireted back to manage beneficiaries page")
@then("User should click Save button and user is redireted back to manage beneficiaries page")
def user_click_save_button(page, add_beneficiary_page, test_context):
    
    with allure.step("Clicking Save button and redirecting to manage beneficiaries page"):
        logger.info("Step 4: Clicking Save button to submit beneficiary")
        
        # Wait for form to be fully processed and save button to be enabled
        page.wait_for_timeout(1000)
        
        # Click Save button
        add_beneficiary_page.click_save_button()
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="08_Save_Button_Clicked", attachment_type=allure.attachment_type.PNG)
        
        page.wait_for_load_state('networkidle')
        
        add_beneficiary_page.wait_for_modal_to_close()
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="09_Modal_Closed_Redirected_To_Manage_Bene", attachment_type=allure.attachment_type.PNG)
        
        logger.info("Save button clicked - beneficiary submitted and redirected to manage beneficiaries page")
        test_context['beneficiary_saved'] = True


@when("User should verify befinaficieries is added successfully on manage beneficiaries page with correct information")
def user_verify_beneficiary_added(page, manage_bene_detail_page, test_context):
   
    with allure.step("Verifying beneficiary is added successfully on manage beneficiaries page"):
        logger.info("Step 5: Verifying beneficiary details on manage beneficiaries page")
        
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)
        
        first_name = test_context['beneficiary_first_name']
        last_name = test_context['beneficiary_last_name']
        relation = test_context['beneficiary_relation']
        
        full_name = f"{first_name} {last_name}"
        logger.info(f"Looking for beneficiary: {full_name} with relationship: {relation}")
        
        manage_bene_detail_page.verifyBeneficiaryDetails(full_name, relation)
        
        # Save full beneficiary name in context for downstream use
        test_context['beneficiary_full_name'] = full_name
        logger.info(f"Saved beneficiary_full_name to context: {full_name}")

        # Attach DOM snapshot
        dom_snapshot = page.content()
        allure.attach(dom_snapshot, name="10_DOM_Beneficiary_Verified", attachment_type=allure.attachment_type.HTML)

        # Attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name="10_Beneficiary_Verified_On_Manage_Bene_Page", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f"Beneficiary '{full_name}' verified successfully with relationship '{relation}'")
        test_context['beneficiary_verified'] = True


@when(parsers.re(r'User should fill beneficiary form with type "(?P<bene_type>.*)" and relation "(?P<relation>.*)" ' \
r'and first name "(?P<first_name>.*)" and last name "(?P<last_name>.*)" and SSN "(?P<ssn>.*)" ' \
r'and DOB "(?P<dob>.*)" for validation'))
def user_fill_beneficiary_form_for_validation(page, add_beneficiary_page, bene_type, relation, first_name, last_name, ssn, dob, test_context):
    """
    Validation-specific step that allows empty/invalid fields for testing error messages.
    Does not assert on fields being filled, just attempts to enter provided values.
    """
    with allure.step("Filling beneficiary form for validation testing"):
        logger.info("Filling beneficiary form with validation data (may include empty/invalid fields)")
        
        logger.info(f" - Selecting beneficiary type: {bene_type}")
        add_beneficiary_page.select_beneficiary_type_as(bene_type)
        page.wait_for_timeout(300)
        
        logger.info(f" - Selecting relationship type: {relation}")
        add_beneficiary_page.select_designation_as(relation)
        page.wait_for_timeout(300)
        
        if relation.lower() in ['spouse', 'non-spouse']:
            if first_name:
                logger.info(f" - Entering first name: {first_name}")
                add_beneficiary_page.enter_first_name(first_name)
            else:
                logger.info(" - Skipping first name (empty for validation test)")
            
            if last_name:
                logger.info(f" - Entering last name: {last_name}")
                add_beneficiary_page.enter_last_name(last_name)
            else:
                logger.info(" - Skipping last name (empty for validation test)")
            
            if ssn:
                logger.info(f" - Entering SSN: {ssn[:3] if len(ssn) >= 3 else ssn}-**-****")
                add_beneficiary_page.enter_social_security_number(ssn)
            else:
                logger.info(" - Skipping SSN (empty for validation test)")
            
            if dob:
                logger.info(f" - Entering DOB: {dob}")
                add_beneficiary_page.enter_date_of_birth(dob)
            else:
                logger.info(" - Skipping DOB (empty for validation test)")
        
        elif relation.lower() == 'trust':
            name_parts = [first_name, last_name]
            full_name = ' '.join(part for part in name_parts if part)
            
            if full_name:
                logger.info(f" - Entering Trust name: {full_name}")
                add_beneficiary_page.enter_name(full_name)
            else:
                logger.info(" - Skipping Trust name (empty for validation test)")
            
            if ssn:
                logger.info(" - Selecting Tax ID type: Social Security Number (SSN)")
                add_beneficiary_page.selectTaxIdType("Social Security Number (SSN)")
                page.wait_for_timeout(300)
                add_beneficiary_page.enterTaxIdValue(ssn)
            else:
                logger.info(" - Skipping Tax ID (empty for validation test)")
            
            if dob:
                logger.info(f" - Entering Date of Trust: {dob}")
                add_beneficiary_page.enter_date_of_trust(dob)
            else:
                logger.info(" - Skipping Date of Trust (empty for validation test)")
        
        elif relation.lower() == 'entity':
            name_parts = [first_name, last_name]
            full_name = ' '.join(part for part in name_parts if part)
            
            if full_name:
                logger.info(f" - Entering Entity name: {full_name}")
                add_beneficiary_page.enter_name(full_name)
            else:
                logger.info(" - Skipping Entity name (empty for validation test)")
            
            if ssn:
                logger.info(f" - Entering TIN: {ssn[:2] if len(ssn) >= 2 else ssn}-**-****")
                add_beneficiary_page.enterTinValue(ssn)
            else:
                logger.info(" - Skipping TIN (empty for validation test)")
        
        logger.info(" - Selecting at least one account")
        add_beneficiary_page.selectAtLeastOneAccountForBeneficiary()
        
        test_context['validation_first_name'] = first_name if first_name else ''
        test_context['validation_last_name'] = last_name if last_name else ''
        test_context['validation_ssn'] = ssn if ssn else ''
        test_context['validation_dob'] = dob if dob else ''
        test_context['validation_bene_type'] = bene_type
        test_context['validation_relation'] = relation
        
        logger.info(f"Validation form filled - Type: {bene_type}, Relation: {relation}")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Validation_Form_State", attachment_type=allure.attachment_type.PNG)


@when(parsers.parse('User should select beneficiary type as "{bene_type}" and relationship type as "{relation}" and enter first name "{first_name}" and last name "{last_name}" and SSN "{ssn}" and DOB "{dob}" and do not select any account'))
def user_fill_form_without_account_selection(page, add_beneficiary_page, test_context, bene_type, relation, first_name, last_name, ssn, dob):
    """Fill beneficiary form without selecting any account to trigger validation error."""
    
    with allure.step(f"Filling form without account selection: {bene_type}, {relation}, {first_name} {last_name}"):
        logger.info(f"Filling form without selecting any account: {bene_type}, {relation}, {first_name} {last_name}")
        
        page.wait_for_load_state('networkidle')
        
        logger.info(f" - Selecting beneficiary type: {bene_type}")
        add_beneficiary_page.select_beneficiary_type_as(bene_type)
        page.wait_for_timeout(300)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Beneficiary_Type_Selected", attachment_type=allure.attachment_type.PNG)
        
        logger.info(f" - Selecting relationship type: {relation}")
        add_beneficiary_page.select_designation_as(relation)
        page.wait_for_timeout(300)
        
        logger.info(f" - Entering first name: {first_name}")
        add_beneficiary_page.enter_first_name(first_name)
        
        logger.info(f" - Entering last name: {last_name}")
        add_beneficiary_page.enter_last_name(last_name)
        
        logger.info(f" - Entering SSN: {ssn}")
        add_beneficiary_page.enter_social_security_number(ssn)
        
        logger.info(f" - Entering DOB: {dob}")
        add_beneficiary_page.enter_date_of_birth(dob)
        
        logger.info(" - Intentionally skipping account selection to trigger validation")
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Form_Filled_No_Account_Selected", attachment_type=allure.attachment_type.PNG)
        
        logger.info("Form filled without account selection")
        test_context['form_filled'] = True
        test_context['beneficiary_first_name'] = first_name
        test_context['beneficiary_last_name'] = last_name


@then(parsers.parse('Verify the beneficiary "{first_name} {last_name}" is added successfully with designation "{designation}"'))
def verify_beneficiary_added_with_designation(page, manage_bene_detail_page, first_name, last_name, designation, test_context):
   
    with allure.step(f"Verifying beneficiary '{first_name} {last_name}' is added in {designation} section"):
        logger.info(f"Step: Verifying beneficiary is added successfully in {designation} section")
        
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"01_Before_Verify_{first_name}_{last_name}_{designation}", attachment_type=allure.attachment_type.PNG)
        
        stored_beneficiary_name = test_context.get('added_beneficiary_name')
     
        beneficiary_name_to_verify = stored_beneficiary_name or f"{first_name} {last_name}"
        
        account_identifier = test_context.get('selected_account_info')
        
        is_verified = manage_bene_detail_page.verify_beneficiary_in_designation_section(
            beneficiary_name=beneficiary_name_to_verify,
            designation=designation,
            account_identifier=account_identifier
        )
        
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"02_After_Verify_{first_name}_{last_name}_{designation}_{'PASS' if is_verified else 'FAIL'}", attachment_type=allure.attachment_type.PNG)
        
        assert is_verified, "Beneficiary was not added successfully"

        test_context['beneficiary_full_name'] = beneficiary_name_to_verify
        logger.info(f"Saved beneficiary_full_name to context: {beneficiary_name_to_verify}")


@then('click on edit button for the added beneficiary and verify the edit beneficiary form is displayed with correct information')
def click_edit_and_verify_form(page, manage_bene_detail_page, edit_beneficiary_page, test_context):
    beneficiary_name = test_context.get('added_beneficiary_name', '')
    relation = test_context.get('beneficiary_relation', '')
    first_name = test_context.get('beneficiary_first_name', '')
    last_name = test_context.get('beneficiary_last_name', '')

    with allure.step(f"Click Edit button and verify form for '{beneficiary_name}'"):
        logger.info(f"Step: Clicking Edit button for '{beneficiary_name}'")

        page.wait_for_load_state('networkidle')
        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"01_Before_Edit_Click_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        manage_bene_detail_page.click_edit_button(beneficiary_name)

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(800)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"02_Edit_Form_Opened_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        is_visible = edit_beneficiary_page.is_edit_form_visible()
        assert is_visible, "Edit Beneficiary form did not appear after clicking Edit button"
        logger.info("[OK] Edit Beneficiary form is visible")

        is_correct = edit_beneficiary_page.verify_form_info(first_name, last_name, relation)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"03_Form_Verification_{'PASS' if is_correct else 'FAIL'}_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        assert is_correct, (
            f"Edit form data mismatch for '{beneficiary_name}': "
            f"expected first='{first_name}', last='{last_name}', relation='{relation}'"
        )
        logger.info(f"[OK] Edit form verified ΓÇö data matches for '{beneficiary_name}'")


@then(parsers.parse('change the designation to "{designation}" and save'))
def change_designation_and_save(page, edit_beneficiary_page, test_context, designation):
    beneficiary_name = test_context.get('added_beneficiary_name', '')

    with allure.step(f"Change designation to '{designation}' and save for '{beneficiary_name}'"):
        logger.info(f"Step: Changing designation to '{designation}' for '{beneficiary_name}'")

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"01_Before_Designation_Change_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        edit_beneficiary_page.select_designation_for_active_account(designation)
        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"02_Designation_{designation}_Selected_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        edit_beneficiary_page.click_save()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"03_After_Save_Designation_{designation}_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        test_context['updated_designation'] = designation
        logger.info(f"[OK] Designation changed to '{designation}' and saved for '{beneficiary_name}'")


@then(parsers.parse('Verify "Added" label is displayed for "{beneficiary_name}"'))
def verify_added_label_displayed(page, manage_bene_detail_page, beneficiary_name):

    with allure.step(f"Verifying 'ADDED' label is displayed for beneficiary '{beneficiary_name}'"):
        logger.info(f"Step: Verifying ADDED label is present for '{beneficiary_name}'")

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1500)  # allow chip re-render after network settles

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"01_Before_ADDED_Label_Check_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        added_label = manage_bene_detail_page.get_added_label_locator(beneficiary_name)

        # Diagnostics: log all chip labels and name spans visible on the page
        all_chips = page.locator("span[class*='MuiChip-label']").all_inner_texts()
        logger.info(f"[DIAG] Chip labels on page: {all_chips}")
        all_names = page.locator("span[class*='MuiTypography-cardTextPrimary']").all_inner_texts()
        logger.info(f"[DIAG] Beneficiary name spans on page: {all_names}")

        # .first already applied in get_added_label_locator; wait_for is safe
        added_label.wait_for(state='visible', timeout=30000)

        is_visible = added_label.is_visible()

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"02_ADDED_Label_{'FOUND' if is_visible else 'NOT_FOUND'}_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        assert is_visible, f"'ADDED' label not found for beneficiary '{beneficiary_name}'"
        logger.info(f"'ADDED' label successfully verified for '{beneficiary_name}'")
        
       

@then(parsers.parse('update the beneficiary first name to "{new_first_name}" and last name to "{new_last_name}" and save'))
def update_beneficiary_name_and_save(page, edit_beneficiary_page, test_context, new_first_name, new_last_name):
    beneficiary_name = test_context.get('added_beneficiary_name', '')

    with allure.step(f"Update name to '{new_first_name} {new_last_name}' and save"):
        logger.info(f"Step: Updating name for '{beneficiary_name}' to '{new_first_name} {new_last_name}'")

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"01_Before_Name_Update_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        edit_beneficiary_page.update_name_fields(new_first_name, new_last_name)
        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"02_Name_Updated_{new_first_name}_{new_last_name}", attachment_type=allure.attachment_type.PNG)

        edit_beneficiary_page.click_save()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"03_After_Save_{new_first_name}_{new_last_name}", attachment_type=allure.attachment_type.PNG)

        test_context['added_beneficiary_name'] = f"{new_first_name} {new_last_name}"
        suffix = test_context.get('beneficiary_suffix', '')
        full_name = f"{new_first_name} {new_last_name} {suffix}".strip() if suffix else f"{new_first_name} {new_last_name}"
        test_context['beneficiary_full_name'] = full_name
        logger.info(f"[OK] Name updated to '{new_first_name} {new_last_name}' and saved")
        logger.info(f"Saved beneficiary_full_name to context: {full_name}")


@then(parsers.parse('verify beneficiary "{beneficiary_name}" is displayed on the page'))
def verify_beneficiary_name_on_page(page, manage_bene_detail_page, beneficiary_name):
    with allure.step(f"Verify beneficiary '{beneficiary_name}' is displayed on the page"):
        logger.info(f"Step: Verifying '{beneficiary_name}' is visible on the page")

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"01_Before_Name_Verify_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        name_locator = page.locator(
            f"xpath=//span[contains(@class,'MuiTypography-cardTextPrimary') and "
            f"contains(normalize-space(text()),'{beneficiary_name}')]"
        )
        name_locator.wait_for(state='visible', timeout=15000)
        is_visible = name_locator.is_visible()

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"02_Name_{'FOUND' if is_visible else 'NOT_FOUND'}_{beneficiary_name.replace(' ', '_')}", attachment_type=allure.attachment_type.PNG)

        assert is_visible, f"Beneficiary '{beneficiary_name}' not found on the page after name update"
        logger.info(f"[OK] Beneficiary '{beneficiary_name}' verified on the page")


# ============================================================================
# Existing Beneficiary Flow Steps
# ============================================================================

@when(parsers.parse('User captures first "{relation}" beneficiary name from manage bene page'))
def user_captures_bene_name_by_relation(page, manage_bene_detail_page, relation, test_context):
    with allure.step(f"Capturing first '{relation}' beneficiary name from manage bene page"):
        logger.info(f"Step: Capturing first '{relation}' beneficiary name from manage bene page")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Capture_Bene_By_Relation", attachment_type=allure.attachment_type.PNG)

        name = manage_bene_detail_page.get_first_beneficiary_name_by_relation(relation)

        test_context['target_bene_name'] = name
        test_context['target_bene_relation'] = relation

        allure.attach(
            f"Name: {name}\nRelation: {relation}",
            name="Captured_Bene_Name_And_Relation",
            attachment_type=allure.attachment_type.TEXT
        )
        logger.info(f"[OK] Saved to context ΓÇö name='{name}', relation='{relation}'")


@when(parsers.parse('User captures first "{relation}" beneficiary name from manage bene page, clicks edit button, captures info, and navigates to edit page'))
def user_captures_bene_by_relation_and_opens_edit(page, manage_bene_detail_page, edit_beneficiary_page, relation, test_context):
    with allure.step(f"Capturing first '{relation}' beneficiary and opening edit page"):
        logger.info(f"Step: Capturing first '{relation}' beneficiary, clicking Edit, and opening edit page")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Capture_And_Edit_Bene_By_Relation", attachment_type=allure.attachment_type.PNG)

        beneficiary_name = manage_bene_detail_page.get_first_beneficiary_name_by_relation(relation)

        name_parts = beneficiary_name.split()
        if relation.lower() in ('trust', 'entity'):
            beneficiary_first_name = beneficiary_name
            beneficiary_last_name = ''
        else:
            beneficiary_first_name = name_parts[0] if name_parts else beneficiary_name
            beneficiary_last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        test_context['target_bene_name'] = beneficiary_name
        test_context['target_bene_relation'] = relation
        test_context['first_bene_name'] = beneficiary_name
        test_context['first_bene_relationship'] = relation
        test_context['added_beneficiary_name'] = beneficiary_name
        test_context['beneficiary_full_name'] = beneficiary_name
        test_context['beneficiary_name'] = beneficiary_name
        test_context['beneficiary_first_name'] = beneficiary_first_name
        test_context['beneficiary_last_name'] = beneficiary_last_name
        test_context['beneficiary_relation'] = relation

        allure.attach(
            f"Name: {beneficiary_name}\nRelation: {relation}",
            name="Captured_Bene_Name_And_Relation_For_Edit",
            attachment_type=allure.attachment_type.TEXT
        )

        manage_bene_detail_page.click_edit_button(beneficiary_name)

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(800)

        is_visible = edit_beneficiary_page.is_edit_form_visible()

        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Capture_And_Edit_Bene_By_Relation", attachment_type=allure.attachment_type.PNG)

        assert is_visible, f"Edit Beneficiary form did not appear after clicking Edit for '{beneficiary_name}'"
        logger.info(f"[OK] Captured '{beneficiary_name}' ({relation}) and opened the edit page")


@when(parsers.parse('User selects "{bene_type}" beneficiary from the dropdown and captures the name'))
def user_selects_existing_beneficiary(page, add_beneficiary_page, bene_type, test_context):

    with allure.step(f"Selecting existing beneficiary from dropdown and capturing name (bene_type={bene_type})"):
        logger.info(f"Step: Selecting existing beneficiary from dropdown ΓÇö bene_type='{bene_type}'")

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Select_Existing_Bene", attachment_type=allure.attachment_type.PNG)

        # Use target name captured from manage-bene page (by relation) if available,
        # otherwise fall back to selecting the first non-New option.
        target_name = test_context.get('target_bene_name')
        if target_name:
            logger.info(f"Selecting by pre-captured target name: '{target_name}'")
            bene_name = add_beneficiary_page.select_existing_beneficiary_by_name(target_name)
        else:
            logger.info("No target name in context ΓÇö selecting first existing beneficiary")
            bene_name = add_beneficiary_page.select_first_existing_beneficiary()

        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="After_Select_Existing_Bene", attachment_type=allure.attachment_type.PNG)

        # Split "First L Last" ΓåÆ first_name="First L", last_name="Last" so badge step constructs full name correctly
        parts = bene_name.split()
        first_name = " ".join(parts[:-1]) if len(parts) > 1 else bene_name
        last_name = parts[-1] if len(parts) > 1 else ""

        test_context['beneficiary_full_name'] = bene_name
        test_context['beneficiary_first_name'] = first_name
        test_context['beneficiary_last_name'] = last_name
        test_context['beneficiary_suffix'] = ""
        test_context['added_beneficiary_name'] = bene_name
        test_context['bene_type'] = bene_type

        allure.attach(
            bene_name,
            name="Captured_Existing_Beneficiary_Name",
            attachment_type=allure.attachment_type.TEXT
        )
        logger.info(f"Captured existing beneficiary name: {bene_name}")


# ΓöÇΓöÇ Relationship radio button validation / toggle (Existing bene SpouseΓåöNon-Spouse) ΓöÇΓöÇ
@then("Spouse and Non-Spouse relationship options should be disabled")
def verify_spouse_non_spouse_radios_disabled(page, add_beneficiary_page, test_context):

    with allure.step("Verifying Spouse and Non-Spouse radio buttons are disabled"):
        logger.info("Step: Verifying Spouse and Non-Spouse relationship radios are disabled")

        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Spouse_NonSpouse_Disabled_Check", attachment_type=allure.attachment_type.PNG)

        spouse_disabled = add_beneficiary_page.spouse_radio.is_disabled()
        non_spouse_disabled = add_beneficiary_page.non_spouse_radio.is_disabled()

        allure.attach(
            f"Spouse disabled: {spouse_disabled}\nNon-Spouse disabled: {non_spouse_disabled}",
            name="Spouse_NonSpouse_Radio_Disabled_Status",
            attachment_type=allure.attachment_type.TEXT
        )

        assert spouse_disabled, "Expected Spouse radio button to be disabled for Trust/Entity beneficiary"
        assert non_spouse_disabled, "Expected Non-Spouse radio button to be disabled for Trust/Entity beneficiary"
        logger.info("[OK] Spouse and Non-Spouse radio buttons are correctly disabled")


@then("Trust and Entity relationship options should be disabled")
def verify_trust_entity_radios_disabled(page, add_beneficiary_page, test_context):

    with allure.step("Verifying Trust and Entity radio buttons are disabled"):
        logger.info("Step: Verifying Trust and Entity relationship radios are disabled")

        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Trust_Entity_Disabled_Check", attachment_type=allure.attachment_type.PNG)

        trust_disabled = add_beneficiary_page.trust_radio.is_disabled()
        entity_disabled = add_beneficiary_page.entity_radio.is_disabled()

        allure.attach(
            f"Trust disabled: {trust_disabled}\nEntity disabled: {entity_disabled}",
            name="Trust_Entity_Radio_Disabled_Status",
            attachment_type=allure.attachment_type.TEXT
        )

        assert trust_disabled, "Expected Trust radio button to be disabled for Spouse/Non-Spouse beneficiary"
        assert entity_disabled, "Expected Entity radio button to be disabled for Spouse/Non-Spouse beneficiary"
        logger.info("[OK] Trust and Entity radio buttons are correctly disabled")


@when("User switches to the opposite relationship type")
def user_switches_opposite_relationship(page, add_beneficiary_page, test_context):

    relation = test_context.get('target_bene_relation', '').lower()

    with allure.step(f"Switching from '{relation}' to the opposite relationship type"):
        logger.info(f"Step: Switching relationship from '{relation}' to opposite")

        if relation == 'spouse':
            opposite = 'Non-Spouse'
        elif relation == 'non-spouse':
            opposite = 'Spouse'
        else:
            raise ValueError(
                f"Cannot toggle from '{relation}' ΓÇö only Spouse/Non-Spouse are toggleable. "
                "Ensure 'User captures first <relation> beneficiary' step ran before this step."
            )

        add_beneficiary_page.select_designation_as(opposite)
        test_context['target_bene_relation'] = opposite.lower()

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"After_Switch_To_{opposite}", attachment_type=allure.attachment_type.PNG)

        allure.attach(
            f"Previous: {relation}\nSwitched to: {opposite}",
            name="Relationship_Toggle",
            attachment_type=allure.attachment_type.TEXT
        )
        logger.info(f"[OK] Switched relationship from '{relation}' to '{opposite}'")


@then("Beneficiary personal fields should be pre-filled and disabled")
def verify_bene_fields_disabled_generic(page, add_beneficiary_page, test_context):

    relation = test_context.get('target_bene_relation', '').lower()

    with allure.step("Verifying beneficiary personal fields are pre-filled and disabled"):
        logger.info(f"Step: Verifying beneficiary personal fields are disabled (relation='{relation}')")

        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Bene_Fields_Check", attachment_type=allure.attachment_type.PNG)

        if relation in ('trust', 'entity'):
            relation_key = 'Trust'
        elif relation in ('spouse', 'non-spouse'):
            relation_key = 'Spouse'
        else:
            # Auto-detect: individual fields exist for Spouse/Non-Spouse, name-only for Trust/Entity
            try:
                add_beneficiary_page.first_name_input.wait_for(state="attached", timeout=3000)
                relation_key = 'Spouse'
            except Exception:
                relation_key = 'Trust'
            logger.info(f"Auto-detected relation type: '{relation_key}'")

        disabled_status = add_beneficiary_page.verify_existing_beneficiary_fields_disabled(relation_key)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Bene_Fields_Disabled_Status", attachment_type=allure.attachment_type.PNG)

        allure.attach(
            "\n".join(f"{k}: {'DISABLED' if v else 'NOT DISABLED'}" for k, v in disabled_status.items()),
            name="Bene_Field_Disabled_Status",
            attachment_type=allure.attachment_type.TEXT
        )

        failed_fields = [field for field, is_disabled in disabled_status.items() if not is_disabled]
        assert not failed_fields, (
            f"Expected beneficiary fields to be disabled but are not: {failed_fields}"
        )
        logger.info("[OK] All beneficiary personal fields are pre-filled and disabled")


@then("Spouse/Non-Spouse beneficiary personal fields should be pre-filled and disabled")
def verify_individual_bene_fields_disabled(page, add_beneficiary_page, test_context):

    with allure.step("Verifying First Name, Last Name, SSN, DOB are pre-filled and disabled"):
        logger.info("Step: Verifying Spouse/Non-Spouse personal fields are disabled")

        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Individual_Fields_Check", attachment_type=allure.attachment_type.PNG)

        # Pass 'Spouse' ΓÇö the page method uses this to select the individual-fields branch
        disabled_status = add_beneficiary_page.verify_existing_beneficiary_fields_disabled('Spouse')

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Individual_Fields_Disabled_Status", attachment_type=allure.attachment_type.PNG)

        allure.attach(
            "\n".join(f"{k}: {'DISABLED' if v else 'NOT DISABLED'}" for k, v in disabled_status.items()),
            name="Individual_Field_Disabled_Status",
            attachment_type=allure.attachment_type.TEXT
        )

        failed_fields = [field for field, is_disabled in disabled_status.items() if not is_disabled]
        assert not failed_fields, (
            f"Expected Spouse/Non-Spouse fields to be disabled but are not: {failed_fields}"
        )
        logger.info("[OK] All Spouse/Non-Spouse personal fields are pre-filled and disabled")


@then("Trust/Entity beneficiary name field should be pre-filled and disabled")
def verify_trust_entity_name_field_disabled(page, add_beneficiary_page, test_context):

    with allure.step("Verifying Trust/Entity Name field is pre-filled and disabled"):
        logger.info("Step: Verifying Trust/Entity Name field is disabled")

        page.wait_for_timeout(500)

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Before_Trust_Entity_Name_Check", attachment_type=allure.attachment_type.PNG)

        # Pass 'Trust' ΓÇö the page method uses this to select the name-field-only branch
        disabled_status = add_beneficiary_page.verify_existing_beneficiary_fields_disabled('Trust')

        screenshot = page.screenshot()
        allure.attach(screenshot, name="Trust_Entity_Name_Field_Status", attachment_type=allure.attachment_type.PNG)

        allure.attach(
            "\n".join(f"{k}: {'DISABLED' if v else 'NOT DISABLED'}" for k, v in disabled_status.items()),
            name="Trust_Entity_Field_Disabled_Status",
            attachment_type=allure.attachment_type.TEXT
        )

        failed_fields = [field for field, is_disabled in disabled_status.items() if not is_disabled]
        assert not failed_fields, (
            f"Expected Trust/Entity Name field to be disabled but is not: {failed_fields}"
        )
        logger.info("[OK] Trust/Entity Name field is pre-filled and disabled")


@then(parsers.parse('User should verify the existing beneficiary appears in the "{designation}" section'))
def verify_existing_beneficiary_in_section(page, manage_bene_detail_page, designation, test_context):

    with allure.step(f"Verifying existing beneficiary appears in the '{designation}' section"):
        logger.info(f"Step: Verifying existing beneficiary in '{designation}' section")

        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        bene_name = test_context.get('beneficiary_full_name') or test_context.get('added_beneficiary_name')
        assert bene_name, "No beneficiary name captured in test_context ΓÇö ensure 'User selects an existing beneficiary' step ran first"

        screenshot = page.screenshot()
        allure.attach(screenshot, name=f"Before_Verify_Existing_Bene_{designation}", attachment_type=allure.attachment_type.PNG)

        is_verified = manage_bene_detail_page.verify_beneficiary_in_designation_section(
            beneficiary_name=bene_name,
            designation=designation
        )

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Existing_Bene_Verify_{designation}_{'PASS' if is_verified else 'FAIL'}",
            attachment_type=allure.attachment_type.PNG
        )

        assert is_verified, (
            f"Existing beneficiary '{bene_name}' was not found in the '{designation}' section"
        )
        logger.info(f"[OK] Existing beneficiary '{bene_name}' verified in '{designation}' section")
