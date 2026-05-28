
from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.shared.locators.account_wizard_locators import AccountWizardLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountWizardPage(BasePage):
    PAGE_URL = (
        "https://test11.ewealthmanager.com/DNeWM/NBT/List/ClientAccounts.aspx?AccountId=AI6H26"
    )

    def __init__(self, page: Page):
        super().__init__(page)
        loc = AccountWizardLocators
        self.account_wizard_link: Locator = page.get_by_role('link', name=loc.ACCOUNT_WIZARD_LINK)
        self.account_wizard_header: Locator = page.get_by_role('heading', name=loc.ACCOUNT_WIZARD_HEADING)
        self.selected_account_label: Locator = page.locator(loc.SELECTED_ACCOUNT_LABEL)
        self.complete_and_submit_btn: Locator = page.locator(loc.COMPLETE_AND_SUBMIT_BTN)
        self.address_change_link: Locator = page.locator(loc.ADDRESS_CHANGE_LINK)
        self.next_button: Locator = page.locator(loc.NEXT_BUTTON)
        self.loading_modal: Locator = page.locator(loc.LOADING_MODAL)
        self.add_ach_link: Locator = page.get_by_role('link', name=loc.ADD_ACH_LINK)
    
    def get_account_label_locator(self, account_number: str) -> Locator:
        """Get locator for account label by account number"""
        return self.page.locator(f"//label[contains(text(), '{account_number}')]")
    
    def get_selected_account_checkbox_locator(self, account_number: str) -> Locator:
        """Get locator for selected account checkbox by account number"""
        return self.page.locator(f"//label[contains(text(), '{account_number}')]/preceding-sibling::div//input[@checked]")
    
    def get_request_item_locator(self, request: str) -> Locator:
        """Get locator for request item by request name"""
        return self.page.locator(f"//li[contains(text(), '{request}')]")
    
    def get_type_item_locator(self, type_name: str) -> Locator:
        """Get locator for type item by type name"""
        if type_name == "Cancel":
            return self.page.locator("//li[.//b[normalize-space()='Systematic Withdrawal']]/following-sibling::li[normalize-space()='Cancel']")
        elif type_name == "Establish":
            return self.page.locator("//li[text()='Establish'][4]")
        else:
            return self.page.locator(f"//li[contains(text(), '{type_name}')]")

    def navigate(self) -> None:
        logger.info(f"AccountWizardPage navigate - Current URL: {self.page.url}")

        if self.PAGE_URL in self.page.url:
            logger.info("Already on account detail page")
            self.page.wait_for_load_state("domcontentloaded", timeout=120000)
        else:
            logger.info(f"Navigating to: {self.PAGE_URL}")
            self.page.goto(self.PAGE_URL, wait_until="networkidle", timeout=120000)
        self.dismiss_cookie_banner()
        logger.info("Account detail page ready")

    def click_account_wizard(self) -> None:
        logger.info("Clicking Account Wizard link")
        self.account_wizard_link.wait_for(state="visible", timeout=10000)
        self.account_wizard_link.click()
        self.page.wait_for_load_state("networkidle", timeout=120000)
        self.dismiss_cookie_banner()
        logger.info("Account Wizard link clicked")

    def verify_account_wizard_page_loaded(self, expected_client_name: str = None) -> None:
        logger.info("Verifying Account Wizard page is loaded")

        self.account_wizard_header.wait_for(state="visible", timeout=10000)
        header_text = self.get_text(self.account_wizard_header)

        if header_text and "Account Wizard" in header_text:
            logger.info(f"Account Wizard page loaded successfully. Header: {header_text}")
        else:
            raise Exception(
                f"Account Wizard page header not found or incorrect. Found: {header_text}"
            )

        if expected_client_name:
            self.client_name.wait_for(state="visible", timeout=10000)
            client_name_text = self.get_text(self.client_name)
            logger.info(f"Client name displayed: {client_name_text}")

            if expected_client_name not in client_name_text:
                raise Exception(
                    f"Expected client name '{expected_client_name}' not found. Found: {client_name_text}"
                )
            logger.info(f"Client name verified: {client_name_text}")

    def select_and_fetch_account_by_client_id(self, client_id: str) -> list:
        logger.info(f"Looking for account radio button containing client_id: {client_id}")

        # Label that contains the client_id number in its text
        label_locator = self.page.locator(f"xpath=//label[contains(text(),'{client_id}')]")
        label_locator.wait_for(state="visible", timeout=15000)

        # The uniform div.radio wrapper is the preceding-sibling of the label's parent td children
        # Structure: div.radio > span > input; then label as sibling of div.radio
        radio_div = self.page.locator(
            f"xpath=//label[contains(text(),'{client_id}')]/preceding-sibling::div[contains(@class,'radio')]"
        )

        # Check if already selected (uniform adds class 'checked' to the span inside div.radio)
        checked_span = self.page.locator(
            f"xpath=//label[contains(text(),'{client_id}')]"
            f"/preceding-sibling::div[contains(@class,'radio')]//span[contains(@class,'checked')]"
        )

        if checked_span.count() > 0:
            logger.info(f"Account radio for client_id '{client_id}' is already selected")
        else:
            logger.info(f"Account radio for client_id '{client_id}' is NOT selected — clicking to select")
            self.dismiss_cookie_banner()
            # JS click bypasses any z-index overlay (e.g. onetrust-pc-dark-filter) intercepting pointer events
            radio_div.evaluate("el => el.click()")
            # Wait for the ASP.NET postback triggered by onclick
            self.page.wait_for_load_state("networkidle", timeout=120000)
            logger.info(f"[OK] Account radio for client_id '{client_id}' selected")

        account_text = (label_locator.first.text_content() or "").strip()
        logger.info(f"Selected account information: {account_text}")

        if not account_text:
            return []

        parts = [p.strip() for p in account_text.split(",") if p is not None]
        return parts

    def click_add_ach_instructions(self):
        """Click on Add ACH Instructions link"""
        logger.info("Clicking Add ACH Instructions link")
        
        # Wait for any existing loading modals to disappear first
        self.add_ach_link.wait_for(state='visible', timeout=120000)
        if self.loading_modal.count() > 0:
            logger.info("Waiting for loading modal to disappear")
            try:
                self.loading_modal.wait_for(state="hidden", timeout=120000)
            except:
                logger.warning("Loading modal wait timed out, continuing")
        
        # Wait again right before click in case modal reappears
        if self.loading_modal.count() > 0 and self.loading_modal.is_visible():
            logger.info("Loading modal still visible, waiting before click")
            self.loading_modal.wait_for(state="hidden", timeout=120000)
        
        self.dismiss_cookie_banner()
        # JS click bypasses any z-index overlay (e.g. onetrust-consent-sdk) intercepting pointer events
        self.add_ach_link.evaluate("el => el.click()")
        
        # Wait for navigation/modal to load
        self.page.wait_for_load_state("domcontentloaded", timeout=120000)

        logger.info("Add ACH Instructions link clicked")

    def click_account(self, account_number: str):
        """Click on account checkbox by account number"""
        logger.info(f"Selecting account: {account_number}")
        
        # Check if already selected
        selected_checkbox = self.get_selected_account_checkbox_locator(account_number)
        if selected_checkbox.count() > 0:
            logger.info(f"Account {account_number} already selected")
            return
        
        # Click the label to select the account
        account_label = self.get_account_label_locator(account_number)
        account_label.wait_for(state='visible', timeout=20000)
        account_label.click()
        logger.info(f"Account {account_number} selected")

    def select_request(self, request: str):
        """Select a request type from the dropdown"""
        logger.info(f"Selecting request: {request}")
        
        # Wait for JS to load
        self.page.wait_for_load_state('domcontentloaded')
        self.dismiss_cookie_banner()
        
        request_item = self.get_request_item_locator(request)
        request_item.wait_for(state='visible', timeout=20000)
        request_item.click(force=True)
        logger.info(f"Request '{request}' selected")

    def select_type(self, type_name: str):
        """Select a type from the dropdown"""
        logger.info(f"Selecting type: {type_name}")
        
        # Wait for JS to load
        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_timeout(500)
        self.dismiss_cookie_banner()
        
        type_item = self.get_type_item_locator(type_name)
        type_item.wait_for(state='visible', timeout=20000)
        type_item.click(force=True)
        logger.info(f"Type '{type_name}' selected")

    def click_complete_and_submit(self):
        """Click the Complete and Submit button"""
        logger.info("Clicking Complete and Submit button")
        if self.loading_modal.count() > 0 and self.loading_modal.is_visible():
            logger.info("Waiting for loading spinner to disappear before Complete and Submit")
            self.loading_modal.wait_for(state="hidden", timeout=120000)
        self.complete_and_submit_btn.wait_for(state='visible', timeout=30000)
        self.complete_and_submit_btn.scroll_into_view_if_needed()
        self.complete_and_submit_btn.click(force=True)
        logger.info("Complete and Submit button clicked")

    def click_dm_link(self):
        """Click on Update Addresses (DM Link) and navigate to DM Tool page"""
        logger.info("Clicking on Update Addresses link")
        
        if self.loading_modal.count() > 0 and self.loading_modal.is_visible():
            logger.info("Waiting for spinner to disappear")
            self.loading_modal.wait_for(state="hidden", timeout=120000)
        
        self.address_change_link.wait_for(state='visible', timeout=120000)
        self.dismiss_cookie_banner()
        # JS click bypasses any z-index overlay (e.g. onetrust-pc-dark-filter) intercepting pointer events
        with self.page.expect_navigation(timeout=30000):
            self.address_change_link.evaluate("el => el.click()")
        logger.info("Navigated to DM Tool page")

    def click_next_btn_for_swp(self):
        """Click Next button for SWP Establish - returns SWPEstablishLandingPage"""
        from pages.stp.stp_swp.swp_establish_landing_page import SWPEstablishLandingPage
        
        logger.info("Clicking Next button for SWP")
        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.click()
        
        # Wait for next button to become clickable again (page transition)
        self.page.wait_for_timeout(5000)
        
        logger.info("Next button for SWP clicked successfully")
        return SWPEstablishLandingPage(self.page)

    def click_next_button_for_establish_aip(self):
        """Click Next button for Establish AIP - returns EstablishAIPLandingPage"""
        from pages.establish_aip_landing_page import EstablishAIPLandingPage
        
        logger.info("Clicking Next button for Establish AIP")
        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.click()
        
        # Wait for next button to become clickable again (page transition)
        self.page.wait_for_timeout(5000)
        
        logger.info("Next button for Establish AIP clicked successfully")
        return EstablishAIPLandingPage(self.page)
