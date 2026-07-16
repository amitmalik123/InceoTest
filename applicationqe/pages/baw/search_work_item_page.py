"""Search Work Item Page - BAW Search Work Item functionality"""

from playwright.sync_api import Locator, Page

from locators.baw.search_work_item_locators import SearchWorkItemLocators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.wait_utils import WaitContext

logger = get_allure_logger(__name__)


class SearchWorkItemPage(BasePage):
    """Search Work Item Page class for searching work items"""

    PAGE_NAME = "Search Work Item Page"

    # Last-fetched parent B#. Used by the Excel reporter as a fallback when the
    # test fails before the step writes parent_b_number to context.
    last_parent_b_number: str = ""

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        # Locators for Search Work Item page
        # External ID textbox is inside an iframe with title "Coach"
        self.external_id_textbox: Locator = page.locator(SearchWorkItemLocators.COACH_FRAME).content_frame.get_by_role("textbox", name=SearchWorkItemLocators.EXTERNAL_ID_TEXTBOX_ROLE)
        self.search_button: Locator = page.locator(SearchWorkItemLocators.COACH_FRAME).content_frame.get_by_role("button", name=SearchWorkItemLocators.SEARCH_BUTTON_ROLE)
        self.details_link: Locator = page.locator(SearchWorkItemLocators.COACH_FRAME).content_frame.locator(SearchWorkItemLocators.DETAILS_LINK)
        self.parent_b_number: Locator = page.locator(SearchWorkItemLocators.COACH_FRAME).content_frame.locator(SearchWorkItemLocators.PARENT_B_NUMBER)
        # Diagnostic locator: ANY ParentBNumberCell regardless of content (for empty-cell debugging)
        self.parent_b_number_cell_any: Locator = page.locator(SearchWorkItemLocators.COACH_FRAME).content_frame.locator(SearchWorkItemLocators.PARENT_B_NUMBER_CELL_ANY)

    def enter_external_id_and_click_search(self, external_id: str) -> None:
        with logger.step("Enter external id and click on search button", page=self.page):
            logger.info(f"Entering external ID: {external_id}")
            # Render-safe readiness: ensure element is in DOM, visible, and enabled.
            self.external_id_textbox.wait_for(state="attached", timeout=30000)
            self.external_id_textbox.wait_for(state="visible", timeout=30000)
            with WaitContext(timeout=30.0) as wait:
                wait.until_visible(self.external_id_textbox)
                wait.until_enabled(self.external_id_textbox)
            logger.info("External ID textbox is visible")
            
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
            self.wait_for_load_state("networkidle", timeout=30000)
            self.wait_for_loading_data()

            # Check if details link is visible, if not click search again
            if not self.details_link.is_visible():
                logger.warning("Details link not visible, clicking search again")
                self.click_search_button()
                self.wait_for_timeout(2000)
           
            # Wait for details link to be visible
            self.details_link.wait_for(state="visible", timeout=30000)
            logger.info("Details link is visible")
            max_retries = 10
            retry_wait_ms = 15000
            last_error: Exception | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    # Make sure search results are rendered
                    self.details_link.wait_for(state="visible", timeout=30000)
                    logger.info(f"Details link visible (attempt {attempt}/{max_retries})")

                    # Wait for parent B cell to appear in the same results row
                    self.parent_b_number.wait_for(state="visible", timeout=15000)
                    logger.info("Parent B number element is visible in DOM")

                    # Defensive: confirm the cell text actually starts with 'B' (not just whitespace)
                    cell_text = (self.parent_b_number.inner_text(timeout=5000) or "").strip()
                    if not cell_text.startswith("B"):
                        raise ValueError(
                            f"ParentBNumberCell visible but text not populated yet: '{cell_text}'"
                        )
                    logger.info(f"Parent B# cell populated: {cell_text}")
                    break
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Parent B number not yet populated (attempt {attempt}/{max_retries}), "
                            f"waiting {retry_wait_ms}ms then re-running search..."
                        )
                        # Wait for BAW to process, then re-run search to refresh the row
                        self.wait_for_timeout(retry_wait_ms)
                        try:
                            self.click_search_button()
                            self.wait_for_load_state("networkidle", timeout=30000)
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
            SearchWorkItemPage.last_parent_b_number = b_num.strip()

            return b_num.strip()

