"""
Switch ID Page Object Model for Proposals application.
Handles role switching and user ID selection operations.
"""

import logging
from playwright.sync_api import Locator, Page

from ..base_page import BasePage
from pages.proposal.helper_functions import select_if_visible

logger = logging.getLogger(__name__)


class SwitchIDPage(BasePage):
    """Switch ID page for role and user selection."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.id_input: Locator = page.locator("#ctl00_cphContentArea_txtLookUp")
        self.role_radio_button: Locator = page.locator("#radAgents")
        self.continue_button: Locator = page.get_by_role("button", name="Continue")
        self.switch_id_link: Locator = page.get_by_role("link", name="Switch ID")

    def goto_switch_id_page(self) -> None:
        """Navigate to the Switch ID page."""
        # Increase timeout to 60s for Step-Up MFA redirect navigation
        self.switch_id_link.click(timeout=60000)
        self.id_input.wait_for(state="visible", timeout=60000)

    def select_id(self, advisor_id: str) -> None:
        """
        Switch ID to the specified advisor.

        Args:
            advisor_id: The advisor ID to switch to.
        """
        self.goto_switch_id_page()
        self.id_input.click()
        self.id_input.fill(advisor_id)
        self.id_input.press("Enter")
        
        # Create user_id_link dynamically with the actual advisor_id passed in
        user_id_link: Locator = self.page.get_by_role("link", name=advisor_id)
        user_id_link.wait_for(state="visible", timeout=60000)
        user_id_link.click(timeout=60000)
        
        select_if_visible(self.role_radio_button)
        select_if_visible(self.continue_button)
        self.switch_id_link.wait_for(state="visible", timeout=60000)
