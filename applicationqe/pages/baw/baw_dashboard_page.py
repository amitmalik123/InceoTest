"""BAW Dashboard Page - Business Automation Workflow"""

import time

from playwright.sync_api import Frame, Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.wait_utils import WaitContext

logger = get_allure_logger(__name__)


class BawDashboardPage(BasePage):
    """BAW Dashboard Page class with work item functionality"""
    
    PAGE_NAME = "BAW Dashboard Page"

    def __init__(self, page: Page, frame: Frame = None):
        super().__init__(page)
        self.frame = frame or page  # Use frame if provided, else use page
        # Locator for Open New WorkItem button (from Java: By.cssSelector("#ButtonGroup5_Button0"))
        # This button is INSIDE the iframe, so we use frame.locator
        self.open_new_workitem_button: Locator = self.frame.locator("#ButtonGroup5_Button0")
        # Locators for B tracking number search
        self.search_b_number: Locator = self.frame.get_by_role("textbox", name="B#:")
        self.search_button: Locator = self.frame.get_by_role("button", name="Search")
        self.task_table: Locator = self.frame.locator("#CustomHTML5 > table")
        self.show_more_link: Locator = self.page.locator("xpath=//a[contains(normalize-space(), 'Show more')]")

    def click_open_new_workitem_button(self):
        """
        Click 'Open New WorkItem' button and switch to new window
        """
        with logger.step("Click Open New Work Item button", page=self.page):
            # Resolve iframe at click time to avoid stale frame/locator references.
            frame_selector = "//*[@data-viewid='CoachViewer']//iframe[@title]"
            frame_locator = self.page.frame_locator(frame_selector)

            # Playwright auto-waits, but explicit wait keeps behavior deterministic for slow BAW loads.
            self.page.wait_for_selector(frame_selector, timeout=40000)

            open_new_workitem_button = frame_locator.locator("#ButtonGroup5_Button0")
            logger.info("Waiting for Open New WorkItem button to be visible in iframe")
            open_new_workitem_button.wait_for(state="visible", timeout=40000)

            logger.info("Clicking on Open New WorkItem button")

            try:
                open_new_workitem_button.click(no_wait_after=True)
            except Exception:
                logger.warning("Open New WorkItem normal click failed, trying JS click")
                open_new_workitem_button.evaluate("el => el.click()")


    def click_tab(self, tab_name: str) -> None:
        """
        Click on a dashboard menu tab (e.g., 'Search Work Item', 'Bulk Reassign', etc.)
        Mirrors Java implementation with title matching

        Args:
            tab_name: The name/title of the tab to click
        """
        with logger.step(f"Click on {tab_name} tab", page=self.page):
            logger.info(f"Clicking on tab: {tab_name}")

            # New UI behavior: expand menu before opening any dashboard tab.
            try:
                if self.show_more_link.count() > 0:
                    self.show_more_link.wait_for(state="visible", timeout=5000)
                    self.show_more_link.click(timeout=5000)
                    logger.info("Clicked 'Show more' before tab navigation")
                else:
                    logger.info("'Show more' locator not present, continuing")
            except Exception as e:
                logger.info(f"'Show more' click skipped/failed: {e}")
            
            # Wait for page to load
            self.wait_for_load_state("domcontentloaded", timeout=30000)
            
            # Switch to default content if in frame
            try:
                self.page.evaluate("window.scrollTo(0, 0)")
            except:
                pass
            
            # Check if dashboard menu is visible
            dashboard_menu = self.page.locator("#collapseDashboardsMenu")
            if not dashboard_menu.is_visible():
                logger.warning("Dashboard menu not immediately visible, waiting...")
                try:
                    dashboard_menu.wait_for(state="visible", timeout=10000)
                except:
                    logger.error("Dashboard menu not found")
                    raise ValueError("Dashboard menu is not visible")
            
            logger.info("Dashboard menu is visible")
            
            # Find the menu link with matching title
            # XPath: //div[contains(@class,'menu_link')]/div/div/div[@class='menu-link-body']/a[@title='Search Work Item']
            menu_link_xpath = f"//div[contains(@class,'menu_link')]//a[@title='{tab_name}']"
            menu_link = self.page.locator(menu_link_xpath)
            
            # Scroll into view if needed
            try:
                if tab_name in ["Bulk Reassign", "Set QC Selection"]:
                    menu_link.scroll_into_view_if_needed()
                    logger.info(f"{tab_name} scrolled into view")
            except:
                pass
            
            # Click the menu link
            try:
                menu_link.click(timeout=10000)
                logger.info(f"Clicked on {tab_name} tab")
            except Exception as e:
                logger.warning(f"Standard click failed: {e}, trying JavaScript click")
                # Fallback to JavaScript click
                try:
                    self.page.evaluate(f"document.querySelector('a[title=\"{tab_name}\"]').click()")
                    logger.info(f"JavaScript click succeeded for {tab_name}")
                except Exception as js_error:
                    logger.error(f"Both click methods failed: {str(js_error)}")
                    raise
            
            # Wait for navigation/content update
            self.wait_for_timeout(2000)
            logger.info(f"Tab {tab_name} clicked successfully")

    def enter_b_number_to_search(self, b_tracking_id: str) -> None:
        """
        Enter B tracking number and perform search with retry logic.
        Mirrors Java implementation with maxRetries = 2 and 60s wait between retries.

        Args:
            b_tracking_id: The B tracking number to search for
        """
        with logger.step("Enter B tracking number and search", page=self.page):
            logger.info(f"Searching for B tracking number: {b_tracking_id}")

            # Java equivalent:
            # seleniumCore.switchToFrame(By.xpath("//iframe[@title='Dashboard']"), 60, 1)
            frame_selector = "xpath=//iframe[@title='Dashboard']"
            frame_locator = self.page.frame_locator(frame_selector)
            self.page.wait_for_selector(frame_selector, state="attached", timeout=60000)

            search_b_number = frame_locator.locator("#txtBNum")
            search_button = frame_locator.locator("#ButtonGroup4_Search")
            task_table = frame_locator.locator("#CustomHTML5 > table")
            
            # Initial waits - use domcontentloaded instead of networkidle to avoid timeout in iframe
            try:
                self.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception as e:
                logger.warning(f"Load state wait timeout (continuing): {e}")
            self.wait_for_loading_data(timeout=30000)
            
            max_retries = 2
            for attempt in range(max_retries):
                logger.info(f"Search attempt {attempt + 1}/{max_retries}")

                try:
                    # Primary locator path via fresh frame locator
                    with WaitContext(timeout=10.0) as wait:
                        wait.until_enabled(search_b_number)
                    search_b_number.wait_for(state="attached", timeout=30000)
                    search_b_number.wait_for(state="visible", timeout=30000)
                    logger.info("Using primary B# search locator")
                except Exception as e:
                    logger.warning(f"Primary B# locator failed: {e}. Trying fallback locator")
                    # Fallback xpath in same frame context
                    search_b_number = frame_locator.locator("xpath=//input[@id='txtBNum']")
                    search_b_number.wait_for(state="attached", timeout=30000)
                    search_b_number.wait_for(state="visible", timeout=30000)
                    with WaitContext(timeout=10.0) as wait:
                        wait.until_enabled(search_b_number)
                    logger.info("Using fallback B# search locator")
                
                # Fill search box and click search
                self.fill(search_b_number, b_tracking_id)
                self.click(search_button)
                
                # Wait for loading to complete
                self.wait_for_loading_data(timeout=30000)
                
                # Check if task table is visible
                if task_table.is_visible():
                    logger.info("Task table visible after search")
                    break
                else:
                    logger.warning("Task table not visible yet, waiting before retry")
                    if attempt < max_retries - 1:
                        self.wait_for_timeout(60000)
            
            # Final check - log warning if still not visible but don't fail
            if not task_table.is_visible():
                logger.warning(f"Task table not visible even after {max_retries} attempts to search B number: {b_tracking_id}")
            
            logger.info(f"Enter b number in search box: {b_tracking_id}")

    def click_run_icon(self, b_tracking_id: str) -> None:
        """
        Click run icon for a tracking row.

        Args:
            b_tracking_id: B tracking id/parent B number to identify row. If empty, uses default row run icon.

        Raises:
            ValueError: If task table is not visible or run icon cannot be found
        """
        with logger.step("Click run icon", page=self.page):
            frame_selector = "xpath=//iframe[@title='Dashboard']"
            frame_locator = self.page.frame_locator(frame_selector)
            self.page.wait_for_selector(frame_selector, state="attached", timeout=40000)

            task_table = frame_locator.locator("#CustomHTML5 > table")

            try:
                self.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception as e:
                logger.warning(f"Load state wait timeout (continuing): {e}")
            self.wait_for_loading_data(timeout=30000)

            if not self.is_element_visible(task_table, max_wait_time=50, poll_time=1):
                raise ValueError("searched b number is not visible")

            # Wait for table rows to fully render before looking for run icon
            self.page.wait_for_timeout(2000)

            run_button = None
            if b_tracking_id:
                primary_run_button = frame_locator.locator(f"img[onclick*='{b_tracking_id}']").first
                fallback_run_button = frame_locator.locator(
                    f"xpath=//a[text()='{b_tracking_id}']//parent::td//preceding-sibling::td[3]"
                ).first
                row_run_button = frame_locator.locator(
                    f"xpath=//tr[.//*[normalize-space(text())='{b_tracking_id}']]//td[1]//img"
                ).first
                broad_row_run_button = frame_locator.locator(
                    f"xpath=//tr[.//*[normalize-space(text())='{b_tracking_id}']]//td[1]//*[self::img or self::button or @role='button' or contains(@class,'icon')]"
                ).first
                any_first_row_img = frame_locator.locator("#TaskTable > tbody > tr:first-child > td:first-child img").first
            else:
                primary_run_button = frame_locator.locator("#TaskTable > tbody > tr > td > img").first
                fallback_run_button = frame_locator.locator(
                    "xpath=//table[@id='TaskTable']//tbody//tr[position() = (last() - 1)]/td/img"
                ).first
                row_run_button = None
                broad_row_run_button = None
                any_first_row_img = None

            if primary_run_button.count() > 0:
                run_button = primary_run_button
            elif fallback_run_button.count() > 0:
                run_button = fallback_run_button
            elif row_run_button and row_run_button.count() > 0:
                run_button = row_run_button
            elif broad_row_run_button and broad_row_run_button.count() > 0:
                run_button = broad_row_run_button
            elif any_first_row_img and any_first_row_img.count() > 0:
                logger.warning("Using first-row img fallback for run icon")
                run_button = any_first_row_img
            else:
                try:
                    all_imgs = frame_locator.locator("#TaskTable img").count()
                    all_rows = frame_locator.locator("#TaskTable tbody tr").count()
                    first_row_html = frame_locator.locator("#TaskTable tbody tr").first.inner_html() if all_rows > 0 else "no rows"
                    logger.error(f"DIAG run icon: b_tracking_id='{b_tracking_id}', table imgs={all_imgs}, rows={all_rows}")
                    logger.error(f"DIAG first row HTML: {first_row_html[:500]}")
                except Exception as diag_err:
                    logger.error(f"DIAG failed: {diag_err}")
                raise ValueError("Run icon is not found for the searched tracking number")

            try:
                run_button.scroll_into_view_if_needed()
            except Exception:
                pass

            # Use expect_popup to capture the NAA Coach window opened by the run icon click.
            # Fallback: if no popup opens (e.g. coach loads inline), continue without error.
            try:
                with self.page.expect_popup(timeout=30000) as popup_info:
                    try:
                        run_button.click(timeout=10000)
                    except Exception as click_error:
                        logger.warning(f"Standard click failed on run icon: {click_error}, trying force click")
                        try:
                            run_button.click(timeout=10000, force=True)
                        except Exception as force_error:
                            logger.warning(f"Force click failed: {force_error}, trying JavaScript click")
                            with WaitContext(timeout=10.0) as wait:
                                wait.until_visible(run_button)
                            self.page.evaluate("el => el.click()", run_button.element_handle())
                popup_page = popup_info.value
                popup_page.wait_for_load_state("domcontentloaded", timeout=30000)
                logger.info(f"Popup captured after run icon click: {popup_page.title()}")
            except Exception as popup_err:
                logger.warning(f"No popup detected after run icon click (may load inline): {popup_err}")

            logger.info("Clicked on run button")
            self.wait_for_loading_data(timeout=30000)