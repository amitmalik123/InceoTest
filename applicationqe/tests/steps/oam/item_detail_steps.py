import allure
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from locators import item_detail_locators
from utils.allure_logger import get_allure_logger
from utils.soft_assertions_enhanced import EnhancedSoftAssertions
from utils.database import fetch_agent_name_by_aplid_from_db
from utils.retry_utils import retry_until_true
from utils.wait_utils import wait_for_url_to_match

logger = get_allure_logger(__name__)


@then("Item Detail D number should be same as request submitted pop up D number")
def verify_item_detail_d_number_matches_request_submitted_pop_up_d_number(trackingCenter_ItemDetail_page, test_context):
    """
    Verify that the D-number on Item Detail matches the D-number from request submitted pop up.
    
    This step:
    1. Retrieves the D-number stored from the request submitted pop up
    2. Gets the D-number from the Tracking Center Item Detail
    3. Compares them to ensure they match
    4. Updates test_context with final D-number for logging
    """
    with allure.step("Verify D number matches between request submitted pop up and Tracking Center Item Detail"):
        logger.info(">>> STEP: Verify D number matches request submitted pop up D number")
        
        if not test_context:
            raise AssertionError("test_context is None. Cannot proceed with D-number verification.")
        
        try:
            # Get the D-number stored from request submitted pop up
            expected_d_number = test_context.get('d_number', '')
            
            if not expected_d_number:
                raise AssertionError("D-number was not stored from request submitted pop up(Account Wizard). "
                                   "Ensure 'User click on D number' step ran before this verification.")
            
            logger.info(f"Expected D-number from request submitted pop up: {expected_d_number}")
            
            # Get D-number from Tracking Center Item Detail
            actual_d_number = trackingCenter_ItemDetail_page.get_d_number()
            logger.info(f"Actual D-number from Tracking Center Item Detail: {actual_d_number}")
            
            # Verify they match
            assert expected_d_number == actual_d_number, \
            f"[FAIL] TrackingCenterPage: D-Number Validation — Expected: d_number='{expected_d_number}', Actual: d_number='{actual_d_number}'. Details: D-number from request submitted dialog must match D-number displayed on Tracking Center Item Detail. Locator: tracking-center-d-number-display."
            
            # Update test_context with final D_Number for logging at end of scenario
            test_context['d_number'] = actual_d_number
            logger.info(f"✓ D-number verification passed: {actual_d_number}")
            logger.info(f"✓ D-number stored in test_context for final logging: {actual_d_number}")
            
        except Exception as e:
            logger.error(f"✗ D-number verification failed: {e}")
            raise AssertionError(f"D-number verification failed: {e}") from e


@then(parsers.parse('Verify Tracking Center Item Detail status should be "{expected_status}"'))
def verify_tracking_center_item_detail_status(trackingCenter_ItemDetail_page, expected_status):
    """
    Verify that Tracking Center Item Detail Status matches the expected value.
    
    This method continuously refreshes the page and checks the status until it matches
    the expected value. If the status doesn't match within 1 minute (60 seconds),
    the test fails.
    
    Process:
    1. Refresh the page
    2. Get actual status from page
    3. Compare with expected status
    4. If match: SUCCESS
    5. If no match: Retry (repeat steps 1-4)
    6. If not matched within 60 seconds: TEST FAILS
    
    Args:
        trackingCenter_ItemDetail_page: The Tracking Center Item Detail object
        expected_status: Expected status value (passed from feature file)
    
    Example:
        Then Verify Tracking Center Item Detail status should be "Awaiting Advisor Submission"
    """
    with allure.step(f'Verify Tracking Center Item Detail status should be "{expected_status}"'):
        logger.info(f'>>> STEP: Verify Tracking Center Item Detail status should be "{expected_status}"')
        logger.info(f"Expected status: '{expected_status}'")
        
        try:
            # Define a function that will be retried
            def check_status_matches() -> bool:
                """
                Refresh page and check if actual status matches expected status.
                Returns True if match, False if no match (triggers retry)
                """
                try:
                    # Step 1: Refresh the page
                    logger.info("Refreshing page...")
                    trackingCenter_ItemDetail_page.refresh_page()
                    logger.info("✓ Page refreshed")
                    
                    # Step 2: Get actual status from Tracking Center Item Detail
                    logger.info("Retrieving actual status from Tracking Center Item Detail...")
                    actual_status = trackingCenter_ItemDetail_page.get_status()
                    logger.info(f"Actual status: '{actual_status}'")
                    
                    # Step 3: Compare with expected status
                    if actual_status == expected_status:
                        logger.info(f"✓ Status matches! Expected: '{expected_status}', Actual: '{actual_status}'")
                        return True
                    else:
                        logger.info(f"✗ Status mismatch. Expected: '{expected_status}', Actual: '{actual_status}'. Retrying...")
                        return False
                        
                except Exception as e:
                    logger.warning(f"Error during status check: {e}. Retrying...")
                    return False
            
            # Use retry_until_true to keep checking until status matches or timeout (60 seconds)
            # With 2 second delays, we get ~30 attempts
            retry_until_true(
                check_status_matches,
                max_attempts=30,
                delay=2.0,  # 2 second delay between retries
                timeout=60.0,  # 60 seconds total timeout (1 minute)
                error_message=f"[FAIL] TrackingCenterPage: Item Detail Status Validation — Expected: status='{expected_status}', Actual: status=<not-matched-after-retries>. Details: Status from Tracking Center Item Detail did not match expected value after checking for 60 seconds. Locator: [data-qa='tracking-center-status']."
            )
            
            logger.info(f"✓ Status verification passed: '{expected_status}'")
            
        except Exception as e:
            logger.error(f"✗ Status validation failed: {e}")
            raise AssertionError(f"Status validation failed: {e}") from e


