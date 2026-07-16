from playwright.sync_api import Page
from pages.ewm.base_page import BasePage
from pages.stp.stp_addACHIntrcutions.locators.add_ach_summary_locators import AddACHSummaryLocators
from pages.stp.stp_addACHIntrcutions.add_ach_confirmation_page import AddACHConfirmationPage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AddACHSummaryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        loc = AddACHSummaryLocators
        
        # Headers
        self.request_summary_header = page.locator(loc.REQUEST_SUMMARY_HEADER)
        self.request_summary_subheader = page.locator(loc.REQUEST_SUMMARY_SUBHEADER)
        
        # Summary block elements
        self.summary_block_list = page.locator(loc.SUMMARY_BLOCK_LIST)
        self.summary_labels = page.locator(loc.SUMMARY_LABELS)
        self.summary_values = page.locator(loc.SUMMARY_VALUES)
        
        # Investment accounts
        self.investment_accounts_single = page.locator(loc.INVESTMENT_ACCOUNTS_SINGLE)
        self.investment_accounts_multi = page.locator(loc.INVESTMENT_ACCOUNTS_MULTI)
        
        # Alerts
        self.advisor_alert = page.locator(loc.ADVISOR_ALERT)
        
        # SLOA options
        self.sloa_text = page.get_by_test_id(loc.SLOA_TEXT_TESTID)
        
        # Disclosure/Agreements section
        self.agreements_title = page.locator(loc.AGREEMENTS_TITLE)
        self.agreements_subheader = page.locator(loc.AGREEMENTS_SUBHEADER)
        self.agreements_bullets = page.locator(loc.AGREEMENTS_BULLETS)
        
        # Buttons
        self.submit_button = page.get_by_role("button", name=loc.SUBMIT_BUTTON)
        self.submit_button_alt = page.locator(loc.SUBMIT_BUTTON_ALT)
        
        # Loading indicators
        self.spinner_locator = page.locator(loc.SPINNER)
        
        # Numbering patterns for account validation
        self.numbered_pattern = page.locator(loc.NUMBERED_PATTERN)
    
    def get_numbered_pattern_locator(self):
        """Helper method to get numbered pattern locator"""
        return self.numbered_pattern

    def get_request_summary_header(self) -> str:
        """Get the Request Summary header text"""
        logger.info("Getting Request Summary header")
        header = self.request_summary_header.inner_text()
        logger.info(f"Request Summary header: {header}")
        return header

    def get_request_summary_subheader(self) -> str:
        """Get the Request Summary subheader text"""
        logger.info("Getting Request Summary subheader")
        subheader = self.request_summary_subheader.inner_text()
        logger.info(f"Request Summary subheader: {subheader}")
        return subheader

    def get_summary_block_list(self) -> list:
        """Get all summary block values as a list"""
        logger.info("Getting summary block values")
        
        values = self.summary_block_list.all_inner_texts()
        values = [v.strip() for v in values if v.strip()]
        
        logger.info(f"Summary block values: {values}")
        return values

    def mask_account_number(self, account_number: str) -> str:
        """Mask account number to show only last 4 digits"""
        if len(account_number) <= 4:
            return account_number
        
        last_4 = account_number[-4:]
        masked = "*" * (len(account_number) - 4) + last_4
        logger.info(f"Masked account number: {account_number} -> {masked}")
        return masked

    def get_sloa_displayed(self) -> str:
        """Get the displayed SLOA option"""
        logger.info("Getting SLOA displayed value")
        
        # Look for SLOA value element by test-id
        try:
            sloa_text = self.sloa_text.first.inner_text()
            logger.info(f"SLOA displayed: {sloa_text}")
            return sloa_text
        except Exception as e:
            logger.warning(f"SLOA option not found on page: {e}")
            return ""

    def get_single_investment_account(self) -> str:
        """Get single investment account details"""
        logger.info("Getting single investment account")
        
        account_detail = self.investment_accounts_single.first.inner_text()
        logger.info(f"Single investment account: {account_detail}")
        return account_detail

    def get_investment_accounts(self) -> str:
        """Get all investment accounts as comma-separated string"""
        logger.info("Getting multiple investment accounts")
        
        # For multiple accounts, get the text from the ordered list
        accounts_text = self.investment_accounts_multi.inner_text()
        logger.info(f"Multiple investment accounts: {accounts_text}")
        return accounts_text

    def check_single_account_no_numbering(self) -> bool:
        """Check if single account is displayed without numbering (1., 2., etc.)"""
        logger.info("Checking if single account has no numbering")
        
        has_numbering = self.numbered_pattern.count() > 0
        
        logger.info(f"Single account numbering check: {not has_numbering}")
        return not has_numbering

    def check_multi_account_with_numbering(self) -> bool:
        """Check if multiple accounts are displayed with numbering"""
        logger.info("Checking if multiple accounts have numbering")
        
        has_numbering = self.numbered_pattern.count() > 0
        
        logger.info(f"Multiple accounts numbering check: {has_numbering}")
        return has_numbering

    def is_advisor_alert_visible(self) -> bool:
        """Check if advisor alert is visible"""
        logger.info("Checking if advisor alert is visible")
        is_visible = self.advisor_alert.is_visible()
        logger.info(f"Advisor alert visible: {is_visible}")
        return is_visible

    def get_advisor_alert(self) -> str:
        """Get the advisor alert text"""
        logger.info("Getting advisor alert text")
        alert_text = self.advisor_alert.inner_text()
        logger.info(f"Advisor alert: {alert_text}")
        return alert_text

    def get_agreements_title(self) -> str:
        logger.info("Getting agreements title")
        title = self.agreements_title.inner_text()
        logger.info(f"Agreements title: {title}")
        return title

    def get_agreements_subheader(self) -> str:
        """Get the Agreements/Disclosure subheader"""
        logger.info("Getting agreements subheader")
        subheader = self.agreements_subheader.inner_text()
        logger.info(f"Agreements subheader: {subheader}")
        return subheader

    def get_agreements_bullets(self) -> str:
        """Get the Agreements/Disclosure bullet points as text"""
        logger.info("Getting agreements bullets")
        bullets_text = self.agreements_bullets.inner_text()
        logger.info(f"Agreements bullets: {bullets_text}")
        return bullets_text

    def click_submit(self):
        """Click the Submit button on summary page"""
        logger.info("Clicking Submit button")
        
        # Wait for any loading spinners to disappear
        try:
            self.spinner_locator.wait_for(state='hidden', timeout=10000)
            logger.info("Loading spinner disappeared")
        except Exception as e:
            logger.info(f"No spinner found or already hidden: {e}")
        
        # Wait for page to be stable
        try:
            self.page.wait_for_load_state('domcontentloaded', timeout=10000)
        except:
            logger.warning("Timeout waiting for domcontentloaded")
        
        self.page.wait_for_timeout(2000)
        
        # Wait for submit button to be present and visible
        try:
            self.submit_button.wait_for(state='visible', timeout=15000)
            logger.info("Submit button is visible")
        except Exception as e:
            logger.error(f"Submit button not visible: {e}")
            # Try alternative locator
            if self.submit_button_alt.count() > 0:
                self.submit_button = self.submit_button_alt
                logger.info("Using alternative Submit button locator")
        
        # Scroll to submit button
        self.submit_button.scroll_into_view_if_needed()
        self.page.wait_for_timeout(1000)
        
        # Try multiple click strategies
        clicked = False
        
        # Strategy 1: Regular click
        if not clicked:
            try:
                self.submit_button.click(timeout=5000)
                clicked = True
                logger.info("Submit button clicked (regular click)")
            except Exception as e:
                logger.warning(f"Regular click failed: {e}")
        
        # Strategy 2: Force click
        if not clicked:
            try:
                self.submit_button.click(force=True, timeout=5000)
                clicked = True
                logger.info("Submit button clicked (force click)")
            except Exception as e:
                logger.warning(f"Force click failed: {e}")
        
        # Strategy 3: JavaScript click
        if not clicked:
            try:
                self.page.evaluate("""(selector) => {
                    const button = document.evaluate(selector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue ||
                                 Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Submit'));
                    if (button) button.click();
                }""", "//button[contains(text(), 'Submit')]")
                clicked = True
                logger.info("Submit button clicked (JavaScript click)")
            except Exception as e:
                logger.error(f"JavaScript click failed: {e}")
        
        if not clicked:
            raise Exception("Failed to click Submit button after all strategies")
        
        # Wait for page transition
        self.page.wait_for_timeout(3000)
        
        return AddACHConfirmationPage(self.page)
