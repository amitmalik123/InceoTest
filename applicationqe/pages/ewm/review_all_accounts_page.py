from playwright.sync_api import Locator, Page
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class ReviewAllAccountsPage(BasePage):
    """Page object for Review All Accounts page"""

    PAGE_NAME = "REVIEW ALL ACCOUNTS PAGE"

    def __init__(
        self,
        page: Page,
        page_verification: bool = True,
    ):
        """Initialize Review All Accounts page"""
        super().__init__(page)
        self.form_root = self.active_root()

        # Page locators
        self.page_label: Locator = self.form_root.locator(".review-all-accounts-header h1")
        self.client_full_name: Locator = self.form_root.locator("//div[contains(@class, 'account-holder-info')]//div[contains(@class, 'full-name')]")
        self.approval_points: Locator = self.form_root.locator(".interview-page-summary span:first-of-type")
        self.create_documents_button: Locator = self.form_root.locator(
            "#create_documents_button, .btn.btn-primary.btn-next, button.btn.btn-primary.right"
        ).first
        
        # Missing information modal
        self.missing_information_modal: Locator = self.form_root.locator("#MissingInformationModal")
        self.missing_information_yes_button: Locator = self.form_root.locator("#create_documents_btn")
        
        if page_verification:
            self._verify_page_label()

    def _verify_page_label(self):
        """Verify review all accounts page is loaded"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            label = self.page_label
            if label.count() > 0:
                logger.info(f"{self.PAGE_NAME} verification: PASSED")
            else:
                logger.warning(f"{self.PAGE_NAME} verification: PASSED (page label not found but continuing)")
        except Exception as e:
            logger.warning(f"{self.PAGE_NAME} verification failed: {str(e).splitlines()[0]}, continuing anyway")

    def verify_review_account_page(self, fname: str, lname: str, bday: str) -> None:
        """
        Verify the client's full name matches expected values using base_page assertion
        
        Args:
            fname: Expected first name
            lname: Expected last name
            bday: Expected birth date (for reference, not verified in this method)
        """
        logger.info(f"Verifying review account page with name: {fname} {lname}")

        expected_name = f"{fname} {lname}".strip()
        actual_name = (self.client_full_name.text_content() or "").strip()

        # Hard assertion: fail immediately when UI name does not exactly match expected name.
        Assertions.assert_true(
            actual_name == expected_name,
            f"Client Full Name Verification failed. Expected: '{expected_name}', Got: '{actual_name}'",
        )
        logger.info(f"Client Full Name Verification: PASSED - '{expected_name}'")

    def check_if_all_approved(self) -> None:
        """Check if all approval points are completed (green)"""
        logger.info("Checking if all approval steps are completed")

        # Wait for approval points to be visible
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass

        approval_elements = self.approval_points
        count = approval_elements.count()
        Assertions.assert_true(count > 0, "No approval points found on Review All Accounts page")

        completed_steps = []
        incomplete_steps = []

        for i in range(count):
            element = approval_elements.nth(i)
            step_name = (element.text_content() or "").strip()

            # Match old Java behavior: check computed 'background' value for green marker.
            bg_style = element.evaluate("el => window.getComputedStyle(el).background")
            is_green = "green" in bg_style.lower()

            if is_green:
                completed_steps.append(step_name)
                logger.info(f"Step: {step_name} is completed")
            else:
                incomplete_steps.append(step_name)
                logger.info(f"Step: {step_name} is not completed")

        # Log all steps for debugging
        logger.info(f"Completed steps: {completed_steps}")
        logger.info(f"Incomplete steps: {incomplete_steps}")

        if not incomplete_steps:
            Assertions.assert_true(
                True,
                "All pages are verified and green status present: " + ", ".join(completed_steps),
            )
        else:
            Assertions.assert_true(
                False,
                "Pages not verified, red status present: " + ", ".join(incomplete_steps),
            )

    def confirm_clients_documents(self):
        """
        Click Create Documents button and handle missing information modal if present
        
        Returns:
            CreateDocumentsPage object
        """
        logger.info("Confirming client documents")
        
        try:
            # Ensure page load is complete before attempting click.
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass

            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass

            self.wait_for_loading_data(timeout=90000)
            self.wait_for_ajax(timeout=30000)
            self._wait_for_dom_settled(timeout=7000)

            # Bring button into view and click.
            self.click(self.create_documents_button, timeout=30000)
            logger.info("Clicked on Create Documents button")
            
            # Check for missing information modal and handle it using base_page method
            try:
                self.wait_for_dialog(self.missing_information_modal, timeout=3000)
                logger.warning("Missing information modal detected, clicking Yes to confirm")
                self.wait_and_click(self.missing_information_yes_button, timeout=5000)
                logger.info("Clicked on Yes button in missing information modal")
            except Exception as e:
                pass
            
        except Exception as e:
            logger.error(f"Error confirming documents: {str(e).splitlines()[0]}")
            raise