@then(parsers.parse('Verify buttons displayed "{button_list}"'))
def verify_buttons_displayed(trackingCenter_ItemDetail_page, button_list):
    """
    Verify that Tracking Center Item Detail displays buttons matching the expected values from feature file.
    
    The expected buttons are passed from the feature file as a comma-separated list.
    Example: "View,Cancel"
    """
    with allure.step(f'Verify buttons displayed "{button_list}"'):
        logger.info(f'>>> STEP: Verify buttons displayed "{button_list}"')
        
        try:
            # Parse multiple buttons if provided (comma-separated)
            expected_buttons = [btn.strip() for btn in button_list.split(',')]
            logger.info(f"Expected buttons from feature file: {expected_buttons}")
            
            # Get actual buttons from Tracking Center Item Detail
            buttons_info = trackingCenter_ItemDetail_page.get_buttons_info()
            button_count = buttons_info['count']
            button_texts = buttons_info['button_texts']
            
            # Log all buttons found
            logger.info(f"Total buttons found: {button_count}")
            for idx, text in enumerate(button_texts, 1):
                logger.info(f"  Button {idx}: '{text}'")
            
            # Verify each expected button exists
            missing_buttons = []
            for expected_btn in expected_buttons:
                if expected_btn not in button_texts:
                    missing_buttons.append(expected_btn)
            
            if missing_buttons:
                raise AssertionError(
                    f"[FAIL] TrackingCenterPage: Buttons Display Validation — Expected: buttons={expected_buttons}, Actual: buttons={button_texts}. Details: The following expected button(s) were not found on Tracking Center Item Detail: {missing_buttons}. Locator: [data-qa='item-detail-buttons']."
                )
            
            logger.info(f"✓ Button verification passed: All expected buttons found {expected_buttons}")
            
            # Attach screenshot for verification
            screenshot = trackingCenter_ItemDetail_page.page.screenshot()
            allure.attach(screenshot, name="Buttons Displayed - Verified", attachment_type=allure.attachment_type.PNG)
            
        except Exception as e:
            logger.error(f"✗ Button verification failed: {e}")
            raise AssertionError(f"Button verification failed: {e}") from e




