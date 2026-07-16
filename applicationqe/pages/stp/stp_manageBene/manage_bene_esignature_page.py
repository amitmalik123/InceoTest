from typing import Union

from playwright.sync_api import FrameLocator, Locator, Page

from pages.ewm.base_page import BasePage
from pages.stp.stp_manageBene.locators.manage_bene_esignature_locators import ManageBeneESignatureLocators
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ManageBeneESignaturePage(BasePage):

    def __init__(self, context: Union[Page, FrameLocator]):
        super().__init__(context)
        self._ctx = context
        loc = ManageBeneESignatureLocators

        self.page_heading: Locator = context.get_by_text(loc.PAGE_HEADING, exact=True)
        self.any_party_subheading: Locator = context.get_by_text(loc.ANY_PARTY_SUBHEADING, exact=True)

        self.account_holder_dropdown: Locator = context.get_by_role(loc.ACCOUNT_HOLDER_DROPDOWN)
        self.account_holder_native_input: Locator = context.locator(loc.ACCOUNT_HOLDER_NATIVE_INPUT)

        self.email_input: Locator = context.get_by_role("textbox").nth(loc.EMAIL_INPUT_INDEX)
        self.phone_input: Locator = context.get_by_role("textbox").nth(loc.PHONE_INPUT_INDEX)

        self.by_email_radio: Locator = context.get_by_label(loc.BY_EMAIL_RADIO_LABEL)
        self.in_person_radio: Locator = context.get_by_label(loc.IN_PERSON_RADIO_LABEL)

        self.certify_checkbox: Locator = context.get_by_role(loc.CERTIFY_CHECKBOX_ROLE)

        self.back_to_beneficiaries_button: Locator = context.get_by_role(
            "button", name=loc.BACK_TO_BENEFICIARIES_BUTTON
        )
        self.continue_to_review_button: Locator = context.get_by_role(
            "button", name=loc.CONTINUE_TO_REVIEW_BUTTON
        )

    def wait_for_page_load(self, timeout: int = 15000) -> None:
        logger.info("Waiting for e-Signature Details page to load")
        self.page_heading.wait_for(state="visible", timeout=timeout)
        logger.info("e-Signature Details page loaded")

    def select_first_account_holder(self) -> str:
        """Clicks the Authorized Account Holder dropdown and selects the first available option.
        Returns the text of the selected option so it can be stored in test_context."""
        logger.info("Clicking Authorized Account Holder dropdown")
        self.account_holder_dropdown.click()
        first_option = self._ctx.get_by_role("option").first
        first_option.wait_for(state="visible", timeout=30000)
        selected_text = first_option.inner_text().strip()
        first_option.click()
        logger.info(f"Selected first account holder option: '{selected_text}'")
        return selected_text

    def select_account_holder(self, name: str) -> None:
        logger.info(f"Selecting account holder: {name}")
        self.account_holder_dropdown.click()
        option = self._ctx.get_by_role("option", name=name)
        option.wait_for(state="visible", timeout=10000)
        option.click()
        logger.info(f"Account holder '{name}' selected")

    def get_selected_account_holder(self) -> str:
        return self.account_holder_native_input.input_value()

    def enter_email(self, email: str) -> None:
        logger.info(f"Entering email: {email}")
        self.email_input.clear(timeout=60000)
        self.email_input.fill(email, timeout=60000)
        logger.info("Email entered")

    def get_email(self) -> str:
        return self.email_input.input_value()

    def enter_phone(self, phone: str) -> None:
        logger.info(f"Entering phone: {phone}")
        self.phone_input.clear(timeout=60000)
        self.phone_input.fill(phone, timeout=60000)
        logger.info("Phone entered")

    def get_phone(self) -> str:
        return self.phone_input.input_value()

    def select_method_by_email(self) -> None:
        logger.info("Selecting signature method: By Email")
        self.by_email_radio.check()
        logger.info("By Email method selected")

    def select_method_in_person(self) -> None:
        logger.info("Selecting signature method: In Person")
        self.in_person_radio.check()
        logger.info("In Person method selected")

    def is_by_email_selected(self) -> bool:
        return self.by_email_radio.is_checked()

    def is_in_person_selected(self) -> bool:
        return self.in_person_radio.is_checked()

    def get_selected_method(self) -> str:
        if self.by_email_radio.is_checked():
            return "email"
        if self.in_person_radio.is_checked():
            return "inPerson"
        return ""

    def check_certify(self) -> None:
        logger.info("Checking certify checkbox")
        if not self.certify_checkbox.is_checked():
            self.certify_checkbox.check()
        logger.info("Certify checkbox checked")

    def uncheck_certify(self) -> None:
        logger.info("Unchecking certify checkbox")
        if self.certify_checkbox.is_checked():
            self.certify_checkbox.uncheck()
        logger.info("Certify checkbox unchecked")

    def is_certify_checked(self) -> bool:
        return self.certify_checkbox.is_checked()

    def is_continue_to_review_enabled(self) -> bool:
        return self.continue_to_review_button.is_enabled()

    def click_back_to_beneficiaries(self) -> None:
        logger.info("Clicking Back to Beneficiaries button")
        self.back_to_beneficiaries_button.click()
        logger.info("Back to Beneficiaries clicked")

    def click_continue_to_review(self) -> None:
        logger.info("Clicking Continue to Review button")
        self.continue_to_review_button.wait_for(state="visible", timeout=10000)
        self.continue_to_review_button.click()
        logger.info("Continue to Review clicked")

    def is_continue_to_review_enabled(self) -> bool:
        return self.continue_to_review_button.is_enabled()

    def fill_esignature_form(
        self,
        account_holder: str,
        email: str,
        phone: str,
        method: str = "email",
    ) -> None:
        logger.info(
            f"Filling e-Signature form: holder={account_holder}, "
            f"email={email}, phone={phone}, method={method}"
        )
        self.select_account_holder(account_holder)
        self.enter_email(email)
        self.enter_phone(phone)
        if method == "inPerson":
            self.select_method_in_person()
        else:
            self.select_method_by_email()
        self.check_certify()
        logger.info("e-Signature form filled successfully")

    def click_continue_to_review(self) -> None:
        logger.info("Clicking Continue to Review button")
        self.continue_to_review_button.wait_for(state="visible", timeout=10000)
        self.continue_to_review_button.click()
        logger.info("Continue to Review clicked")

    def get_field_error(self, field: str) -> str:
        input_el = self.email_input if field == "email" else self.phone_input
        describedby = input_el.get_attribute("aria-describedby")
        if describedby:
            error_el = self._ctx.locator(f'[id="{describedby}"]')
            if error_el.count() > 0 and error_el.first.is_visible():
                return error_el.first.inner_text().strip()
        label_text = "Email" if field == "email" else "Phone"
        group = self._ctx.locator(f"label:has-text('{label_text}'), p:has-text('{label_text}')").first
        helper = group.locator("xpath=following-sibling::p[contains(@class,'Mui-error')]")
        if helper.count() > 0:
            return helper.first.inner_text().strip()
        return ""

    def get_phone_actual_value(self) -> str:
        return self.phone_input.input_value()

    def trigger_validation(self) -> None:
        logger.info("Triggering field validation by clicking Continue to Review")
        self.email_input.click()
        self.email_input.press("Tab")
        self.phone_input.click()
        self.phone_input.press("Tab")
        self._ctx.wait_for_timeout(300)
        self.continue_to_review_button.click(force=True)
        self._ctx.wait_for_timeout(500)
