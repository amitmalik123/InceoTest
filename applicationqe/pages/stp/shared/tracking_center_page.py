from playwright.sync_api import Locator, Page, expect

from pages.stp.shared.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class TrackingCenterPage(BasePage):
    PAGE_URL = "https://test11.ewealthmanager.com/AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail/A034607033"

    def __init__(self, page: Page):
        super().__init__(page)
        self.roth_str_label: Locator = page.get_by_text("Roth Conversion")
        self.logout_link: Locator = page.get_by_role("link", name="Logout")
        self.bodycontent_div: Locator = page.locator("div#BodyContent")
        
        # Tracking center navigation and search locators (used in tracking_center_steps.py)
        self.tracking_center_link: Locator = page.locator("//ul[@id='mainMenu']//a[contains(text(),'Tracking Center')]")
        self.loading_spinner_modal: Locator = page.locator("//*[@id='loadingImageModal' and contains(@style,'block')]")
        self.search_input: Locator = page.locator("#client_search_input")
        self.search_button: Locator = page.locator("#searchbutton")
        
        # Item details locators (used in tracking_center_steps.py)
        self.address_text_detail: Locator = page.locator("//table[@id='TrackingCenterItemDetailNotesGrid']/tbody/tr[2]/td[4]")
        self.view_button: Locator = page.locator("//a[text()='View']")
        self.view_documents_header: Locator = page.locator("//div[@class='modal-title' and text()='View Documents']")
        self.pdf_list_table: Locator = page.locator("//div[@class='modal-body']//div[@id='PDFListTable']")
        self.document_links: Locator = page.locator("//div[@id='PDFListTable']//a[@name='pdfDetails']")
        self.esignature_button: Locator = page.locator('#resendRequest')

        # Electronic Signature Management modal
        self.esign_mgmt_dialog: Locator = page.locator('[aria-describedby="resendDialog"]')
        self.esign_mgmt_title: Locator = page.locator('#resendDialog').locator('xpath=preceding-sibling::div[contains(@class,"ui-dialog-titlebar")]//span[contains(@class,"ui-dialog-title")]')
        self.esign_mgmt_content: Locator = page.locator('#resendDialog')
        self.esign_resend_button: Locator = page.locator('#btnResendReminder1')
    
    def get_account_src_label(self, expected: str) -> Locator:
        """Get account source label locator by expected text"""
        return self.page.get_by_text(expected)
    
    def get_first_item_by_number(self, item_number: str) -> Locator:
        """Get first item locator by item number"""
        return self.page.locator(f"//td[contains(text(),'{item_number}')]").first
    
    def get_status_by_agent_id(self, agent_id: str) -> Locator:
        """Get status locator by agent ID"""
        return self.page.locator(f"//span[contains(text(),'{agent_id}')]/parent::div//child::span[3]")

    def navigate(self) -> None:
        logger.info(f"Navigating to tracking center page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        logger.info("Tracking center page loaded")

    def verify_account_src(self, expected: str) -> None:
        logger.info(f"Verifying account source: {expected}")
        account_src_label = self.get_account_src_label(expected)
        expect(account_src_label).to_have_text(expected)
        logger.info(f"Account source {expected} verified")

    def verify_roth_str(self, expected: str) -> None:
        logger.info(f"Verifying Roth STR: {expected}")
        expect(self.roth_str_label).to_have_text(expected)
        logger.info(f"Roth STR {expected} verified")

    def click_logout(self) -> None:
        logger.info("Clicking logout")
        self.click(self.logout_link)
        logger.info("Logout clicked")

    def click_bodycontent(self) -> None:
        logger.info("Clicking body content")
        self.click(self.bodycontent_div)

    def _wait_for_spinner(self) -> None:
        if self.loading_spinner_modal.count() > 0 and self.loading_spinner_modal.is_visible():
            self.loading_spinner_modal.wait_for(state='hidden', timeout=30000)

    def click_tracking_center_link(self) -> None:
        self.tracking_center_link.wait_for(state='visible', timeout=10000)
        self.tracking_center_link.click()
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)
        self.page.wait_for_timeout(2000)
        self._wait_for_spinner()

    def search_for_item(self, item_number: str) -> None:
        self.search_input.wait_for(state='visible', timeout=10000)
        self.search_input.fill(item_number)
        self.search_button.wait_for(state='visible', timeout=10000)
        self.search_button.click()
        self.page.wait_for_timeout(1000)
        self._wait_for_spinner()
        self.page.wait_for_timeout(2000)

    def click_first_item(self, item_number: str) -> None:
        first_item = self.get_first_item_by_number(item_number)
        first_item.wait_for(state='visible', timeout=20000)
        first_item.click()
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)
        self.page.wait_for_timeout(2000)

    def get_address_detail_text(self) -> str:
        self.address_text_detail.wait_for(state='visible', timeout=10000)
        return self.address_text_detail.inner_text().upper()

    def verify_address_details(
        self,
        test: str,
        mailing_after: list,
        legal_after: list,
        display_only_mailing: bool = False,
    ) -> None:
        detail_text = self.get_address_detail_text()
        failed = []
        if test in ['CheckBox', 'Mailing']:
            for component in mailing_after:
                if component and component.upper() not in detail_text:
                    failed.append(f"Mailing component missing: {component}")
            if display_only_mailing:
                if "LEGAL ADDRESS" in detail_text:
                    failed.append("Legal Address should not be displayed")
                if "CUSTODIAN" not in detail_text:
                    failed.append("Custodian should be displayed")
        if test in ['CheckBox', 'Legal']:
            for component in legal_after:
                if component and component.upper() not in detail_text:
                    failed.append(f"Legal component missing: {component}")
        assert not failed, f"Address verification failed: {failed}. Detail text: {detail_text}"

    def verify_status_complete(self, agent_id: str) -> None:
        status_locator = self.get_status_by_agent_id(agent_id)
        if status_locator.count() > 0:
            status_text = status_locator.inner_text()
            assert status_text == "Complete", f"Status should be 'Complete' but found: {status_text}"

    def click_view_and_verify_documents(self) -> None:
        self.view_button.wait_for(state='visible', timeout=10000)
        self.view_button.click()
        self.view_documents_header.wait_for(state='visible', timeout=10000)
        self.pdf_list_table.wait_for(state='visible', timeout=10000)
        document_count = self.document_links.count()
        assert document_count > 0, f"Expected at least 1 document but found: {document_count}"

    def click_esignature_button(self, timeout: int = 30000) -> None:
        """Click the eSignature button on the Tracking Center Item Detail page.

        The button is an anchor with id='resendRequest' and class='eSignResend item-detail-button'.
        Clicking it opens the eSignature resend modal/page.

        Args:
            timeout: Maximum time to wait for the button in milliseconds

        Raises:
            AssertionError: If the button is not visible within the timeout
        """
        logger.info("Clicking eSignature button on Tracking Center Item Detail page...")
        try:
            self.esignature_button.wait_for(state='visible', timeout=timeout)
            self.esignature_button.click()
            self.page.wait_for_load_state('domcontentloaded', timeout=timeout)
            logger.info("[PASS] eSignature button clicked")
        except Exception as e:
            raise AssertionError(
                f"[FAIL] eSignature button (#resendRequest) not clickable within "
                f"{timeout / 1000}s: {str(e).splitlines()[0]}"
            ) from e

    def verify_esign_management_modal(self, timeout: int = 30000) -> None:
        """Verify the 'Electronic Signature Management' modal is visible.

        The modal is a jQuery UI dialog identified by aria-describedby='resendDialog'.
        It contains a table of signers with columns: Full Name, Email Address, Phone,
        Status, Actions (Resend button).

        Args:
            timeout: Maximum time to wait for the modal in milliseconds

        Raises:
            AssertionError: If the modal is not visible within the timeout
        """
        logger.info("Verifying Electronic Signature Management modal is visible...")
        try:
            self.esign_mgmt_content.wait_for(state='visible', timeout=timeout)
            logger.info("[PASS] Electronic Signature Management modal is visible")
        except Exception as e:
            raise AssertionError(
                f"[FAIL] Electronic Signature Management modal (#resendDialog) not visible "
                f"within {timeout / 1000}s: {str(e).splitlines()[0]}"
            ) from e

    def click_resend_button(self, timeout: int = 30000) -> None:
        """Click the Resend button inside the Electronic Signature Management modal.

        Targets the first Resend button: id='btnResendReminder1', class='btn btn-primary'.
        After clicking, waits briefly for any confirmation or page state change.

        Args:
            timeout: Maximum time to wait for the button in milliseconds

        Raises:
            AssertionError: If the Resend button is not clickable within the timeout
        """
        logger.info("Clicking Resend button in Electronic Signature Management modal...")
        try:
            self.esign_resend_button.wait_for(state='visible', timeout=timeout)
            self.esign_resend_button.click()
            self.page.wait_for_timeout(2000)
            logger.info("[PASS] Resend button clicked")
        except Exception as e:
            raise AssertionError(
                f"[FAIL] Resend button (#btnResendReminder1) not clickable within "
                f"{timeout / 1000}s: {str(e).splitlines()[0]}"
            ) from e

    def navigate_and_verify_address_then_view(
        self,
        item_number: str,
        test: str,
        mailing_after: list,
        legal_after: list,
        display_only_mailing: bool,
        agent_id: str,
    ) -> None:
        self.click_tracking_center_link()
        self.search_for_item(item_number)
        self.click_first_item(item_number)
        self.verify_address_details(test, mailing_after, legal_after, display_only_mailing)
        self.verify_status_complete(agent_id)
        self.click_view_and_verify_documents()
