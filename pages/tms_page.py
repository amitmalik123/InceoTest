import re

from playwright.sync_api import Locator, Page

from config.settings import get_settings
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class TMSPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.clients_tab: Locator = page.locator("//a[text()='Clients']")
        self.account_list_link: Locator = page.locator("//a[text()='Account List']")
        self.search_input: Locator = page.locator("//input[@name='search_input']")
        self.search_button: Locator = page.locator("//button[@type='submit']")
        self.account_information_link: Locator = page.locator("//a[normalize-space()='Account Information']")
        self.tax_management_service_link: Locator = page.locator("//a[text()='Tax Management Service']")
        self.account_name_header: Locator = page.locator(
            "//div[@class='account-information-content']//h1//strong"
            " | //div[@class='account-information-content']//h1//Strong"
        )
        self.account_number_header: Locator = page.locator(
            "//div[@class='account-information-content']//h1[@class='gbmask']"
        )
        self.loading_spinner: Locator = page.locator(
            "//div[contains(@class,'loading-indicator-component__spinner')]"
        )
        self.loading_indicator: Locator = page.locator(
            "//*[contains(@class, 'loading-indication-component')"
            " and contains(@class, 'isVisible')]"
        )
        self.loading_modal: Locator = page.locator("#loadingImageModal")

    def _account_number_locator(self, account_number: str) -> Locator:
        return self.page.locator(f"//td[normalize-space()='{account_number}']")

    def wait_for_all_spinners_to_disappear(self, timeout: int = 30000) -> None:
        logger.info("Waiting for loading indicators to disappear")
        spinner_count = self.loading_spinner.count()
        for index in range(spinner_count):
            self.loading_spinner.nth(index).wait_for(state="hidden", timeout=timeout)

        indicator_count = self.loading_indicator.count()
        for index in range(indicator_count):
            self.loading_indicator.nth(index).wait_for(state="hidden", timeout=timeout)

        try:
            self.loading_modal.wait_for(state="hidden", timeout=timeout)
        except Exception:
            # Modal is not always present.
            pass

    def navigate_to_tms_page(self, account_number: str, timeout: int = 30000) -> None:
        logger.info("Navigating to TMS page")
        current_url = self.page.url or ""
        if current_url.startswith("about:blank"):
            settings = get_settings()
            home_url = settings.get_app_config("ewm").get("home_url", settings.base_url)
            logger.info(f"Recovered from about:blank before TMS navigation, opening {home_url}")
            self.page.goto(home_url, timeout=timeout)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

        self.click(self.clients_tab, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)

        self.wait_for_element(self.account_list_link, timeout=timeout)
        self.click(self.account_list_link, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)

        self.wait_for_element(self.search_input, timeout=timeout)
        self.fill(self.search_input, account_number, timeout=timeout)
        self.click(self.search_button, timeout=timeout)

        self.wait_for_element(self._account_number_locator(account_number), timeout=timeout)
        self.click(self._account_number_locator(account_number), timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)

        self.wait_for_element(self.account_information_link, timeout=timeout)
        self.click(self.account_information_link, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)

    def assert_tax_management_service_present(self, timeout: int = 10000) -> None:
        logger.info("Validating Tax Management Service link is present")
        try:
            self.wait_for_element(self.tax_management_service_link, timeout=timeout)
        except Exception as exc:
            raise AssertionError("Tax Management Service link is not present") from exc
        logger.info("Tax Management Service link is present")

    def open_tax_management_service(self, timeout: int = 10000) -> None:
        logger.info("Opening Tax Management Service section")
        self.wait_for_element(self.tax_management_service_link, timeout=timeout)
        self.click(self.tax_management_service_link, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)

    def _row_by_label(self, label: str) -> Locator:
        return self.page.locator(
            "//div[@id='tax-management-service']//div[contains(@class,'gbmask')]"
            f"[.//b[normalize-space()='{label}']"
            " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
        )

    def _value_for_label(self, label: str, timeout: int = 10000) -> str:
        rows = self._row_by_label(label)
        row_count = rows.count()
        if row_count == 0:
            raise AssertionError(f"No rows found for label '{label}'")

        row_text = ""
        for index in range(row_count):
            row = rows.nth(index)
            if row.is_visible():
                row_text = " ".join((row.inner_text(timeout=timeout) or "").split())
                break

        if not row_text:
            raise AssertionError(f"No visible row found for '{label}'")
        if ":" not in row_text:
            raise AssertionError(f"Unable to parse value for '{label}'. Row text: '{row_text}'")
        value = row_text.split(":", 1)[1].strip()
        if not value:
            raise AssertionError(f"Value for '{label}' is empty")
        return value

    def _assert_currency_or_none(self, label: str, value: str) -> None:
        if value.lower() == "none":
            return
        if not re.fullmatch(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})", value):
            raise AssertionError(
                f"Invalid value for '{label}'. Expected currency like $0.00 or 'None', got: '{value}'"
            )

    def _assert_percentage_or_none(self, label: str, value: str) -> None:
        if value.lower() == "none":
            return
        if not re.fullmatch(r"\d+(?:\.\d{2})%", value):
            raise AssertionError(
                f"Invalid value for '{label}'. Expected percentage like 24.00% or 'None', got: '{value}'"
            )

    def assert_tms_financial_values_valid(self, timeout: int = 10000) -> None:
        logger.info("Validating TMS tax rates and gain budget values are non-null and formatted")
        self.assert_federal_terms_valid(timeout=timeout)
        self.assert_gain_budgets_valid(timeout=timeout)

    def assert_federal_terms_valid(self, timeout: int = 10000) -> tuple[str, str]:
        self.open_tax_management_service(timeout=timeout)
        federal_short_term = self._value_for_label("Federal Short Term:", timeout=timeout)
        federal_long_term = self._value_for_label("Federal Long Term:", timeout=timeout)

        self._assert_percentage_or_none("Federal Short Term:", federal_short_term)
        self._assert_percentage_or_none("Federal Long Term:", federal_long_term)

        logger.info(
            f"Federal tax rates validated | Federal Short={federal_short_term} | "
            f"Federal Long={federal_long_term}"
        )
        return federal_short_term, federal_long_term

    def assert_gain_budgets_valid(self, timeout: int = 10000) -> tuple[str, str]:
        self.open_tax_management_service(timeout=timeout)
        short_term_gain_budget = self._value_for_label("Short Term Gain Budget:", timeout=timeout)
        long_term_gain_budget = self._value_for_label("Long Term Gain Budget:", timeout=timeout)

        self._assert_currency_or_none("Short Term Gain Budget:", short_term_gain_budget)
        self._assert_currency_or_none("Long Term Gain Budget:", long_term_gain_budget)

        logger.info(
            f"Gain budgets validated | Short Budget={short_term_gain_budget} | "
            f"Long Budget={long_term_gain_budget}"
        )
        return short_term_gain_budget, long_term_gain_budget

    def assert_account_fields_alphanumeric_and_not_editable(self, timeout: int = 10000) -> tuple[str, str]:
        self.wait_for_element(self.account_name_header, timeout=timeout)
        self.wait_for_element(self.account_number_header, timeout=timeout)

        account_name = " ".join((self.account_name_header.first.inner_text(timeout=timeout) or "").split())
        account_number_text = " ".join(
            (self.account_number_header.first.inner_text(timeout=timeout) or "").split()
        )

        if not account_name:
            raise AssertionError("Account Name header text is empty")

        if not re.fullmatch(r"[A-Za-z0-9, ]+", account_name):
            raise AssertionError(
                f"Invalid Account Name: '{account_name}'. Expected alphanumeric characters, spaces, and commas only"
            )

        account_number_match = re.search(r"Account\s*#\s*([A-Za-z0-9]+)", account_number_text, re.IGNORECASE)
        account_number = account_number_match.group(1) if account_number_match else account_number_text
        if not re.fullmatch(r"[A-Za-z0-9]+", account_number):
            raise AssertionError(
                f"Invalid Account Number: '{account_number_text}'. Expected format like 'Account #9999981'"
                " or an alphanumeric value"
            )

        editable_control = self.page.locator(
            "//div[@class='account-information-content']//input[not(@readonly) and not(@disabled)]"
            " | //div[@class='account-information-content']//textarea[not(@readonly) and not(@disabled)]"
            " | //div[@class='account-information-content']//*[@contenteditable='true']"
        ).first
        if editable_control.count() > 0 and editable_control.is_visible(timeout=timeout):
            raise AssertionError("Account information section has editable controls, but expected read-only")

        logger.info(
            f"Account fields validated | Account Name={account_name} | Account Number={account_number}"
        )
        return account_name, account_number
