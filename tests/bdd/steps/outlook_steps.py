from datetime import datetime
from typing import Optional
import allure
from playwright.sync_api import Page
from pytest_bdd import when, then
from pages.docusign_page import DocuSignPage
from pages.outlook_page import OutlookPage
from utils.allure_logger import get_allure_logger
from utils.database import fetch_agent_name_by_aplid_from_db

logger = get_allure_logger(__name__)


@when("User fetches OTP from email")
def fetch_otp_from_outlook(page: Page):
    """Fetch OTP from Outlook using OutlookPage helper.

    This is a placeholder step; adjust the submitting_time and
    max_wait_time_in_seconds as per your scenario needs.
    """
    with allure.step("Fetch OTP from Outlook"):
        logger.info("Initializing OutlookPage and fetching OTP")
        otp_page = OutlookPage.from_config(page)
        submitting_time = datetime.now().time()
        otp = otp_page.get_otp_with_retry(submitting_time, max_wait_time_in_seconds=60)

        if otp:
            allure.attach(otp, name="Fetched OTP", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach(
                "No OTP fetched", name="Fetched OTP", attachment_type=allure.attachment_type.TEXT
            )

@when("User login to the email and search the authorized signer email")
def user_login_to_the_email_and_search_the_authorized_signer_email(page: Page, test_context):
    """Login to Outlook and search for authorized signer email using the stored D number."""
    with allure.step("User login to the email and search the authorized signer email"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError(
                "D-number not found in test_context. Ensure the step that clicks and stores the D-number runs before this step."
            )

        outlook_page = OutlookPage.from_config(page)
        outlook_email_page = None
        try:
            outlook_email_page = outlook_page.login_outlook(context_message="search authorized signer email")
            outlook_page.search_authorized_signer_email(outlook_email_page, d_number)
            # Store the outlook page in test_context for the next step
            test_context["outlook_email_page"] = outlook_email_page
        finally:
            # Don't close the page here; let the next step handle it
            try:
                page.bring_to_front()
            except Exception:
                pass

@then("Verify authorized signer email content")
def fetch_authorized_signer_email_subject_and_body_step(page: Page, test_context):
    """Verify authorized signer email content and fetch subject and body."""
    with allure.step("Verify authorized signer email content"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError(
                "D-number not found in test_context. Ensure the step that stores the D-number runs before this step."
            )
        
        outlook_email_page = test_context.get("outlook_email_page")
        if not outlook_email_page:
            logger.warning("Outlook email page not found in test_context. Creating new login session...")
            outlook_page = OutlookPage.from_config(page)
            outlook_email_page = outlook_page.login_outlook(context_message="verify authorized signer email")
            outlook_page.search_authorized_signer_email(outlook_email_page, d_number)
        
        try:
            outlook_page = OutlookPage.from_config(page)
            actual_subject, actual_body = outlook_page.fetch_authorized_signer_email_subject_and_body(outlook_email_page, d_number)
            
            logger.info(f"Authorized Signer Email Subject: {actual_subject}")
            logger.info(f"Authorized Signer Email Body (first 500 chars): {actual_body[:500]}")
            
            # Step: Get expected email subject and body from test data
            test_data = test_context.get("test_data", {})
            expected_subject = test_data.get("Expected_AuthorizedSigner_Email_Subject", "")
            expected_body = test_data.get("Expected_AuthorizedSigner_Email_Body", "")
            document_creator_role = test_data.get("Document_Creator_Role", "")
            authorized_signer_role = test_data.get("Authorized_Signer_Role", "")
            agent_id = test_data.get("Agent", "")
            username = test_data.get("username", "")
            
            # Log expected values
            logger.info(f"Expected Authorized Signer Email Subject (before substitution): {expected_subject}")
            logger.info(f"Expected Authorized Signer Email Body (before substitution) (first 500 chars): {expected_body[:500] if expected_body else ''}")
            logger.info(f"Document Creator Role: {document_creator_role}")
            logger.info(f"Authorized Signer Role: {authorized_signer_role}")
            
            # Fetch agent names based on roles
            # For document creator role
            if document_creator_role.upper() in ["FA", "AGENT"]:
                document_creator_aplid = agent_id
            else:  # SAU or OA (both use username)
                document_creator_aplid = username
            
            document_creator_role_name = fetch_agent_name_by_aplid_from_db(document_creator_aplid, document_creator_role)
            logger.info(f"Document Creator Role Name: {document_creator_role_name}")
            
            # For authorized signer role
            if authorized_signer_role.upper() in ["FA", "AGENT"]:
                authorized_signer_aplid = agent_id
            else:  # SAU or OA (both use username)
                authorized_signer_aplid = username
            
            authorized_signer_role_name = fetch_agent_name_by_aplid_from_db(authorized_signer_aplid, authorized_signer_role)
            logger.info(f"Authorized Signer Role Name: {authorized_signer_role_name}")
            
            # Replace placeholders in expected subject and body
            expected_subject_resolved = expected_subject.replace("<D Number>", d_number)
            expected_subject_resolved = expected_subject_resolved.replace("<Document_Creator_Role_Name>", document_creator_role_name or "")
            expected_subject_resolved = expected_subject_resolved.replace("<Authorized_Signer_Role_Name>", authorized_signer_role_name or "")
            expected_subject = expected_subject_resolved

            expected_body_resolved = expected_body.replace("<Document_Creator_Role_Name>", document_creator_role_name or "")
            expected_body_resolved = expected_body_resolved.replace("<Authorized_Signer_Role_Name>", authorized_signer_role_name or "")
            expected_body = expected_body_resolved
            
            logger.info(f"Actual Authorized Signer Email Subject: {actual_subject}")
            logger.info(f"Actual Authorized Signer Email Body (first 500 chars): {actual_body[:500] if actual_body else ''}")
            logger.info(f"Expected Authorized Signer Email Subject (after substitution): {expected_subject}")
            logger.info(f"Expected Authorized Signer Email Body (after substitution) (first 500 chars): {expected_body[:500] if expected_body else ''}")
            
            # Attach both actual and expected to Allure report
            with allure.step("Email content comparison"):
                allure.attach(
                    actual_subject,
                    name="Actual Authorized Signer Email Subject",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    expected_subject,
                    name="Expected Authorized Signer Email Subject (resolved)",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    actual_body[:1000],
                    name="Actual Authorized Signer Email Body",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    expected_body[:1000] if expected_body else "No expected body provided",
                    name="Expected Authorized Signer Email Body (resolved)",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Attach role information to Allure report
            with allure.step("Scenario Role Information"):
                allure.attach(
                    document_creator_role,
                    name="Document Creator Role",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    authorized_signer_role,
                    name="Authorized Signer Role",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    document_creator_role_name or "Not found",
                    name="Document Creator Role Name",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    authorized_signer_role_name or "Not found",
                    name="Authorized Signer Role Name",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Verify email content matches expected
            with allure.step("Verify email content"):
                # Strip whitespace for comparison to handle CSV parsing issues with extra spaces/newlines
                actual_subject_stripped = actual_subject.strip()
                expected_subject_stripped = expected_subject.strip()
                actual_body_stripped = actual_body.strip()
                expected_body_stripped = expected_body.strip()
                
                if actual_subject_stripped != expected_subject_stripped:
                    error_msg = f"Email subject mismatch.\nExpected: {expected_subject_stripped}\nActual: {actual_subject_stripped}"
                    logger.error(error_msg)
                    allure.attach(error_msg, name="Subject Mismatch", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(error_msg)
                
                # For email body, use substring match since Outlook may add headers, warnings, and footers
                # Check if expected body text is contained within the actual body
                if expected_body_stripped not in actual_body_stripped:
                    error_msg = f"Email body mismatch.\nExpected (substring): {expected_body_stripped}\nActual: {actual_body_stripped}"
                    logger.error(error_msg)
                    allure.attach(error_msg, name="Body Mismatch", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(error_msg)
                
                logger.info("✓ Email subject and body match expected values")
                allure.attach("Email subject and body match expected values", name="Verification Result", attachment_type=allure.attachment_type.TEXT)
            
        finally:
            # Don't close the email page here - it's needed by the next step
            # "User perform advisor signature 'by mail' method" to click the Review Document link
            try:
                page.bring_to_front()
            except Exception:
                pass

@when("User login to the email and complete the Workflow Approver signature")
def user_login_to_the_email_and_complete_the_workflow_approver_signature(page: Page, test_context):
    """Login to Outlook and complete the authorized signer DocuSign flow using the stored D number."""
    with allure.step("User login to the email and complete the Workflow Approver signature"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError(
                "D-number not found in test_context. Ensure the step that clicks and stores the D-number runs before this step."
            )

        outlook_page = OutlookPage.from_config(page)
        outlook_page.login_and_complete_the_signing_without_otp(d_number)

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="DocuSign Page Loaded",
            attachment_type=allure.attachment_type.PNG
        )

@when("User login to the email and fetch the latest OTP")
def user_login_to_the_email_and_fetch_the_latest_otp(page: Page, test_context):
    """Login to Outlook and fetch the latest OTP using the stored D number."""
    with allure.step("User login to the email and fetch the latest OTP"):
        docu_sign_page = DocuSignPage(page)
        docu_sign_page.complete_signing_with_outlook_otp(max_wait_time_in_seconds=60, session_timeout_check=False)

@then("Verify that the carbon copy of the signed document has been received in the email")
def user_verifies_carbon_copy_received_in_email(page: Page, test_context):
    """Login to Outlook and verify that the carbon copy of the signed document has been received in the email using the stored D number."""
    with allure.step("Verify that the carbon copy of the signed document has been received in the email"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError(
                "D-number not found in test_context. Ensure the step that clicks and stores the D-number runs before this step."
            )

        outlook_page = OutlookPage.from_config(page)
        outlook_page.login_and_click_the_carbon_copy(d_number)

        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="DocuSign Page Loaded",
            attachment_type=allure.attachment_type.PNG
        )

@when("User click on Review Document link in authorized signer email")
def user_click_on_review_document_link_in_authorized_signer_email(page: Page, test_context):
    """Click on Review Document link in the authorized signer email."""
    with allure.step("Click on Review Document link in authorized signer email"):
        outlook_email_page = test_context.get("outlook_email_page")
        if not outlook_email_page:
            raise ValueError(
                "Outlook email page not found in test_context. Ensure the email search step runs before this step."
            )
        
        try:
            outlook_page = OutlookPage.from_config(page)
            docusign_page = outlook_page.click_review_document_link(outlook_email_page)
            
            logger.info("✓ Successfully clicked Review Document link")
            allure.attach("Review Document link clicked, DocuSign page opened", name="Review Document Action", attachment_type=allure.attachment_type.TEXT)
            
            # Store DocuSign page in context for future steps if needed
            test_context["docusign_page"] = docusign_page
            
        except Exception as ex:
            logger.error(f"Error clicking Review Document link: {ex}")
            allure.attach(str(ex), name="Error clicking Review Document", attachment_type=allure.attachment_type.TEXT)
            raise        