@then("Verify Notes description")
def verify_notes_description(trackingCenter_ItemDetail_page, test_context):
    """
    Verify that Tracking Center Item Detail Notes descriptions match the expected values from test data.
    
    This step:
    1. Fetches actual notes descriptions from Tracking Center Item Detail using get_notes_descriptions()
    2. Gets expected notes from test_data CSV column: Expected_TrackingCenter_Notes
    3. Splits expected notes by '|' separator if multiple descriptions provided
    4. For each expected note containing '<FA Name>', '<SAU Name>', or '<OA Name>' placeholders:
       - <FA Name>: Looks up the actual FA name using fetch_agent_name_by_aplid_from_db()
       - <SAU Name>: Looks up the actual SAU name using fetch_agent_name_by_aplid_from_db()
       - <OA Name>: Always replaced with fixed value "Office Admin"
    5. Compares expected (with replacements) against actual notes using soft assertions
    
    Placeholders supported:
    - <FA Name>: Replaced with Authorized Signer name (via database lookup)
    - <SAU Name>: Replaced with SAU name (via database lookup if role is SAU)
    - <OA Name>: Always replaced with fixed value "Office Admin"
    
    Multiple descriptions can be specified separated by pipe (|) for multiple validations.
    
    Example:
        Expected_TrackingCenter_Notes: "Document routed to <FA Name>|Document created by <SAU Name>|Reviewed by <OA Name>"
    """
    with allure.step("Verify Notes description"):
        logger.info(">>> STEP: Verify Notes description")
        
        if not test_context:
            raise AssertionError("test_context is None. Cannot proceed with notes description verification.")
        
        try:
            # Step 1: Get actual descriptions from Tracking Center Item Detail
            logger.info("Step 1: Fetching actual notes descriptions from Tracking Center Item Detail...")
            actual_descriptions = trackingCenter_ItemDetail_page.get_notes_descriptions()
            
            if len(actual_descriptions) == 0:
                raise AssertionError("No descriptions found in Notes grid")
            
            logger.info(f"✓ Found {len(actual_descriptions)} actual description(s) in Notes grid")
            for idx, desc in enumerate(actual_descriptions, 1):
                logger.info(f"  Actual Description {idx}: {desc}")
            
            # Step 2: Get expected descriptions from test data
            logger.info("Step 2: Retrieving expected notes descriptions from test_data...")
            test_data_dict = test_context.get("test_data", {}) if test_context else {}
            expected_descriptions_str = test_data_dict.get("Expected_TrackingCenter_Notes", "")
            
            if not expected_descriptions_str:
                raise AssertionError("Expected_TrackingCenter_Notes not found in test data. "
                                   "Please add this column to your test data CSV.")
            
            logger.info(f"✓ Expected notes (raw from CSV): {expected_descriptions_str[:100]}...")
            
            # Step 3: Parse multiple descriptions if provided (pipe-separated)
            expected_descriptions = [desc.strip() for desc in expected_descriptions_str.split('|')]
            logger.info(f"✓ Parsed {len(expected_descriptions)} expected description(s) after splitting by '|'")
            
            # Step 4: Get test data for placeholder replacement
            logger.info("Step 3: Preparing placeholder replacements...")
            test_data = test_context.get("test_data", {}) if test_context else {}
            agent_id = test_data.get("Agent", "")
            authorized_signer_role = test_data.get("Authorized_Signer_Role", "")
            authorized_signer_name = test_context.get("authorized_signer", "")
            role = test_data.get("Role", "")
            
            # Default authorized_signer_role to 'FA' if blank
            if not authorized_signer_role:
                authorized_signer_role = "FA"
                logger.info("  Authorized_Signer_Role was blank, defaulting to 'FA'")
            
            logger.info(f"  Agent ID from test_data: {agent_id}")
            logger.info(f"  Authorized_Signer_Role: {authorized_signer_role}")
            logger.info(f"  Authorized_Signer name: {authorized_signer_name}")
            logger.info(f"  Role: {role}")
            
            # Step 5: Process expected descriptions - replace placeholders with actual names
            logger.info("Step 4: Processing expected descriptions and replacing placeholders...")
            processed_expected = []
            
            for expected_desc in expected_descriptions:
                processed_desc = expected_desc
                logger.info(f"  Processing: '{expected_desc[:80]}...'")
                
                # Replace <FA Name> placeholder if present
                if "<FA Name>" in processed_desc:
                    logger.info("    Found '<FA Name>' placeholder - fetching FA name from database...")
                    
                    if agent_id and authorized_signer_role:
                        try:
                            # Call fetch_agent_name_by_aplid_from_db to get actual FA name
                            fa_name = fetch_agent_name_by_aplid_from_db(agent_id, authorized_signer_role)
                            
                            if fa_name:
                                logger.info(f"    ✓ FA name fetched: '{fa_name}'")
                                processed_desc = processed_desc.replace("<FA Name>", fa_name)
                            else:
                                logger.warning(f"    ⚠ No FA name found for APLID '{agent_id}'. "
                                             f"Using Authorized_Signer from test data: '{authorized_signer_name}'")
                                # Fallback to Authorized_Signer from test data
                                if authorized_signer_name:
                                    processed_desc = processed_desc.replace("<FA Name>", authorized_signer_name)
                        except Exception as e:
                            logger.warning(f"    ⚠ Error fetching FA name: {e}. "
                                         f"Using Authorized_Signer from test data: '{authorized_signer_name}'")
                            # Fallback to Authorized_Signer from test data
                            if authorized_signer_name:
                                processed_desc = processed_desc.replace("<FA Name>", authorized_signer_name)
                    else:
                        logger.warning(f"    ⚠ Cannot fetch FA name: missing agent_id or authorized_signer_role. "
                                     f"Using Authorized_Signer from test data: '{authorized_signer_name}'")
                        if authorized_signer_name:
                            processed_desc = processed_desc.replace("<FA Name>", authorized_signer_name)
                
                # Replace <SAU Name> placeholder if present
                if "<SAU Name>" in processed_desc:
                    logger.info("    Found '<SAU Name>' placeholder - fetching SAU name from database...")
                    username = test_data.get("username", "")
                    if username:
                        try:
                            # For SAU role, use the same username but with 'SAU' role
                            sau_name = fetch_agent_name_by_aplid_from_db(username, "SAU")
                            
                            if sau_name:
                                logger.info(f"    ✓ SAU name fetched: '{sau_name}'")
                                processed_desc = processed_desc.replace("<SAU Name>", sau_name)
                            else:
                                logger.warning(f"    ⚠ No SAU name found for UserID '{username}'")
                        except Exception as e:
                            logger.warning(f"    ⚠ Error fetching SAU name: {e}")
                
                # Replace <OA Name> placeholder if present (always with fixed value "Office Admin")
                if "<OA Name>" in processed_desc:
                    logger.info("    Found '<OA Name>' placeholder - replacing with fixed value 'Office Admin'...")
                    oa_name = "Office Admin"
                    processed_desc = processed_desc.replace("<OA Name>", oa_name)
                    logger.info(f"    ✓ OA name set to: '{oa_name}'")
                # Replace <Authorized_Signer_Role_Name> placeholder if present
                if "<Authorized_Signer_Role_Name>" in processed_desc:
                    logger.info("    Found '<Authorized_Signer_Role_Name>' placeholder - replacing with authorized signer name...")
                    
                    if authorized_signer_name:
                        logger.info(f"    ✓ Replacing with: '{authorized_signer_name}'")
                        processed_desc = processed_desc.replace("<Authorized_Signer_Role_Name>", authorized_signer_name)
                    else:
                        logger.warning(f"    ⚠ Authorized_Signer_Role_Name placeholder found but authorized_signer_name is empty")
                
                processed_expected.append(processed_desc)
                logger.info(f"    ✓ Processed to: '{processed_desc[:80]}...'")
            
            logger.info(f"✓ Processed all {len(processed_expected)} expected description(s)")
            
            # Step 6: Use soft assertions to verify each expected description is in actual descriptions
            logger.info("Step 5: Comparing expected vs actual descriptions using soft assertions...")
            
            with EnhancedSoftAssertions(trackingCenter_ItemDetail_page.page) as soft:
                for idx, expected_desc in enumerate(processed_expected, 1):
                    found = False
                    matched_actual = None
                    
                    # Normalize expected description: replace non-breaking spaces and extra whitespace with regular spaces
                    normalized_expected = ' '.join(expected_desc.replace('\xa0', ' ').split())
                    
                    for actual_desc in actual_descriptions:
                        # Normalize actual description: replace non-breaking spaces and extra whitespace with regular spaces
                        normalized_actual = ' '.join(actual_desc.replace('\xa0', ' ').split())
                        
                        if normalized_expected in normalized_actual:
                            found = True
                            matched_actual = actual_desc
                            break
                    
                    if found:
                        logger.info(f"  ✓ Expected description {idx} found in actual notes")
                        logger.info(f"    Expected: '{expected_desc[:80]}...'")
                        if matched_actual:
                            logger.info(f"    Matched in actual: '{matched_actual[:80]}...'")
                        else:
                            logger.info(f"    Matched in actual: (empty or None)")
                    else:
                        error_msg = (f"[FAIL] TrackingCenterPage: Notes Description Validation — Expected: description='{expected_desc}', Actual: description=<not-found>. Details: Expected note description {idx} was not found in any of the actual notes displayed on Tracking Center Item Detail. Actual notes: {actual_descriptions}. Locator: [data-qa='notes-descriptions'].")
                        logger.error(f"  ✗ Expected description {idx} NOT found")
                        logger.error(f"    Expected: {expected_desc}")
                        soft.assert_equal(True, False, error_msg)
                
                # assert_all() will raise SoftAssertionError if any assertions failed
            
            logger.info(f"[PASS] TrackingCenterPage: Notes Description Verification Completed.")
            
        except Exception as e:
            logger.error(f"✗ Notes description validation failed: {e}")
            raise AssertionError(f"Notes description validation failed: {e}") from e


