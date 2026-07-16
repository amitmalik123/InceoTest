from playwright.sync_api import Locator, Page

from pages.ewm.base_page import BasePage
from pages.stp.stp_swp.locators.withdrawal_signature_not_required_modal_locators import WithdrawalSignatureNotRequiredModalLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class WithdrawalSignatureNotRequiredModalPage(BasePage):
    
    def __init__(self, page: Page):
        super().__init__(page)
        ctx = self.active_root()
        loc = WithdrawalSignatureNotRequiredModalLocators
        self.signature_not_required_radio: Locator = ctx.locator(loc.SIGNATURE_NOT_REQUIRED_RADIO)
        self.print_signature_radio: Locator = ctx.locator(loc.PRINT_SIGNATURE_RADIO)
        self.request_signature_radio: Locator = ctx.locator(loc.REQUEST_SIGNATURE_RADIO)
        self.continue_button: Locator = ctx.locator(loc.CONTINUE_BUTTON)
    
    def click_submit_without_signature(self, request_type: str):
        """Click signature not required radio and continue button"""
        logger.info(f"Clicking submit without signature for: {request_type}")
        
        self.signature_not_required_radio.wait_for(state='visible', timeout=10000)
        self.signature_not_required_radio.click()
        logger.info("Clicked signature not required radio")
        
        self.continue_button.click()
        logger.info("Clicked continue button")
        
        self.page.wait_for_timeout(1000)
        
        if request_type in ["Contributions", "Cancel"]:
            logger.info(f"Navigating to MIMO Transaction Request Page for {request_type}")
        else:
            logger.info("Switching to iframe for withdrawal method modal")
            if self.page.locator("#esig_iframe").count() > 0:
                logger.info("esig_iframe found")

    def click_request_esign_signature(self):
        """Select 'Request client electronic signature' radio and click Continue."""
        logger.info("Selecting 'Request client electronic signature' radio")
        self.request_signature_radio.wait_for(state='visible', timeout=10000)
        self.request_signature_radio.click()
        logger.info("Clicked e-sign radio")

        self.continue_button.click()
        logger.info("Clicked Continue button for e-sign flow")

        self.page.wait_for_timeout(1000)
