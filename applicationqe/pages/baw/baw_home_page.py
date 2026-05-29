"""BAW Home Page - Business Automation Workflow"""

from playwright.sync_api import Locator, Page

from locators.baw.baw_dashboard_locators import BawDashboardLocators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class BawHomePage(BasePage):
    """BAW Home Page class with dashboard navigation"""
    
    PAGE_NAME = "BAW Home Page"

    def __init__(self, page: Page):
        super().__init__(page)
        # Locators for BAW home page (from Java: By.xpath patterns)
        self.show_more_link: Locator = page.locator(BawDashboardLocators.SHOW_MORE_LINK)
        self.dashboard_link: Locator = page.locator("//a[contains(text(),'Dashboard')]")
        self.dashboard_frame: Locator = page.locator(BawDashboardLocators.COACH_IFRAME).first

    def click_show_more(self) -> None:
        """Click 'Show more' link if visible"""
        with logger.step("Click Show more link if visible", page=self.page):
            try:
                self.show_more_link.wait_for(state="visible", timeout=5000)
                logger.info("Show more link found")
                self.scroll_into_view(self.show_more_link)
                self.click(self.show_more_link)
                logger.info("Clicked on Show more link")
            except Exception as e:
                logger.info(f"Show more link not visible (optional step): {e}")

    def click_dashboard(self) -> None:
        """Click Dashboard link"""
        with logger.step("Click Dashboard link", page=self.page):
            logger.info("Waiting for Dashboard link to be visible")
            self.dashboard_link.wait_for(state="visible", timeout=20000)
            
            logger.info("Clicking on Dashboard link")
            self.click(self.dashboard_link)
            logger.info("Clicked on Dashboard link")

    def move_to_dashboard(self) -> "BawDashboardPage":
        """
        Navigate to dashboard and switch to iframe

        Returns:
            BawDashboardPage instance
        """
        with logger.step("Move to Dashboard", page=self.page):
            self.click_show_more()
            self.click_dashboard()
            
            # Wait for iframe to be visible
            logger.info("Waiting for dashboard frame to be visible")
            self.dashboard_frame.wait_for(state="visible", timeout=30000)
            
            # Wait for page to load
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Get the iframe element handle
            logger.info("Switching to dashboard iframe")
            iframe_element = self.dashboard_frame.element_handle()
            frame = iframe_element.content_frame()
            if not frame:
                raise ValueError("Dashboard iframe content is not available")

            dashboard_ready = frame.locator(
                "#ButtonGroup5_Button0, #CustomHTML5, #txtBNum, #TaskTable"
            ).first

            try:
                dashboard_ready.wait_for(state="visible", timeout=20000)
            except Exception:
                logger.warning("Dashboard frame is visible but content is blank. Retrying Dashboard click once.")
                self.click_dashboard()
                self.dashboard_frame.wait_for(state="visible", timeout=30000)

                iframe_element = self.dashboard_frame.element_handle()
                if not iframe_element:
                    raise ValueError("Dashboard iframe element was not found after retry")

                frame = iframe_element.content_frame()
                if not frame:
                    raise ValueError("Dashboard iframe content is not available after retry")

                dashboard_ready = frame.locator(
                    "#ButtonGroup5_Button0, #CustomHTML5, #txtBNum, #TaskTable"
                ).first
                dashboard_ready.wait_for(state="visible", timeout=30000)
            
            # Import here to avoid circular imports
            from pages.baw.baw_dashboard_page import BawDashboardPage
            
            logger.info("Successfully navigated to Dashboard and switched to iframe")
            return BawDashboardPage(self.page, frame)
