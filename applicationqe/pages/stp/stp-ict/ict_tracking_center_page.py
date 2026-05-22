from typing import Any, Optional

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger
from locators.stp.stp_ict.ict_tracking_center_locators import ICTTrackingCenterLocators
from validations.ict_tracking_center_validations import TrackingCenterValidations

logger = setup_logger(__name__)


class TrackingCenterPage(BasePage):
    PAGE_URL = 'https://test11.ewealthmanager.com/AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail/A034607033'

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ICTTrackingCenterLocators()
        self.account_src_label: Optional[Locator] = None  # Will be set dynamically
        self.logout_link: Locator = self.resolve_locator(self.locators.LOGOUT_LINK)
        self.bodycontent_div: Locator = self.resolve_locator(self.locators.BODY_CONTENT)
        self._validations = TrackingCenterValidations(self.page)

    def navigate(self) -> None:
        logger.info(f"Navigating to tracking center page: {self.PAGE_URL}")
        self.page.goto(self.PAGE_URL)
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Tracking center page loaded")

    def verify_account_src(self, expected: str) -> None:
        logger.info(f"Delegating account source verification to validations: {expected}")
        self._validations.validate_account_src(expected)
        logger.info(f"Account source {expected} verified")

    def verify_roth_str(self, expected: str) -> None:
        logger.info(f"Delegating Roth STR verification to validations: {expected}")
        self._validations.validate_roth_str(expected)
        logger.info(f"Roth STR {expected} verified")

    def click_logout(self) -> None:
        logger.info("Clicking logout")
        self.logout_link.click()
        logger.info("Logout clicked")

    def get_d_number(self) -> str:
        """Return the current item number (D# or B#) from the hidden #ItemNumber input."""
        logger.info("Getting item number from tracking center detail page")
        # #ItemNumber is a hidden input — get its value attribute, not inner_text
        item_el = self.page.locator(ICTTrackingCenterLocators.ITEM_NUMBER)
        item_el.wait_for(state='attached', timeout=15000)
        value = item_el.get_attribute('value') or ''
        logger.info(f"Item number: {value}")
        return value.strip()

    def get_status(self) -> str:
        """Return the status label text from the tracking center detail page."""
        logger.info("Getting status from tracking center detail page")
        try:
            with open('reports/tracking_center_detail.html', 'w', encoding='utf-8') as f:
                f.write(self.page.content())
        except Exception:
            pass
        # Status label: <span>Status: </span> <label>...</label>
        status_label = self.page.locator(ICTTrackingCenterLocators.ITEM_STATUS)
        status_label.wait_for(state='visible', timeout=10000)
        value = status_label.inner_text().strip()
        logger.info(f"Status: {value}")
        return value

    def refresh_page(self) -> None:
        """Reload the page and wait for it to load."""
        self.page.reload()
        self.page.wait_for_load_state('networkidle', timeout=30000)

    def wait_for_b_number(self, timeout_ms: int = 120000, poll_ms: int = 5000) -> str:
        """Poll (refresh) until the ItemNumber changes from D# to B#. Returns the B# value."""
        import time
        logger.info("Waiting for item number to flip from D# to B#")
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            item_el = self.page.locator(ICTTrackingCenterLocators.ITEM_NUMBER)
            try:
                # ITEM_NUMBER is a hidden input — use get_attribute('value')
                item_el.wait_for(state='attached', timeout=5000)
                value = (item_el.get_attribute('value') or '').strip()
                logger.info(f"Current item number: {value}")
                if value.startswith('B'):
                    logger.info(f"Item number flipped to B#: {value}")
                    return value
            except Exception:
                pass
            self.page.reload()
            self.page.wait_for_load_state('networkidle', timeout=30000)
            self.page.wait_for_timeout(poll_ms)
        raise TimeoutError(f"Item number did not flip to B# within {timeout_ms}ms")
