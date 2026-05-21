from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions

logger = get_allure_logger(__name__)


class LookupPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.switch_id_link: Locator = page.get_by_role("link", name="Switch ID")
        self.lookup_user_id_input: Locator = page.locator(
            "input[name='ctl00$cphContentArea$txtLookUp']"
        )
        self.find_button: Locator = page.get_by_role("button", name="Find", exact=True)
        self.select_role_continue_button: Locator = page.get_by_role("button", name="Continue")
        self.results_row: Locator = page.locator("//td[normalize-space(text())='Agent']/parent::tr")
        self.sso_user_link: Locator = page.locator("//td[normalize-space(text())='Agent']/parent::tr/td[6]/a[1]")
        self.name_user_link: Locator = page.locator("//td[normalize-space(text())='Agent']/parent::tr/td[2]/a[1]")
        self.broker_dealer_row: Locator = page.locator("//td[normalize-space(text())='Broker Dealer']/parent::tr")
        self.broker_dealer_sso_link: Locator = page.locator(
            "//td[normalize-space(text())='Broker Dealer']/parent::tr/td[6]/a"
        )

    def click_broker_dealer_result(self, timeout: int = 30000) -> None:
        """Click the SSO link in the Broker Dealer row."""
        logger.info("Clicking SSO link for Broker Dealer")
        self._dismiss_cookie_popup()
        # Ensure Broker Dealer row is visible before clicking
        self.broker_dealer_row.first.wait_for(state="visible", timeout=timeout)
        logger.attach_screenshot(self.page, name="Before_Broker_Dealer_Click")
        bd_link = self.broker_dealer_sso_link.first
        bd_link.scroll_into_view_if_needed()
        bd_link.highlight()
        logger.info(f"Broker Dealer link text: {bd_link.inner_text()}")
        bd_link.click(timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        logger.attach_screenshot(self.page, name="After_Broker_Dealer_Click")
        logger.info(f"Broker Dealer SSO link clicked successfully. URL: {self.page.url}")

    def choose_role(self, timeout: int = 5000) -> None:
        """Click Continue on the role selection page if displayed."""
        if not self.is_visible(self.select_role_continue_button, timeout=timeout):
            logger.info("Role selection page not displayed, skipping role selection")
            return
        logger.info("Role selection page detected, clicking Continue")
        self.click(self.select_role_continue_button, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info("Continue clicked, role selection completed")

    def impersonate_agent(self, user_id: str, timeout: int = 30000) -> None:
        """Open Switch ID, search for the user, and select the agent result."""
        self.open_switch_id(timeout=timeout)
        self.search_user_id(user_id, timeout=timeout)
        self.click_agent_result(timeout=timeout)

    def impersonate_broker_dealer(self, user_id: str, timeout: int = 30000) -> None:
        """Open Switch ID, search for the user, and click the Broker Dealer link."""
        self.open_switch_id(timeout=timeout)
        self.search_user_id(user_id, timeout=timeout, wait_locator=self.broker_dealer_row.first)
        self.click_broker_dealer_result(timeout=timeout)

    def open_switch_id(self, timeout: int = 30000) -> None:
        """Click on the Switch ID link to open the lookup page."""
        Assertions.assert_true(
            self.is_visible(self.switch_id_link, timeout=timeout),
            "Switch ID is not present on admin login page"
        )
        logger.info("Opening Switch ID lookup")
        self.click(self.switch_id_link, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        # Dismiss cookie popup if it reappears (common in new browser contexts)
        self._dismiss_cookie_popup()
        self.wait_for_element(self.lookup_user_id_input, timeout=timeout)

    def _dismiss_cookie_popup(self, timeout: int = 2000) -> None:
        """Dismiss cookie consent popups. Delegates to BasePage.close_chat_popups()."""
        self.close_chat_popups()

    def search_user_id(self, user_id: str, timeout: int = 30000, wait_locator: Locator = None) -> None:
        """Enter a user ID in the lookup field and click Find."""
        logger.info(f"Searching for agent user id: {user_id}")
        self._dismiss_cookie_popup()
        self.fill(self.lookup_user_id_input, user_id, timeout=timeout)
        self._dismiss_cookie_popup()
        # Retry Find button click in case cookie popup blocks it
        for attempt in range(3):
            try:
                self.click(self.find_button, timeout=10000)
                break
            except Exception:
                logger.warning(f"Find button click attempt {attempt + 1} failed, retrying...")
                self._dismiss_cookie_popup()
                if attempt == 2:
                    raise
        self.wait_for_spinner_to_disappear()
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self._dismiss_cookie_popup()
        target = wait_locator if wait_locator else self.results_row.first
        self.wait_for_element(target, state="visible", timeout=timeout)

    def click_agent_result(self, timeout: int = 30000) -> None:
        """Click on the agent row in the lookup results."""
        logger.info("Selecting agent from lookup results")
        sso_visible = self.is_visible(self.sso_user_link.first, timeout=timeout)
        name_visible = self.is_visible(self.name_user_link.first, timeout=timeout)

        if sso_visible:
            target = self.sso_user_link.first
        elif name_visible:
            target = self.name_user_link.first
        else:
            raise RuntimeError("No visible agent result link found after search")

        target.scroll_into_view_if_needed()
        self.click(target, timeout=timeout, no_wait_after=True)
        logger.info("Switching to agent — success")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
