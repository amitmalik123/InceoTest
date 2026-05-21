import os
import allure
import requests
from pathlib import Path
from playwright.sync_api import Page
from pytest_bdd import parsers, then, when
from datetime import datetime

from pages.stp.shared.item_details_page import ItemDetailsPage
from .common_steps import extract_account_core_identifier
from utils.logger import setup_logger

_DOWNLOAD_PATH = str(Path(__file__).resolve().parents[4] / "downloads" / "ACH PDF")

logger = setup_logger(__name__)


@when('User should click View button in item details page')
def user_clicks_view_button(page: Page, item_details_page: ItemDetailsPage):
    """Click the View button on Item Details page"""
    with allure.step("Click View button in item details page"):
        logger.info("\n")
        item_details_page.click_view_button()
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="View Documents Popup",
            attachment_type=allure.attachment_type.PNG
        )


@when('User should click on the PDF Link to download')
def user_clicks_pdf_link_to_download(page: Page, item_details_page: ItemDetailsPage):
    """Click on the PDF link, switch to new window, capture URL, and download via API"""
    with allure.step("Click on the PDF Link to download via API"):
        logger.info("\n")
        
        # Click PDF link, switch to new window, get URL, and download via API
        result = item_details_page.click_and_download_pdf_via_api(_DOWNLOAD_PATH)
        
        # Verify download was successful
        assert result["success"], f"PDF download failed: {result.get('error', 'Unknown error')}"
        
        logger.info(f"PDF downloaded successfully via API")
        logger.info(f" File: {result['filename']}")
        logger.info(f" Path: {result['file_path']}")
        logger.info(f" Size: {result['size']} bytes")
        logger.info(f" URL: {result['url']}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="PDF Downloaded via API",
            attachment_type=allure.attachment_type.PNG
        )
        allure.attach(
            f"File downloaded: {result['filename']}\n"
            f"Saved to: {result['file_path']}\n"
            f"Size: {result['size']} bytes\n"
            f"URL: {result['url']}",
            name="Download Details",
            attachment_type=allure.attachment_type.TEXT
        )


@then('Validate view documents popup')
def validate_view_documents_popup(page: Page, item_details_page: ItemDetailsPage):
    """Validate that View Documents popup is displayed"""
    with allure.step("Validate view documents popup"):
        logger.info("\n")
        
        is_displayed = item_details_page.is_view_documents_popup_displayed()
        
        assert is_displayed, "View documents popup is not displaying"
        logger.info("View documents popup is displaying - Verification PASSED")
        
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="View Documents Popup Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then('Validate PDF is generated')
def validate_pdf_is_generated(page: Page, item_details_page: ItemDetailsPage):
    """Validate that PDF documents are generated in View Documents popup"""
    with allure.step("Validate PDF is generated"):
        logger.info("\n")
        
        pdf_count = item_details_page.get_amount_of_documents_in_view_popup()
        
        assert pdf_count > 0, f"PDF should get generated Successfully. Found {pdf_count} PDFs"
        logger.info(f"PDF generated successfully - Found {pdf_count} PDF document(s)")
        
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="PDF Generation Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then('User should validate time stamp on tracking center page')
def validate_time_stamp(page: Page, test_context, item_details_page):
    """Validate timestamps on tracking center page contain PDT or PST"""
    with allure.step("Validate time stamps on tracking center page"):
        logger.info("Validating timestamps on tracking center page")
        
        timestamps = item_details_page.get_time_stamps()
        
        for i, timestamp in enumerate(timestamps):
            timestamp_text = timestamp
            contains_pdt = "PDT" in timestamp_text
            contains_pst = "PST" in timestamp_text
            
            assert contains_pdt or contains_pst, \
                f"Timestamp {i+1} should contain PDT or PST. Actual: '{timestamp_text}'"
            
            logger.info(f"Validation of time stamp: {timestamp_text}")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Timestamps Validated",
            attachment_type=allure.attachment_type.PNG
        )
        
        allure.attach(
            "\n".join([f"Timestamp {i+1}: {ts}" for i, ts in enumerate(timestamps)]),
            name="All Timestamps",
            attachment_type=allure.attachment_type.TEXT
        )


