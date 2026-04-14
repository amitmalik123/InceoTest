"""APro Prospects List page."""

from playwright.sync_api import Locator, Page

from pages.base_smart_filter_page import BaseSmartFilterPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProspectsListPage(BaseSmartFilterPage):
    """Page object for the APro prospects list page.

    Locators:
      - actions_button: the button that opens the actions dropdown (id `btnMainActionButton`)
      - items_container: the dropdown container (id `items`)
      - create_prospect_item: the menu item text 'Create Prospect'
      - advisor_name_element: the advisor name display in the page header
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        self.actions_button: Locator = page.locator("#btnMainActionButton")
        self.items_container: Locator = page.locator("#items")
        self.create_prospect_item: Locator = page.get_by_text("Create Prospect", exact=True)
        self.advisor_name_element: Locator = page.locator("div.user div.name")

    def open_actions(self) -> None:
        """Open the actions dropdown."""
        logger.info("Opening APro actions dropdown")
        self.click(self.actions_button)

    def wait_for_items(self, timeout: int = 10000) -> None:
        """Wait for the actions items container to be visible."""
        logger.info("Waiting for actions items to be visible")
        self.wait_for_element(self.items_container, state="visible", timeout=timeout)

    def click_create_prospect(self) -> None:
        """Click the 'Create Prospect' item inside the actions dropdown."""
        logger.info("Clicking 'Create Prospect' in APro actions")
        # Ensure dropdown is open and items visible
        try:
            self.wait_for_items()
        except Exception:
            # Attempt to open then wait again
            self.open_actions()
            self.wait_for_items()

        self.click(self.create_prospect_item)

    def get_advisor_name(self) -> str:
        """Get the logged-in advisor name from the page header.

        Returns:
            str: The advisor name displayed in the page header
        """
        logger.info("Retrieving advisor name from page header")
        self.advisor_name_element.wait_for(state="visible", timeout=5000)
        advisor_name = self.advisor_name_element.inner_text().strip()
        logger.info(f"Retrieved advisor name: {advisor_name}")
        return advisor_name
