from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class CreateDocumentsPage(BasePage):
    """Page object for Create Documents page"""

    PAGE_NAME = "CREATE DOCUMENTS PAGE"

    def __init__(
        self,
        page: Page,
        page_verification: bool = True,
    ):
        """Initialize Create Documents page"""
        super().__init__(page)
        self.form_root = self.active_root()

        # Page locators
        self.page_label: Locator = self.form_root.locator(".PageHeading")
        self.create_documents_button: Locator = self.form_root.locator("//button[@class='btn btn-primary btn-next'] | //button[@id='create_documents_button']")
        self.esignature_button: Locator = self.form_root.locator(
            "xpath=//*[@id='eSignatureButton']"
            " | //button[contains(@id, 'eSignature') or contains(@class, 'eSignatureButton')"
            " or contains(translate(normalize-space(.), 'ESIGNATURE', 'esignature'), 'esignature')]"
            " | //a[contains(translate(normalize-space(.), 'ESIGNATURE', 'esignature'), 'esignature')]"
            " | //input[contains(translate(@value, 'ESIGNATURE', 'esignature'), 'esignature')"
            " or contains(translate(@id, 'ESIGNATURE', 'esignature'), 'esignature')]"
        )
        self.error_exclamation: Locator = self.form_root.locator("div.error-exclamation:visible")
        self.upload_paperwork_modal_title: Locator = self.form_root.locator("#confirmOverwriteModalLabel")
        self.upload_paperwork_modal_yes_button: Locator = self.form_root.locator("#button-overwrite-approval")
        self.documents_processing_spinner: Locator = self.form_root.locator('[class*="spinner"], [class*="loading"]')
        
        if page_verification:
            self._verify_page_label()

    def _verify_page_label(self):
        """Verify create documents page is loaded"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            if self.page_label.count() > 0:
                logger.info(f"{self.PAGE_NAME} verification: PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} page label not found, continuing anyway")
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification failed: {str(e).splitlines()[0]}, continuing anyway")

    def create_documents_confirmation(self):
  
        try:
            # Fail fast if page has visible validation errors
            error_count = self.error_exclamation.count()
            if error_count > 0:
                msgs = [self.error_exclamation.nth(i).locator("..").inner_text().strip() for i in range(error_count)]
                Assertions.assert_equal(
                    error_count, 0,
                    f"Create Documents page has validation errors: {'; '.join(filter(None, msgs))}"
                )

            # Wait for create documents button to be visible and click
            self.click(self.create_documents_button)

            # Wait for navigation to View Documents page to complete before checking eSignature.
            try:
                self.page.wait_for_url("**/Documents/View**", timeout=90000)
            except Exception:
                pass
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
    
            # Refresh root/locators after navigation in case context changed.
            self.form_root = self.active_root()
            self.page_label = self.form_root.locator(".PageHeading")
            self.form_root.locator("#view-documents-page").wait_for(state="visible", timeout=60000)
            self.esignature_button = self.form_root.locator(
                "xpath=//*[@id='eSignatureButton']"
                " | //button[contains(@id, 'eSignature') or contains(@class, 'eSignatureButton')"
                " or contains(translate(normalize-space(.), 'ESIGNATURE', 'esignature'), 'esignature')]"
                " | //a[contains(translate(normalize-space(.), 'ESIGNATURE', 'esignature'), 'esignature')]"
                " | //input[contains(translate(@value, 'ESIGNATURE', 'esignature'), 'esignature')"
                " or contains(translate(@id, 'ESIGNATURE', 'esignature'), 'esignature')]"
            )

            try:
                self.form_root.locator(".PageHeading", has_text="View Documents").wait_for(state="visible", timeout=30000)
            except Exception:
                pass

            self.esignature_button.wait_for(state="visible", timeout=120000)
            
        except Exception as e:
            logger.error(f"Error creating documents: {str(e).splitlines()[0]}")
            raise

