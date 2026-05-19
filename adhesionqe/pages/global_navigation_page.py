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

        # Global search bar
        self.global_search_input: Locator = page.locator("input#global-search")
        # Search results dropdown container
        self.global_search_results: Locator = page.locator("div#search-results")
        # Clients section within search results
        self.global_search_clients_section: Locator = page.locator(
            "div#search-results generic:has-text('CLIENTS')"
        )
        self.global_search_clients_table: Locator = page.locator("table#clients-results")
        # Accounts section within search results
        self.global_search_accounts_section: Locator = page.locator(
            "div#search-results generic:has-text('ACCOUNTS')"
        )
        self.global_search_accounts_table: Locator = page.locator("table#accounts-results")
        self.global_search_accounts_results: Locator = page.locator(
            "table#accounts-results tbody tr"
        )

        # Action menu items
        self.action_menu_items: Locator = page.locator("div#divActionMenuItems")
        self.action_lock_unlock: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Lock/Unlock')"
        )
        self.action_cash_management: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Cash Management')"
        )
        self.action_rebalancing: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Rebalancing')"
        )
        self.action_change_allocation: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Change Allocation')"
        )
        self.action_change_settings: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Change Settings')"
        )
        self.action_create_proposal: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Create/Edit Proposal')"
        )
        self.action_unenroll: Locator = page.locator(
            "div#divActionMenuItems div:has-text('Unenroll')"
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

    def search(self, query: str) -> None:
        """Type a search query into the global search bar."""
        logger.info(f"Searching for: {query}")
        self.click(self.global_search_input)
        self.fill(self.global_search_input, query)

    def clear_search(self) -> None:
        """Clear the search input field."""
        logger.info("Clearing global search")
        self.global_search_input.clear()

    # -----------------
    # Action menu helpers
    # -----------------
    def click_action_item(self, action_name: str) -> None:
        """Click an action menu item by name."""
        logger.info(f"Clicking action: {action_name}")
        action_map = {
            "Lock/Unlock": self.action_lock_unlock,
            "Cash Management": self.action_cash_management,
            "Rebalancing": self.action_rebalancing,
            "Change Allocation": self.action_change_allocation,
            "Change Settings": self.action_change_settings,
            "Create/Edit Proposal": self.action_create_proposal,
            "Unenroll": self.action_unenroll,
        }
        locator = action_map.get(action_name)
        if locator:
            self.click(locator)
        else:
            raise ValueError(f"Unknown action: {action_name}")

    def click_lock_unlock(self) -> None:
        logger.info("Clicking Lock/Unlock action")
        self.click(self.action_lock_unlock)

    def click_cash_management(self) -> None:
        logger.info("Clicking Cash Management action")
        self.click(self.action_cash_management)

    def click_rebalancing(self) -> None:
        logger.info("Clicking Rebalancing action")
        self.click(self.action_rebalancing)

    def click_change_allocation(self) -> None:
        logger.info("Clicking Change Allocation action")
        self.click(self.action_change_allocation)

    def click_change_settings(self) -> None:
        logger.info("Clicking Change Settings action")
        self.click(self.action_change_settings)

    def click_create_proposal(self) -> None:
        logger.info("Clicking Create/Edit Proposal action")
        self.click(self.action_create_proposal)

    def click_unenroll(self) -> None:
        logger.info("Clicking Unenroll action")
        self.click(self.action_unenroll)
