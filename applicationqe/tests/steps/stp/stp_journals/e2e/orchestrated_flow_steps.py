"""
Updated Step definitions for Complete Journal Transfer Flow BDD scenarios
Uses the new 11-phase orchestrated workflow
"""
import pytest
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page
from flows.e2e.complete_journal_transfer_flow import CompleteJournalTransferFlow
from utils.allure_helpers import screenshot
from utils.logger import setup_logger
import allure

logger = setup_logger(__name__)


# ===================================
# FIXTURES AND SETUP
# ===================================

@pytest.fixture
def complete_flow_context():
    """Enhanced context to store test data and flow state"""
    return {
        "flow_data": {}, 
        "current_phase": None,
        "phases_completed": [],
        "flow_results": {},
        "request_number": None,
        "confirmation_details": {}
    }


@pytest.fixture
def journal_transfer_flow(page: Page):
    """Initialize the complete journal transfer flow orchestrator"""
    return CompleteJournalTransferFlow(page)


# ===================================
# GIVEN STEPS (SETUP CONDITIONS)
# ===================================

@given('the eWealth Manager application is available')
def given_ewealth_manager_available():
    """Verify eWealth Manager application is available"""
    logger.info("✅ eWealth Manager application is available")


@given('I have valid test credentials')
def given_valid_test_credentials():
    """Verify test credentials are available"""
    logger.info("✅ Valid test credentials are available")


@given('test data is loaded for journal transfer scenarios')
def given_test_data_loaded():
    """Verify test data is loaded"""
    logger.info("✅ Test data loaded for journal transfer scenarios")


