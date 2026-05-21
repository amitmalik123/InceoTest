"""Search Work Item Page - BAW Search Work Item functionality"""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class SearchWorkItemPage(BasePage):
    """Search Work Item Page class for searching work items"""

    PAGE_NAME = "Search Work Item Page"

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        # Locators for Search Work Item page
        # External ID textbox is inside an iframe with title "Coach"
        self.external_id_textbox: Locator = page.locator("iframe[title=\"Coach\"]").content_frame.get_by_role("textbox", name="External ID")
        self.search_button: Locator = page.locator("iframe[title=\"Coach\"]").content_frame.get_by_role("button", name="Search")
        self.details_link: Locator = page.locator("iframe[title=\"Coach\"]").content_frame.locator("xpath=//a[text()='Details' and not(@title)][1]")
        self.parent_b_number: Locator = page.locator("iframe[title=\"Coach\"]").content_frame.locator("xpath=//div[@data-viewid='ParentBNumberCell' and starts-with(text(),'B')]")
        # Diagnostic locator: ANY ParentBNumberCell regardless of content (for empty-cell debugging)
        self.parent_b_number_cell_any: Locator = page.locator("iframe[title=\"Coach\"]").content_frame.locator("xpath=//div[@data-viewid='ParentBNumberCell']")

    def enter_external_id_and_click_search(self, external_id: str) -> None:
        logger.info(f"Entering external ID: {external_id}")
        self.fill(self.external_id_textbox, external_id, timeout=30000)
        logger.info(f"Entered external ID: {external_id}")
        self.click_search_button()
        logger.info("Search completed with external ID")

    def click_search_button(self) -> None:
        """
        Click the search button on Search Work Item page.
        
        Mirrors Java implementation: waitForElementToBeVisible -> click
        """
        with logger.step("Click on search button", page=self.page):
            logger.info("Clicking search button")
            
            # Wait for search button to be visible
            self.search_button.wait_for(state="visible", timeout=30000)
            logger.info("Search button is visible")
            
            # Click the search button
            self.click(self.search_button)
            logger.info("Search button clicked successfully")

    def fetch_parent_b_number(self) -> str:
        """
        Fetch the parent B number from search results.

        BAW takes time to populate Parent B in the search results row after
        HRC submit. We re-run the search (NOT click Details, which navigates
        away from the results) until the Parent B cell appears.

        Raises:
            ValueError: If parent B number is not found or is empty
        """
        with logger.step("Fetch parent B number", page=self.page):
            logger.info("Fetching parent B number from search results")

            # Wait for page loading to complete
            self.wait_for_load_state("domcontentloaded", timeout=30000)
            self.wait_for_loading_data()

            max_retries = 4
            last_error: Exception | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    # Make sure search results are rendered
                    self.details_link.wait_for(state="visible", timeout=30000)
                    logger.info(f"Details link visible (attempt {attempt}/{max_retries})")

                    # Wait for parent B cell to appear in the same results row
                    self.parent_b_number.wait_for(state="visible", timeout=15000)
                    logger.info("Parent B number element is visible in DOM")
                    break
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Parent B number not yet populated (attempt {attempt}/{max_retries}), "
                            f"re-running search after short wait..."
                        )
                        # Wait for BAW to process, then re-run search to refresh the row
                        self.wait_for_timeout(5000)
                        try:
                            self.click_search_button()
                            self.wait_for_load_state("domcontentloaded", timeout=30000)
                            self.wait_for_loading_data()
                        except Exception as search_err:
                            logger.warning(f"Re-running search failed: {search_err}")
                    else:
                        logger.error(
                            f"Parent B number element not found after {max_retries} attempts: {e}"
                        )
                        # Diagnostic: log what's actually in the ParentBNumberCell column
                        try:
                            cell_count = self.parent_b_number_cell_any.count()
                            logger.error(f"[DIAG] Found {cell_count} ParentBNumberCell element(s) in results")
                            for idx in range(min(cell_count, 5)):
                                try:
                                    cell_text = self.parent_b_number_cell_any.nth(idx).inner_text(timeout=5000)
                                    logger.error(f"[DIAG] ParentBNumberCell[{idx}] text: '{cell_text}'")
                                except Exception as diag_err:
                                    logger.error(f"[DIAG] Could not read ParentBNumberCell[{idx}]: {diag_err}")
                            if cell_count == 0:
                                try:
                                    details_count = self.details_link.count()
                                    logger.error(f"[DIAG] Details link count in results: {details_count}")
                                except Exception:
                                    pass
                        except Exception as diag_err:
                            logger.error(f"[DIAG] ParentBNumberCell diagnostic failed: {diag_err}")
                        raise ValueError("Parent B# not found")

            # Scroll into view
            try:
                self.parent_b_number.scroll_into_view_if_needed()
                logger.info("Parent B number element scrolled into view")
            except Exception:
                pass

            # Get the text of parent B number
            b_num = self.get_text(self.parent_b_number, timeout=30000)

            if not b_num or b_num.strip() == "":
                logger.error("Parent B number is empty or not generated")
                raise ValueError("Parent B# not found")

            logger.info(f"Fetched parent B number: {b_num}")

            return b_num.strip()
