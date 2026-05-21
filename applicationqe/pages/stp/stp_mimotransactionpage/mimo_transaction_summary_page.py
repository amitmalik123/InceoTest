from typing import Dict
from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_mimotransactionpage.locators.mimo_transaction_summary_locators import MIMOTransactionSummaryLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MIMOTransactionSummaryPage(BasePage):
    PAGE_NAME = "MIMO Transaction Summary Page"
    
    def __init__(self, page: Page):
        super().__init__(page)
        loc = MIMOTransactionSummaryLocators
        
        self.transaction_summary_title: Locator = page.locator(loc.TRANSACTION_SUMMARY_TITLE)
        
        self.back_button: Locator = page.locator(loc.BACK_BUTTON)
        self.submit_button: Locator = page.locator(loc.SUBMIT_BUTTON)
        self.submit_to_review_button: Locator = page.locator(loc.SUBMIT_TO_REVIEW_BUTTON)
        self.submit_or_submit_for_review: Locator = page.locator(loc.SUBMIT_OR_SUBMIT_FOR_REVIEW)
        self.esign_and_submit: Locator = page.locator(loc.ESIGN_AND_SUBMIT)
        
        self.account_info: Locator = page.locator(loc.ACCOUNT_INFO)
        
        self.disclosures_title: Locator = page.locator(loc.DISCLOSURES_TITLE)

        self.disclosures_title_contribution: Locator = page.locator(loc.DISCLOSURES_TITLE_CONTRIBUTION)
        self.disclosures_list_contribution: Locator = page.locator(loc.DISCLOSURES_LIST_CONTRIBUTION)

        self.disclaimer_text: Locator = page.locator(loc.DISCLAIMER_TEXT)
        self.disclosures_list: Locator = page.locator(loc.DISCLOSURES_LIST)
        
        self.disclosures_title_cancel: Locator = page.locator(loc.DISCLOSURES_TITLE_CANCEL)
        self.disclaimer_text_cancel: Locator = page.locator(loc.DISCLAIMER_TEXT_CANCEL)
        self.disclosures_list_cancel: Locator = page.locator(loc.DISCLOSURES_LIST_CANCEL)
        
        self.request_details_label: Locator = page.locator(loc.REQUEST_DETAILS_LABEL)
        self.destination_label: Locator = page.locator(loc.DESTINATION_LABEL)
        self.bank_name_header: Locator = page.locator(loc.BANK_NAME_HEADER)
        self.account_number_header: Locator = page.locator(loc.ACCOUNT_NUMBER_HEADER)
        
        self.bottom_error: Locator = page.locator(loc.BOTTOM_ERROR)
        
        self.loading_spinner: Locator = page.locator(loc.LOADING_SPINNER)
    
    def get_request_header(self) -> str:
        """Get the REQUEST DETAILS heading text"""
        header_locator = self.page.locator("//h3[@aria-label = 'category-group-name' and text()='Request Details']")
        return header_locator.inner_text()
    
    def get_headers(self) -> list:
        """Get all category group item name headers"""
        headers_locator = self.page.locator("//h4[@aria-label='category-group-item-name']")
        headers_locator.first.wait_for(state="visible", timeout=10000)
        return headers_locator.all_inner_texts()
    
    def verify_destination_values(self) -> list:
        """Get all category group item values"""
        values_locator = self.page.locator("//p[@aria-label='category-group-item-value']")
        values_locator.first.wait_for(state="visible", timeout=10000)
        return values_locator.all_inner_texts()
    
    def wait_for_page_load(self):
        """Wait for MIMO Transaction Summary Page to load"""
        logger.info("Waiting for MIMO Transaction Summary Page to load")
        
        spinner = self.page.locator("//div[@data-testid='loading-spinner']")
        try:
            spinner.wait_for(state='hidden', timeout=60000)
        except Exception:
            logger.warning("Loading spinner wait timed out or spinner never appeared — continuing")
        
        self.transaction_summary_title.wait_for(state='visible', timeout=35000)
        logger.info("MIMO Transaction Summary Page loaded")
    
    # def get_summary_page_details(self, category_name: str) -> Dict[str, str]:
    #     """Get summary page details for a specific category"""
    #     logger.info(f"Getting summary page details for category: {category_name}")

    #     xpath = f"//h3[normalize-space(text())='{category_name}']//following-sibling::div//h4"
    #     locator = self.page.locator(xpath)

    #     try:
    #         if locator.count() > 0:
    #             locator.first.scroll_into_view_if_needed()
    #     except Exception as e:
    #         logger.warning(f"Failed to scroll summary category into view: {e}")

    #     elements_text = [elem.inner_text().strip() for elem in locator.all()]

    #     details: Dict[str, str] = {}
    #     for i in range(0, len(elements_text), 2):
    #         try:
    #             key = elements_text[i]
    #             value = elements_text[i + 1]
    #         except IndexError:
    #             logger.warning(f"Odd number of summary elements for category '{category_name}', skipping last item")
    #             break
    #         details[key] = value

    #     logger.info(f"Summary page details: {details}")
    #     return details
    
    def get_disclosures_title(self) -> str:
        """Get disclosures title"""
        try:
            self.disclosures_title.scroll_into_view_if_needed(timeout=5000)
            self.disclosures_title.wait_for(state='visible', timeout=10000)
        except Exception as e:
            logger.warning(f"Failed to scroll/wait for disclosures title: {e}")
        return self.disclosures_title.inner_text(timeout=10000)
    
    def get_disclosures_title_for_cancel_swp(self) -> str:
        """Get disclosures title for Cancel SWP"""
        return self.disclosures_title_cancel.inner_text()
    
    def get_disclosures_title_for_contribution(self) -> str:
        """Get disclosures title for Contribution"""
        self.disclosures_title_contribution.scroll_into_view_if_needed(timeout=5000)
        return self.disclosures_title_contribution.inner_text(timeout=10000)
    
    def get_disclosures_list_for_contribution(self) -> str:
        """Get disclosures list for Contribution"""
        self.disclosures_list_contribution.scroll_into_view_if_needed(timeout=5000)
        return self.disclosures_list_contribution.inner_text(timeout=10000)
    
    
    def get_disclaimer_text(self) -> str:
        """Get disclaimer text"""
        self.disclaimer_text.scroll_into_view_if_needed(timeout=5000)
        return self.disclaimer_text.inner_text(timeout=10000)
    
    def get_disclaimer_text_for_cancel_swp(self) -> str:
        """Get disclaimer text for Cancel SWP"""
        return self.disclaimer_text_cancel.inner_text()
    
    def get_disclosures_list(self) -> str:
        """Get disclosures list as text"""
        self.disclosures_list.scroll_into_view_if_needed(timeout=5000)
        return self.disclosures_list.inner_text(timeout=10000)
    
    def get_disclosures_list_for_cancel_swp(self) -> str:
        """Get disclosures list for Cancel SWP as text"""
        return self.disclosures_list_cancel.inner_text()
    
    def get_request_type(self) -> str:
        """Get request type"""
        return self.page.locator("//h4[normalize-space()='Request Type']").inner_text()
    
    def click_back(self):
        """Click back button"""
        logger.info("Clicking Back button")
        self.back_button.wait_for(state='visible', timeout=10000)
        self.back_button.click()
        logger.info("Clicked Back button")
    
    def click_submit(self):
        """Click submit button"""
        logger.info("Clicking Submit button")
        self.submit_button.wait_for(state='visible', timeout=10000)
        self.submit_button.click()
        
        try:
            self.loading_spinner.wait_for(state='hidden', timeout=60000)
        except Exception:
            logger.warning("Loading spinner wait timed out after submit — continuing")
        
        submission_error = self.page.locator("//div[@data-testid='submission-error-message']")
        for i in range(2):
            if submission_error.is_visible(timeout=5000):
                self.page.wait_for_timeout(3000)
                self.submit_button.click()
            else:
                break
        
        logger.info("Submit clicked successfully")
    
    def click_submit_for_review(self):
        """Click submit for review button"""
        logger.info("Clicking Submit for Review button")
        self.submit_to_review_button.wait_for(state='visible', timeout=10000)
        self.submit_to_review_button.click()
        logger.info("Submit for Review clicked successfully")
    
    def click_esign_and_submit(self):
        """Click E-Sign and Submit button"""
        logger.info("Clicking E-Sign and Submit button")
        self.esign_and_submit.wait_for(state='visible', timeout=10000)
        self.esign_and_submit.click()
        logger.info("E-Sign and Submit clicked successfully")
    
    def click_submit_or_submit_for_review_button(self):
        """Click submit or submit for review button"""
        logger.info("Clicking Submit or Submit for Review button")
        button_text = self.submit_or_submit_for_review.inner_text()
        self.submit_or_submit_for_review.click()
        logger.info(f"Clicked button: {button_text}")
    
    def get_account_info(self):
        """Get account information from summary page"""
        elements = self.account_info.all()
        return [elem.inner_text() for elem in elements]

    def validate_account_details_information_from_mimo_summary(self, account_details: list):
        """Validate account details on the MIMO Summary Page.

        Expects account_details like Java: [accountName, accountNumber, ...]
        Asserts that the UI elements (first three items) are contained in the provided
        account_details values (matching Java contains() checks).
        """
        logger.info("Validating account details on MIMO Summary Page")

        elems = self.get_account_info()
        if len(elems) < 3:
            raise AssertionError("Account info elements not found or incomplete on MIMO Summary Page")

        # Join all account_details parts so we can match elems against the full label
        # (e.g. elems[1] may now be the account number "40007734" which appears in the
        # wizard label part "(Account # 40007734" rather than at index [1])
        account_details_text = ", ".join(account_details)

        try:
            assert elems[0] in account_details[0] or account_details[0] in elems[0] or account_details[0].strip() in elems[0], (
                f"the value : {account_details[0]} - does not contain : {elems[0]}"
            )
            # elems[1] may contain account number or account type - search across all parts
            assert (
                elems[1] in account_details_text
                or any(elems[1] in part for part in account_details)
                or any(part.strip() in elems[1] for part in account_details if part.strip())
            ), (
                f"the value at page position [1]: '{elems[1]}' - was not found in account details: {account_details_text}"
            )
            # elems[2] may contain account strategy/type - search across all parts
            assert (
                elems[2] in account_details_text
                or any(elems[2] in part for part in account_details)
                or any(part.strip() in elems[2] for part in account_details if part.strip())
            ), (
                f"the value at page position [2]: '{elems[2]}' - was not found in account details: {account_details_text}"
            )
        except AssertionError:
            logger.exception("Account detail validation failed")
            raise

        logger.info("Account details on summary page validated successfully")
    
    def validate_transaction_summary_page_is_displayed(self) -> bool:
        """Validate transaction summary page is displayed"""
        return self.transaction_summary_title.is_visible(timeout=10000)

    def get_field_value(self, label: str) -> str:
        self.request_details_label.scroll_into_view_if_needed()
        locator = self.page.locator(
            f"//h4[@aria-label='category-group-item-name' and normalize-space(text())='{label}']"
            f"/following-sibling::h4[@aria-label='category-group-item-value']"
        )
        return locator.inner_text()

    def get_bottom_error(self) -> str:
        """Get bottom error message"""
        return self.bottom_error.inner_text()

    def get_summary_page_details(self, category_name: str) -> Dict[str, str]:
        xpath = f"//h3[text()='{category_name}']//following-sibling::div//h4"
        locator = self.page.locator(xpath)

        locator.first.scroll_into_view_if_needed()

        category_details = [el.inner_text() for el in locator.all()]

        details: Dict[str, str] = {}
        for i in range(0, len(category_details), 2):
            details[category_details[i]] = category_details[i + 1]

        return details
    
    def get_summarypage_details(self, category_name: str) -> Dict[str, str]:
        xpath = f"//h3[text()='{category_name}']//following-sibling::div//h4"
        locator = self.page.locator(xpath)

        locator.first.scroll_into_view_if_needed()

        category_details = [el.inner_text() for el in locator.all()]

        details: Dict[str, str] = {}
        for i in range(0, len(category_details), 2):
            details[category_details[i]] = category_details[i + 1]

        return details
        
    # def get_summary_page_details(self, category_name: str) -> Dict[str, str]:
    #     logger.info(f"Getting summary page details for category: {category_name}")
        
    #     category_items_xpath = f"//h3[text()='{category_name}']//parent::div//div[@aria-label='category-group-item']"
    #     category_items = self.page.locator(category_items_xpath)
        
    #     if category_items.count() > 0:
    #         category_items.first.scroll_into_view_if_needed()
    #         category_items.first.wait_for(state="visible", timeout=10000)
        
    #     details = {}
    #     count = category_items.count()
        
    #     for i in range(count):
    #         item = category_items.nth(i)
            
    #         field_name_locator = item.locator(".//h4[@aria-label='category-group-item-name']")
    #         field_value_locator = item.locator(".//h4[@aria-label='category-group-item-value']")
            
    #         if field_name_locator.count() > 0 and field_value_locator.count() > 0:
    #             field_name = field_name_locator.inner_text()
    #             field_value = field_value_locator.inner_text()
    #             details[field_name] = field_value
    #             logger.info(f"  {field_name}: {field_value}")
        
    #     return details

    def summary_page_qualified_values(self):
        
        logger.info("Getting qualified information value elements")
        
        qualified_info_values = self.page.locator(
            "//h3[text()='QUALIFIED INFORMATION']//parent::div//div[@aria-label='category-group-item']//h4[@aria-label='category-group-item-value']"
        )
        
        qualified_info_values.first.wait_for(state="visible", timeout=10000)
        
        count = qualified_info_values.count()
        elements = [qualified_info_values.nth(i) for i in range(count)]
        
        logger.info(f"Found {count} qualified information value elements")
        return elements

    def list_string_summary_page_qualified_values(self):
        """
        Get the text content of all qualified information values as a string list.
        
        Returns:
            List of strings containing the text of each value field
            [Distribution Reason text, Federal Tax text, State Tax text, State text, Net Amount text]
        """
        logger.info("Getting qualified information values as string list")
        
        qualified_info_values = self.page.locator(
            "//h3[text()='QUALIFIED INFORMATION']//parent::div//div[@aria-label='category-group-item']//h4[@aria-label='category-group-item-value']"
        )
        
        qualified_info_values.first.wait_for(state="visible", timeout=10000)
        
        values = qualified_info_values.all_text_contents()
        
        logger.info(f"Qualified information values: {values}")
        return values
