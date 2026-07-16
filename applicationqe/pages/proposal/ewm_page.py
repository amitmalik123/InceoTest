"""
EWM Page Object Model for Proposals application.
Handles navigation and logout operations on the eWM home page.
"""

import logging
from playwright.sync_api import Locator, Page

from ..base_page import BasePage

logger = logging.getLogger(__name__)


class EwmPage(BasePage):
    """EWM page with navigation and logout functionality."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.ewm_root = self.active_root()

        # Navigation Links
        self.logout_link: Locator = self.ewm_root.get_by_role("link", name="Logout")
        self.account_wizard_link: Locator = self.ewm_root.get_by_role("link", name="Account Wizard")
        # Filter clients link to avoid strict mode violation (multiple elements match "Clients" text)
        self.clients_link: Locator = self.ewm_root.locator(
            'a[role="link"]:has-text("Clients")[href*="/Clients/ClientList"]'
        )
        self.investments_link: Locator = self.ewm_root.get_by_role("link", name="Investments")
        # Legacy (test11/silo/prod): sidebar link with no space, followed by a Launch img
        self.portfolio_engine_link: Locator = self.ewm_root.get_by_role("link", name="PortfolioEngine", exact=True)
        self.launch_portfolio_engine_img: Locator = self.ewm_root.locator('img[alt="Launch Portfolio Engine"]').first
        # Navbar (test01): button-styled link on the Investments page, navigates in same tab
        self.portfolio_engine_nav_button: Locator = self.ewm_root.get_by_role("link", name="Portfolio Engine", exact=True)
        self.create_new_client: Locator = self.ewm_root.locator("#ctl00_cphContentArea_Button1")

        # Login Page Elements
        # EXCEPTION: stays on bare page — used to detect post-logout redirect to login page,
        # which is outside the iframe
        self.username_textbox: Locator = page.get_by_role("textbox", name="Username")

        # Client Management Elements
        self.client_search_input: Locator = self.ewm_root.get_by_role("textbox", name="client_search_input").or_(
            self.ewm_root.locator("#client_search_input")
        )
        self.search_button: Locator = self.ewm_root.get_by_role("button", name="search").or_(
            self.ewm_root.locator("#searchbutton")
        )
        self.no_results_message: Locator = self.ewm_root.get_by_text("No search results were found")
        self.client_grid_cells: Locator = self.ewm_root.locator(
            'td[role="gridcell"][aria-describedby="ClientListGrid_clientName"]'
        )
        self.new_client_experience_decline: Locator = self.ewm_root.get_by_role("button", name="No, Thank You")

    def logout(self) -> None:
        """
        Performs logout operation and waits for redirect to login page.
        """
        self.logout_link.click()
        self.username_textbox.wait_for(state="visible")

    def open_account_wizard(self) -> None:
        """
        Clicks the Account Wizard navigation link.
        """
        self.account_wizard_link.click()

    def search_for_client(self, client_name: str) -> None:
        """
        Search for a client by name.
        
        Args:
            client_name: The name of the client to search for
        """
        self.clients_link.click()
        # Wait for content to load (form_root-scoped for iframe compatibility)
        self.ewm_root.locator("body").wait_for(state="visible", timeout=15000)
        
        # Decline new client experience if it appears
        try:
            self.new_client_experience_decline.click(timeout=1000)
        except Exception:
            pass  # Not always present
        
        # Fill search input and search
        self.client_search_input.fill(client_name)
        self.search_button.click()