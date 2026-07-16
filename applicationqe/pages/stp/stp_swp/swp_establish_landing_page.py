from playwright.sync_api import Locator, Page

from pages.ewm.base_page import BasePage
from pages.stp.stp_swp.locators.swp_establish_landing_locators import SWPEstablishLandingLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishLandingPage(BasePage):
    """SWP Establish Landing Page - Page Object Model for Systematic Withdrawal Plan"""

    def __init__(self, page: Page):
        super().__init__(page)
        ctx = self.active_root()
        loc = SWPEstablishLandingLocators
        
        # Header elements
        self.swp_establish_header: Locator = ctx.locator(loc.SWP_ESTABLISH_HEADER)
        self.swp_establish_subheader: Locator = ctx.locator(loc.SWP_ESTABLISH_SUBHEADER)
        self.advisor_id_text: Locator = ctx.locator(loc.ADVISOR_ID_TEXT)
        self.advisor_id_value: Locator = ctx.locator(loc.ADVISOR_ID_VALUE)
        
        # Footer elements
        self.privacy_security_link: Locator = ctx.locator(loc.PRIVACY_SECURITY_LINK)
        self.terms_of_use_link: Locator = ctx.locator(loc.TERMS_OF_USE_LINK)
        self.supported_browsers_link: Locator = ctx.locator(loc.SUPPORTED_BROWSERS_LINK)
        self.as_copyrights: Locator = ctx.locator(loc.AS_COPYRIGHTS)
        
        # Action buttons
        self.add_button: Locator = ctx.locator(loc.ADD_BUTTON)
        self.cancel_button: Locator = ctx.locator(loc.CANCEL_BUTTON)
        
        # Account Information section
        self.account_information_header: Locator = ctx.locator(loc.ACCOUNT_INFORMATION_HEADER)
        self.account_info: Locator = ctx.locator(loc.ACCOUNT_INFO)
        self.market_value: Locator = ctx.locator(loc.MARKET_VALUE)
        self.cash_available: Locator = ctx.locator(loc.CASH_AVAILABLE)
        self.tooltip_btn: Locator = ctx.locator(loc.TOOLTIP_BTN)
        self.tooltip: Locator = ctx.locator(loc.TOOLTIP)
        
        # SWP Plans section
        self.swp_plan_header: Locator = ctx.locator(loc.SWP_PLAN_HEADER)
        self.swp_subheader: Locator = ctx.locator(loc.SWP_SUBHEADER)
        self.no_active_swp: Locator = ctx.locator(loc.NO_ACTIVE_SWP)
        self.active_swp: Locator = ctx.locator(loc.ACTIVE_SWP)
        
        # Error messages
        self.error_close_button: Locator = ctx.locator(loc.ERROR_CLOSE_BUTTON)
        self.deceased_error_heading: Locator = ctx.locator(loc.DECEASED_ERROR_HEADING)
        self.deceased_error_subheading: Locator = ctx.locator(loc.DECEASED_ERROR_SUBHEADING)
        
        # Oops message
        self.oops_message: Locator = ctx.locator(loc.OOPS_MESSAGE)
        self.reload_btn: Locator = ctx.locator(loc.RELOAD_BTN)
        
        # Discard dialog
        self.yes_exit_btn: Locator = ctx.locator(loc.YES_EXIT_BTN)
        self.no_stay_btn: Locator = ctx.locator(loc.NO_STAY_BTN)
        self.discard_message: Locator = ctx.locator(loc.DISCARD_MESSAGE)
        self.discard_message_subheader: Locator = ctx.locator(loc.DISCARD_MESSAGE_SUBHEADER)
        
        # Simple view elements - Check
        self.check_label: Locator = ctx.locator(loc.CHECK_LABEL)
        self.click_on_check: Locator = ctx.locator(loc.CLICK_ON_CHECK)
        self.detail_view_check: Locator = ctx.locator(loc.DETAIL_VIEW_CHECK)

    def verify_page_loaded(self) -> bool:
        """Verify SWP Establish Landing Page is loaded"""
        try:
            self.swp_establish_header.wait_for(state='visible', timeout=10000)
            self.swp_establish_subheader.wait_for(state='visible', timeout=10000)
            self.advisor_id_text.wait_for(state='visible', timeout=10000)
            self.advisor_id_value.wait_for(state='visible', timeout=10000)
            logger.info("SWP Establish Landing Page verification PASSED")
            return True
        except Exception as e:
            logger.warning(f"SWP Establish Landing Page verification FAILED: {e}")
            return False

    def get_advisor_id(self) -> str:
        """Get advisor ID value"""
        self.advisor_id_value.wait_for(state='visible')
        advisor_id = self.advisor_id_value.text_content()
        logger.info(f"Advisor ID: {advisor_id}")
        return advisor_id

    def get_header_text(self) -> str:
        """Get SWP Establish header text"""
        self.swp_establish_header.wait_for(state='visible')
        header_text = self.swp_establish_header.text_content()
        return header_text

    def get_subheader_text(self) -> str:
        """Get SWP Establish subheader text"""
        self.swp_establish_subheader.wait_for(state='visible')
        subheader_text = self.swp_establish_subheader.text_content()
        return subheader_text

    def click_add_button(self) -> None:
        """Click on ADD + button to add a new SWP record"""
        logger.info("Clicking on ADD + button")
        
        # Wait for any spinners to disappear
        self.page.wait_for_load_state('domcontentloaded')
        self.page.wait_for_timeout(8000)
        
        self.add_button.wait_for(state='visible', timeout=10000)
        self.add_button.click()
        
        logger.info("ADD + button clicked successfully")

    def click_cancel_button(self) -> None:
        """Click on Cancel button"""
        logger.info("Clicking on Cancel button")
        
        self.page.wait_for_load_state('domcontentloaded')
        self.cancel_button.wait_for(state='visible', timeout=10000)
        self.cancel_button.click()
        
        logger.info("Cancel button clicked")

    def get_account_information_header(self) -> str:
        """Get account information header text"""
        self.account_information_header.wait_for(state='visible')
        account_info_header = self.account_information_header.text_content()
        logger.info(f"Account Information Header: {account_info_header}")
        return account_info_header

    def get_account_details(self) -> str:
        """Get account details text"""
        self.account_info.wait_for(state='visible')
        account_details = self.account_info.text_content()
        logger.info(f"Account Details: {account_details}")
        return account_details

    def get_market_value(self) -> str:
        """Get market value text"""
        market_value = self.market_value.text_content()
        logger.info(f"Market Value: {market_value}")
        return market_value

    def get_cash_available(self) -> str:
        """Get cash available text"""
        self.cash_available.wait_for(state='visible', timeout=10000)
        cash_available = self.cash_available.text_content()
        logger.info(f"Cash Available: {cash_available}")
        return cash_available

    def get_swp_plan_header(self) -> str:
        """Get SWP Plans header text"""
        swp_plan = self.swp_plan_header.text_content()
        logger.info(f"SWP Plan Header: {swp_plan}")
        return swp_plan

    def get_no_active_swp_text(self) -> str:
        """Get no active SWP message text"""
        no_active = self.no_active_swp.text_content()
        logger.info(f"No Active SWP: {no_active}")
        return no_active

    def get_active_swp_text(self) -> str:
        """Get active SWP text"""
        active = self.active_swp.text_content()
        logger.info(f"Active SWP: {active}")
        return active

    def validate_buttons_on_swp_establish_page(self) -> bool:
        """Validate both Add and Cancel buttons are present"""
        add_button_found = self.add_button.is_visible()
        cancel_button_found = self.cancel_button.is_visible()
        return add_button_found and cancel_button_found

    def click_privacy_and_security(self) -> None:
        """Click Privacy and Security Policy link"""
        self.privacy_security_link.wait_for(state='visible')
        self.privacy_security_link.click()
        logger.info("Privacy and Security Policy link clicked")

    def click_terms_of_use(self) -> None:
        """Click Terms of Use link"""
        self.terms_of_use_link.wait_for(state='visible')
        self.terms_of_use_link.click()
        logger.info("Terms of Use link clicked")

    def click_supported_browsers(self) -> None:
        """Click Supported Browsers link"""
        self.supported_browsers_link.wait_for(state='visible')
        self.supported_browsers_link.click()
        logger.info("Supported Browsers link clicked")

    def get_error_close_button_text(self) -> str:
        """Get error close button text"""
        self.error_close_button.wait_for(state='visible')
        close_button_text = self.error_close_button.text_content()
        return close_button_text

    def click_error_close_button(self) -> None:
        """Click error close button"""
        self.error_close_button.wait_for(state='visible')
        self.error_close_button.click()
        logger.info("Error close button clicked")

    def get_deceased_error_heading(self) -> str:
        """Get deceased error heading text"""
        self.deceased_error_heading.wait_for(state='visible')
        return self.deceased_error_heading.text_content()

    def get_deceased_error_subheading(self) -> str:
        """Get deceased error subheading text"""
        self.deceased_error_subheading.wait_for(state='visible')
        return self.deceased_error_subheading.text_content()