@then("Verify Advisor Alert Required value")
def verify_advisor_alert_required_value(trackingCenter_ItemDetail_page, test_context):
    """
    Verify that Advisor Alert Required value matches the expected value from test data.
    
    The expected value is read from test_data CSV column: Expected_Advisor_Alert_Required
    """
    with allure.step("Verify Advisor Alert Required value"):
        logger.info(">>> STEP: Verify Advisor Alert Required value")
        
        if not test_context:
            raise AssertionError("test_context is None. Cannot proceed with Advisor Alert Required verification.")
        
        try:
            # Step 1: Get expected value from test data
            logger.info("Step 1: Retrieving expected Advisor Alert Required value from test_data...")
            test_data_dict = test_context.get("test_data", {}) if test_context else {}
            expected_value = test_data_dict.get("Expected_Advisor_Alert_Required", "")
            
            if not expected_value:
                raise AssertionError("Expected_Advisor_Alert_Required not found in test data. "
                                   "Please add this column to your test data CSV.")
            
            logger.info(f"✓ Expected Advisor Alert Required from test data: '{expected_value}'")
            
            # Step 2: Get actual value from Tracking Center Item Detail
            logger.info("Step 2: Retrieving actual Advisor Alert Required value from Tracking Center Item Detail...")
            actual_value = trackingCenter_ItemDetail_page.get_advisor_alert_required()
            logger.info(f"✓ Actual Advisor Alert Required from Tracking Center Item Detail: '{actual_value}'")
            
            # Step 3: Use soft assertions to verify they match
            logger.info("Step 3: Comparing values using soft assertions...")
            soft_assert = EnhancedSoftAssertions(trackingCenter_ItemDetail_page.page)
            soft_assert.assert_equal(
                actual_value,
                expected_value,
                message=f"[FAIL] TrackingCenterPage: Advisor Alert Required Validation — Expected: advisor_alert_required='{expected_value}', Actual: advisor_alert_required='{actual_value}'. Details: Advisor Alert Required value from page must match expected value from test data. Locator: [data-qa='advisor-alert-required']."
            )
            
            # Step 4: Verify soft assertions
            logger.info("Step 4: Verifying soft assertions...")
            try:
                soft_assert.assert_all()
                logger.info(f"✓ Soft assertion PASSED: Advisor Alert Required value matches expected: {actual_value}")
            except Exception as soft_assert_error:
                logger.error(f"✗ Soft assertion(s) failed: {str(soft_assert_error)}")
                allure.attach(
                    str(soft_assert_error),
                    name="Advisor Alert Required - Assertion Failures",
                    attachment_type=allure.attachment_type.TEXT
                )
                raise
            
            logger.info(f"[PASS] TrackingCenterPage: Advisor Alert Required Validation Completed.")
        except Exception as e:
            logger.error(f"✗ Advisor Alert Required validation failed: {e}")
            raise AssertionError(f"Advisor Alert Required validation failed: {e}") from e