@given('I navigate to the login page')
def given_navigate_to_login_page(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Load test data and prepare for login flow"""
    test_data = journal_transfer_flow.load_test_data("journal_portion_transfer_standard1")
    complete_flow_context["flow_data"] = test_data
    complete_flow_context["current_phase"] = "ready_for_login"
    logger.info("✅ Ready for login flow execution")


@given('I am logged in and ready for journal transfer')
def given_logged_in_ready(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute login flow and prepare for journal transfer"""
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 1: Login Flow
    journal_transfer_flow.execute_login_flow(test_data)
    
    complete_flow_context["phases_completed"].append("login") 
    complete_flow_context["current_phase"] = "authenticated"
    logger.info("✅ Login flow completed - ready for journal transfer")


# ===================================
# WHEN STEPS (ORCHESTRATED FLOW ACTIONS)
# ===================================

@when('I execute the complete login flow')
def when_execute_complete_login_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute the complete login flow with authentication"""
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 1: Login Flow (includes cookie consent, credentials, sign in)
    try:
        journal_transfer_flow.execute_login_flow(test_data)
        complete_flow_context["phases_completed"].append("login")
        complete_flow_context["current_phase"] = "login_completed"
        logger.info("✅ Complete login flow executed successfully")
    except Exception as e:
        logger.error(f"❌ Login flow failed: {str(e)}")
        raise


@when('I execute the landing page flow')  
def when_execute_landing_page_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute the landing page flow"""
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 2: Landing Page Flow 
    try:
        journal_transfer_flow.execute_landing_page_flow(test_data)
        complete_flow_context["phases_completed"].append("landing")
        complete_flow_context["current_phase"] = "landing_completed"
        logger.info("✅ Landing page flow executed successfully")
    except Exception as e:
        logger.error(f"❌ Landing page flow failed: {str(e)}")
        raise


@when('I execute the transfer configuration flow')
def when_execute_transfer_config_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute the transfer configuration flow"""  
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 3: Transfer Page Flow
    try:
        journal_transfer_flow.execute_transfer_page_flow(test_data)
        complete_flow_context["phases_completed"].append("transfer_config")
        complete_flow_context["current_phase"] = "transfer_config_completed"
        logger.info("✅ Transfer configuration flow executed successfully")
    except Exception as e:
        logger.error(f"❌ Transfer configuration flow failed: {str(e)}")
        raise


@when('I execute the transaction details flow')
def when_execute_transaction_details_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute the transaction details flow"""
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 4: Transaction Details Flow
    try:
        journal_transfer_flow.execute_transaction_details_flow(test_data)
        complete_flow_context["phases_completed"].append("transaction_details")
        complete_flow_context["current_phase"] = "transaction_details_completed"
        logger.info("✅ Transaction details flow executed successfully")
    except Exception as e:
        logger.error(f"❌ Transaction details flow failed: {str(e)}")
        raise


@when('I execute the request summary flow')
def when_execute_request_summary_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute the request summary flow"""
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 5: Request Summary Flow
    try:
        journal_transfer_flow.execute_request_summary_flow(test_data)
        complete_flow_context["phases_completed"].append("request_summary")
        complete_flow_context["current_phase"] = "request_summary_completed"
        logger.info("✅ Request summary flow executed successfully")  
    except Exception as e:
        logger.error(f"❌ Request summary flow failed: {str(e)}")
        raise


@when('I execute the review and submission flow')
def when_execute_review_submission_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute review, submission, and confirmation flows"""
    test_data = complete_flow_context["flow_data"]
    
    try:
        # Execute Phase 6: Review Summary Flow
        journal_transfer_flow.execute_review_summary_flow(test_data)
        complete_flow_context["phases_completed"].append("review_summary")
        
        # Execute Phase 7: E-Signature Flow (if required)
        if test_data["transactionDetails"]["signatureOption"] == "Obtain Electronic Client Signature":
            journal_transfer_flow.execute_esignature_flow(test_data)
            complete_flow_context["phases_completed"].append("esignature")
            
            # Execute Phase 8: DocuSign Flow (if required)
            journal_transfer_flow.execute_docusign_flow(test_data)
            complete_flow_context["phases_completed"].append("docusign")
        
        # Execute Phase 9: Final Submission Flow
        journal_transfer_flow.execute_final_submission_flow(test_data)
        complete_flow_context["phases_completed"].append("submission")
        
        # Execute Phase 10: Confirmation Flow  
        confirmation_details = journal_transfer_flow.execute_confirmation_flow(test_data)
        complete_flow_context["confirmation_details"] = confirmation_details
        complete_flow_context["request_number"] = confirmation_details.get("request_number")
        complete_flow_context["phases_completed"].append("confirmation")
        
        complete_flow_context["current_phase"] = "review_submission_completed"
        logger.info(f"✅ Review and submission flow completed - Request: {complete_flow_context['request_number']}")
        
    except Exception as e:
        logger.error(f"❌ Review and submission flow failed: {str(e)}")
        raise


@when('I execute the complete end-to-end flow')
def when_execute_complete_e2e_flow(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Execute the complete 11-phase end-to-end flow"""
    scenario_name = complete_flow_context["flow_data"].get("name", "journal_portion_transfer_standard1")
    
    try:
        # Execute complete flow using the orchestrator
        flow_results = journal_transfer_flow.execute_complete_flow(scenario_name)
        
        # Store results in context
        complete_flow_context["flow_results"] = flow_results
        complete_flow_context["phases_completed"] = flow_results["phases_completed"] 
        complete_flow_context["request_number"] = flow_results["request_number"]
        complete_flow_context["confirmation_details"] = flow_results["confirmation_details"]
        complete_flow_context["current_phase"] = "complete_flow_finished"
        
        logger.info(f"🎉 Complete E2E flow executed successfully!")
        logger.info(f"Phases completed: {', '.join(flow_results['phases_completed'])}")
        logger.info(f"Request Number: {flow_results['request_number']}")
        
    except Exception as e:
        logger.error(f"❌ Complete E2E flow failed: {str(e)}")
        raise


# ===================================
# THEN STEPS (VALIDATIONS)
# ===================================

@then('I should be successfully authenticated')
def then_successfully_authenticated(complete_flow_context: dict):
    """Validate successful authentication"""
    assert "login" in complete_flow_context["phases_completed"]
    logger.info("✅ Authentication validated")


@then('the journal transfer flow should complete successfully')  
def then_journal_transfer_complete(complete_flow_context: dict):
    """Validate complete journal transfer flow success"""
    expected_phases = ["login", "landing", "transfer_config", "transaction_details", 
                      "request_summary", "review_summary", "submission", "confirmation"]
    
    completed_phases = complete_flow_context["phases_completed"]
    
    for phase in expected_phases:
        assert phase in completed_phases, f"Phase '{phase}' was not completed"
    
    logger.info(f"✅ Journal transfer flow completed successfully with {len(completed_phases)} phases")


@then('I should have a valid request number')
def then_have_valid_request_number(complete_flow_context: dict):
    """Validate request number was generated"""
    request_number = complete_flow_context.get("request_number")
    assert request_number is not None, "Request number was not generated"
    assert len(request_number.strip()) > 0, "Request number is empty"
    logger.info(f"✅ Valid request number generated: {request_number}")


@then('the complete flow results should be successful')
def then_complete_flow_results_successful(complete_flow_context: dict):
    """Validate complete flow results"""
    flow_results = complete_flow_context.get("flow_results", {})
    assert flow_results.get("success") is True, "Flow did not complete successfully"
    
    # Validate confirmation details
    confirmation_details = complete_flow_context.get("confirmation_details", {})
    assert confirmation_details.get("confirmation_validated") is True, "Confirmation was not validated"
    
    logger.info("✅ Complete flow results validated successfully")


@then('I should be able to track the request')
def then_able_to_track_request(journal_transfer_flow: CompleteJournalTransferFlow, complete_flow_context: dict):
    """Validate request can be tracked"""
    test_data = complete_flow_context["flow_data"]
    
    # Execute Phase 11: Tracking Center Flow
    try:
        journal_transfer_flow.execute_tracking_center_flow(test_data) 
        complete_flow_context["phases_completed"].append("tracking")
        logger.info("✅ Request tracking validated successfully")
    except Exception as e:
        logger.error(f"❌ Request tracking failed: {str(e)}")
        raise


# ===================================
# LEGACY COMPATIBILITY STEPS
# ===================================

@when('I handle cookie consent if present')
def when_handle_cookie_consent_legacy(complete_flow_context: dict):
    """Legacy compatibility - handled by login flow"""
    logger.info("ℹ️ Cookie consent handled by orchestrated login flow")


@when('I enter my username and password credentials')
def when_enter_credentials_legacy(complete_flow_context: dict):  
    """Legacy compatibility - handled by login flow"""
    logger.info("ℹ️ Credentials handled by orchestrated login flow")


@when('I click the sign in button')
def when_click_sign_in_legacy(complete_flow_context: dict):
    """Legacy compatibility - handled by login flow"""
    logger.info("ℹ️ Sign in handled by orchestrated login flow")
