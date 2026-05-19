"""Base page object for pages with smart filter functionality.

Provides generic filter selectors and helpers that work across all pages
with a similar left-side filter panel structure (e.g., Prospects, Accounts).

Pages should inherit from this class and can override or add page-specific filter methods.
"""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class BaseSmartFilterPage(BasePage):
    """Base POM for pages with smart filter functionality.

    Provides generic filter selectors and helpers that work across all pages
    with similar left-side filter panel structure.

    Locators:
      - filter_panel: The main smart filter panel container
      - filter_sections: All filter section containers
      - filter_checkboxes: All filter checkbox inputs
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Generic smart filter selectors (work on any page with this structure)
        self.filter_panel: Locator = page.locator(".smart-filter-panel")
        self.filter_sections: Locator = page.locator(".smart-filter-panel .section")
        self.filter_checkboxes: Locator = page.locator(".smart-filter-panel input[type='checkbox']")

    def click_filter_section(self, section_name: str) -> None:
        """Toggle a filter section open/closed by section title.

        Args:
            section_name: The exact text of the section title (e.g., "Status", "Investment Amount")
        """
        logger.info(f"Toggling filter section: {section_name}")
        section = self.filter_sections.filter(has=self.page.get_by_text(section_name, exact=True))
        section.locator(".title").click()

    def select_filter_by_text(self, option_text: str) -> None:
        """Select a filter option by its label text.

        Args:
            option_text: The exact text of the filter option label
        """
        logger.info(f"Selecting filter option: {option_text}")
        # Click the label to toggle the associated checkbox
        label = self.filter_panel.locator(f"label:has-text('{option_text}')")
        label.click()

    def deselect_filter_by_text(self, option_text: str) -> None:
        """Deselect a filter option by its label text.

        Args:
            option_text: The exact text of the filter option label
        """
        logger.info(f"Deselecting filter option: {option_text}")
        # Click the label to toggle the associated checkbox
        label = self.filter_panel.locator(f"label:has-text('{option_text}')")
        label.click()

    def clear_all_filters(self) -> None:
        """Clear all selected filters."""
        logger.info("Clearing all filters")
        # Find all checked checkboxes and click their associated labels
        checked_checkboxes = self.filter_panel.locator("input[type='checkbox']:checked")
        count = checked_checkboxes.count()
        logger.info(f"Found {count} checked filters to clear")

        # Click labels for each checked checkbox (iterate in reverse to avoid stale references)
        for i in range(count - 1, -1, -1):
            checkbox = checked_checkboxes.nth(i)
            checkbox_id = checkbox.get_attribute("id")
            label = self.filter_panel.locator(f"label[for='{checkbox_id}']")
            label.click()
            logger.info(f"Cleared filter with ID: {checkbox_id}")

    def get_active_filter_count(self) -> int:
        """Get the number of currently active filters.

        Returns:
            int: Count of checked filter checkboxes
        """
        count = self.page.locator(".smart-filter-panel input[type='checkbox']:checked").count()
        logger.info(f"Active filter count: {count}")
        return count

    def is_filter_selected(self, option_text: str) -> bool:
        """Check if a specific filter option is currently selected.

        Args:
            option_text: The exact text of the filter option label

        Returns:
            bool: True if the filter is checked, False otherwise
        """
        label = self.filter_panel.locator(f"label:has-text('{option_text}')")
        checkbox_id = label.get_attribute("for")
        # Find the preceding input checkbox and check if it's checked
        checkbox = self.filter_panel.locator(f"input[type='checkbox'][id='{checkbox_id}']")
        is_checked = checkbox.is_checked()
        logger.info(f"Filter '{option_text}' is selected: {is_checked}")
        return is_checked

    def wait_for_filter_panel(self, timeout: int = 10000) -> None:
        """Wait for the filter panel to be visible.

        Args:
            timeout: Timeout in milliseconds
        """
        logger.info("Waiting for filter panel to be visible")
        self.wait_for_element(self.filter_panel, state="visible", timeout=timeout)

    def click_export_button(self):
        """Click the export button.

        Note: The caller should use DownloadManager to handle the download.
        """
        logger.info("Clicking export button")
        export_button = self.page.locator("#btnGridExport")
        export_button.click()

    def is_export_button_visible(self) -> bool:
        """Check if the export button is visible.

        Waits briefly for the button to become visible (e.g., after grid loads).

        Returns:
            bool: True if export button is visible, False otherwise
        """
        export_button = self.page.locator("#btnGridExport")
        try:
            # Wait for element to be visible up to 5 seconds
            export_button.wait_for(state="visible", timeout=5000)
            logger.info("Export button visible: True")
            return True
        except Exception as e:
            logger.info(f"Export button visible: False ({str(e)})")
            return False

    def get_checked_filter_count(self) -> int:
        """Get the count of currently checked filter checkboxes (per spec §2.5).

        This method is useful for asserting "no filters active" without naming each one.

        Returns:
            int: Count of currently checked filter checkboxes
        """
        count = self.page.locator(".smart-filter-panel input[type='checkbox']:checked").count()
        logger.info(f"Checked filter count: {count}")
        return count
