"""APro Proposal History/Actions step (wizard-7)."""

import shutil
from pathlib import Path

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalHistoryPage(BasePage):
    """Page object for APro proposal History/Actions step (wizard-7).

    Handles history details display, actions dropdown, and proposal deletion.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 8 (History/Actions) container
        self.step_history_panel: Locator = page.locator("#proposal-wizard-7")

        # History details display
        self.history_client_name: Locator = page.locator("#history-client-name")
        self.history_strategy: Locator = page.locator("#history-strategy")
        self.history_composite: Locator = page.locator("#history-composite")
        self.history_investment_amount: Locator = page.locator("#history-investment-amount")
        self.history_current_status: Locator = page.locator("#history-current-status")

        # Actions dropdown and items
        self.history_actions_button: Locator = page.locator("#btnHistoryActions")
        self.history_actions_items: Locator = page.locator("#historyActionsItems")
        self.history_action_enroll: Locator = page.locator("#action-enroll")
        self.history_action_view_email: Locator = page.locator("#action-view-email")
        self.history_action_copy: Locator = page.locator("#action-copy")
        self.history_action_delete: Locator = page.locator("#action-delete")
        self.confirm_delete_button: Locator = page.locator(
            "button.k-button.k-primary", has_text="Delete"
        )

        # Copy Proposal modal
        self.copy_proposal_modal: Locator = page.locator("#copy-proposal-dialog")
        self.copy_proposal_confirm_button: Locator = page.locator(
            ".k-dialog-actions button", has_text="Copy"
        )

    def wait_for_history_step(self, timeout: int = 10000) -> None:
        """Wait for the History/Actions (wizard step 8, proposal-wizard-7) to be visible."""
        logger.info("Waiting for History (step 8) to be visible")
        self.wait_for_element(self.step_history_panel, state="visible", timeout=timeout)

    def get_history_details(self) -> dict:
        """Extract currently visible history details from the panel.

        Returns:
            Dict with keys: client, strategy, composite, investment, status
        """
        logger.info("Extracting history details from DOM")

        details = {
            "client": self._get_element_text(self.history_client_name),
            "strategy": self._get_element_text(self.history_strategy),
            "composite": self._get_element_text(self.history_composite),
            "investment": self._get_element_text(self.history_investment_amount),
            "status": self._get_element_text(self.history_current_status),
        }

        logger.info(f"History details: {details}")
        return details

    def _get_element_text(self, locator: Locator) -> str:
        """Safely get text from an element."""
        try:
            return locator.inner_text().strip()
        except Exception:
            return ""

    def wait_for_history_details(self, timeout: int = 15000) -> dict:
        """Wait for history details to populate, then return them.

        Waits for the step to be visible and details to be populated (all fields non-empty).

        Args:
            timeout: Wait timeout in ms

        Returns:
            Dict of history details
        """
        logger.info("Waiting for History/Actions details to populate")

        self.wait_for_history_step(timeout=timeout)

        # Wait for all fields to have actual content (not just '--' or empty)
        max_attempts = 60
        attempt = 0

        while attempt < max_attempts:
            details = self.get_history_details()

            # Check if all required fields have actual data (not dashes or empty)
            all_populated = (
                details.get("client")
                and details["client"] != "--"
                and details["client"] != ""
                and details.get("strategy")
                and details["strategy"] != "--"
                and details["strategy"] != ""
                and details.get("composite")
                and details["composite"] != "--"
                and details["composite"] != ""
                and details.get("investment")
                and details["investment"] != "--"
                and details["investment"] != ""
                and details.get("status")
                and details["status"] != "--"
                and details["status"] != ""
            )

            if all_populated:
                return details

            if attempt < max_attempts - 1:
                self.page.wait_for_timeout(250)  # Wait 250ms between attempts
            attempt += 1

        # Timeout reached - log what we got
        logger.error(
            f"History details not fully populated after {max_attempts} attempts (15s total)"
        )
        logger.error(f"Got: {details}")
        return details

    def open_history_actions(self) -> None:
        """Open the History Actions dropdown."""
        logger.info("Opening History Actions dropdown")
        self.click(self.history_actions_button)
        self.wait_for_element(self.history_actions_items, state="visible", timeout=5000)

    def click_history_action(self, action: str) -> None:
        """Click a named action from the History Actions dropdown.

        Args:
            action: Action name (e.g., "Enroll", "ViewEmail", "Copy", "Delete")
        """
        logger.info(f"Clicking history action: {action}")

        self.open_history_actions()

        # Map action names to their ID selectors
        action_map = {
            "enroll": self.history_action_enroll,
            "view/email proposal": self.history_action_view_email,
            "viewemail": self.history_action_view_email,
            "copy": self.history_action_copy,
            "delete": self.history_action_delete,
        }

        # Find the action item by ID or partial match
        action_item = None
        action_lower = action.lower()

        # Try direct map first
        if action_lower in action_map:
            action_item = action_map[action_lower]
        else:
            # Try partial matches
            for key, locator in action_map.items():
                if key in action_lower or action_lower in key:
                    action_item = locator
                    break

        if not action_item:
            # Fallback to text search
            action_item = self.history_actions_items.locator(f":text('{action}')").first

        try:
            # Wait for the item to be visible AND clickable
            action_item.wait_for(state="visible", timeout=5000)
            self.page.wait_for_timeout(300)  # Extra wait for UI to be fully interactive
            self.click(action_item)
            logger.info(f"Successfully clicked action: {action}")
        except Exception as exc:
            logger.error(f"Failed to click action '{action}': {exc}")
            raise

    def delete_selected_proposal(self, timeout: int = 10000) -> None:
        """Delete the currently selected proposal.

        Opens the actions menu, clicks Delete, confirms in the confirmation dialog,
        and cleans up the tmp folder.

        Args:
            timeout: Operation timeout in ms
        """
        logger.info("Deleting selected proposal")

        # Click Delete from actions menu
        self.click_history_action("Delete")

        # Confirm deletion
        self.confirm_delete_button.wait_for(state="visible", timeout=timeout)
        logger.info("Confirmed proposal deletion")
        self.click(self.confirm_delete_button)

        # Clean up tmp folder
        tmp_dir = Path("tmp")
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
            logger.info("Cleared tmp folder")

    def enroll_account(self) -> None:
        """Click the 'Enroll Account' action from the History Actions dropdown."""
        logger.info("Enrolling account")
        self.click_history_action("Enroll")

    def view_email_proposal(self) -> None:
        """Click the 'View/Email Proposal' action from the History Actions dropdown."""
        logger.info("Viewing/Emailing proposal")
        self.click_history_action("ViewEmail")

    def copy_proposal(self) -> None:
        """Click the 'Copy Proposal' action from the History Actions dropdown."""
        logger.info("Copying proposal")
        self.click_history_action("Copy")

    def click_copy_proposal(self) -> None:
        """Alias for copy_proposal(). Click the 'Copy Proposal' action."""
        logger.info("Clicking Copy Proposal action")
        self.copy_proposal()

    def accept_copy_proposal_confirmation(self, timeout: int = 10000) -> None:
        """Accept the Copy Proposal confirmation modal.

        Waits for the modal to appear and clicks the Copy button to confirm.

        Args:
            timeout: Wait timeout in ms
        """
        logger.info("Accepting Copy Proposal confirmation modal")
        self.wait_for_element(self.copy_proposal_modal, state="visible", timeout=timeout)
        self.click(self.copy_proposal_confirm_button)
        logger.info("Copy Proposal confirmed")
