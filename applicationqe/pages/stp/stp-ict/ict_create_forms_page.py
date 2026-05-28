from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.create_forms_locators import CreateFormsLocators
from validations.create_forms_validations import CreateFormsValidations

logger = setup_logger(__name__)


class CreateFormsPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/ISCT/CreateForms'

    def __init__(self, page: Page):
        super().__init__(page)
        self._validations = CreateFormsValidations(self.page)

    def verify_required_forms_present(self) -> None:
        """Save HTML for diagnostics then validate required forms."""
        logger.info("Verifying required forms on Create Forms page")
        try:
            with open('reports/create_forms_page.html', 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass
        self._validations.validate_required_forms_present()

    def click_complete_and_submit(self) -> None:
        logger.info("Clicking Complete and Submit")
        self.page.wait_for_load_state('networkidle', timeout=30000)
        self.page.locator(CreateFormsLocators.COMPLETE_AND_SUBMIT).click()
        logger.info("Complete and Submit clicked")

    def select_proceed_without_signature(self) -> None:
        """Ensure the 'Proceed and submit without a client signature' radio is selected.
        The radio uses uniform.js (opacity:0) so we cannot wait_for visible — use force click.
        """
        logger.info("Selecting Proceed without client signature")
        try:
            with open('reports/after_complete_and_submit.html', 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass
        radio = self.page.locator(CreateFormsLocators.PROCEED_WITHOUT_SIG_RADIO)
        # Wait for it to be attached (it's in the DOM but opacity:0)
        radio.wait_for(state='attached', timeout=10000)
        if not radio.is_checked():
            radio.click(force=True)
            logger.info("Proceed without signature radio clicked")
        else:
            logger.info("Proceed without signature radio already selected by default")

    def click_continue_on_popup(self) -> None:
        logger.info("Clicking Continue (OnlineSubmitbutton) on signature popup")
        # Save HTML right before clicking for diagnostics
        try:
            with open('reports/before_continue_click.html', 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass
        btn = self.resolve_locator(CreateFormsLocators.CONTINUE_BUTTON)
        btn.wait_for(state='visible', timeout=15000)
        btn.click()
        logger.info("Continue clicked")


    #def click_next(self) -> None:
    #    logger.info("Clicking Next button on Create Forms page")
    #    self.page.locator(CreateFormsLocators.NEXT).click()
    #    logger.info("Next button clicked")