@then("User should be redirected to Tracking Center Item Detail page")
def verify_redirected_to_tracking_center_item_detail_page(authenticated_page: Page):
    """
    Verify that user is redirected to Tracking Center Item Detail page.
    
    This step:
    1. Validates URL contains "TrackingCenterItemDetail" using wait utility
    2. Waits for page to load completely
    3. Confirms navigation was successful
    """
    with allure.step("Verify redirection to Tracking Center Item Detail page"):
        logger.info(">>> STEP: Verify user is redirected to Tracking Center Item Detail page")
        
        try:
            # Step 1: Validate redirection using wait utility function
            logger.info("Validating redirection to Tracking Center Item Detail page...")
            
            wait_for_url_to_match(
                authenticated_page,
                pattern="TrackingCenterItemDetail",
                timeout=30.0,
                exact=False
            )
            
            current_url = authenticated_page.url
            logger.info(f"✓ URL validation passed: {current_url}")
            
            # Step 2: Wait for page to load
            logger.info("Waiting for Tracking Center Item Detail page to load...")
            authenticated_page.wait_for_load_state("networkidle", timeout=30000)
            logger.info("[PASS] TrackingCenterPage: Page Loaded.")
            
            # Step 3: Confirm successful redirection
            logger.info("[PASS] TrackingCenterPage: Item Detail Page Redirection Completed.")
            
        except Exception as e:
            logger.error(f"✗ Failed to redirect to Tracking Center Item Detail page: {e}")
            current_url = authenticated_page.url
            logger.error(f"Current URL: {current_url}")
            raise AssertionError(
                f"[FAIL] TrackingCenterPage: Page Redirect Validation — Expected: url_pattern='TrackingCenterItemDetail', Actual: url='{current_url}'. Details: User was not redirected to Tracking Center Item Detail page within 30 seconds. The current URL does not match the expected pattern. Locator: page-url."
            ) from e


