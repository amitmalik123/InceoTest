import re
from datetime import datetime
from typing import Optional, Tuple
import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pytest_bdd import when, then, parsers
from config.settings import get_settings
from pages.docusign_page import DocuSignPage
from pages.outlook_page import OutlookPage
from utils.allure_logger import get_allure_logger
from utils.database import fetch_agent_name_by_aplid_from_db

logger = get_allure_logger(__name__)


def _open_outlook(ewm_page: Page) -> Tuple[Page, OutlookPage]:
    """Open Outlook in a new tab, sign in if needed, and return (email_page, outlook_page_obj)."""
    outlook_email_page = ewm_page.context.new_page()
    outlook_email_page.goto(get_settings().outlook_url, wait_until="domcontentloaded")
    outlook_page = OutlookPage.from_config(outlook_email_page)
    if not outlook_page.handle_sign_in():
        raise RuntimeError("Outlook sign-in did not complete successfully.")
    try:
        outlook_page.loading_logo.wait_for(state="hidden", timeout=10_000)
    except Exception:
        pass
    return outlook_email_page, outlook_page


@when("User fetches OTP from email")
def fetch_otp_from_outlook(page: Page):
    with allure.step("Fetch OTP from Outlook"):
        logger.info("Opening Outlook and fetching OTP")
        outlook_email_page, outlook_page = _open_outlook(page)
        try:
            otp = outlook_page.get_otp_with_retry(timeout=60)
            if otp:
                allure.attach(otp, name="Fetched OTP", attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("No OTP fetched", name="Fetched OTP", attachment_type=allure.attachment_type.TEXT)
        finally:
            outlook_email_page.close()
            page.bring_to_front()

@when(parsers.parse('User login to the email and search the authorized signer email with subject "{email_subject}" and body "{email_body}"'))
def user_login_to_the_email_and_search_the_authorized_signer_email(page: Page, test_context, email_subject: str, email_body: str):
    with allure.step("User login to the email and search the authorized signer email"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError("D-number not found in test_context.")

        outlook_email_page, outlook_page = _open_outlook(page)
        outlook_page.search_authorized_signer_email(d_number, subject=email_subject, body=email_body)

        screenshot = outlook_email_page.screenshot()
        allure.attach(screenshot, name="Authorized Signer Email Found", attachment_type=allure.attachment_type.PNG)

        test_context["outlook_email_page"] = outlook_email_page
        test_context["outlook_page"] = outlook_page
        try:
            page.bring_to_front()
        except Exception:
            pass

@then(parsers.parse('Verify email contains subject "{expected_subject}" and body "{expected_body}"'))
def verify_email_subject_and_body(page: Page, test_context, expected_subject: str, expected_body: str):
    with allure.step(f"Verify email contains subject '{expected_subject}' and body '{expected_body}'"):
        outlook_page_obj: Optional[OutlookPage] = test_context.get("outlook_page")
        if not outlook_page_obj:
            raise ValueError("Outlook page not found in test_context. Ensure the email search step runs before this step.")

        d_number = test_context.get("d_number", "")
        actual_subject, actual_body = outlook_page_obj.fetch_authorized_signer_email_subject_and_body(d_number)

        outlook_email_page = test_context.get("outlook_email_page")
        if outlook_email_page:
            screenshot = outlook_email_page.screenshot()
            allure.attach(screenshot, name="Email Content - Before Verification", attachment_type=allure.attachment_type.PNG)

        allure.attach(actual_subject, name="Actual Email Subject", attachment_type=allure.attachment_type.TEXT)
        allure.attach(actual_body[:1000], name="Actual Email Body", attachment_type=allure.attachment_type.TEXT)

        assert expected_subject.strip().lower() in actual_subject.strip().lower(), (
            f"Email subject mismatch.\nExpected to contain: {expected_subject}\nActual: {actual_subject}"
        )
        assert expected_body.strip().lower() in actual_body.strip().lower(), (
            f"Email body mismatch.\nExpected to contain: {expected_body}\nActual (first 500): {actual_body[:500]}"
        )

        if outlook_email_page:
            screenshot = outlook_email_page.screenshot()
            allure.attach(screenshot, name="Email Content - Verified", attachment_type=allure.attachment_type.PNG)

        logger.info("Γ£ô Email subject and body verified successfully")


@then("Verify authorized signer email content")
def fetch_authorized_signer_email_subject_and_body_step(page: Page, test_context):
    with allure.step("Verify authorized signer email content"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError(
                "D-number not found in test_context. Ensure the step that stores the D-number runs before this step."
            )
        
        outlook_email_page = test_context.get("outlook_email_page")
        outlook_page_obj: Optional[OutlookPage] = test_context.get("outlook_page")

        if not outlook_email_page or not outlook_page_obj:
            logger.warning("Outlook page not found in test_context. Creating new login session...")
            outlook_email_page, outlook_page_obj = _open_outlook(page)
            outlook_page_obj.search_authorized_signer_email(d_number)

        try:
            actual_subject, actual_body = outlook_page_obj.fetch_authorized_signer_email_subject_and_body(d_number)
            
            logger.info(f"Authorized Signer Email Subject: {actual_subject}")
            logger.info(f"Authorized Signer Email Body (first 500 chars): {actual_body[:500]}")

            test_data = test_context.get("test_data", {})
            expected_subject = test_data.get("Expected_AuthorizedSigner_Email_Subject", "")
            expected_body = test_data.get("Expected_AuthorizedSigner_Email_Body", "")
            document_creator_role = test_data.get("Document_Creator_Role", "")
            authorized_signer_role = test_data.get("Authorized_Signer_Role", "")
            agent_id = test_data.get("Agent", "")
            username = test_data.get("username", "")

            logger.info(f"Expected Authorized Signer Email Subject (before substitution): {expected_subject}")
            logger.info(f"Expected Authorized Signer Email Body (before substitution) (first 500 chars): {expected_body[:500] if expected_body else ''}")
            logger.info(f"Document Creator Role: {document_creator_role}")
            logger.info(f"Authorized Signer Role: {authorized_signer_role}")

            if document_creator_role:
                if document_creator_role.upper() in ["FA", "AGENT"]:
                    document_creator_aplid = agent_id
                else:
                    document_creator_aplid = username
                document_creator_role_name = fetch_agent_name_by_aplid_from_db(document_creator_aplid, document_creator_role)
            else:
                document_creator_role_name = ""
                logger.warning("Document_Creator_Role is empty in test data; skipping DB lookup for document creator name.")
            logger.info(f"Document Creator Role Name: {document_creator_role_name}")

            test_context["document_creator_role_name"] = document_creator_role_name
            logger.info(f"  Stored document_creator_role_name in test_context: {document_creator_role_name}")

            authorized_signer_role_name = test_context.get("authorized_signer")
            if not authorized_signer_role_name:
                logger.warning("Authorized signer not found in test_context. Will fetch from database...")
            else:
                logger.info(f"Γ£ô Authorized signer name retrieved from test_context")
            logger.info(f"Authorized Signer Role Name: {authorized_signer_role_name}")

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

            with allure.step("Verify email content"):
                actual_subject_stripped = actual_subject.strip()
                expected_subject_stripped = expected_subject.strip()
                actual_body_stripped = actual_body.strip()
                expected_body_stripped = expected_body.strip()
                
                if actual_subject_stripped != expected_subject_stripped:
                    error_msg = f"Email subject mismatch.\nExpected: {expected_subject_stripped}\nActual: {actual_subject_stripped}"
                    logger.error(error_msg)
                    allure.attach(error_msg, name="Subject Mismatch", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(error_msg)

                if expected_body_stripped not in actual_body_stripped:
                    error_msg = f"Email body mismatch.\nExpected (substring): {expected_body_stripped}\nActual: {actual_body_stripped}"
                    logger.error(error_msg)
                    allure.attach(error_msg, name="Body Mismatch", attachment_type=allure.attachment_type.TEXT)
                    raise AssertionError(error_msg)
                
                logger.info("Γ£ô Email subject and body match expected values")
                allure.attach("Email subject and body match expected values", name="Verification Result", attachment_type=allure.attachment_type.TEXT)

        finally:
            try:
                page.bring_to_front()
            except Exception:
                pass

@when("User login to the email and complete the Workflow Approver signature")
def user_login_to_the_email_and_complete_the_workflow_approver_signature(page: Page, test_context):
    with allure.step("User login to the email and complete the Workflow Approver signature"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError("D-number not found in test_context.")

        outlook_email_page, outlook_page = _open_outlook(page)
        try:
            outlook_page._click_inbox_search_and_select(d_number, retries=3, subject="AssetMark for eSig")

            with outlook_email_page.expect_popup() as popup_info:
                outlook_page.review_document_link.click()

            docusign_raw_page = popup_info.value
            docusign_page = DocuSignPage(docusign_raw_page)
            docusign_page.verify_docusign_page_loaded()
            docusign_page.complete_ersd_and_finish()

            screenshot = page.screenshot()
            allure.attach(screenshot, name="DocuSign Page Loaded", attachment_type=allure.attachment_type.PNG)
        finally:
            outlook_email_page.close()
            try:
                docusign_raw_page.close()
            except Exception:
                pass
            page.bring_to_front()

@when("User login to the email and fetch the latest OTP")
def user_login_to_the_email_and_fetch_the_latest_otp(page: Page, test_context):
    """Login to Outlook and fetch the latest OTP using the stored D number."""
    with allure.step("User login to the email and fetch the latest OTP"):
        docu_sign_page = DocuSignPage(page)
        docu_sign_page.complete_signing_with_outlook_otp(max_wait_time_in_seconds=60, session_timeout_check=False)

@then("Verify that the carbon copy of the signed document has been received in the email")
def user_verifies_carbon_copy_received_in_email(page: Page, test_context):
    with allure.step("Verify that the carbon copy of the signed document has been received in the email"):
        d_number = test_context.get("d_number")
        if not d_number:
            raise ValueError("D-number not found in test_context.")

        outlook_email_page, outlook_page = _open_outlook(page)
        try:
            outlook_page._click_inbox_search_and_select(
                d_number,
                retries=3,
                subject="AssetMark for eSig",
                body="All signers have completed the request and AssetMark has approved. Please process these documents.",
            )

            with outlook_email_page.expect_popup() as popup_info:
                outlook_page.view_completed_document_link.click()

            docusign_raw_page = popup_info.value
            docusign_page = DocuSignPage(docusign_raw_page)
            docusign_page.verify_docusign_page_loaded()

            screenshot = page.screenshot()
            allure.attach(screenshot, name="DocuSign Page Loaded", attachment_type=allure.attachment_type.PNG)
        finally:
            outlook_email_page.close()
            try:
                docusign_raw_page.close()
            except Exception:
                pass
            page.bring_to_front()

@when("User click on Review Document link in authorized signer email")
def user_click_on_review_document_link_in_authorized_signer_email(page: Page, test_context):
    with allure.step("Click on Review Document link in authorized signer email"):
        outlook_page_obj: Optional[OutlookPage] = test_context.get("outlook_page")
        if not outlook_page_obj:
            raise ValueError("Outlook page not found in test_context. Ensure the email search step runs before this step.")

        try:
            docusign_page = outlook_page_obj.click_review_document_link()
            ds_page = DocuSignPage(docusign_page)

            docusign_page.wait_for_load_state("domcontentloaded", timeout=30_000)
            try:
                ds_page.verify_send_now_button.wait_for(state="visible", timeout=20_000)
                logger.info("DocuSign 'Send Now' page is ready")
            except Exception:
                logger.warning("'Send Now' button not visible after 20s ΓÇö page may have already advanced")

            screenshot = docusign_page.screenshot()
            allure.attach(screenshot, name="DocuSign - Page After Review Document Click", attachment_type=allure.attachment_type.PNG)

            docusign_page.bring_to_front()
            logger.info("Γ£ô Successfully clicked Review Document link")
            test_context["docusign_page"] = docusign_page
        except Exception as ex:
            logger.error(f"Error clicking Review Document link: {ex}")
            allure.attach(str(ex), name="Error clicking Review Document", attachment_type=allure.attachment_type.TEXT)
            raise


@when("User accepts DocuSign Electronic Record consent and clicks continue")
def user_accepts_docusign_ersd_consent(page: Page, test_context):
    """Accept the 'Review and continue' ERSD consent modal on DocuSign and click Continue."""
    with allure.step("Accept DocuSign Electronic Record consent and click Continue"):
        docusign_page = test_context.get("docusign_page")
        if not docusign_page:
            raise ValueError("DocuSign page not found in test_context. Ensure the Review Document step runs first.")

        try:
            docusign_page.bring_to_front()
            ds_page = DocuSignPage(docusign_page)

            ds_page.ersd_modal.wait_for(state="visible", timeout=15_000)
            logger.info("DocuSign ERSD consent modal is visible")

            screenshot = docusign_page.screenshot()
            allure.attach(screenshot, name="DocuSign - Consent Modal", attachment_type=allure.attachment_type.PNG)

            ds_page.ersd_consent_checkbox_label.wait_for(state="visible", timeout=5_000)
            ds_page.ersd_consent_checkbox_label.click()
            logger.info("Clicked ERSD consent checkbox label")

            ds_page.ersd_continue_button.wait_for(state="visible", timeout=5_000)
            ds_page.ersd_continue_button.click()
            logger.info("Clicked Continue on ERSD consent modal")

            ds_page.ersd_modal.wait_for(state="hidden", timeout=15_000)
            docusign_page.wait_for_load_state("domcontentloaded", timeout=15_000)

            screenshot = docusign_page.screenshot()
            allure.attach(screenshot, name="DocuSign - After Consent Continue", attachment_type=allure.attachment_type.PNG)
            logger.info("Γ£ô ERSD consent accepted, proceeding to verification page")

        except Exception as ex:
            logger.error(f"Error accepting DocuSign ERSD consent: {ex}")
            try:
                screenshot = docusign_page.screenshot()
                allure.attach(screenshot, name="Error - DocuSign Consent", attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
            allure.attach(str(ex), name="Error accepting consent", attachment_type=allure.attachment_type.TEXT)
            raise


@when("User click on Review Document and submit the otp")
def user_click_on_review_document_and_submit_otp(page: Page, test_context):
    """Click REVIEW DOCUMENT in the open Outlook email, then on DocuSign click Send Now and submit the OTP fetched from Outlook."""
    with allure.step("Click Review Document and submit OTP"):
        outlook_email_page = test_context.get("outlook_email_page")
        if not outlook_email_page:
            raise ValueError("Outlook email page not found in test_context. Ensure the email search step runs before this step.")

        outlook_page_obj: Optional[OutlookPage] = test_context.get("outlook_page")
        if not outlook_page_obj:
            outlook_page_obj = OutlookPage.from_config(outlook_email_page)

        with outlook_email_page.expect_popup() as popup_info:
            outlook_page_obj.click_review_document_link()
            logger.info("Clicked REVIEW DOCUMENT link")

        docusign_raw_page = popup_info.value
        ds_page = DocuSignPage(docusign_raw_page)
        docusign_raw_page.wait_for_load_state("domcontentloaded", timeout=30_000)

        screenshot = outlook_email_page.screenshot()
        allure.attach(screenshot, name="After clicking Review Document", attachment_type=allure.attachment_type.PNG)

        ds_page.verify_send_now_button.wait_for(state="visible", timeout=20_000)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - Send Now Page", attachment_type=allure.attachment_type.PNG)

        ds_page.verify_send_now_button.click()
        logger.info("Clicked Send Now button on DocuSign verify page")

        docusign_raw_page.wait_for_load_state("domcontentloaded", timeout=15_000)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - After Send Now", attachment_type=allure.attachment_type.PNG)

        otp = outlook_page_obj.get_otp_with_retry(timeout=60)
        if not otp:
            raise RuntimeError("Could not fetch OTP from Outlook for DocuSign verification.")
        logger.info(f"Fetched OTP from Outlook: {otp}")

        ds_page.submit_otp(otp)
        logger.info("OTP submitted to DocuSign successfully")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - OTP Submitted", attachment_type=allure.attachment_type.PNG)

        test_context["docusign_page"] = docusign_raw_page
        try:
            page.bring_to_front()
        except Exception:
            pass


def _fetch_and_store_otp(ewm_page: Page, test_context: dict) -> str:
    """Open Outlook (reusing existing session if available), fetch the latest DocuSign
    verification code OTP, store it in test_context['docusign_otp'], and return it.

    Args:
        ewm_page: The main EWM Playwright page (used to open a new tab if needed).
        test_context: pytest-bdd shared context dict.

    Returns:
        6-digit OTP string.

    Raises:
        RuntimeError: If OTP cannot be fetched within the timeout.
    """
    outlook_email_page = test_context.get("outlook_email_page")
    outlook_page_obj: Optional[OutlookPage] = test_context.get("outlook_page")

    if not outlook_email_page or not outlook_page_obj:
        logger.info("No existing Outlook session in test_context ΓÇö opening a new one.")
        outlook_email_page, outlook_page_obj = _open_outlook(ewm_page)
        test_context["outlook_email_page"] = outlook_email_page
        test_context["outlook_page"] = outlook_page_obj

    otp = outlook_page_obj.get_otp_with_retry(timeout=90)
    if not otp:
        raise RuntimeError("Could not fetch DocuSign OTP from Outlook within timeout.")

    test_context["docusign_otp"] = otp
    logger.info(f"OTP fetched and stored in test_context: {otp}")
    return otp


@when("User clicks Send Now button on DocuSign verification page")
def user_clicks_send_now_on_docusign(page: Page, test_context):
    """Click the 'Send Now' button on DocuSign's 'confirm it's really you' page
    and verify the OTP entry page loads."""
    with allure.step("Click Send Now on DocuSign verification page"):
        docusign_raw_page = test_context.get("docusign_page")
        if not docusign_raw_page:
            raise ValueError("DocuSign page not found in test_context. Ensure 'User click on Review Document link' step runs first.")

        docusign_raw_page.bring_to_front()
        ds_page = DocuSignPage(docusign_raw_page)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - Send Now Page", attachment_type=allure.attachment_type.PNG)

        ds_page.verify_send_now_button.wait_for(state="visible", timeout=20_000)
        ds_page.verify_send_now_button.click()
        logger.info("Clicked 'Send Now' button on DocuSign verification page")

        ds_page.verify_otp_title.wait_for(state="visible", timeout=15_000)
        logger.info("OTP entry page ('Enter your code') is visible")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - OTP Entry Page", attachment_type=allure.attachment_type.PNG)


@when("User fetches OTP from Outlook and submits on DocuSign")
def user_fetches_otp_from_outlook_and_submits(page: Page, test_context):
    """Fetch the latest DocuSign verification code from Outlook inbox,
    enter it in the DocuSign OTP field, and click Confirm Code."""
    with allure.step("Fetch OTP from Outlook and submit on DocuSign"):
        docusign_raw_page = test_context.get("docusign_page")
        if not docusign_raw_page:
            raise ValueError("DocuSign page not found in test_context. Ensure Send Now step runs before this.")

        # Fetch OTP from Outlook and store in test_context
        otp = _fetch_and_store_otp(page, test_context)
        logger.info(f"OTP to submit: {otp}")

        allure.attach(otp, name="DocuSign OTP Fetched", attachment_type=allure.attachment_type.TEXT)

        docusign_raw_page.bring_to_front()
        ds_page = DocuSignPage(docusign_raw_page)

        ds_page.verify_otp_input.wait_for(state="visible", timeout=15_000)
        ds_page.verify_otp_input.fill(otp)
        logger.info("OTP entered in DocuSign verification code field")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - OTP Entered", attachment_type=allure.attachment_type.PNG)

        ds_page.verify_confirm_button.wait_for(state="visible", timeout=10_000)
        ds_page.verify_confirm_button.click()
        logger.info("Clicked 'Confirm Code' button on DocuSign")

        docusign_raw_page.wait_for_load_state("domcontentloaded", timeout=15_000)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - After Confirm Code", attachment_type=allure.attachment_type.PNG)

        try:
            page.bring_to_front()
        except Exception:
            pass


@when("User scrolls to sign button clicks on it adopts signature and clicks Finish")
def user_scrolls_signs_adopts_and_finishes(page: Page, test_context):
    """On the DocuSign signing page (popup): scroll to the sign tab,
    click it, adopt the signature in the modal, then click Finish."""
    with allure.step("Scroll to sign button, adopt signature and click Finish"):
        docusign_raw_page = test_context.get("docusign_page")
        if not docusign_raw_page:
            raise ValueError("DocuSign page not found in test_context. Ensure the OTP step runs first.")

        ds_page = DocuSignPage(docusign_raw_page)
        docusign_raw_page.bring_to_front()
        docusign_raw_page.wait_for_load_state("domcontentloaded", timeout=20_000)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - Signing Page", attachment_type=allure.attachment_type.PNG)

        # Scroll to the sign button (located on the last page of the document)
        ds_page.signature_tab_button.first.wait_for(state="visible", timeout=15_000)
        ds_page.signature_tab_button.first.scroll_into_view_if_needed()
        logger.info("Scrolled to sign button")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - Sign Button Visible", attachment_type=allure.attachment_type.PNG)

        ds_page.signature_tab_button.first.click()
        logger.info("Clicked sign button ΓÇö waiting for Adopt Your Signature modal")

        ds_page.adopt_signature_modal.wait_for(state="visible", timeout=15_000)
        logger.info("Adopt Your Signature modal is visible")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - Adopt Signature Modal", attachment_type=allure.attachment_type.PNG)

        ds_page.adopt_and_sign_button.wait_for(state="visible", timeout=10_000)
        ds_page.adopt_and_sign_button.click()
        logger.info("Clicked 'Adopt and Sign' button")

        ds_page.adopt_signature_modal.wait_for(state="hidden", timeout=15_000)
        logger.info("Adopt modal closed ΓÇö signature applied")

        try:
            ds_page.signature_applied_tab.wait_for(state="visible", timeout=15_000)
            logger.info("Signature confirmed ΓÇö button shows 'Signature Applied'")
        except Exception:
            # Fallback: check aria-invalid is cleared on the first sign tab
            aria_invalid = ds_page.signature_tab_button.first.get_attribute("aria-invalid")
            if aria_invalid == "true":
                logger.warning("Signature may not have been applied ΓÇö aria-invalid still true")
            else:
                logger.info("Signature confirmed ΓÇö aria-invalid cleared")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - Signature Applied", attachment_type=allure.attachment_type.PNG)

        try:
            ds_page.finish_button.wait_for(state="visible", timeout=10_000)
            ds_page.finish_button.click()
        except Exception:
            ds_page.action_bar_finish_button.wait_for(state="visible", timeout=10_000)
            ds_page.action_bar_finish_button.click()
        logger.info("Clicked Finish button on DocuSign")

        docusign_raw_page.wait_for_load_state("domcontentloaded", timeout=15_000)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - After Finish", attachment_type=allure.attachment_type.PNG)
        logger.info("Γ£ô DocuSign signing complete")


@then('DocuSign shows "You\'re Done Signing" and user clicks Continue')
def user_verifies_done_signing_and_clicks_continue(page: Page, test_context):
    """Verify the 'You're Done Signing' confirmation modal appears and click Continue."""
    with allure.step("Verify 'You're Done Signing' modal and click Continue"):
        docusign_raw_page = test_context.get("docusign_page")
        if not docusign_raw_page:
            raise ValueError("DocuSign page not found in test_context. Ensure the sign step runs first.")

        docusign_raw_page.bring_to_front()
        ds_page = DocuSignPage(docusign_raw_page)

        # Wait for the modal
        ds_page.done_signing_modal.wait_for(state="visible", timeout=15_000)
        logger.info("'You're Done Signing' modal is visible")

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - You're Done Signing", attachment_type=allure.attachment_type.PNG)

        # Assert title text
        title_text = ds_page.done_signing_title.inner_text()
        assert "done signing" in title_text.lower(), (
            f"Expected 'You're Done Signing' modal title, got: '{title_text}'"
        )
        allure.attach(title_text, name="Done Signing Modal Title", attachment_type=allure.attachment_type.TEXT)
        logger.info(f"Modal title verified: '{title_text}'")

        # Click Continue
        ds_page.done_signing_continue_btn.wait_for(state="visible", timeout=10_000)
        ds_page.done_signing_continue_btn.click()
        logger.info("Clicked Continue on 'You're Done Signing' modal")

        docusign_raw_page.wait_for_load_state("domcontentloaded", timeout=15_000)

        screenshot = docusign_raw_page.screenshot()
        allure.attach(screenshot, name="DocuSign - After Done Signing Continue", attachment_type=allure.attachment_type.PNG)
        logger.info("Γ£ô Done Signing flow complete")
