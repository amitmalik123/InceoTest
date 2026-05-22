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

        # Navigation Links
        self.logout_link: Locator = page.get_by_role("link", name="Logout")
        self.account_wizard_link: Locator = page.get_by_role("link", name="Account Wizard")
        self.clients_link: Locator = page.get_by_role("link", name="Clients")
        self.create_new_client: Locator = page.get_by_role("button", name="Go").first
        
        # Portfolio Engine Navigation
        self.investments_link: Locator = page.get_by_role("link", name="Investments")
        self.portfolio_engine_link: Locator = page.get_by_role("link", name="PortfolioEngine", exact=True)
        self.launch_portfolio_engine_img: Locator = page.get_by_role("img", name="Launch Portfolio Engine").first

        # Login Page Elements
        self.username_textbox: Locator = page.get_by_role("textbox", name="Username")

        # Client Management Elements
        self.client_search_input: Locator = page.get_by_role("textbox", name="client_search_input").or_(
            page.locator("#client_search_input")
        )
        self.search_button: Locator = page.get_by_role("button", name="search").or_(
            page.locator("#searchbutton")
        )
        self.no_results_message: Locator = page.get_by_text("No search results were found")
        self.client_grid_cells: Locator = page.locator(
            'td[role="gridcell"][aria-describedby="ClientListGrid_clientName"]'
        )
        self.delete_client_link: Locator = page.locator("#ctl00_cphContentArea_lnkDeleteClient")
        self.new_client_experience_decline: Locator = page.get_by_role("button", name="No, Thank You")
        self.delete_confirmation_text: Locator = page.get_by_text("There are two ways to get started")

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
            client_name: The name of the client to search for (format: "FirstName LastName")
        """
        self.clients_link.click()
        self.page.wait_for_load_state()
        
        # Decline new client experience if it appears
        try:
            self.new_client_experience_decline.click(timeout=1000)
        except Exception:
            pass  # Not always present
        
        # Fill search input and search
        self.client_search_input.fill(client_name)
        self.search_button.click()

    def delete_client(self) -> None:
        """
        Click the delete client link, accept the JS confirm dialog,
        and wait for the redirect to the empty-client confirmation page.
        Must be called after selecting a client.
        """
        logger.debug("Clicking delete client link")
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.delete_client_link.click()
        self.delete_confirmation_text.wait_for(state="visible")