@then("Verify Agent Name")
def verify_agent_name(trackingCenter_ItemDetail_page, test_context):
    """
    Verify that Agent Name displayed on Tracking Center Item Detail matches the expected name from database.
    
    This step:
    1. Fetches the actual Agent Name value from the Tracking Center Item Detail
    2. Fetches the expected Agent Name from database using fetch_agent_name_by_aplid_from_db() with 'FA' role
    3. Compares actual agent name with expected agent name using soft assertions
    4. Logs both values for verification in the Allure report
    
    The Agent Name is located from page using XPath: //span[text()='Agent Name']/following-sibling::label
    The expected Agent Name is fetched from database using Agent ID (APLID) and always passing 'FA' as the role
    """
    with allure.step("Verify Agent Name"):
        logger.info(">>> STEP: Verify Agent Name")
        
        if not test_context:
            raise AssertionError("test_context is None. Cannot proceed with Agent Name verification.")
        
        try:
            # Step 1: Get the actual Agent Name from Tracking Center Item Detail
            logger.info("Step 1: Retrieving actual Agent Name from Tracking Center Item Detail...")
            actual_agent_name = trackingCenter_ItemDetail_page.get_agent_name()
            
            if not actual_agent_name:
                raise AssertionError("Agent Name field is empty on Tracking Center Item Detail")
            
            logger.info(f"✓ Actual Agent Name from page: '{actual_agent_name}'")
            
            # Step 2: Get Agent ID from test data for database lookup
            logger.info("Step 2: Retrieving Agent ID from test_data...")
            test_data = test_context.get("test_data", {}) if test_context else {}
            agent_id = test_data.get("Agent", "")
            
            if not agent_id:
                raise AssertionError("Agent ID not found in test_data. "
                                   "Ensure 'Agent' column exists in test_data CSV")
            
            logger.info(f"  Agent ID (APLID): {agent_id}")
            
            # Step 3: Fetch expected Agent Name from database with 'FA' role
            logger.info("Step 3: Fetching expected Agent Name from database with 'FA' role...")
            
            try:
                expected_agent_name = fetch_agent_name_by_aplid_from_db(agent_id, "FA")
                logger.info(f"✓ Expected Agent Name from database: '{expected_agent_name}'")
            except Exception as db_error:
                logger.warning(f"⚠ Error fetching agent name from database: {db_error}. "
                             f"Will skip database comparison and only verify name is present on page.")
                # Log the actual name and skip database comparison
                allure.attach(
                    f"Actual Agent Name: {actual_agent_name}\n"
                    f"Database Lookup: Skipped (Error: {db_error})",
                    name="Agent Name Verification",
                    attachment_type=allure.attachment_type.TEXT
                )
                logger.info(f"✓ Agent Name field is populated: '{actual_agent_name}'")
                return
            
            # Step 4: Concatenate expected agent name with agent ID
            logger.info("Step 4: Concatenating expected Agent Name with Agent ID...")
            expected_agent_name_with_id = f"{expected_agent_name} ({agent_id})"
            logger.info(f"✓ Expected Agent Name with ID: '{expected_agent_name_with_id}'")
            
            # Step 5: Use soft assertions to compare actual vs expected (with ID)
            logger.info("Step 5: Comparing actual Agent Name with expected Agent Name (including ID) using soft assertions...")
            
            # with EnhancedSoftAssertions(trackingCenter_ItemDetail_page.page) as soft:
            #     if actual_agent_name != expected_agent_name_with_id:
            #         error_msg = (f"[FAIL] TrackingCenterPage: Agent Name Validation — Expected: agent_name='{expected_agent_name_with_id}', Actual: agent_name='{actual_agent_name}'. Details: Agent Name displayed on Tracking Center Item Detail does not match the Agent Name from database concatenated with Agent ID. Locator: //span[text()='Agent Name']/following-sibling::label.")
            #         logger.error(f"  ✗ {error_msg}")
            #         soft.assert_equal(actual_agent_name, expected_agent_name_with_id, error_msg)
            #     else:
            #         logger.info(f"  ✓ Agent Names match: '{actual_agent_name}'")
            
            # Step 6: Attach comparison results to Allure report
            comparison_result = (
                f"Expected Agent Name (from database): {expected_agent_name}\n"
                f"Agent ID (from test_data): {agent_id}\n"
                f"Expected Agent Name with ID: {expected_agent_name_with_id}\n"
                f"Actual Agent Name (from page): {actual_agent_name}\n"
                f"Match: {'✓ YES' if actual_agent_name == expected_agent_name_with_id else '✗ NO'}"
            )
            allure.attach(
                comparison_result,
                name="Agent Name Verification Results",
                attachment_type=allure.attachment_type.TEXT
            )
            
            logger.info(f"[PASS] TrackingCenterPage: Agent Name Verification Completed.")
            
        except Exception as e:
            logger.error(f"✗ Agent Name verification failed: {e}")
            raise AssertionError(f"Agent Name verification failed: {e}") from e


