from playwright.sync_api import Locator, Page

from pages.stp.shared.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SWPEstablishLandingPage(BasePage):
    """SWP Establish Landing Page - Page Object Model for Systematic Withdrawal Plan"""

    def __init__(self, page: Page):
        super().__init__(page)
        
        # Header elements
        self.swp_establish_header: Locator = page.locator("//p[text()='Systematic Withdrawal Plan']")
        self.swp_establish_subheader: Locator = page.locator("//p[text()='Establish']")
        self.advisor_id_text: Locator = page.locator("//p[text()='Advisor ID']")
        self.advisor_id_value: Locator = page.locator("//span[contains(text(),'AG')]")
        
        # Footer elements
        self.privacy_security_link: Locator = page.locator("//div[text()='Privacy and Security Policy']")
        self.terms_of_use_link: Locator = page.locator("//div[text()='Terms of Use']")
        self.supported_browsers_link: Locator = page.locator("//div[text()='Supported Browsers']")
        self.as_copyrights: Locator = page.locator("//div[@class='sc-jxOSlx epJOzn']")
        
        # Action buttons
        self.add_button: Locator = page.locator("//button[text()='ADD +']")
        self.cancel_button: Locator = page.locator("(//button[text()='Cancel'])[1]")
        
        # Account Information section
        self.account_information_header: Locator = page.locator("//span[text()='Account Information']")
        self.account_info: Locator = page.locator("//span[@class='MuiTypography-root MuiTypography-body1 MuiCardHeader-subheader css-1cnfykm']")
        self.market_value: Locator = page.locator("//div[@class='MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 css-bcrxyx'][1]")
        self.cash_available: Locator = page.locator("//div[@class='MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-12 css-bcrxyx'][2]")
        self.tooltip_btn: Locator = page.locator("//div[@class='sc-kzqdkY bHJfVD']")
        self.tooltip: Locator = page.locator("//div[@role='tooltip']")
        
        # SWP Plans section
        self.swp_plan_header: Locator = page.locator("//span[@class='MuiTypography-root MuiTypography-h5 MuiCardHeader-title css-1od5tcn']")
        self.swp_subheader: Locator = page.locator("//span[contains(@class,'css-pj59b1')]")
        self.no_active_swp: Locator = page.locator("//div[@class='sc-bOhtcR dOwMgM MuiBox-root css-0']")
        self.active_swp: Locator = page.locator("//div[@class='sc-BQMaI dsCHCa MuiBox-root css-0']")
        
        # Error messages
        self.error_close_button: Locator = page.locator("//button[text()='Close']")
        self.deceased_error_heading: Locator = page.locator("//span[text()='Unclaimed asset or deceased accounts not eligible.']")
        self.deceased_error_subheading: Locator = page.locator("//div[text()='Unclaimed asset or deceased accounts are not eligible. Please contact your Relationship Manager with any questions or email us at ']")
        
        # Oops message
        self.oops_message: Locator = page.locator("//div[@class='sc-dSCufp kVspaA']")
        self.reload_btn: Locator = page.locator("//button[contains(text(), 'Reload') and contains(@class, 'MuiButton-containedPrimary')]")
        
        # Discard dialog
        self.yes_exit_btn: Locator = page.locator("//button[contains(text(), 'YES, EXIT') and contains(@class, 'MuiButton-containedPrimary')]")
        self.no_stay_btn: Locator = page.locator("//button[text()='NO, STAY']")
        self.discard_message: Locator = page.locator("//h3[contains(@class, 'MuiTypography-h3')]")
        self.discard_message_subheader: Locator = page.locator("//h5[contains(@class, 'MuiTypography-h5')]")
        
        # Simple view elements - Check
        self.check_label: Locator = page.locator("//p[text()='Check']/parent::div")
        self.click_on_check: Locator = page.locator("//p[text()='Check'][1]")
        self.detail_view_check: Locator = page.locator("//div[@class='sc-epqpcT bKDNff MuiBox-root css-0']")

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
