from pathlib import Path

from playwright.sync_api import Locator, Page

from config.settings import get_settings
from locators.PR import rgl_locators
from pages.PR.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class RGLPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._init_locators()

    def _init_locators(self) -> None:
        """Initialize locators using active_root for both iframe and non-iframe scenarios.
        
        The active_root() method automatically detects:
        - New navbar: Returns iframe context ("All Clients" iframe)
        - Old navbar: Returns main page context
        
        All locators wrapped with form_root work in both contexts seamlessly.
        """
        # Get the active root context (iframe or main page)
        self.form_root = self.active_root()
        
        # Navigation links
        self.clients_tab: Locator = self.form_root.locator(rgl_locators.CLIENTS_TAB)
        self.gain_loss_link: Locator = self.form_root.locator(rgl_locators.GAIN_LOSS_LINK)
        self.account_information_link: Locator = self.form_root.locator(
            rgl_locators.ACCOUNT_INFORMATION_LINK
        )
        self.account_list_link: Locator = self.form_root.locator(rgl_locators.ACCOUNT_LIST_LINK)
        
        # Buttons and inputs
        self.search_button: Locator = self.form_root.locator(rgl_locators.SEARCH_BUTTON)
        
        # Search input by name attribute
        self.client_list_search_input: Locator = self.form_root.locator(
            rgl_locators.CLIENT_LIST_SEARCH_INPUT
        )
        
        # Additional locators
        self.cash_advantage_checkbox: Locator = self.page.locator(
            rgl_locators.CASH_ADVANTAGE_CHECKBOX
        )
        self.cash_advantage_label: Locator = self.page.locator(rgl_locators.CASH_ADVANTAGE_LABEL)
        self.apply_button: Locator = self.page.locator(rgl_locators.APPLY_BUTTON)
        self.first_account_row: Locator = self.page.locator(rgl_locators.FIRST_ACCOUNT_ROW)
        self.first_non_cash_advantage_account_row: Locator = self.page.locator(
            rgl_locators.FIRST_NON_CASH_ADVANTAGE_ACCOUNT_ROW
        )
        self.learn_more_about_link: Locator = self.page.locator(rgl_locators.LEARN_MORE_ABOUT_LINK)
        self.cash_advantage_account: Locator = self.form_root.locator(
            rgl_locators.CASH_ADVANTAGE_ACCOUNT
        )
        self.mouse_over_date: Locator = self.form_root.locator(rgl_locators.MOUSE_OVER_DATE)
        self.all_option: Locator = self.form_root.locator(rgl_locators.ALL_OPTION)
        self.solution_types_dropdown: Locator = self.form_root.locator(
            rgl_locators.SOLUTION_TYPES_DROPDOWN
        )
        self.list_of_headers: Locator = self.form_root.locator(rgl_locators.LIST_OF_HEADERS)
        self.header_expander: Locator = self.form_root.locator(rgl_locators.HEADER_EXPANDER)
        self.proceeds_list: Locator = self.form_root.locator(rgl_locators.PROCEEDS_LIST)
        self.cost_basis_list: Locator = self.form_root.locator(rgl_locators.COST_BASIS_LIST)
        self.gain_loss_list: Locator = self.form_root.locator(rgl_locators.GAIN_LOSS_LIST)
        self.income_list: Locator = self.form_root.locator(rgl_locators.INCOME_LIST)
        self.expanded_header: Locator = self.form_root.locator(rgl_locators.EXPANDED_HEADER)
        self.print_button: Locator = self.form_root.locator(rgl_locators.PRINT_BUTTON)
        self.download_button: Locator = self.form_root.locator(rgl_locators.DOWNLOAD_BUTTON)
        self.csv_link: Locator = self.form_root.locator(rgl_locators.CSV_LINK)
        self.xls_link: Locator = self.form_root.locator(rgl_locators.XLS_LINK)
        self.individual_dropdown: Locator = self.form_root.locator(rgl_locators.INDIVIDUAL_DROPDOWN)
        self.individual_account: Locator = self.form_root.locator(rgl_locators.INDIVIDUAL_ACCOUNT)
        self.net_investment: Locator = self.form_root.locator(rgl_locators.NET_INVESTMENT)
        self.client_names: Locator = self.form_root.locator(rgl_locators.CLIENT_NAMES)
        self.net_column: Locator = self.page.locator(rgl_locators.NET_COLUMN)
        # Loading indicators - search in iframe context
        self.loading_spinner: Locator = self.form_root.locator(rgl_locators.LOADING_SPINNER)
        self.loading_indicator: Locator = self.form_root.locator(rgl_locators.LOADING_INDICATOR)
        self.loading_modal: Locator = self.form_root.locator(rgl_locators.LOADING_MODAL)

    def _client_name_locator(self, client_name: str) -> Locator:
        # Client name appears in search results inside the iframe
        return self.form_root.locator(f"//td[normalize-space()='{client_name}']")

    def _is_cash_advantage_selected(self) -> bool:
        checkbox_class = (self.cash_advantage_checkbox.get_attribute("class") or "").lower()
        checkbox_aria_checked = (self.cash_advantage_checkbox.get_attribute("aria-checked") or "").lower()
        if checkbox_aria_checked == "true":
            return True
        if any(token in checkbox_class for token in ["checked", "selected", "active"]):
            return True
        return False

    def _toggle_cash_advantage(self, timeout: int = 30000) -> None:
        # The underlying toggle can be hidden while the label remains visible/clickable.
        self.wait_for_element(self.cash_advantage_label, timeout=timeout)
        self.cash_advantage_label.scroll_into_view_if_needed()
        self.click(self.cash_advantage_label, timeout=timeout)

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

    def navigate_to_gain_loss_page(self, client_name: str, timeout: int = 30000) -> None:
        logger.info("Navigating to Gain/Loss page")
        current_url = self.page.url or ""
        if current_url.startswith("about:blank"):
            settings = get_settings()
            home_url = settings.get_app_config("ewm").get("home_url", settings.base_url)
            logger.info(f"Recovered from about:blank before RGL navigation, opening {home_url}")
            self.page.goto(home_url, timeout=timeout)
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

        self.click(self.clients_tab, timeout=timeout)
        self._search_and_navigate_to_gain_loss(client_name, timeout=timeout)

    def navigate_to_gain_loss_page_from_clients(self, client_name: str, timeout: int = 30000) -> None:
        """Navigate to the Gain/Loss page assuming we are already on the clients list page.
        Used by the new navbar flow where the clients tab has already been clicked."""
        logger.info("Navigating to Gain/Loss page (already on clients page)")
        self._search_and_navigate_to_gain_loss(client_name, timeout=timeout)

    def _search_and_navigate_to_gain_loss(self, client_name: str, timeout: int = 30000) -> None:
        self.wait_for_element(self.client_list_search_input, timeout=timeout)
        self.fill(self.client_list_search_input, client_name, timeout=timeout)
        self.click(self.search_button, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.wait_for_element(self._client_name_locator(client_name), timeout=timeout)
        self.click(self._client_name_locator(client_name), timeout=timeout)
        # Wait for "All Clients" iframe to detach - confirms we've fully left the clients list page
        try:
            self.page.locator('iframe[title="All Clients"]').wait_for(state="detached", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        # Now re-init - active_root() will correctly find the client detail content iframe
        self._init_locators()
        self.wait_for_element(self.gain_loss_link, timeout=timeout)
        self.click(self.gain_loss_link, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        logger.info("Gain/Loss page displayed")

    def navigate_account_information(self, timeout: int = 30000) -> None:
        logger.info("Navigating to account information for Cash Advantage account")
        self.click(self.clients_tab, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.wait_for_element(self.account_list_link, timeout=timeout)
        self.click(self.account_list_link, timeout=timeout)
        self.wait_for_element(self.solution_types_dropdown, timeout=timeout)
        self.solution_types_dropdown.hover()
        self.page.wait_for_timeout(1000)
        self.wait_for_element(self.cash_advantage_checkbox, state="attached", timeout=timeout)
        self.cash_advantage_label.scroll_into_view_if_needed()
        self.page.wait_for_timeout(2000)
        self._toggle_cash_advantage(timeout=timeout)
        self.page.wait_for_timeout(500)
        if not self._is_cash_advantage_selected():
            logger.info("Cash Advantage checkbox toggled off; selecting again before Apply")
            self._toggle_cash_advantage(timeout=timeout)
            self.page.wait_for_timeout(500)
        self.apply_button.wait_for(state="visible", timeout=timeout)
        self.apply_button.click(timeout=timeout)
        self.page.wait_for_timeout(4000)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(5000)
        self.wait_for_element(self.first_account_row, timeout=timeout)
        self.page.wait_for_timeout(3000)
        self.click(self.first_account_row, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(3000)
        try:
            self.wait_for_element(self.learn_more_about_link, timeout=timeout)
            logger.info("Self learn more about link is visible")
        except Exception as exc:
            raise AssertionError("Self learn more about link is not visible") from exc

    def navigate_account_information_non_cash_advantage(self, timeout: int = 30000) -> None:
        logger.info("Navigating to account information for non Cash Advantage account")
        self.click(self.clients_tab, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.wait_for_element(self.account_list_link, timeout=timeout)
        self.click(self.account_list_link, timeout=timeout)
        self.wait_for_element(self.solution_types_dropdown, timeout=timeout)
        self.solution_types_dropdown.hover()
        self.page.wait_for_timeout(1000)
        self.wait_for_element(self.cash_advantage_checkbox, state="attached", timeout=timeout)
        self.cash_advantage_label.scroll_into_view_if_needed()
        self.page.wait_for_timeout(1000)
        if self._is_cash_advantage_selected():
            logger.info("Cash Advantage checkbox is selected; unselecting for non-cash account flow")
            self._toggle_cash_advantage(timeout=timeout)
            self.page.wait_for_timeout(500)
        self.apply_button.wait_for(state="visible", timeout=timeout)
        self.apply_button.click(timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(3000)
        self.wait_for_element(self.first_non_cash_advantage_account_row, timeout=max(timeout, 45000))
        self.click(self.first_non_cash_advantage_account_row, timeout=max(timeout, 45000))
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(3000)
        if self.learn_more_about_link.first.is_visible(timeout=5000):
            raise AssertionError("Self learn more about link is visible")
        logger.info("Self learn more about link is not visible")

    def verify_bancorp_link_opens_updated_url(self, timeout: int = 30000) -> None:
        logger.info("Verifying updated Bancorp link opens in new tab")
        self.wait_for_element(self.learn_more_about_link, timeout=timeout)
        with self.page.context.expect_page() as new_page_info:
            self.click(self.learn_more_about_link, timeout=timeout)
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

        try:
            new_page.wait_for_url("**talea.thebancorp.com/**", timeout=15000)
        except Exception:
            # One retry in the same tab for transient navigation failures.
            if (new_page.url or "").startswith("chrome-error://"):
                new_page.reload(wait_until="domcontentloaded", timeout=timeout)
                new_page.wait_for_url("**talea.thebancorp.com/**", timeout=15000)

        current_url = new_page.url
        expected_url = "https://talea.thebancorp.com/"
        if not current_url.startswith(expected_url):
            raise AssertionError(
                f"Unexpected Bancorp URL. Expected prefix: {expected_url} got: {current_url}"
            )
        new_page.close()

    def verify_outdated_bancorp_url_not_present(self, timeout: int = 30000) -> None:
        logger.info("Verifying outdated Bancorp URL is not present")
        self.wait_for_element(self.learn_more_about_link, timeout=timeout)
        with self.page.context.expect_page() as new_page_info:
            self.click(self.learn_more_about_link, timeout=timeout)
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

        if (new_page.url or "").startswith("chrome-error://"):
            try:
                new_page.reload(wait_until="domcontentloaded", timeout=timeout)
            except Exception:
                pass

        current_url = new_page.url
        outdated_url = "https://cashadvantageadvisors.ebanking-services.com/eAM/Credential/Index?appId=beb&brand=cashadvantageadvisors"
        if current_url == outdated_url or current_url.startswith(outdated_url):
            raise AssertionError(
                f"Outdated Bancorp URL found: {current_url}"
            )
        logger.info(f"✓ Outdated URL not present. Current URL: {current_url}")
        new_page.close()

    def verify_no_bancorp_url_present(self, timeout: int = 30000) -> None:
        logger.info("Verifying no Bancorp URL is present")
        try:
            self.learn_more_about_link.wait_for(state="visible", timeout=5000)
            raise AssertionError("'Learn more about additional account information' link should not be present for non-Cash Advantage accounts")
        except Exception as e:
            if "should not be present" in str(e):
                raise
            logger.info("✓ No Bancorp link present - as expected for non-Cash Advantage accounts")

    def apply_date_filter_all(self, timeout: int = 10000) -> None:
        logger.info("Applying date filter: All")
        self.wait_for_element(self.mouse_over_date, timeout=timeout)
        self.mouse_over_date.hover()
        self.wait_for_element(self.all_option, timeout=timeout)
        self.click(self.all_option, timeout=timeout)
        self.page.wait_for_timeout(1000)

    def expand_all_headers(self, timeout: int = 10000) -> None:
        header_count = self.header_expander.count()
        if header_count == 0:
            return
        for index in range(header_count):
            self.header_expander.nth(index).click(timeout=timeout)

    def close_expanded_headers(self, timeout: int = 10000) -> None:
        while self.expanded_header.count() > 0:
            self.expanded_header.first.click(timeout=timeout)

    def assert_headers_present(self, properties_path: str, timeout: int = 10000) -> None:
        logger.info("Validating RGL headers against properties file")
        self.wait_for_element(self.list_of_headers.first, timeout=timeout)
        header_count = self.list_of_headers.count()
        if header_count == 0:
            raise AssertionError("No headers found on Gain/Loss page")

        expected_headers = self._load_expected_headers(properties_path)
        if not expected_headers:
            raise AssertionError("No expected headers found in properties file")

        all_matched = True
        for index in range(header_count):
            header = self.list_of_headers.nth(index)
            header.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            actual_text = (header.text_content() or "").strip()
            if not actual_text:
                continue

            if not self._matches_any_expected(actual_text, expected_headers):
                logger.error(f"Unexpected header: {actual_text}")
                all_matched = False

        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)

        if not all_matched:
            raise AssertionError("Header validation failed")

    def _load_expected_headers(self, properties_path: str) -> list[str]:
        props_file = Path(properties_path)
        if not props_file.exists():
            app_root = Path(__file__).resolve().parents[1]
            candidates = [
                app_root / properties_path,
                app_root / Path(properties_path).name,
                app_root / "tests" / "bdd" / "resources" / Path(properties_path).name,
            ]
            for candidate in candidates:
                if candidate.exists():
                    props_file = candidate
                    break
            else:
                raise FileNotFoundError(f"Properties file not found: {properties_path}")

        expected = []
        for line in props_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            _, value = line.split("=", 1)
            value = value.strip()
            if value:
                expected.append(value)
        return expected

    def _matches_any_expected(self, actual_text: str, expected_headers: list[str]) -> bool:
        for expected in expected_headers:
            if expected in actual_text:
                return True
        return False

    def assert_costbasis_proceeds_gainloss(self, timeout: int = 10000) -> None:
        logger.info("Validating Costbasis, Proceeds, Gain/Loss values")
        self.close_expanded_headers(timeout=timeout)
        self.wait_for_element(self.header_expander.first, timeout=timeout)
        self.page.wait_for_timeout(1000)

        list_header_expander = [self.header_expander.nth(i) for i in range(self.header_expander.count())]
        headers = [self.list_of_headers.nth(i) for i in range(self.list_of_headers.count())]

        for index, expander in enumerate(list_header_expander):
            self.close_expanded_headers(timeout=timeout)
            expander.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            header_name = ""
            if index < len(headers):
                header_name = (headers[index].text_content() or "").strip()
            logger.info(f"Expanding header {index}: {header_name}")
            expander.click(timeout=max(timeout, 20000))
            self.page.wait_for_timeout(1000)

            cost_basis_texts = [text.strip() for text in self.cost_basis_list.all_inner_texts()]
            proceeds_texts = [text.strip() for text in self.proceeds_list.all_inner_texts()]
            gain_loss_texts = [text.strip() for text in self.gain_loss_list.all_inner_texts()]
            income_texts = [text.strip() for text in self.income_list.all_inner_texts()]

            row_count = min(len(cost_basis_texts), len(proceeds_texts), len(gain_loss_texts))

            if row_count > 0:
                sum_cost_basis = 0.0
                sum_proceeds = 0.0
                sum_gain_loss = 0.0
                last_displayed_gain_loss = 0.0
                last_calculated_gain_loss = 0.0
                last_proceed = 0.0
                last_cost_basis = 0.0

                for row_index in range(row_count):
                    cost_text = cost_basis_texts[row_index]
                    proceeds_text = proceeds_texts[row_index]
                    gain_loss_text = gain_loss_texts[row_index]

                    if not cost_text or not proceeds_text or not gain_loss_text:
                        continue

                    cost_basis = self._parse_currency(cost_text)
                    proceeds = self._parse_currency(proceeds_text)
                    gain_loss = self._parse_currency(gain_loss_text)
                    calculated_gain_loss = proceeds - cost_basis

                    if row_index < row_count - 1:
                        sum_cost_basis += cost_basis
                        sum_proceeds += proceeds
                        sum_gain_loss += gain_loss

                    if round(calculated_gain_loss, 2) != round(gain_loss, 2):
                        logger.warning(
                            "Gain/Loss mismatch on row %s: proceeds=%s cost_basis=%s displayed=%s expected=%s",
                            row_index + 1,
                            proceeds,
                            cost_basis,
                            gain_loss,
                            calculated_gain_loss,
                        )

                    if row_index == row_count - 1:
                        last_displayed_gain_loss = self._round_2(gain_loss)
                        last_calculated_gain_loss = self._round_2(calculated_gain_loss)
                        last_proceed = self._round_2(proceeds)
                        last_cost_basis = self._round_2(cost_basis)

                total_cost_basis = self._round_2(sum_cost_basis)
                total_proceeds = self._round_2(sum_proceeds)
                total_gain_loss = self._round_2(sum_gain_loss)

                logger.info(
                    f"Header '{header_name}' totals: cost_basis={total_cost_basis} "
                    f"proceeds={total_proceeds} gain_loss={total_gain_loss} | "
                    f"summary: cost_basis={last_cost_basis} proceeds={last_proceed} "
                    f"gain_loss={last_calculated_gain_loss}"
                )

                if total_cost_basis != last_cost_basis:
                    logger.error(
                        f"Header '{header_name}' cost basis mismatch: total={total_cost_basis} "
                        f"summary={last_cost_basis}"
                    )
                    raise AssertionError("Costbasis total does not match summary row")
                if total_proceeds != last_proceed:
                    logger.error(
                        f"Header '{header_name}' proceeds mismatch: total={total_proceeds} "
                        f"summary={last_proceed}"
                    )
                    raise AssertionError("Proceeds total does not match summary row")
                if total_gain_loss != last_calculated_gain_loss:
                    logger.error(
                        f"Header '{header_name}' gain/loss mismatch: total={total_gain_loss} "
                        f"summary={last_calculated_gain_loss}"
                    )
                    raise AssertionError("Gain/Loss total does not match summary row")
            else:
                sum_proceeds = 0.0
                sum_income = 0.0
                last_proceed = 0.0
                last_income = 0.0

                row_count = min(len(proceeds_texts), len(income_texts))

                for row_index in range(row_count):
                    proceeds_text = proceeds_texts[row_index]
                    income_text = income_texts[row_index]

                    if not proceeds_text or not income_text:
                        continue

                    proceeds = self._parse_currency(proceeds_text)
                    income = self._parse_currency(income_text)

                    if round(proceeds, 2) != round(income, 2):
                        logger.warning(
                            "Proceeds/Income mismatch on row %s: proceeds=%s income=%s",
                            row_index + 1,
                            proceeds,
                            income,
                        )

                    if row_index < row_count - 1:
                        sum_proceeds += proceeds
                        sum_income += income

                    if row_index == row_count - 1:
                        last_proceed = self._round_2(proceeds)
                        last_income = self._round_2(income)

                total_proceeds = self._round_2(sum_proceeds)
                total_income = self._round_2(sum_income)

                logger.info(
                    f"Header '{header_name}' totals: proceeds={total_proceeds} "
                    f"income={total_income} | summary: proceeds={last_proceed} "
                    f"income={last_income}"
                )

                if total_proceeds != last_proceed:
                    raise AssertionError("Proceeds total does not match summary row")
                if total_income != last_income:
                    raise AssertionError("Income total does not match summary row")



    @staticmethod
    def _round_2(value: float) -> float:
        return round(value, 2)

    @staticmethod
    def _parse_currency(text: str) -> float:
        cleaned = (
            text.replace("(", "-")
            .replace(")", "")
            .replace("$", "")
            .replace(",", "")
            .strip()
        )
        if not cleaned:
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse currency from: '{text}'")
            return 0.0
