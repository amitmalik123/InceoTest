from typing import Union

from playwright.sync_api import FrameLocator, Locator, Page

from pages.stp.shared.base_page import BasePage
from pages.stp.stp_manageBene.locators.manage_bene_review_locators import ManageBeneReviewLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageBeneReviewPage(BasePage):

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        self._ctx = context
        loc = ManageBeneReviewLocators

        self.review_beneficiaries_heading: Locator = context.get_by_text(loc.REVIEW_BENEFICIARIES_HEADING, exact=True)
        self.review_esignature_heading: Locator = context.get_by_text(loc.REVIEW_ESIGNATURE_HEADING, exact=True)
        self.acknowledgements_heading: Locator = context.get_by_text(loc.ACKNOWLEDGEMENTS_HEADING, exact=True)

        self.account_title: Locator = context.locator(loc.ACCOUNT_TITLE).nth(1)

        self.primary_section_header: Locator = context.get_by_text(loc.PRIMARY_SECTION_HEADER, exact=True)
        self.contingent_section_header: Locator = context.get_by_text(loc.CONTINGENT_SECTION_HEADER, exact=True)

        self.primary_beneficiary_names: Locator = context.locator(loc.PRIMARY_BENEFICIARY_NAMES)
        self.primary_beneficiary_relationships: Locator = context.locator(loc.PRIMARY_BENEFICIARY_RELATIONSHIPS)
        self.beneficiary_allocations: Locator = context.locator(loc.BENEFICIARY_ALLOCATIONS)

        self.added_chips: Locator = context.locator(loc.ADDED_CHIPS)

        self.signers_label: Locator = context.get_by_text(loc.SIGNERS_LABEL, exact=True)
        self.signer_name: Locator = context.locator(loc.SIGNER_NAME)
        self.signer_details: Locator = context.locator(loc.SIGNER_DETAILS)

        self.acknowledgements_content: Locator = context.locator(loc.ACKNOWLEDGEMENTS_CONTENT).first

        self.back_to_esignature_button: Locator = context.get_by_role(
            "button", name=loc.BACK_TO_ESIGNATURE_BUTTON
        )
        self.submit_to_advisor_button: Locator = context.get_by_role(
            "button", name=loc.SUBMIT_TO_ADVISOR_BUTTON
        )

    def wait_for_page_load(self, timeout: int = 15000) -> None:
        logger.info("Waiting for Review page to load")
        self.review_beneficiaries_heading.wait_for(state="visible", timeout=timeout)
        logger.info("Review page loaded")

    def get_beneficiary_by_name(self, full_name: str) -> Locator:
        """Return a locator for a beneficiary row using XPath axis matching on the name text.
        Uses contains() so a partial name (without suffix) still matches."""
        xpath = (
            f"//span[contains(@class,'MuiTypography-cardTextPrimary') and "
            f"contains(normalize-space(text()),'{full_name}')]"
            f"/ancestor::div[contains(@class,'MuiBox-root') and contains(@class,'css-1yw9ps3')]"
        )
        return self._ctx.locator(f"xpath={xpath}")

    def is_beneficiary_visible(self, full_name: str) -> bool:
        """Check if a beneficiary with the exact full name is visible on the Review page."""
        locator = self.get_beneficiary_by_name(full_name)
        return locator.is_visible()

    def get_added_badge_for_beneficiary(self, full_name: str) -> Locator:
        """Return the ADDED chip locator for a specific beneficiary name using XPath following-sibling axis."""
        xpath = (
            f"//span[contains(@class,'MuiTypography-cardTextPrimary') and "
            f"normalize-space(text())='{full_name}']"
            f"/ancestor::div[contains(@class,'css-1yw9ps3')]"
            f"/following-sibling::div[contains(@class,'css-he77x2')]"
            f"//span[contains(@class,'MuiChip-label')]"
        )
        return self._ctx.locator(f"xpath={xpath}")

    def click_submit_to_advisor(self) -> None:
        logger.info("Clicking 'Submit to Advisor' button")
        self.submit_to_advisor_button.wait_for(state="attached", timeout=30000)
        self.submit_to_advisor_button.scroll_into_view_if_needed(timeout=30000)
        self.submit_to_advisor_button.wait_for(state="visible", timeout=30000)
        self.submit_to_advisor_button.click()
        logger.info("'Submit to Advisor' button clicked")

    def get_account_title(self) -> str:
        return self.account_title.inner_text().strip()

    def get_primary_beneficiary_name(self, index: int = 0) -> str:
        return self.primary_beneficiary_names.nth(index).inner_text().strip()

    def get_beneficiary_relationship(self, index: int = 0) -> str:
        return self.primary_beneficiary_relationships.nth(index).inner_text().strip()

    def get_beneficiary_allocation(self, index: int = 0) -> str:
        return self.beneficiary_allocations.nth(index).inner_text().strip()

    def is_added_chip_visible(self, index: int = 0) -> bool:
        return self.added_chips.nth(index).is_visible()

    def get_signer_name(self) -> str:
        return self.signer_name.inner_text().strip()

    def get_signer_details(self) -> str:
        return self.signer_details.inner_text().strip()

    def get_signer_email(self) -> str:
        details = self.get_signer_details()
        parts = [p.strip() for p in details.split("•")]
        return parts[0] if parts else ""

    def get_signer_phone(self) -> str:
        details = self.get_signer_details()
        parts = [p.strip() for p in details.split("•")]
        return parts[1] if len(parts) > 1 else ""

    def get_signer_method(self) -> str:
        details = self.get_signer_details()
        parts = [p.strip() for p in details.split("•")]
        return parts[2] if len(parts) > 2 else ""

    def is_acknowledgements_section_visible(self) -> bool:
        return self.acknowledgements_heading.is_visible()

    def click_back_to_esignature(self) -> None:
        logger.info("Clicking Back to e-Signature Details button")
        self.back_to_esignature_button.click()
        logger.info("Back to e-Signature Details clicked")

    def click_submit(self) -> None:
        logger.info("Clicking Submit button")
        self.submit_button.wait_for(state="visible", timeout=10000)
        self.submit_button.click()
        logger.info("Submit clicked")

    def is_submit_enabled(self) -> bool:
        return self.submit_button.is_enabled()

    def verify_review_page(
        self,
        account_title: str = None,
        signer_name: str = None,
        signer_email: str = None,
        signer_phone: str = None,
        signer_method: str = None,
    ) -> None:
        logger.info("Verifying Review page content")
        self.wait_for_page_load()

        if account_title:
            actual = self.get_account_title()
            assert account_title in actual, f"Account title mismatch: expected '{account_title}' in '{actual}'"
            logger.info(f"Account title verified: {actual}")

        if signer_name:
            actual = self.get_signer_name()
            assert signer_name in actual, f"Signer name mismatch: expected '{signer_name}' in '{actual}'"
            logger.info(f"Signer name verified: {actual}")

        if signer_email:
            actual = self.get_signer_email()
            assert signer_email in actual, f"Signer email mismatch: expected '{signer_email}' in '{actual}'"
            logger.info(f"Signer email verified: {actual}")

        if signer_phone:
            actual = self.get_signer_phone()
            assert signer_phone in actual, f"Signer phone mismatch: expected '{signer_phone}' in '{actual}'"
            logger.info(f"Signer phone verified: {actual}")

        if signer_method:
            actual = self.get_signer_method()
            assert signer_method in actual, f"Signer method mismatch: expected '{signer_method}' in '{actual}'"
            logger.info(f"Signer method verified: {actual}")

        logger.info("Review page verification complete")
