from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AccountApprovalPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.account_approval_tab: Locator = page.get_by_role(
            "link", name="Account Approval"
        )
        self.client_search_input: Locator = page.locator("#client_search_input")
        self.search_go_button: Locator = page.locator("#searchbutton")
        self.readme_checkbox: Locator = page.locator("input#readme")
        self.approve_button: Locator = page.locator("input#approve")
        self.reject_button: Locator = page.locator("input#reject")
        self.cancel_button: Locator = page.locator("input#cancel")
        self.done_button: Locator = page.locator("input#done")

    def click_account_approval_tab(self, timeout: int = 30000) -> None:
        """Click the Account Approval tab in the main menu."""
        logger.info("Clicking Account Approval tab")
        self.click(self.account_approval_tab, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        logger.info("Account Approval tab clicked successfully")

    def search_client_and_submit(self, client_name: str, timeout: int = 30000) -> None:
        """Search for client in BD Approval list, retry up to 3 times, and click the approval request."""
        client_link = self.page.locator("td a").filter(has_text=client_name).first

        for attempt in range(1, 4):
            logger.info(f"Search attempt {attempt}/3 for client: {client_name}")
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            self.client_search_input.fill("")
            self.fill(self.client_search_input, client_name, timeout=timeout)
            self.click(self.search_go_button, timeout=timeout)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            self.page.wait_for_timeout(3000)

            try:
                client_link.wait_for(state="visible", timeout=15000)
                logger.info(f"Client '{client_name}' found — clicking approval request")
                self.click(client_link, timeout=timeout)
                self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
                return
            except Exception:
                logger.warning(f"Client not found on attempt {attempt}")
                if attempt < 3:
                    self.page.reload(wait_until="domcontentloaded", timeout=timeout)

        raise ValueError(f"Client '{client_name}' not found in BD Approval list after 3 attempts")

    def approve_or_reject_account(self, action: str, timeout: int = 30000) -> None:
        """Approve, Reject, or Cancel the account.

        For Approve / Reject the readme checkbox is checked first.
        For Cancel the checkbox is skipped.
        """
        if action in ("Approve", "Reject"):
            logger.info("Clicking readme checkbox")
            self.click(self.readme_checkbox, timeout=timeout)

        button_map = {
            "Approve": self.approve_button,
            "Reject": self.reject_button,
            "Cancel": self.cancel_button,
        }
        button = button_map.get(action)
        if button is None:
            raise ValueError(f"Unknown action '{action}'. Expected: Approve, Reject, or Cancel")

        logger.info(f"Clicking {action} button")
        self.click(button, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

        if action in ("Approve", "Reject"):
            logger.info("Clicking Done button")
            self.click(self.done_button, timeout=timeout)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

        logger.attach_screenshot(self.page, name=f"Account_{action}")
        logger.info(f"Account {action} action completed")