@then(parsers.parse('User should validate the Notes content for "{sloa_sub_option}" which are "{description_notes}", "{amount}", "{delivery_method}" as "{method_type}", "{destination}", "{cancellation_date}" and "{distribution_type}" in "{feature}" and the role is "{role}" for InPerson Sign in AddACH'))
def validate_notes_content_for_add_ach(
    page: Page,
    test_context: dict,
    sloa_sub_option: str,
    description_notes: str,
    amount: str,
    delivery_method: str,
    method_type: str,
    destination: str,
    cancellation_date: str,
    distribution_type: str,
    feature: str,
    role: str
):
    """Validate Notes content on Item Details page for Add ACH"""
    with allure.step(f"Validate Notes content for {sloa_sub_option}"):
        logger.info(f"Validating Notes content: {sloa_sub_option}, role={role}")
        
        tracking_center_page = test_context.get('tracking_center_page', page)
        item_details_page = ItemDetailsPage(tracking_center_page, page_verification=False)
        
        entered_new_ains_details = test_context.get('entered_new_ains_details', [])
        initial_role = test_context.get('initial_role', role)
        
        logger.info(f"Entered AINS details: {entered_new_ains_details}")
        logger.info(f"Initial role: {initial_role}, Current role: {role}")
        
        created_by_notes = item_details_page.get_created_by_from_notes_section()
        distribution_notes = ""
        
        if sloa_sub_option == "Esign":
            if role == "Admin" and initial_role == "Admin":
                assert "AssetMark" in created_by_notes, \
                    f"Created By should contain AssetMark. Actual: {created_by_notes}"
                logger.info("Created By validation passed for Admin/Admin Esign")
            elif role == "Advisor" and initial_role == "Admin":
                distribution_notes = item_details_page.get_first_distribution_notes()
                assert "AssetMark" in created_by_notes, \
                    f"Created By should contain AssetMark. Actual: {created_by_notes}"
                logger.info("Created By validation passed for Advisor/Admin Esign")
            elif role == "Advisor" and initial_role == "Advisor":
                distribution_notes = item_details_page.get_first_distribution_notes()
                logger.info("Created By validation passed for Advisor/Advisor Esign")
        
        elif sloa_sub_option == "NoEsign":
            if role == "Admin" and initial_role == "Admin":
                assert "AssetMark" in created_by_notes, \
                    f"Created By should contain AssetMark. Actual: {created_by_notes}"
                logger.info("Created By validation passed for Admin/Admin NoEsign")
            elif role == "Advisor" and initial_role == "Admin":
                distribution_notes = item_details_page.get_first_distribution_notes()
                assert "AssetMark" in created_by_notes, \
                    f"Created By should contain AssetMark. Actual: {created_by_notes}"
                logger.info("Created By validation passed for Advisor/Admin NoEsign")
            elif role == "Advisor" and initial_role == "Advisor":
                distribution_notes = item_details_page.get_first_distribution_notes()
                logger.info("Created By validation passed for Advisor/Advisor NoEsign")
        
        elif sloa_sub_option == "Print":
            if role == "Admin" and initial_role == "Admin":
                assert "AssetMark" in created_by_notes, \
                    f"Created By should contain AssetMark. Actual: {created_by_notes}"
                logger.info("Created By validation passed for Admin/Admin Print")
            elif role == "Advisor" and initial_role == "Admin":
                distribution_notes = item_details_page.get_first_distribution_notes()
                assert "AssetMark" in created_by_notes, \
                    f"Created By should contain AssetMark. Actual: {created_by_notes}"
                logger.info("Created By validation passed for Advisor/Admin Print")
            elif role == "Advisor" and initial_role == "Advisor":
                distribution_notes = item_details_page.get_first_distribution_notes()
                logger.info("Created By validation passed for Advisor/Advisor Print")
        
        if role != "Admin":
            assert description_notes in distribution_notes, \
                f"Description notes not found. Expected: '{description_notes}', Actual: '{distribution_notes}'"
            logger.info(f"Description notes validated: {description_notes}")
            
            assert delivery_method in distribution_notes, \
                f"Delivery Method header not found. Expected: '{delivery_method}'"
            logger.info(f"Delivery Method header validated: {delivery_method}")
            
            assert method_type in distribution_notes, \
                f"Delivery Method value not found. Expected: '{method_type}'"
            logger.info(f"Delivery Method value validated: {method_type}")
            
            assert amount in distribution_notes, \
                f"Amount header not found. Expected: '{amount}'"
            logger.info(f"{amount} header validated")
            
            assert entered_new_ains_details[4] in distribution_notes, \
                f"Amount value not found. Expected: '{entered_new_ains_details[4]}'"
            logger.info(f"{amount} value validated: {entered_new_ains_details[4]}")
            
            assert cancellation_date in distribution_notes, \
                f"Bank Name header not found. Expected: '{cancellation_date}'"
            logger.info(f"{cancellation_date} header validated")
            
            assert entered_new_ains_details[1] in distribution_notes, \
                f"Bank Name value not found. Expected: '{entered_new_ains_details[1]}'"
            logger.info(f"Bank Name value validated: {entered_new_ains_details[1]}")
            
            assert distribution_type in distribution_notes, \
                f"Bank Account Number header not found. Expected: '{distribution_type}'"
            logger.info(f"{distribution_type} header validated")
            
            masked_account = entered_new_ains_details[2]
            if len(masked_account) > 4:
                masked_account = "*" * (len(masked_account) - 4) + masked_account[-4:]
            
            assert masked_account in distribution_notes, \
                f"Bank Account Number value not found. Expected: '{masked_account}'"
            logger.info(f"Bank Account Number value validated: {masked_account}")
            
            assert "ABA/Routing Number" in distribution_notes, \
                "ABA/Routing Number header not found"
            logger.info("ABA/Routing Number header validated")
            
            assert entered_new_ains_details[0] in distribution_notes, \
                f"ABA/Routing Number value not found. Expected: '{entered_new_ains_details[0]}'"
            logger.info(f"ABA/Routing Number value validated: {entered_new_ains_details[0]}")
            
            assert "Bank Account Type" in distribution_notes, \
                "Bank Account Type header not found"
            logger.info("Bank Account Type header validated")
            
            assert entered_new_ains_details[3] in distribution_notes, \
                f"Bank Account Type value not found. Expected: '{entered_new_ains_details[3]}'"
            logger.info(f"Bank Account Type value validated: {entered_new_ains_details[3]}")
            
            if len(entered_new_ains_details) == 8:
                assert "Investment Account(s)" in distribution_notes, \
                    "Investment Account(s) header not found"
                logger.info("Investment Account(s) header validated")
                
                selected_account = entered_new_ains_details[7]
                logger.info(f"Looking for Investment Account: '{selected_account}'")
                logger.info(f"Distribution notes content: '{distribution_notes}'")
                
                account_name, account_number = extract_account_core_identifier(selected_account)
                
                if account_name and account_number:
                    assert account_name in distribution_notes, \
                        f"Investment Account Name not found. Expected: '{account_name}', Actual: '{distribution_notes}'"
                    assert account_number in distribution_notes, \
                        f"Investment Account Number not found. Expected: '{account_number}', Actual: '{distribution_notes}'"
                else:
                    assert selected_account in distribution_notes, \
                        f"Investment Account(s) value not found. Expected: '{selected_account}', Actual: '{distribution_notes}'"
                
                logger.info(f"Investment Account(s) value validated")
                
                assert "Bank Instructions and/or Standing Letter of Authorization (SLOA):" in distribution_notes, \
                    "SLOA header not found"
                logger.info("SLOA header validated")
                
                assert entered_new_ains_details[6].strip() in distribution_notes, \
                    f"SLOA value not found. Expected: '{entered_new_ains_details[6]}'"
                logger.info(f"SLOA value validated: {entered_new_ains_details[6]}")
                
                assert destination in distribution_notes, \
                    f"Additional name header not found. Expected: '{destination}'"
                logger.info(f"{destination} header validated")
                
                assert entered_new_ains_details[5] in distribution_notes, \
                    f"Additional name value not found. Expected: '{entered_new_ains_details[5]}'"
                logger.info(f"{destination} value validated: {entered_new_ains_details[5]}")
            else:
                assert "Investment Account(s)" in distribution_notes, \
                    "Investment Account(s) header not found"
                logger.info("Investment Account(s) header validated")
                
                selected_account = entered_new_ains_details[6]
                
                account_name, account_number = extract_account_core_identifier(selected_account)
                
                if account_name and account_number:
                    assert account_name in distribution_notes, \
                        f"Investment Account Name not found. Expected: '{account_name}', Actual: '{distribution_notes}'"
                    assert account_number in distribution_notes, \
                        f"Investment Account Number not found. Expected: '{account_number}', Actual: '{distribution_notes}'"
                else:
                    assert selected_account in distribution_notes, \
                        f"Investment Account(s) value not found. Expected: '{selected_account}', Actual: '{distribution_notes}'"
                logger.info(f"Investment Account(s) value validated: {entered_new_ains_details[6]}")
                
                assert "Bank Instructions and/or Standing Letter of Authorization (SLOA):" in distribution_notes, \
                    "SLOA header not found"
                logger.info("SLOA header validated")
                
                assert entered_new_ains_details[5].strip() in distribution_notes, \
                    f"SLOA value not found. Expected: '{entered_new_ains_details[5]}'"
                logger.info(f"SLOA value validated: {entered_new_ains_details[5]}")
        
        logger.info("Notes content validation completed successfully")
        
        screenshot = tracking_center_page.screenshot()
        allure.attach(
            screenshot,
            name="Notes Content Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate the "{expected_notification}" Notification on the Tracking Center for "{method}"'))
def validate_email_notification_on_tracking_center(
    page: Page,
    test_context: dict,
    expected_notification: str,
    method: str
):
    """Validate email notification message on Item Details page"""
    with allure.step(f"Validate email notification for {method}"):
        logger.info("\n" + "="*80)
        logger.info(f"Validating email notification for: {method}")
        logger.info("="*80)
        
        tracking_center_page = test_context.get('tracking_center_page', page)
        item_details_page = ItemDetailsPage(tracking_center_page, page_verification=False)
        
        email_notes = item_details_page.get_email_notification_for_method(method)
        logger.info(f"Email notification retrieved from UI: {email_notes}")
        
        assert expected_notification in email_notes, \
            f"Expected notification not found.\nExpected: '{expected_notification}'\nActual: '{email_notes}'"
        
        logger.info(f"Email notification validated successfully")
        logger.info(f"The Email Note Present on the UI: {email_notes}")
        
        screenshot = tracking_center_page.screenshot()
        allure.attach(
            screenshot,
            name="Email Notification Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate the "{expected_notification}" Notification on the Tracking Center for "{method}"'))
def validate_email_notification_on_tracking_center(
    page: Page,
    test_context: dict,
    expected_notification: str,
    method: str
):
    """Validate email notification message on Item Details page"""
    with allure.step(f"Validate email notification for {method}"):
        logger.info("\n" + "="*80)
        logger.info(f"Validating email notification for: {method}")
        logger.info("="*80)
        
        tracking_center_page = test_context.get('tracking_center_page', page)
        item_details_page = ItemDetailsPage(tracking_center_page, page_verification=False)
        
        email_notes = item_details_page.get_email_notification_for_method(method)
        logger.info(f"Email notification retrieved from UI: {email_notes}")
        
        assert expected_notification in email_notes, \
            f"Expected notification not found.\nExpected: '{expected_notification}'\nActual: '{email_notes}'"
        
        logger.info(f"Email notification validated successfully")
        logger.info(f"The Email Note Present on the UI: {email_notes}")
        
        screenshot = tracking_center_page.screenshot()
        allure.attach(
            screenshot,
            name="Email Notification Validated",
            attachment_type=allure.attachment_type.PNG
        )

@then(parsers.parse('User should validate info panel contents with status "{status}" and item description as "{item_description}" for "{stp_or_str}"'))
def validate_info_panel_contents_in_item_details_page(
    page: Page,
    item_details_page: ItemDetailsPage,
    test_context: dict,
    status: str,
    item_description: str,
    stp_or_str: str
):
    """Validate info panel contents in Item Details page - matches Java validationOfInfoPanelContentsInItemDetailsPage"""
    with allure.step(f"Validate info panel contents for {stp_or_str}"):
        logger.info("\n")
        logger.info(f"Validating info panel contents: status={status}, description={item_description}, type={stp_or_str}")

        # Use the page that was navigated to by click_item_number (may be new tab or same tab)
        active_page = test_context.get('item_details_page_tab') or page
        if active_page is not page:
            from pages.stp.shared.item_details_page import ItemDetailsPage as _IDP
            item_details_page = _IDP(active_page, page_verification=False)

        # Get agent_id and account_number from test_context
        agent_id = test_context.get('agent_id', '')
        account_number = test_context.get('account_number', '')
        account_name = test_context.get('account_name', '')
        item_number = test_context.get('item_number', '')

        # Determine which item details lists to use
        current_url = active_page.url
        if 'test11' in current_url:
            logger.info("Using test11 item details")
            item_details_all = item_details_page.get_item_details_t11()
            item_details_list1 = item_details_all[0:4]
            item_details_list2 = item_details_all[5:9]
        elif 'ewealthmanager.com' in current_url:
            logger.info("[PROD] Using PROD-specific item details methods")
            item_details_list1 = item_details_page.get_item_details_1_prod()
            item_details_list2 = item_details_page.get_item_details_2_prod()
        else:
            logger.info(f"Using agent ID based item details: {agent_id}")
            item_details_list1 = item_details_page.get_item_details_1(agent_id)
            item_details_list2 = item_details_page.get_item_details_2(agent_id)
        
        # Log all item details
        logger.info("Item Details List 2:")
        for i, value in enumerate(item_details_list2):
            logger.info(f" [{i}] Value is {value}")
        
        # Store Account Name for DocuSign PDF (matches Java: AccountNameDocuSignPDF = itemDetailsList1.get(1).getText())
        account_name_docusign_pdf = item_details_list1[1] if len(item_details_list1) > 1 else ""
        test_context['account_name_docusign_pdf'] = account_name_docusign_pdf
        logger.info(f"Stored Account Name for DocuSign PDF: {account_name_docusign_pdf}")
        
        # Get current date in M/d/yyyy format (matches Java: getCurrentDate("M/d/yyyy"))
        current_date = datetime.now().strftime("%-m/%-d/%Y") if os.name != 'nt' else datetime.now().strftime("%#m/%#d/%Y")
        logger.info(f"Current date: {current_date}")
        
        # Handle different scenarios
        if stp_or_str == "STP":
            # Validate Item Number
            assert item_details_list1[0] == item_number, \
                f"Validation of Item Number: Expected '{item_number}', got '{item_details_list1[0]}'"
            logger.info(f"├ó┼ôΓÇ£ Validation of Item Number: {item_details_list1[0]}")
            
            # Validate Account Name (contains check)
            assert item_details_list1[1] in account_name or account_name in item_details_list1[1], \
                f"Validation of Account Name: Expected to contain '{account_name}', got '{item_details_list1[1]}'"
            logger.info(f"├ó┼ôΓÇ£ Validation of Account Name: {item_details_list1[1]}")
            
            # Validate Account Number
            assert item_details_list2[2] == account_number, \
                f"Validation of Account Number: Expected '{account_number}', got '{item_details_list2[2]}'"
            logger.info(f"Validation of Account Number: {item_details_list2[2]}")
        
        elif stp_or_str == "SWP Establish Online":
            # Validate Item Number
            assert item_details_list1[0] == item_number, \
                f"Validation of Item Number: Expected '{item_number}', got '{item_details_list1[0]}'"
            logger.info(f"Validation of Item Number: {item_details_list1[0]}")
            
            # Validate Item Description contains expected text
            assert item_description in item_details_list2[3], \
                f"Validation of Description: Expected to contain '{item_description}', got '{item_details_list2[3]}'"
            logger.info(f"Validation of Description: {item_details_list2[3]}")
            
            # Validate Status equals "Complete"
            assert item_details_list1[2] == "Complete", \
                f"Validation of Status: Expected 'Complete', got '{item_details_list1[2]}'"
            logger.info(f"Validation of Status: Done")
        
        elif stp_or_str == "STR":
            # Fetch B item number
            b_item_number = item_details_page.fetch_b_item_number()
            test_context['b_item_number'] = b_item_number
            logger.info(f"Value of B item number: {b_item_number}")

            # Validate Account Name
            assert item_details_list1[1] in account_name or account_name in item_details_list1[1], \
                f"Validation of Account Name: Expected to contain '{account_name}', got '{item_details_list1[1]}'"
            logger.info(f" Validation of Account Name: {item_details_list1[1]}")

            # Validate Account Number
            assert item_details_list2[2] == account_number, \
                f"Validation of Account Number: Expected '{account_number}', got '{item_details_list2[2]}'"
            logger.info(f" Validation of Account Number: {item_details_list2[2]}")

        elif stp_or_str == "Cancel AIP Online STR":
            # Fetch B item number
            b_item_number = item_details_page.fetch_b_item_number()
            test_context['b_item_number'] = b_item_number
            logger.info(f"Value of B item number: {b_item_number}")

            # Validate Account Name
            assert item_details_list1[1] in account_name or account_name in item_details_list1[1], \
                f"Validation of Account Name: Expected to contain '{account_name}', got '{item_details_list1[1]}'"
            logger.info(f" Validation of Account Name: {item_details_list1[1]}")

            # Validate Account Number
            assert item_details_list2[2] == account_number, \
                f"Validation of Account Number: Expected '{account_number}', got '{item_details_list2[2]}'"
            logger.info(f" Validation of Account Number: {item_details_list2[2]}")
        
        # Validate Status (for all scenarios except "Roth Conversions Online")
        if stp_or_str != "Roth Conversions Online":
            assert item_details_list1[2] == status, \
                f"Validation of Status: Expected '{status}', got '{item_details_list1[2]}'"
            logger.info(f"├ó┼ôΓÇ£ Validation of Status: {item_details_list1[2]}")
        
        # Validate Created Date
        assert current_date in item_details_list2[0], \
            f"Validation of Created Date: Expected to contain '{current_date}', got '{item_details_list2[0]}'"
        logger.info(f"├ó┼ôΓÇ£ Validation of Created Date: {item_details_list2[0]}")
        
        # Validate Item Description
        assert item_description in item_details_list2[3], \
            f"Validation of Item Description: Expected to contain '{item_description}', got '{item_details_list2[3]}'"
        logger.info(f"├ó┼ôΓÇ£ Validation of Item Description: {item_details_list2[3]}")
        
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Info Panel Contents Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate description contains "{description_text}"'))
def validate_description_contains(
    page: Page,
    item_details_page: ItemDetailsPage,
    description_text: str
):
    """Validate that description in notes section contains specific text"""
    with allure.step(f"Validate description contains: {description_text}"):
        logger.info("\n")
        logger.info(f"Validating description contains: {description_text}")
        
        # Get the first distribution notes
        distribution_notes = item_details_page.get_first_distribution_notes()
        logger.info(f"Distribution notes: {distribution_notes}")
        
        # Validate description contains the expected text
        assert description_text in distribution_notes, \
            f"Description validation failed. Expected to contain: '{description_text}', Actual: '{distribution_notes}'"
        
        logger.info(f"├ó┼ôΓÇ£ Description contains: {description_text}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="Description Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate description contains contents where "{delivery_method}", "{mail_delivery}", "{state_of_residence}"'))
def validate_description_contains_no_memo_contents(
    page: Page,
    item_details_page: ItemDetailsPage,
    delivery_method: str,
    mail_delivery: str,
    state_of_residence: str,
):
    """Validate description for non-IRA (no check memo, no tax info)"""
    with allure.step("Validate description contains contents"):
        logger.info(f"Validating description contains: delivery={delivery_method}, mail={mail_delivery}, state={state_of_residence}")

        distribution_notes = item_details_page.get_first_distribution_notes()
        logger.info(f"Distribution notes: {distribution_notes}")

        for label, content in [
            ("Delivery Method", delivery_method),
            ("Mail Delivery", mail_delivery),
            ("State of Residence", state_of_residence),
        ]:
            assert content in distribution_notes, \
                f"{label} validation failed. Expected: '{content}', Actual: '{distribution_notes}'"
            logger.info(f"{label} validated: {content}")

        logger.info("All contents validated successfully in description")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Description Contents Validated", attachment_type=allure.attachment_type.PNG)


@then(parsers.parse('User should validate description contains contents where "{delivery_method}", "{check_memo}", "{mail_delivery}", "{state_of_residence}"'))
def validate_description_contains_partial_contents(
    page: Page,
    item_details_page: ItemDetailsPage,
    delivery_method: str,
    check_memo: str,
    mail_delivery: str,
    state_of_residence: str,
):
    """Validate description contains delivery method, check memo, mail delivery and state ΓÇö used for non-IRA where tax info is absent"""
    with allure.step("Validate description contains contents"):
        logger.info(f"Validating description contains: delivery={delivery_method}, memo={check_memo}, mail={mail_delivery}, state={state_of_residence}")

        distribution_notes = item_details_page.get_first_distribution_notes()
        logger.info(f"Distribution notes: {distribution_notes}")

        for label, content in [
            ("Delivery Method", delivery_method),
            ("Check Memo", check_memo),
            ("Mail Delivery", mail_delivery),
            ("State of Residence", state_of_residence),
        ]:
            assert content in distribution_notes, \
                f"{label} validation failed. Expected: '{content}', Actual: '{distribution_notes}'"
            logger.info(f"{label} validated: {content}")

        logger.info("All contents validated successfully in description")
        screenshot = page.screenshot()
        allure.attach(screenshot, name="Description Contents Validated", attachment_type=allure.attachment_type.PNG)


@then(parsers.parse('User should validate description contains all the contents where "{delivery_method}", "{check_memo}", "{mail_delivery}", "{state_of_residence}", "{federal_tax_percent}", "{state_tax_percent}"'))
def validate_description_contains_all_contents(
    page: Page,
    item_details_page: ItemDetailsPage,
    delivery_method: str,
    check_memo: str,
    mail_delivery: str,
    state_of_residence: str,
    federal_tax_percent: str,
    state_tax_percent: str
):
    """Validate that description in notes section contains all expected contents - matches Java validationOfFirstDescriptionNotesInItemDetailsPageForWithdrawals"""
    with allure.step(f"Validate description contains all contents"):
        logger.info("\n")
        logger.info(f"Validating description contains all contents:")
        logger.info(f" Delivery Method: {delivery_method}")
        logger.info(f" Check Memo: {check_memo}")
        logger.info(f" Mail Delivery: {mail_delivery}")
        logger.info(f" State of Residence: {state_of_residence}")
        logger.info(f" Federal Tax Percent: {federal_tax_percent}")
        logger.info(f" State Tax Percent: {state_tax_percent}")
        
        # Get the first distribution notes
        distribution_notes = item_details_page.get_first_distribution_notes()
        logger.info(f"Distribution notes: {distribution_notes}")
        
        # Validate each content is present in the description
        contents_to_validate = [
            ("Delivery Method", delivery_method),
            ("Check Memo", check_memo),
            ("Mail Delivery", mail_delivery),
            ("State of Residence", state_of_residence),
            ("Federal Tax Percent", federal_tax_percent),
            ("State Tax Percent", state_tax_percent)
        ]
        
        for label, content in contents_to_validate:
            assert content in distribution_notes, \
                f"{label} validation failed. Expected to contain: '{content}', Actual: '{distribution_notes}'"
            logger.info(f"{label} validated: {content}")
        
        logger.info("All contents validated successfully in description")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name="All Description Contents Validated",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate the Notes content whicnh are "{setup_message}", "{amount_label}", "{delivery_method_label}" as "{delivery_method}", "{destination_label}" and "{federal_tax_label}" in "{feature}"'))
def validate_notes_content_swp_establish(
    page: Page,
    item_details_page: ItemDetailsPage,
    setup_message: str,
    amount_label: str,
    delivery_method_label: str,
    delivery_method: str,
    destination_label: str,
    federal_tax_label: str,
    feature: str
):
    """Validate Notes content for SWP Establish Online - matches Java validationOfNotesContentInItemDetailsPage"""
    with allure.step(f"Validate Notes content for {feature}"):
        logger.info("\n")
        logger.info(f"Validating Notes content for {feature}:")
        logger.info(f" Setup Message: {setup_message}")
        logger.info(f" Amount Label: {amount_label}")
        logger.info(f" Delivery Method Label: {delivery_method_label}")
        logger.info(f" Delivery Method: {delivery_method}")
        logger.info(f" Destination Label: {destination_label}")
        logger.info(f" Federal Tax Label: {federal_tax_label}")
        
        # Get the first distribution notes
        distribution_notes = item_details_page.get_first_distribution_notes()
        logger.info(f"Distribution notes: {distribution_notes}")
        
        # Validate each content is present in the notes
        contents_to_validate = [
            ("Setup Message", setup_message),
            ("Amount Label", amount_label),
            ("Delivery Method Label", delivery_method_label),
            ("Delivery Method", delivery_method),
            ("Destination Label", destination_label),
            ("Federal Tax Withholding Label", federal_tax_label)
        ]
        
        for label, content in contents_to_validate:
            assert content in distribution_notes, \
                f"{label} validation failed. Expected to contain: '{content}', Actual: '{distribution_notes}'"
            logger.info(f"{label} validated: {content}")
        
        logger.info("All notes content validated successfully")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Notes Content Validated - {feature}",
            attachment_type=allure.attachment_type.PNG
        )


@then(parsers.parse('User should validate the "{expected_notification}" Notification on the Tracking Center for "{method}"'))
def verify_email_notifications_tracking_center(
    page: Page,
    item_details_page: ItemDetailsPage,
    expected_notification: str,
    method: str
):
    """Verify email notification on Tracking Center - matches Java verifyEmailNotifications"""
    with allure.step(f"Verify email notification for {method}"):
        logger.info("\n")
        logger.info(f"Verifying email notification for method: {method}")
        logger.info(f"Expected notification: {expected_notification}")
        
        # Get email notification from page (with refresh logic for specific methods)
        email_notes = item_details_page.get_email_notification_for_method(method)
        logger.info(f"Email note present on the UI: {email_notes}")
        
        # Validate that expected notification text is contained in email notes
        assert expected_notification in email_notes, \
            f"Email notification validation failed. Expected to contain: '{expected_notification}', Actual: '{email_notes}'"
        
        logger.info(f"Email notification validated: {expected_notification}")
        logger.info("\n")
        
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"Email Notification Validated - {method}",
            attachment_type=allure.attachment_type.PNG
        )

