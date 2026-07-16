from typing import Union

from playwright.sync_api import Locator, Page, FrameLocator

from pages.ewm.base_page import BasePage
from pages.stp.stp_manageBene.locators.deceased_bene_locators import DeceasedBeneLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class DeceasedBenePage(BasePage):
    """
    Page object for the Manage Beneficiaries landing page when the household
    contains a deceased account holder.

    UI elements visible on this page:
    - Warning banner: "Deceased Account(s) Not Eligible"
    - Sub-text with contact instructions
    - Account card showing the deceased account holder name with "(Deceased)" label
    - "NOT ELIGIBLE" chip on the account card
    """

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        loc = DeceasedBeneLocators

        # ── Warning banner ────────────────────────────────────────────────────
        self.not_eligible_banner: Locator = context.locator(loc.NOT_ELIGIBLE_BANNER)
        self.not_eligible_banner_subtext: Locator = context.locator(loc.NOT_ELIGIBLE_BANNER_SUBTEXT)

        # ── Account card ──────────────────────────────────────────────────────
        self.deceased_account_card: Locator = context.locator(loc.DECEASED_ACCOUNT_CARD)
        # "(Deceased)" label inside the card
        self.deceased_label: Locator = context.locator(loc.DECEASED_LABEL)
        # "Not Eligible" chip on the card
        self.not_eligible_chip: Locator = context.locator(loc.NOT_ELIGIBLE_CHIP)

    # ── Verification helpers ──────────────────────────────────────────────────

    def is_not_eligible_banner_visible(self) -> bool:
        """Return True if the 'Deceased Account(s) Not Eligible' warning banner is visible."""
        logger.info("Checking visibility of 'Deceased Account(s) Not Eligible' banner")
        try:
            self.not_eligible_banner.wait_for(state="visible", timeout=10000)
            result = self.not_eligible_banner.is_visible()
        except Exception:
            result = False
        logger.info(f"Not-eligible banner visible: {result}")
        return result

    def get_not_eligible_banner_text(self) -> str:
        """Return the heading text of the warning banner."""
        logger.info("Getting not-eligible banner text")
        self.not_eligible_banner.wait_for(state="visible", timeout=10000)
        text = self.not_eligible_banner.inner_text().strip()
        logger.info(f"Banner text: '{text}'")
        return text

    def is_not_eligible_chip_visible(self) -> bool:
        """Return True if the 'NOT ELIGIBLE' chip is visible on the account card."""
        logger.info("Checking visibility of 'Not Eligible' chip on account card")
        try:
            self.not_eligible_chip.wait_for(state="visible", timeout=10000)
            result = self.not_eligible_chip.is_visible()
        except Exception:
            result = False
        logger.info(f"Not-eligible chip visible: {result}")
        return result

    def click_deceased_account_card(self) -> None:
        """Click on the deceased account card."""
        logger.info("Clicking on deceased account card")
        self.deceased_account_card.wait_for(state="visible", timeout=10000)
        self.deceased_account_card.click()
        logger.info("[OK] Deceased account card clicked")

    def get_current_url(self) -> str:
        """Return the current page URL (only available when context is a Page)."""
        if self.page:
            return self.page.url
        return ""
