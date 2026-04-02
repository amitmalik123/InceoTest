from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class GlobalNavigationPage(BasePage):
    """Page object for the global navigation menu (when open).

    Provides locators and simple click helpers for every top-level
    navigation link present in the global navigation HTML.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Top-level links (use data-testid where available)
        self.dashboard_link: Locator = page.get_by_test_id("main-navigation-main-dashboard")
        self.client_households_link: Locator = page.get_by_test_id(
            "main-navigation-client-households"
        )
        self.accounts_link: Locator = page.get_by_test_id("main-navigation-accounts")
        self.allocations_link: Locator = page.get_by_test_id("main-navigation-allocations")

        # Strategist marketplace: toggle + submenu item
        self.strategist_marketplace: Locator = page.get_by_test_id(
            "main-navigation-strategist-marketplace"
        )
        self.strategists_link: Locator = page.get_by_test_id("main-navigation-strategists")

        # The visible button that opens the global navigation (hamburger/menu)
        self.nav_menu_trigger: Locator = page.locator("div.menu-trigger")

        # Research
        self.research_link: Locator = page.get_by_test_id("main-navigation-research")

        # Prospects (standard) and APro proposals (note: same testid used in markup for prospects)
        self.prospects_link: Locator = page.get_by_test_id("main-navigation-prospects")
        # APro-specific entry: prefer href-based locator (fallback to visible text if needed)
        self.proposals_apro_link: Locator = page.locator("a[href='/Proposals']")

        # Adhesion platform external link
        self.adhesion_platform_link: Locator = page.get_by_test_id(
            "main-navigation-adhesion-platform"
        )

    # -----------------
    # Click helpers
    # -----------------
    def click_dashboard(self) -> None:
        logger.info("Clicking Dashboard in global navigation")
        self.click(self.dashboard_link)

    def click_client_households(self) -> None:
        logger.info("Clicking Client Households in global navigation")
        self.click(self.client_households_link)

    def click_accounts(self) -> None:
        logger.info("Clicking Accounts in global navigation")
        self.click(self.accounts_link)

    def click_allocations(self) -> None:
        logger.info("Clicking Allocations in global navigation")
        self.click(self.allocations_link)

    def open_strategist_marketplace(self) -> None:
        logger.info("Opening Strategist Marketplace panel")
        self.click(self.strategist_marketplace)

    def click_strategists(self) -> None:
        logger.info("Clicking Strategists in Strategist Marketplace")
        self.click(self.strategists_link)

    def click_research(self) -> None:
        logger.info("Clicking Research in global navigation")
        self.click(self.research_link)

    def click_prospects(self) -> None:
        logger.info("Clicking Prospects in global navigation")
        self.click(self.prospects_link)

    def click_proposals_apro(self) -> None:
        logger.info("Clicking PROSPECTS (APro) in global navigation")
        self.click(self.proposals_apro_link)

    def click_adhesion_platform(self) -> None:
        logger.info("Clicking Adhesion Platform external link")
        self.click(self.adhesion_platform_link)

    def click_menu_trigger(self) -> None:
        """Open the global navigation by clicking the menu trigger (hamburger)."""
        logger.info("Clicking global navigation menu trigger")
        self.click(self.nav_menu_trigger)
