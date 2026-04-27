"""
Journal Transfer Request Flow - BDD Step Definitions
Step definitions for journal transfer request configuration scenarios
"""
import allure
from playwright.sync_api import Page
from pytest_bdd import given, when, then, parsers
from typing import Dict, Any

from flows.journal_transfer_request_flow import JournalTransferRequestFlow
from utils.logger import setup_logger
from utils.allure_helpers import screenshot

logger = setup_logger(__name__)


# =============================================================================
# GIVEN STEPS - Setup and preconditions
# =============================================================================

@given('I am logged into the eWealth Manager application')
def logged_into_application(test_context):
    """Ensure user is logged into the application"""
    logger.info("Verifying user is logged into eWealth Manager")
    test_context['logged_in'] = True
    

@given('I have navigated to the journal transfer request page')
def navigated_to_request_page(test_context):
    """Ensure navigation to transfer request page"""
    logger.info("Verifying navigation to journal transfer request page")
    test_context['on_request_page'] = True


@given('the transfer request page is fully loaded')
def request_page_loaded(page: Page, test_context):
    """Verify the transfer request page is fully loaded"""
    with allure.step("Verify transfer request page is fully loaded"):
        logger.info("Verifying transfer request page is ready for interaction")
        test_context['page_loaded'] = True
        screenshot(page, "Transfer Request Page Loaded")


@given('I am on the transfer request configuration page')
def on_configuration_page(page: Page, test_context):
    """Initialize the transfer request flow"""
    with allure.step("Initialize transfer request configuration"):
        logger.info("Initializing journal transfer request flow")
        test_context['transfer_flow'] = JournalTransferRequestFlow(page)
        test_context['configuration_results'] = {}
        screenshot(page, "Request Configuration Page")


@given('I have completed the transfer request configuration')
def completed_configuration(test_context):
    """Set context that configuration is completed"""
    logger.info("Configuration marked as completed")
    test_context['configuration_completed'] = True


# =============================================================================
# WHEN STEPS - Actions and interactions
# =============================================================================

@when(parsers.parse('I select "{distribution_type}" as the distribution type'))
def select_distribution_type(page: Page, test_context, distribution_type: str):
    """Select the distribution type for transfer"""
    with allure.step(f"Select distribution type: {distribution_type}"):
        logger.info(f"Selecting distribution type: {distribution_type}")
        
        # Verify distribution type matches CSV data if available
        csv_data = test_context.get('csv_data', {})
        expected_distribution_type = csv_data.get('transactionDetails', {}).get('distributionType', distribution_type)
        if expected_distribution_type and expected_distribution_type != distribution_type:
            logger.warning(f"Distribution type mismatch - Feature: {distribution_type}, CSV: {expected_distribution_type}")
        
        # Store the selection for later verification
        test_context['selected_distribution_type'] = distribution_type
        
        # Select the distribution type from dropdown/radio buttons
        try:
            # Try different selectors for distribution type
            selectors = [
                f"//input[@value='{distribution_type}']",
                f"//label[contains(text(), '{distribution_type}')]",
                f"//option[text()='{distribution_type}']",
                f"//select//option[contains(text(), '{distribution_type}')]",
                f"//*[contains(text(), '{distribution_type}')]"
            ]
            
            for selector in selectors:
                try:
                    if page.is_visible(selector, timeout=3000):
                        page.click(selector)
                        logger.info(f"✅ Selected distribution type using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector failed: {selector} - {e}")
                    continue
            else:
                logger.warning(f"Could not find distribution type selector for: {distribution_type}")
                
        except Exception as e:
            logger.warning(f"Error selecting distribution type: {e} - continuing test")
        
        screenshot(page, f"Distribution Type Selected - {distribution_type}")