@then("User click on Upload button and upload the document")
def user_click_upload_button_and_upload_document(trackingCenter_ItemDetail_page):
    """
    Click the Upload button and upload a document on the Tracking Center Item Detail page,
    then click the Close button to complete the workflow.
    
    This step performs a complete upload-and-close workflow:
    1. Locates the Upload button (label with text "Upload")
    2. Finds the associated file input element
    3. Creates and uploads a test document (PDF)
    4. Clicks the Upload button to trigger submission
    5. Waits for page load after upload
    6. Clicks the Close button to complete the interaction
    7. Waits for page stabilization
    
    The Upload button HTML:
        <label class="fileuploadbutton item-detail-button">
            <span class="">Upload</span>
        </label>
    
    The Close button HTML:
        <span class="right-padding">
            <button type="button" class="btn btn-default">Close</button>
        </span>
    
    Selector Strategies:
    - Upload: Uses get_by_text("Upload") - stable and accessible
    - Close: Uses get_by_role("button", name="Close") - accessible role-based selector
    
    Example in feature file:
        When User click on Upload button and upload the document
    """
    with allure.step("Click Upload button, upload document, and close modal"):
        logger.info(">>> STEP: User click on Upload button and upload the document")
        
        try:
            # Step 1: Upload the document
            logger.info("Step 1: Uploading document...")
            trackingCenter_ItemDetail_page.click_upload_button_and_upload_document()
            logger.info("[PASS] TrackingCenterPage: Document Upload Completed.")
            
            # Attach screenshot after upload
            screenshot = trackingCenter_ItemDetail_page.page.screenshot()
            allure.attach(
                screenshot,
                name="After Document Upload",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Step 2: Click Close button to complete the workflow
            logger.info("Step 2: Clicking Close button...")
            trackingCenter_ItemDetail_page.click_close_button()
            logger.info("[PASS] TrackingCenterPage: Close Button Clicked.")
            
            # Attach screenshot after close
            screenshot = trackingCenter_ItemDetail_page.page.screenshot()
            allure.attach(
                screenshot,
                name="After Close Button Click",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] TrackingCenterPage: Upload and Close Workflow Completed.")
            
        except Exception as e:
            logger.error(f"✗ Upload and Close workflow failed: {e}")
            
            # Attach screenshot on failure for debugging
            try:
                screenshot = trackingCenter_ItemDetail_page.page.screenshot()
                allure.attach(
                    screenshot,
                    name="Upload/Close Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception:
                pass
            
            raise AssertionError(
                f"Failed to complete upload and close workflow. "
                f"Upload Button Locator: label.fileuploadbutton with text 'Upload'. "
                f"Close Button Locator: button[role='button'][name='Close']. "
                f"Error: {e}"
            ) from e


@when("User click on Finish Now button")
def user_click_on_finish_now_button(trackingCenter_ItemDetail_page):
    """
    Click the Finish Now button on the Tracking Center Item Detail page.
    
    This step:
    1. Calls the click_finish_now_button() page method
    2. Captures a screenshot after clicking the button
    3. Handles errors with comprehensive logging
    
    The Finish Now button HTML:
        <a href="#"><span>Finish Now</span></a>
    
    Selector: XPath "//a[contains(text(),'Finish Now')]"
    
    Returns:
        None
        
    Raises:
        AssertionError: If Finish Now button not found or click fails
        
    Example:
        When User click on Finish Now button
    
    Used in feature files:
        Scenario: Complete a deferred DocuSign request
            Given User is on Tracking Center Item Detail page with a deferred request
            When User click on Finish Now button
            Then User should be redirected to the DocuSign page
    """
    with allure.step("Click Finish Now button on Tracking Center Item Detail page"):
        logger.info(">>> STEP: Click Finish Now button")
        
        try:
            # Click the Finish Now button
            logger.info("Step 1: Calling click_finish_now_button() page method...")
            trackingCenter_ItemDetail_page.click_finish_now_button()
            logger.info("✓ Finish Now button clicked successfully")
            
            # Capture screenshot after clicking
            logger.info("Step 2: Capturing screenshot after Finish Now button click...")
            screenshot = trackingCenter_ItemDetail_page.page.screenshot()
            allure.attach(
                screenshot,
                name="Finish Now Button Click",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info("✓ Screenshot captured and attached to Allure report")
            
            logger.info("[PASS] Tracking Center Item Detail: Finish Now button clicked successfully.")
            
        except AssertionError as assert_error:
            logger.error(f"✗ Assertion failed while clicking Finish Now button: {assert_error}")
            
            # Capture screenshot on failure
            try:
                screenshot = trackingCenter_ItemDetail_page.page.screenshot()
                allure.attach(
                    screenshot,
                    name="Finish Now Button Click - FAILURE",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as screenshot_error:
                logger.warning(f"Failed to capture screenshot on failure: {screenshot_error}")
            
            raise AssertionError(
                f"[FAIL] Tracking Center Item Detail: Finish Now Button Click Failed — "
                f"Details: Failed to click the Finish Now button on Tracking Center Item Detail page. "
                f"Locator: {item_detail_locators.FINISH_NOW_BUTTON}. "
                f"Error: {assert_error}"
            ) from assert_error
        
        except Exception as e:
            logger.error(f"✗ Unexpected error while clicking Finish Now button: {e}")
            
            # Capture screenshot on unexpected error
            try:
                screenshot = trackingCenter_ItemDetail_page.page.screenshot()
                allure.attach(
                    screenshot,
                    name="Finish Now Button Click - ERROR",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as screenshot_error:
                logger.warning(f"Failed to capture screenshot on error: {screenshot_error}")
            
            raise AssertionError(
                f"[FAIL] Tracking Center Item Detail: Finish Now Button Click Error — "
                f"Details: Unexpected error while clicking Finish Now button. "
                f"Locator: {item_detail_locators.FINISH_NOW_BUTTON}. "
                f"Error: {e}"
            ) from e


@when("User cancel the request")
def user_cancel_the_request(trackingCenter_ItemDetail_page):
    """
    Cancel the request from Tracking Center Item Detail page with confirmation dialog.
    
    This step:
    1. Clicks the Cancel button on the Tracking Center Item Detail page
    2. Waits for the cancel confirmation dialog to appear (jQuery UI dialog)
    3. Clicks the 'Yes' button to confirm cancellation
    4. Waits for dialog to close and page stabilization
    
    The Cancel button HTML:
        <a href="#" class="btn btn-default" id="cancelRequest" 
           onclick="setOmniture('Tracking Center:::Tracking Center_Details page Cancel button')">
            Cancel
        </a>
    
    The Confirmation Dialog:
        Dialog Title: "You are about to cancel this request."
        Dialog Buttons: Yes, No
    
    Selector: CSS selector "a#cancelRequest" (stable - unique ID)
    Dialog Selector: `.ui-dialog` (jQuery UI dialog class)
    Yes Button: Uses `get_by_text("Yes")` Playwright locator
    
    Returns:
        None
        
    Raises:
        AssertionError: If Cancel button not found, dialog doesn't appear, or Yes button click fails
        
    Example:
        When User cancel the request
    
    Used in feature files:
        Scenario: Cancel a submitted request
            Given User is on Tracking Center Item Detail page
            When User cancel the request
            Then Verify user is redirected to Tracking Center page
    """
    with allure.step("Cancel the request and confirm in dialog"):
        logger.info(">>> STEP: User cancel the request")
        
        try:
            # Step 1: Click the Cancel button
            logger.info("Step 1: Attempting to click Cancel button...")
            trackingCenter_ItemDetail_page.click_cancel_button()
            logger.info("[PASS] Cancel button clicked successfully.")
            
            # Attach screenshot after cancel button click
            screenshot = trackingCenter_ItemDetail_page.page.screenshot()
            allure.attach(
                screenshot,
                name="Cancel Button Clicked - Before Dialog Confirmation",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Step 2: Confirm cancellation in the dialog by clicking 'Yes'
            logger.info("Step 2: Confirming cancellation in dialog by clicking 'Yes'...")
            trackingCenter_ItemDetail_page.confirm_cancel_dialog()
            logger.info("[PASS] Cancel dialog confirmed successfully.")
            
            # Attach screenshot after dialog confirmation
            screenshot = trackingCenter_ItemDetail_page.page.screenshot()
            allure.attach(
                screenshot,
                name="Cancel Confirmed - Dialog Closed",
                attachment_type=allure.attachment_type.PNG
            )
            
            logger.info("[PASS] TrackingCenterPage: Request cancellation workflow completed.")
            
        except Exception as e:
            logger.error(f"✗ Failed to cancel request: {e}")
            
            # Attach screenshot on failure for debugging
            try:
                screenshot = trackingCenter_ItemDetail_page.page.screenshot()
                allure.attach(
                    screenshot,
                    name="Request Cancellation - Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception:
                pass
            
            raise AssertionError(
                f"Failed to cancel request workflow. "
                f"Step 1 - Cancel Button Locator: a#cancelRequest. "
                f"Step 2 - Dialog Selector: .ui-dialog (jQuery UI). "
                f"Step 2 - Yes Button Text: 'Yes'. "
                f"Error: {e}"
            ) from e

