from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class LookupPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.switch_id_link: Locator = page.locator("//ul[@id='userMenu']/li/a[text()='Switch ID']")
        self.lookup_user_id_input: Locator = page.locator(
            "//input[@name='ctl00$cphContentArea$txtLookUp']"
            " | //input[@id='ctl00_cphContentArea_txtLookUp']"
            " | //input[contains(@name,'txtLookUp')]"
            " | //input[contains(@id,'txtLookUp')]"
        ).first
        self.find_button: Locator = page.locator(
            "#ctl00_cphContentArea_btnLookUp, "
            "button[id*='btnLookUp'], "
            "input[id*='btnLookUp'], "
            "button:has-text('Find')"
        ).first
        self.results_row: Locator = page.locator("//td[text()='Agent']/parent::tr")
        self.sso_user_link: Locator = page.locator("//td[text()='Agent']/parent::tr/td[6]/a[1]")
        self.name_user_link: Locator = page.locator("//td[text()='Agent']/parent::tr/td[2]/a[1]")

    def open_switch_id(self, timeout: int = 10000) -> None:
        logger.info("Opening Switch ID lookup")
        self.click(self.switch_id_link, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_element(self.lookup_user_id_input, timeout=timeout)

    def search_user_id(self, user_id: str, timeout: int = 10000) -> None:
        logger.info(f"Searching for agent user id: {user_id}")
        self.fill(self.lookup_user_id_input, user_id, timeout=timeout)
        self.click(self.find_button, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_element(self.results_row.first, state="visible", timeout=timeout)

    def click_agent_result(self, timeout: int = 10000) -> None:
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
        self.click(target, timeout=timeout)
        logger.info("Switching to agent Pass!")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

    def impersonate_agent(self, user_id: str, timeout: int = 10000) -> None:
        self.open_switch_id(timeout=timeout)
        self.search_user_id(user_id, timeout=timeout)
        self.click_agent_result(timeout=timeout)