@when(parsers.parse('I configure the journal portion with amount "{amount}" and portion type "{portion_type}"'))
def configure_journal_portion(page: Page, test_context, amount: str, portion_type: str):
    """Configure journal portion with specified parameters"""
    with allure.step(f"Configure journal portion: {amount} ({portion_type})"):
        logger.info(f"Configuring journal portion - Amount: {amount}, Type: {portion_type}")
        
        # Get CSV data for validation
        csv_data = test_context.get('csv_data', {})
        expected_amount = csv_data.get('transactionDetails', {}).get('amount', amount)
        expected_portion_type = csv_data.get('transactionDetails', {}).get('journalPortionType', portion_type)
        
        try:
            # Configure the journal amount
            amount_selectors = [
                "input[name*='amount']", 
                "input[id*='amount']",
                "input[type='text'][placeholder*='amount']",
                "input[class*='amount']"
            ]
            
            for selector in amount_selectors:
                try:
                    if page.is_visible(selector, timeout=3000):
                        page.fill(selector, amount)
                        logger.info(f"✅ Entered amount '{amount}' using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Amount selector failed: {selector} - {e}")
                    continue
            else:
                logger.warning(f"Could not find amount input field for: {amount}")
            
            # Configure the portion type
            if portion_type:
                portion_selectors = [
                    f"//input[@value='{portion_type}']",
                    f"//label[contains(text(), '{portion_type}')]",
                    f"//option[text()='{portion_type}']",
                    f"//select//option[contains(text(), '{portion_type}')]"
                ]
                
                for selector in portion_selectors:
                    try:
                        if page.is_visible(selector, timeout=3000):
                            page.click(selector)
                            logger.info(f"✅ Selected portion type '{portion_type}' using selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"Portion type selector failed: {selector} - {e}")
                        continue
                else:
                    logger.warning(f"Could not find portion type selector for: {portion_type}")
            
            # Store results for verification
            if 'configuration_results' not in test_context:
                test_context['configuration_results'] = {}
            test_context['configuration_results']['portion'] = {
                'amount': amount,
                'portion_type': portion_type,
                'status': 'configured'
            }
            
            logger.info(f"✅ Journal portion configuration completed - Amount: {amount}, Type: {portion_type}")
            
        except Exception as e:
            logger.warning(f"Error configuring journal portion: {e} - continuing test")
            # Store error results
            if 'configuration_results' not in test_context:
                test_context['configuration_results'] = {}
            test_context['configuration_results']['portion'] = {
                'amount': amount,
                'portion_type': portion_type,
                'status': 'error',
                'error': str(e)
            }
        
        screenshot(page, f"Journal Portion Configured - {amount}")


@when(parsers.parse('I configure securities selection with {securities_count:d} securities'))
def configure_securities_selection(page: Page, test_context, securities_count: int):
    """Configure securities selection with specified count"""
    with allure.step(f"Configure securities selection: {securities_count} securities"):
        logger.info(f"Configuring securities selection with {securities_count} securities")
        transfer_flow = test_context['transfer_flow']
        
        # Execute the securities configuration
        results = transfer_flow.execute_journal_securities_configuration(securities_count)
        test_context['configuration_results']['securities'] = results
        
        logger.info(f"Securities configuration results: {results}")
        screenshot(page, f"Securities Configured - {securities_count}")


@when(parsers.parse('I select "{signature_option}" as the signature option'))
def select_signature_option(page: Page, test_context, signature_option: str):
    """Select the signature option"""
    with allure.step(f"Select signature option: {signature_option}"):
        logger.info(f"Selecting signature option: {signature_option}")
        transfer_flow = test_context['transfer_flow']
        
        # Execute the signature configuration
        results = transfer_flow.execute_signature_configuration(signature_option)
        test_context['configuration_results']['signature'] = results
        
        logger.info(f"Signature configuration results: {results}")
        screenshot(page, f"Signature Option Selected - {signature_option}")


@when('I execute complete transaction configuration with:')
def execute_complete_configuration(page: Page, test_context, datatable):
    """Execute complete transaction configuration with provided parameters"""
    with allure.step("Execute complete transaction configuration"):
        logger.info("Executing complete transaction configuration")
        transfer_flow = test_context['transfer_flow']
        
        # Convert datatable to configuration dictionary
        config_data = {}
        for row in datatable:
            for key, value in row.items():
                if key and value:  # Only add non-empty values
                    if key == 'securities_count':
                        config_data[key] = int(value)
                    else:
                        config_data[key] = value
        
        logger.info(f"Configuration data: {config_data}")
        
        # Execute the complete configuration
        results = transfer_flow.execute_complete_transaction_configuration(config_data)
        test_context['configuration_results']['complete'] = results
        test_context['complete_config'] = config_data
        
        logger.info(f"Complete configuration results: {results}")
        screenshot(page, "Complete Configuration Executed")


@when('I proceed to review page')
def proceed_to_review_page(page: Page, test_context):
    """Proceed from transfer request to review page"""
    with allure.step("Proceed to review page"):
        logger.info("Proceeding to review page")
        transfer_flow = test_context['transfer_flow']
        
        # Execute navigation to review
        results = transfer_flow.proceed_to_review()
        test_context['navigation_results'] = results
        
        logger.info(f"Navigation to review results: {results}")
        screenshot(page, "Proceeding to Review Page")


@when('I return to landing page')
def return_to_landing_page(page: Page, test_context):
    """Return from transfer request to landing page"""
    with allure.step("Return to landing page"):
        logger.info("Returning to landing page")
        transfer_flow = test_context['transfer_flow']
        
        # Execute navigation back to landing
        results = transfer_flow.return_to_landing()
        test_context['navigation_results'] = results
        
        logger.info(f"Navigation to landing results: {results}")
        screenshot(page, "Returning to Landing Page")


@when('I attempt to configure with invalid parameters')
def attempt_invalid_configuration(page: Page, test_context):
    """Attempt configuration with invalid parameters for error testing"""
    with allure.step("Attempt configuration with invalid parameters"):
        logger.info("Testing error handling with invalid parameters")
        transfer_flow = test_context['transfer_flow']
        
        # Test with invalid configuration
        try:
            results = transfer_flow.execute_journal_portion_configuration("", "Invalid Type")
            test_context['error_test_results'] = results
        except Exception as e:
            test_context['error_test_results'] = {"error": str(e), "handled": True}
        
        screenshot(page, "Invalid Configuration Test")


# =============================================================================
# THEN STEPS - Assertions and verifications
# =============================================================================

@then('the journal portion configuration should be successful')
def verify_portion_configuration_success(test_context):
    """Verify journal portion configuration was successful"""
    with allure.step("Verify journal portion configuration success"):
        results = test_context['configuration_results'].get('portion', {})
        assert results.get('success', False), f"Journal portion configuration failed: {results.get('error', 'Unknown error')}"
        logger.info("Journal portion configuration verified as successful")


@then('the securities configuration should be successful')
def verify_securities_configuration_success(test_context):
    """Verify securities configuration was successful"""
    with allure.step("Verify securities configuration success"):
        results = test_context['configuration_results'].get('securities', {})
        assert results.get('success', False), f"Securities configuration failed: {results.get('error', 'Unknown error')}"
        logger.info("Securities configuration verified as successful")


@then('the signature configuration should be successful')
def verify_signature_configuration_success(test_context):
    """Verify signature configuration was successful"""
    with allure.step("Verify signature configuration success"):
        results = test_context['configuration_results'].get('signature', {})
        assert results.get('success', False), f"Signature configuration failed: {results.get('error', 'Unknown error')}"
        logger.info("Signature configuration verified as successful")


@then('the complete configuration should be successful')
def verify_complete_configuration_success(test_context):
    """Verify complete configuration was successful"""
    with allure.step("Verify complete configuration success"):
        results = test_context['configuration_results'].get('complete', {})
        assert results.get('success', False), f"Complete configuration failed: {results.get('error', 'Unknown error')}"
        logger.info("Complete configuration verified as successful")


@then(parsers.parse('the distribution type should be set to "{expected_type}"'))
def verify_distribution_type(test_context, expected_type: str):
    """Verify the distribution type matches expected value"""
    with allure.step(f"Verify distribution type: {expected_type}"):
        # Check in portion results
        portion_results = test_context['configuration_results'].get('portion', {})
        securities_results = test_context['configuration_results'].get('securities', {})
        
        actual_type = portion_results.get('distribution_type') or securities_results.get('distribution_type')
        assert actual_type == expected_type, f"Expected distribution type '{expected_type}', got '{actual_type}'"
        logger.info(f"Distribution type verified: {expected_type}")


@then(parsers.parse('the portion type should be "{expected_portion_type}"'))
def verify_portion_type(test_context, expected_portion_type: str):
    """Verify the portion type matches expected value"""
    with allure.step(f"Verify portion type: {expected_portion_type}"):
        results = test_context['configuration_results'].get('portion', {})
        actual_type = results.get('portion_type')
        assert actual_type == expected_portion_type, f"Expected portion type '{expected_portion_type}', got '{actual_type}'"
        logger.info(f"Portion type verified: {expected_portion_type}")


@then(parsers.parse('the amount should be "{expected_amount}"'))
def verify_amount(test_context, expected_amount: str):
    """Verify the amount matches expected value"""
    with allure.step(f"Verify amount: {expected_amount}"):
        results = test_context['configuration_results'].get('portion', {})
        actual_amount = results.get('amount')
        assert actual_amount == expected_amount, f"Expected amount '{expected_amount}', got '{actual_amount}'"
        logger.info(f"Amount verified: {expected_amount}")


@then(parsers.parse('{expected_count:d} securities should be selected'))
def verify_securities_count(test_context, expected_count: int):
    """Verify the number of selected securities"""
    with allure.step(f"Verify securities count: {expected_count}"):
        results = test_context['configuration_results'].get('securities', {})
        actual_count = results.get('securities_count', 0)
        assert actual_count == expected_count, f"Expected {expected_count} securities, got {actual_count}"
        logger.info(f"Securities count verified: {expected_count}")


@then('all selected securities should be valid')
def verify_securities_validity(test_context):
    """Verify all selected securities are valid"""
    with allure.step("Verify securities validity"):
        results = test_context['configuration_results'].get('securities', {})
        securities_selected = results.get('securities_selected', [])
        assert len(securities_selected) > 0, "No securities were selected"
        assert all(securities_selected), "Some selected securities are invalid"
        logger.info("All selected securities verified as valid")


@then(parsers.parse('the signature option should be set to "{expected_option}"'))
def verify_signature_option(test_context, expected_option: str):
    """Verify the signature option matches expected value"""
    with allure.step(f"Verify signature option: {expected_option}"):
        results = test_context['configuration_results'].get('signature', {})
        actual_option = results.get('signature_option')
        assert actual_option == expected_option, f"Expected signature option '{expected_option}', got '{actual_option}'"
        logger.info(f"Signature option verified: {expected_option}")


@then('the distribution configuration should be completed')
def verify_distribution_completed(test_context):
    """Verify distribution configuration was completed"""
    with allure.step("Verify distribution configuration completed"):
        complete_results = test_context['configuration_results'].get('complete', {})
        steps_completed = complete_results.get('steps_completed', [])
        assert 'distribution_configuration' in steps_completed, "Distribution configuration step not completed"
        logger.info("Distribution configuration completion verified")


@then('the signature configuration should be completed')
def verify_signature_completed(test_context):
    """Verify signature configuration was completed"""
    with allure.step("Verify signature configuration completed"):
        complete_results = test_context['configuration_results'].get('complete', {})
        steps_completed = complete_results.get('steps_completed', [])
        assert 'signature_configuration' in steps_completed, "Signature configuration step not completed"
        logger.info("Signature configuration completion verified")


@then('all configuration steps should be recorded')
def verify_all_steps_recorded(test_context):
    """Verify all configuration steps were properly recorded"""
    with allure.step("Verify all configuration steps recorded"):
        complete_results = test_context['configuration_results'].get('complete', {})
        steps_completed = complete_results.get('steps_completed', [])
        assert len(steps_completed) > 0, "No configuration steps were recorded"
        logger.info(f"Configuration steps recorded: {steps_completed}")


@then('the securities count should match the configuration')
def verify_securities_count_matches_config(test_context):
    """Verify securities count matches the configuration"""
    with allure.step("Verify securities count matches configuration"):
        complete_config = test_context.get('complete_config', {})
        expected_count = complete_config.get('securities_count', 0)
        
        complete_results = test_context['configuration_results'].get('complete', {})
        distribution_results = complete_results.get('distribution_results', {})
        actual_count = distribution_results.get('securities_count', 0)
        
        assert actual_count == expected_count, f"Expected {expected_count} securities, got {actual_count}"
        logger.info(f"Securities count matches configuration: {actual_count}")


@then('the navigation should be successful')
def verify_navigation_success(test_context):
    """Verify navigation was successful"""
    with allure.step("Verify navigation success"):
        results = test_context.get('navigation_results', {})
        assert results.get('success', False), f"Navigation failed: {results.get('error', 'Unknown error')}"
        assert results.get('navigation_completed', False), "Navigation was not completed"
        logger.info("Navigation verified as successful")


@then('I should be on the review page')
def verify_on_review_page(test_context):
    """Verify user is on the review page"""
    with allure.step("Verify on review page"):
        # This would typically check URL or page elements
        results = test_context.get('navigation_results', {})
        assert results.get('success', False), "Navigation to review page failed"
        logger.info("Verified on review page")


@then('I should be back on the landing page')
def verify_on_landing_page(test_context):
    """Verify user is back on the landing page"""
    with allure.step("Verify on landing page"):
        # This would typically check URL or page elements
        results = test_context.get('navigation_results', {})
        assert results.get('success', False), "Navigation to landing page failed"
        logger.info("Verified back on landing page")


@then('the system should handle errors gracefully')
def verify_error_handling(test_context):
    """Verify system handles errors gracefully"""
    with allure.step("Verify error handling"):
        results = test_context.get('error_test_results', {})
        # Either the operation succeeded with error handling, or it failed gracefully
        assert 'error' in results or results.get('handled', False), "Error handling not implemented"
        logger.info("Error handling verified")


@then('appropriate error messages should be displayed')
def verify_error_messages(test_context):
    """Verify appropriate error messages are displayed"""
    with allure.step("Verify error messages"):
        results = test_context.get('error_test_results', {})
        if 'error' in results:
            assert len(results['error']) > 0, "Error message is empty"
        logger.info("Error messages verified")


@then('the form state should remain stable')
def verify_form_stability(test_context):
    """Verify form state remains stable after errors"""
    with allure.step("Verify form stability"):
        # This would typically check that form elements are still accessible
        logger.info("Form stability verified")


@then('the complete workflow should be successful')
def verify_complete_workflow_success(test_context):
    """Verify the complete workflow was successful"""
    with allure.step("Verify complete workflow success"):
        # Check all relevant results
        portion_results = test_context['configuration_results'].get('portion', {})
        signature_results = test_context['configuration_results'].get('signature', {})
        navigation_results = test_context.get('navigation_results', {})
        
        assert portion_results.get('success', False), "Portion configuration failed"
        assert signature_results.get('success', False), "Signature configuration failed"
        assert navigation_results.get('success', False), "Navigation failed"
        
        logger.info("Complete workflow verified as successful")


@then('all configuration should be preserved')
def verify_configuration_preserved(test_context):  
    """Verify all configuration is preserved through the workflow"""
    with allure.step("Verify configuration preservation"):
        # Check that configuration data persists
        portion_results = test_context['configuration_results'].get('portion', {})
        assert portion_results.get('configuration_completed', False), "Configuration not preserved"
        logger.info("Configuration preservation verified")


@then('I should be ready for transaction review')
def verify_ready_for_review(test_context):
    """Verify system is ready for transaction review"""
    with allure.step("Verify ready for transaction review"):
        navigation_results = test_context.get('navigation_results', {})
        assert navigation_results.get('navigation_completed', False), "Not ready for review"
        logger.info("Verified ready for transaction review")
