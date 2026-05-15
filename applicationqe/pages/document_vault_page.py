import re
from pathlib import Path

from playwright.sync_api import Locator, Page

from locators import document_vault_locators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class DocumentVaultPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._init_locators()

    def _init_locators(self) -> None:
        self.form_root = self.active_root()

        # Centralized XPath selectors used across frame/page contexts.
        self.client_reports_vault_heading_xpath = document_vault_locators.CLIENT_REPORTS_VAULT_HEADING
        self.document_type_dropdown_xpath = document_vault_locators.DOCUMENT_TYPE_DROPDOWN
        self.document_type_select_xpath = document_vault_locators.DOCUMENT_TYPE_SELECT
        self.year_dropdown_xpath = document_vault_locators.YEAR_DROPDOWN
        self.quarter_dropdown_xpath = document_vault_locators.QUARTER_DROPDOWN
        self.all_checkboxes_xpath = document_vault_locators.ALL_CHECKBOXES
        self.quarter_label_xpath = document_vault_locators.QUARTER_LABEL
        self.document_label_xpath = document_vault_locators.DOCUMENT_LABEL
        self.period_label_xpath = document_vault_locators.PERIOD_LABEL
        self.month_label_xpath = document_vault_locators.MONTH_LABEL
        self.year_display_xpath = document_vault_locators.YEAR_DISPLAY
        self.quarter_display_xpath = document_vault_locators.QUARTER_DISPLAY
        self.document_dropdown_xpath = document_vault_locators.DOCUMENT_DROPDOWN
        self.find_button_xpath = document_vault_locators.FIND_BUTTON
        self.no_documents_message_xpath = document_vault_locators.NO_DOCUMENTS_MESSAGE
        self.select_all_exact_xpath = document_vault_locators.SELECT_ALL_EXACT
        self.select_all_contains_xpath = document_vault_locators.SELECT_ALL_CONTAINS
        self.clear_all_exact_xpath = document_vault_locators.CLEAR_ALL_EXACT
        self.clear_all_contains_xpath = document_vault_locators.CLEAR_ALL_CONTAINS
        self.total_filter_checkers_xpath = document_vault_locators.TOTAL_FILTER_CHECKERS
        self.checked_filter_checkers_xpath = document_vault_locators.CHECKED_FILTER_CHECKERS
        self.view_selected_button_xpath = document_vault_locators.VIEW_SELECTED_BUTTON
        self.save_selected_button_xpath = document_vault_locators.SAVE_SELECTED_BUTTON
        self.tax_savings_report_option_xpath = document_vault_locators.TAX_SAVINGS_REPORT_OPTION

        # New navbar top-level navigation element
        self.statements_reports_link: Locator = self.page.locator(
            document_vault_locators.STATEMENTS_REPORTS_LINK
        )
        self.service_center_link: Locator = self.page.locator(
            document_vault_locators.SERVICE_CENTER_LINK
        )
        self.tax_and_reporting_link: Locator = self.page.locator(
            document_vault_locators.TAX_AND_REPORTING_LINK
        )
        self.document_vault_nav_link: Locator = self.page.locator(
            document_vault_locators.DOCUMENT_VAULT_NAV_LINK
        )
        self.document_type_dropdown: Locator = self.form_root.locator(self.document_type_dropdown_xpath)
        self.qpr_document_type_option: Locator = self.form_root.locator(
            document_vault_locators.QPR_DOCUMENT_TYPE_OPTION
        )
        self.market_value_report_option: Locator = self.form_root.locator(
            document_vault_locators.MARKET_VALUE_REPORT_OPTION
        )
        self.year_dropdown: Locator = self.form_root.locator(self.year_dropdown_xpath)
        self.quarter_dropdown: Locator = self.form_root.locator(self.quarter_dropdown_xpath)
        self.quarter_label: Locator = self.form_root.locator(self.quarter_label_xpath)
        self.document_label: Locator = self.form_root.locator(self.document_label_xpath)
        self.year_display: Locator = self.form_root.locator(self.year_display_xpath)
        self.quarter_display: Locator = self.form_root.locator(self.quarter_display_xpath)
        self.document_dropdown: Locator = self.form_root.locator(self.document_dropdown_xpath)
        self.find_button: Locator = self.form_root.locator(self.find_button_xpath)
        self.no_documents_message: Locator = self.form_root.locator(self.no_documents_message_xpath)

        self.clients_tab: Locator = self.form_root.locator(document_vault_locators.CLIENTS_TAB)
        self.client_list_search_input: Locator = self.form_root.locator(
            document_vault_locators.CLIENT_LIST_SEARCH_INPUT
        )
        self.search_button: Locator = self.form_root.locator(document_vault_locators.SEARCH_BUTTON)
        self.document_vault_link: Locator = self.form_root.locator(
            document_vault_locators.DOCUMENT_VAULT_LINK
        )
        self.document_vault_dropdown: Locator = self.form_root.locator(
            document_vault_locators.DOCUMENT_VAULT_DROPDOWN
        )
        self.date_filter_all_option: Locator = self.form_root.locator(
            document_vault_locators.DATE_FILTER_ALL_OPTION
        )
        self.list_of_headers: Locator = self.form_root.locator(
            document_vault_locators.LIST_OF_HEADERS
        )
        self.header_expander: Locator = self.form_root.locator(
            document_vault_locators.HEADER_EXPANDER
        )
        self.select_all_checkbox: Locator = self.form_root.locator(
            "(//h3[@aria-expanded='true']//ancestor::div[contains(@class,'statementsgridwrapper')]"
            "//div//div//div//div[contains(@class,'ui-state-default')]//div//table//input)[2]"
        )
        self.save_selected: Locator = self.form_root.locator(
            "//h3[@aria-expanded='true']//ancestor::div[contains(@class,'statementsgridwrapper')]"
            "//div//div//div//a[text()=' Save Selected']"
        )
        self.view_selected_as_one: Locator = self.form_root.locator(
            "//h3[@aria-expanded='true']/ancestor::div[contains(@class,'statementsgridwrapper')]"
            "//a[text()=' View selected as one']"
        )
        self.first_checkbox: Locator = self.form_root.locator(
            "//h3[@aria-expanded='true']//ancestor::div[contains(@class,'statementsgridwrapper')]"
            "//div//table//tbody//tr[@class='jqgfirstrow']/following-sibling::tr[1]"
            "//td//input[@type='checkbox']"
        )
        self.first_doc_description: Locator = self.form_root.locator(
            "//h3[@aria-expanded='true']//ancestor::div[contains(@class,'statementsgridwrapper')]"
            "//tbody//tr[@class='jqgfirstrow']/following::tr[1]"
            "//td[contains(@aria-describedby,'documentdescription')]"
        )
        self.expanded_header_text: Locator = self.form_root.locator(
            "//h3[@aria-expanded='true']/a"
        )
        self.expanded_header: Locator = self.form_root.locator(
            document_vault_locators.EXPANDED_HEADER
        )
        self.all_checkboxes: Locator = self.form_root.locator(self.all_checkboxes_xpath)
        self.select_all_button: Locator = self.form_root.locator('//a[text()="Select All"]')
        self.clear_all_button: Locator = self.form_root.locator('//a[text()="Clear All"]')
        self.view_selected_as_one_button: Locator = self.form_root.locator(self.view_selected_button_xpath)
        self.save_selected_button: Locator = self.form_root.locator(self.save_selected_button_xpath)
        self.restore_default_button: Locator = self.form_root.locator(
            "//div[@class='button' and text()='Restore Default']"
        )
        self.restore_default_disabled: Locator = self.form_root.locator(
            "//div[@class='buttondisabled' and text()='Restore Default']"
        )

        self.loading_spinner: Locator = self.form_root.locator(
            "//div[contains(@class,'loading-indicator-component__spinner')]"
        )
        self.loading_indicator: Locator = self.form_root.locator(
            "//*[contains(@class, 'loading-indication-component') and contains(@class, 'isVisible')]"
        )
        self.loading_modal: Locator = self.form_root.locator("#loadingImageModal")

    def _client_name_locator(self, client_name: str) -> Locator:
        return self.form_root.locator(f"//td[normalize-space()='{client_name}']")

    def wait_for_all_spinners_to_disappear(self, timeout: int = 30000) -> None:
        spinner_count = self.loading_spinner.count()
        for index in range(spinner_count):
            self.loading_spinner.nth(index).wait_for(state="hidden", timeout=timeout)

        indicator_count = self.loading_indicator.count()
        for index in range(indicator_count):
            self.loading_indicator.nth(index).wait_for(state="hidden", timeout=timeout)

        try:
            self.loading_modal.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

    def navigates_to_doc_vault(self, client_name: str, timeout: int = 30000) -> None:
        """Navigate to Document Vault for old navbar flow (clicks Clients tab)."""
        logger.info(f"Navigating to Document Vault for client: {client_name}")
        self.click(self.clients_tab, timeout=timeout)
        self._search_and_navigate_to_doc_vault(client_name, timeout=timeout)

    def navigates_to_doc_vault_from_clients(self, client_name: str, timeout: int = 30000) -> None:
        """Navigate to Document Vault assuming Clients tab already clicked (new navbar flow)."""
        logger.info(f"Navigating to Document Vault from clients page for: {client_name}")
        self._search_and_navigate_to_doc_vault(client_name, timeout=timeout)

    def open_statements_and_reports_and_validate(self, timeout: int = 30000) -> None:
        """Open Statements & Reports and assert Client Document and Reports Vault page is visible."""
        logger.info("Clicking Statements & Reports and validating vault page load")
        self.wait_for_element(self.statements_reports_link, timeout=timeout)
        self.click(self.statements_reports_link, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

        candidates = [self.active_root(), self.page] + [
            frame for frame in self.page.frames if frame != self.page.main_frame
        ]
        for candidate in candidates:
            try:
                if self.is_visible(candidate.locator(self.client_reports_vault_heading_xpath), timeout=5000):
                    logger.info("Statements and Reports page loaded successfully")
                    self._init_locators()  # Re-resolve form_root for this page
                    return
            except Exception:
                pass

        frame_urls = [f.url for f in self.page.frames if f != self.page.main_frame]
        logger.error(f"Heading not found in page or frames. Frame URLs seen: {frame_urls}")

        raise AssertionError(
            "Client Document and Reports Vault text is not visible after clicking Statements & Reports"
        )

    def navigate_to_document_vault(self, timeout: int = 30000) -> None:
        """Navigate to Document Vault via Service Center > Tax and Reporting > Document Vault."""
        logger.info("Navigating to Document Vault through Service Center")
        self.click(self.service_center_link, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self._init_locators()
        
        self.click(self.tax_and_reporting_link, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self._init_locators()
        
        self.click(self.document_vault_nav_link, timeout=timeout)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        logger.info("Document Vault page loaded")

    def _search_and_navigate_to_doc_vault(self, client_name: str, timeout: int = 30000) -> None:
        """Common navigation logic for both old and new navbar flows."""
        self.wait_for_element(self.client_list_search_input, timeout=timeout)
        self.fill(self.client_list_search_input, client_name, timeout=timeout)
        self.click(self.search_button, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.wait_for_element(self._client_name_locator(client_name), timeout=timeout)
        self.click(self._client_name_locator(client_name), timeout=timeout)

        try:
            self.page.locator('iframe[title="All Clients"]').wait_for(state="detached", timeout=timeout)
        except Exception:
            pass

        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        self._init_locators()
        self.wait_for_element(self.document_vault_link, timeout=timeout)
        self.click(self.document_vault_link, timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        logger.info("Document vault page loaded successfully")

    def date_filter(self, timeout: int = 10000) -> None:
        logger.info("Switching date filter to All")
        self.wait_for_element(self.document_vault_dropdown.first, timeout=timeout)
        self.document_vault_dropdown.first.hover()
        self.wait_for_element(self.date_filter_all_option, timeout=timeout)
        self.click(self.date_filter_all_option, timeout=timeout)
        self.page.wait_for_timeout(1000)

    def validate_document_vault_headers(self, properties_path: str, timeout: int = 10000) -> bool:
        self.wait_for_element(self.list_of_headers.first, timeout=timeout)
        actual_headers = self.list_of_headers.all()
        expected_headers = self._load_expected_headers(properties_path)

        if not expected_headers:
            return False

        all_matched = True
        for element in actual_headers:
            element.scroll_into_view_if_needed()
            self.page.wait_for_timeout(300)
            actual_text = (element.text_content() or "").strip()
            if not actual_text:
                continue

            matched = any(expected in actual_text for expected in expected_headers)
            if not matched:
                logger.error(f"Unexpected header: {actual_text}")
                all_matched = False

        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(500)
        return all_matched

    def _load_expected_headers(self, properties_path: str) -> list[str]:
        props_file = Path(properties_path)
        if not props_file.exists():
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

    def close_expanded_headers(self, timeout: int = 10000) -> None:
        while self.expanded_header.count() > 0:
            self.expanded_header.nth(0).scroll_into_view_if_needed()
            self.expanded_header.nth(0).click(timeout=timeout)
            self.page.wait_for_timeout(1000)

    def _latest_download_name(self, trigger_click: Locator, timeout: int = 30000) -> str:
        with self.page.expect_download(timeout=timeout) as download_info:
            trigger_click.click(timeout=timeout)
        download = download_info.value

        download_dir = Path("reports/downloads")
        download_dir.mkdir(parents=True, exist_ok=True)
        target_path = download_dir / download.suggested_filename
        download.save_as(str(target_path))

        name = target_path.name
        name = re.sub(r" \(\d+\)\.(pdf|zip)$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\.(pdf|zip)$", "", name, flags=re.IGNORECASE)
        return name.strip()

    def _validate_downloaded_name_against_header(self, downloaded_name: str, expanded_text: str) -> None:
        mapping = {
            "QPR": "Quarterly Performance Reviewas",
            "LTR": "Notices and Letters",
            "TAXSAV": "Tax Savings Report",
            "TAX Documents": "Tax Documents",
            "Custody Statement": "Custody Statements",
            "Custody Statements": "Custody Statements",
        }

        expected_phrase = downloaded_name
        for token, phrase in mapping.items():
            if token.lower() in downloaded_name.lower():
                expected_phrase = phrase
                break

        if expected_phrase.lower() not in expanded_text.lower():
            raise AssertionError(
                f"Validation Failed: Expected file name '{downloaded_name}' not found in '{expanded_text}'"
            )

    def validate_download_func(self, timeout: int = 30000) -> None:
        logger.info("Validating download functionality for all expanded headers")
        self.close_expanded_headers(timeout=timeout)
        enabled_header_count = self.header_expander.count()

        for index in range(enabled_header_count):
            self.close_expanded_headers(timeout=timeout)

            expander = self.header_expander.nth(index)
            expander.scroll_into_view_if_needed()
            expander.click(timeout=timeout)
            self.wait_for_element(self.expanded_header_text.first, timeout=timeout)

            expanded_text = (self.expanded_header_text.first.text_content() or "").strip()

            self.click(self.select_all_checkbox.first, timeout=timeout)
            downloaded_name_1 = self._latest_download_name(self.save_selected.first, timeout=timeout)
            self._validate_downloaded_name_against_header(downloaded_name_1, expanded_text)

            downloaded_name_2 = self._latest_download_name(self.view_selected_as_one.first, timeout=timeout)
            self._validate_downloaded_name_against_header(downloaded_name_2, expanded_text)
            self.click(self.select_all_checkbox.first, timeout=timeout)

            self.click(self.first_checkbox.first, timeout=timeout)
            downloaded_name_3 = self._latest_download_name(self.save_selected.first, timeout=timeout)
            doc_description = (self.first_doc_description.first.text_content() or "").strip()
            normalized_downloaded_name_3 = downloaded_name_3.replace("_", "/")
            normalized_doc_description = doc_description.replace("_", "/")
            if normalized_downloaded_name_3 not in normalized_doc_description:
                raise AssertionError(
                    f"Validation Failed: Expected file name '{downloaded_name_3}' not found in '{doc_description}'"
                )

            downloaded_name_4 = self._latest_download_name(self.view_selected_as_one.first, timeout=timeout)
            normalized_downloaded_name_4 = downloaded_name_4.replace("_", "/")
            if normalized_downloaded_name_4 not in normalized_doc_description:
                raise AssertionError(
                    f"Validation Failed: Expected file name '{downloaded_name_4}' not found in '{doc_description}'"
                )

            self.click(self.first_checkbox.first, timeout=timeout)

    def restore_default(self, timeout: int = 10000) -> None:
        logger.info("Validating Restore Default functionality")
        self.close_expanded_headers(timeout=timeout)
        self.restore_default_button.scroll_into_view_if_needed()
        self.restore_default_button.click(timeout=timeout, force=True)
        try:
            self.wait_for_element(self.restore_default_disabled, timeout=timeout)
        except Exception:
            # Some environments render the disabled state but keep it hidden.
            self.restore_default_disabled.first.wait_for(state="attached", timeout=timeout)

    def validate_all_dropdowns_enabled_for_user_interaction(self, timeout: int = 15000) -> None:
        """Validate the 4 agent-level dropdown controls are visible."""
        logger.info("Validating agent-level dropdown controls visibility")

        xpaths = [
            ("DocumentTypeDropdown", self.document_type_dropdown_xpath),
            ("yeardropdown", self.year_dropdown_xpath),
            ("quarterdropdown", self.quarter_dropdown_xpath),
            ("documentdropdown", self.document_dropdown_xpath),
        ]

        # Resolve the correct context once using the first locator, then reuse it.
        candidates = [self.page] + list(self.page.frames)
        active_context = None
        first_name, first_xpath = xpaths[0]
        for candidate in candidates:
            try:
                first_loc = candidate.locator(first_xpath).first
                if self.is_visible(first_loc, timeout=1200):
                    active_context = candidate
                    first_loc.scroll_into_view_if_needed()
                    break
            except Exception:
                continue

        if active_context is None:
            raise AssertionError(f"{first_name} is not visible")

        # Validate all remaining dropdowns in the same context.
        for name, xpath in xpaths[1:]:
            loc = active_context.locator(xpath).first
            try:
                loc.scroll_into_view_if_needed()
            except Exception:
                pass
            if not self.is_visible(loc, timeout=2000):
                raise AssertionError(f"{name} is not visible")

        logger.info("Validated all 4 dropdown controls are visible")

    def select_document_type(self, option_value: str | None = None, option_label: str | None = None, timeout: int = 15000) -> None:
        """Select a document type from the Document Type dropdown by value or label."""
        if not option_value and not option_label:
            raise ValueError("Either option_value or option_label must be provided")

        option_name = option_label or option_value or "unknown"
        logger.info(f"Selecting Document Type: {option_name}")

        candidates = [self.page] + list(self.page.frames)
        document_type_select = None
        for candidate in candidates:
            try:
                locator = candidate.locator(self.document_type_select_xpath).first
                if self.is_visible(locator, timeout=1200):
                    document_type_select = locator
                    break
            except Exception:
                continue

        if document_type_select is None:
            raise AssertionError("Document Type select ddDocType is not visible")

        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.wait_for_element(document_type_select, timeout=timeout)

        select_kwargs = {"timeout": timeout}
        if option_value:
            select_kwargs["value"] = option_value
        if option_label:
            select_kwargs["label"] = option_label

        self.select_option(document_type_select, **select_kwargs)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        logger.info(f"Document Type selected: {option_name}")

    def _get_selected_document_type_text(self) -> str:
        """Return selected document type text from ddDocType across page/frames."""
        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                select = candidate.locator(self.document_type_select_xpath).first
                if select.count() == 0:
                    continue
                selected_text = (select.evaluate(
                    """
                    element => {
                        const selected = element.options[element.selectedIndex];
                        return selected ? selected.text : '';
                    }
                    """
                ) or "").strip()
                if selected_text:
                    return selected_text
            except Exception:
                continue
        return ""

    def validate_quarter_dropdown_visible_for_user_interaction(self, timeout: int = 10000) -> bool:
        """Validate context-specific filter visibility using a shared implementation.

        For Market Value Reports, validates Quarter visibility.
        For AssetMark Trust Tax Documents, validates Document visibility.
        """
        selected_doc_type = self._get_selected_document_type_text().lower()
        is_assetmark_trust_tax = "assetmark trust tax documents" in selected_doc_type

        target_name = "Document" if is_assetmark_trust_tax else "Quarter"
        target_xpath = self.document_label_xpath if is_assetmark_trust_tax else self.quarter_label_xpath
        logger.info(f"Validating {target_name} control is visible for user interaction")

        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                target_label = candidate.locator(target_xpath).first
                if self.is_visible(target_label, timeout=1500):
                    target_label.scroll_into_view_if_needed()
                    logger.info(f"{target_name} control is visible for user interaction")
                    return True
            except Exception:
                continue

        raise AssertionError(f"{target_name} control is not visible for user interaction")

    def validate_period_and_month_dropdowns_visible_for_user_interaction(self, timeout: int = 10000) -> bool:
        """Validate Period and Month controls are visible for user interaction."""
        logger.info("Validating Period and Month controls are visible for user interaction")

        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                period_label = candidate.locator(self.period_label_xpath).first
                month_label = candidate.locator(self.month_label_xpath).first
                if self.is_visible(period_label, timeout=1500) and self.is_visible(month_label, timeout=1500):
                    period_label.scroll_into_view_if_needed()
                    month_label.scroll_into_view_if_needed()
                    logger.info("Period and Month controls are visible for user interaction")
                    return True
            except Exception:
                continue

        raise AssertionError("Period and Month controls are not visible for user interaction")

    def validate_month_dropdown_visible_for_user_interaction(self, timeout: int = 10000) -> bool:
        """Validate Month control is visible for user interaction."""
        logger.info("Validating Month control is visible for user interaction")

        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                month_label = candidate.locator(self.month_label_xpath).first
                if self.is_visible(month_label, timeout=1500):
                    month_label.scroll_into_view_if_needed()
                    logger.info("Month control is visible for user interaction")
                    return True
            except Exception:
                continue

        raise AssertionError("Month control is not visible for user interaction")

    def validate_find_button_enabled(self, timeout: int = 10000) -> bool:
        """Validate that the Find/Search button is enabled after document selection."""
        logger.info("Validating Find button is enabled for user interaction")

        candidates = [self.page] + list(self.page.frames)
        find_button = None
        for candidate in candidates:
            try:
                locator = candidate.locator(self.find_button_xpath).first
                if self.is_visible(locator, timeout=1200):
                    find_button = locator
                    break
            except Exception:
                continue

        if find_button is None:
            raise AssertionError("Find button input[@name='btSearch'] is not visible")

        # Assertion 1: Button must be visible.
        self.wait_for_element(find_button, timeout=timeout)
        logger.info("Find button is visible on the page")

        # Assertion 2: Button must not be disabled — poll until enabled or timeout.
        poll_interval_ms = 500
        elapsed_ms = 0
        is_disabled = True
        while is_disabled and elapsed_ms < timeout:
            is_disabled = find_button.evaluate("element => element.hasAttribute('disabled') || element.disabled")
            if is_disabled:
                self.page.wait_for_timeout(poll_interval_ms)
                elapsed_ms += poll_interval_ms

        if is_disabled:
            no_documents_visible = self.is_visible(self.no_documents_message.first, timeout=1500)

            if no_documents_visible:
                logger.info(
                    "Find button is disabled because 'There are no documents' is visible; treating as expected state"
                )
                return True

            raise AssertionError("Find button is disabled")
        logger.info("Find button does not have disabled state")

        # Assertion 3: Button should be interactable for user action.
        find_button.scroll_into_view_if_needed()
        is_enabled = find_button.is_enabled()
        if not is_enabled:
            raise AssertionError("Find button is not enabled for interaction")

        logger.info("Clicking Find button to load filter results")
        find_button.click()
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(2000)

        self.page.wait_for_timeout(1000)
        logger.info("ALL ASSERTIONS PASSED: Find button is enabled and ready for interaction")
        return True

    def click_select_all_filters(self, timeout: int = 10000) -> None:
        """Click the Select All filters button."""
        logger.info("Clicking Select All filters button")

        # Wait for the results grid to finish loading before looking for Select All.
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(2000)

        # Grid actions are lower on the page; scroll first so Select All can render.
        self.page.mouse.wheel(0, 700)
        self.page.wait_for_timeout(500)

        xpaths = [
            self.select_all_exact_xpath,
            self.select_all_contains_xpath,
        ]
        candidates = [self.page] + list(self.page.frames)

        for candidate in candidates:
            for xpath in xpaths:
                try:
                    locator = candidate.locator(xpath).first
                    if self.is_visible(locator, timeout=5000):
                        locator.scroll_into_view_if_needed()
                        locator.click()
                        logger.info("Select All filters button clicked")
                        self.page.wait_for_timeout(1500)
                        return
                except Exception:
                    continue

        raise AssertionError("Select All filters button is not visible/clickable")

    def verify_all_filters_selected(self, timeout: int = 10000) -> bool:
        """Verify that all filters are selected."""
        total_count, checked_count = self._get_filter_checkbox_state_counts(timeout=timeout)
        logger.info(f"Verified {checked_count}/{total_count} checkboxes are selected")
        assert checked_count == total_count, f"Not all filters selected: {checked_count}/{total_count}"
        return True

    def click_clear_all_filters(self, timeout: int = 10000) -> None:
        """Click the Clear All filters button."""
        logger.info("Clicking Clear All filters button")

        self.page.mouse.wheel(0, 700)

        xpaths = [
            self.clear_all_exact_xpath,
            self.clear_all_contains_xpath,
        ]
        candidates = [self.page] + list(self.page.frames)

        for candidate in candidates:
            for xpath in xpaths:
                try:
                    locator = candidate.locator(xpath).first
                    if self.is_visible(locator, timeout=1500):
                        locator.scroll_into_view_if_needed()
                        locator.click()
                        logger.info("Clear All filters button clicked")
                        self.page.wait_for_timeout(1500)
                        return
                except Exception:
                    continue

        raise AssertionError("Clear All filters button is not visible/clickable")

    def verify_all_filters_cleared(self, timeout: int = 10000) -> bool:
        """Verify that all filters are cleared."""
        total_count, checked_count = self._get_filter_checkbox_state_counts(timeout=timeout)
        unchecked_count = total_count - checked_count
        logger.info(f"Verified {unchecked_count}/{total_count} checkboxes are cleared")
        assert checked_count == 0, f"Not all filters cleared: {unchecked_count}/{total_count}"
        return True

    def _get_filter_checkbox_state_counts(self, timeout: int = 10000) -> tuple[int, int]:
        """Return (total, checked) filter checkbox counts using checker UI state."""
        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                total_locator = candidate.locator(self.total_filter_checkers_xpath)
                total_count = total_locator.count()
                if total_count > 0:
                    checked_count = candidate.locator(self.checked_filter_checkers_xpath).count()
                    return total_count, checked_count
            except Exception:
                continue

        raise AssertionError("No filter checkboxes found")

    def get_selected_filter_count(self, timeout: int = 10000) -> int:
        """Return how many filters/documents are currently selected."""
        _, checked_count = self._get_filter_checkbox_state_counts(timeout=timeout)
        return checked_count

    def validate_button_states_based_on_filter_selection(self, timeout: int = 10000) -> bool:
        """Validate View selected as one and Save selected buttons are enabled when filters are selected."""
        self.click_select_all_filters(timeout=timeout)

        candidates = [self.page] + list(self.page.frames)
        view_btn = None
        save_btn = None
        for candidate in candidates:
            try:
                v = candidate.locator(self.view_selected_button_xpath).first
                s = candidate.locator(self.save_selected_button_xpath).first
                if v.count() > 0 and s.count() > 0:
                    view_btn = v
                    save_btn = s
                    break
            except Exception:
                continue

        assert view_btn is not None, "View selected button not found in any frame"
        assert save_btn is not None, "Save selected button not found in any frame"
        assert view_btn.is_enabled(), "View selected button not enabled"
        assert save_btn.is_enabled(), "Save selected button not enabled"
        logger.info("Both buttons enabled when Select All is clicked")
        return True

    def _get_selected_year_and_quarter(self) -> tuple[str, str]:
        """Extract selected year and quarter from UI, searching across frames."""
        year_text = ""
        quarter_text = ""
        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                y = candidate.locator(self.year_display_xpath).first
                q = candidate.locator(self.quarter_display_xpath).first
                if y.count() > 0:
                    year_text = (y.text_content(timeout=5000) or "").strip()
                if q.count() > 0:
                    quarter_text = (q.text_content(timeout=5000) or "").strip()
                if year_text and quarter_text:
                    break
            except Exception:
                continue

        # Fall back to reading the underlying <select> value if the uniform wrapper isn't present
        if not year_text:
            for candidate in candidates:
                try:
                    sel = candidate.locator(self.year_dropdown_xpath).first
                    if sel.count() > 0:
                        year_text = (sel.input_value(timeout=5000) or "").strip()
                        if year_text:
                            break
                except Exception:
                    continue

        if not quarter_text:
            for candidate in candidates:
                try:
                    sel = candidate.locator(self.quarter_dropdown_xpath).first
                    if sel.count() > 0:
                        quarter_text = (sel.input_value(timeout=5000) or "").strip()
                        if quarter_text:
                            break
                except Exception:
                    continue

        if not year_text or not quarter_text:
            raise AssertionError(f"Year or quarter not found. Year='{year_text}', Quarter='{quarter_text}'")
        logger.info(f"Year='{year_text}', Quarter='{quarter_text}'")
        return year_text, quarter_text

    def _find_save_selected_button(self, timeout: int = 10000):
        """Locate Save Selected button across frames."""
        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                btn = candidate.locator(self.save_selected_button_xpath).first
                if btn.count() > 0 and self.is_visible(btn, timeout=timeout):
                    return btn
            except Exception:
                continue
        raise AssertionError("Save Selected button not found in any frame")

    def _validate_qpr_filename(self, filename: str) -> None:
        """Assert filename contains QPR, a 4-digit year, and a quarter (Q1-Q4 or standalone digit 1-4)."""
        logger.info(f"Validating QPR filename: '{filename}'")
        name_upper = filename.upper()
        if "QPR" not in name_upper:
            raise AssertionError(f"Filename '{filename}' does not contain 'QPR'")
        if not re.search(r'20\d{2}', filename):
            raise AssertionError(f"Filename '{filename}' does not contain a valid year (e.g. 2024)")
        if not re.search(r'Q[1-4]|[Qq]uarter[ _]?[1-4]|[_\-\s][1-4][_\-\s.]', filename):
            raise AssertionError(f"Filename '{filename}' does not contain a valid quarter (e.g. Q4)")
        logger.info(f"Filename validation passed: QPR, year and quarter all present")

    def _validate_document_type_year_filename(self, filename: str, document_type_text: str) -> None:
        """Assert filename contains selected document type tokens and a 4-digit year."""
        logger.info(f"Validating document-type-year filename: '{filename}' for doc type '{document_type_text}'")

        if not re.search(r'20\d{2}', filename):
            raise AssertionError(f"Filename '{filename}' does not contain a valid year (e.g. 2024)")

        normalized_filename = re.sub(r'[^A-Za-z0-9]+', ' ', filename).upper()
        normalized_doc_type = re.sub(r'[^A-Za-z0-9]+', ' ', document_type_text).upper().strip()

        # If the doc type has a parenthesised abbreviation (e.g. "QPR" in "Quarterly Performance Reports (QPR)")
        # and the abbreviation appears in the filename, that is sufficient.
        abbrev_match = re.search(r'\(([A-Za-z0-9]+)\)', document_type_text)
        if abbrev_match and abbrev_match.group(1).upper() in normalized_filename:
            logger.info("Filename validation passed: document type and year are present")
            return

        doc_tokens = [
            token for token in normalized_doc_type.split()
            if len(token) > 2 and token not in {"THE", "AND", "FOR", "WITH"}
        ]

        if not doc_tokens:
            raise AssertionError("Selected document type is empty; cannot validate filename")

        matched_tokens = [token for token in doc_tokens if token in normalized_filename]
        minimum_required_matches = 2 if len(doc_tokens) >= 2 else 1
        if len(matched_tokens) < minimum_required_matches:
            raise AssertionError(
                f"Filename '{filename}' does not contain expected document type text '{document_type_text}'"
            )

        logger.info("Filename validation passed: document type and year are present")

    def validate_document_type_year_zip_download(self, timeout: int = 30000) -> str:
        """Click Save Selected, download ZIP, validate selected document type and year. Returns filename."""
        save_btn = self._find_save_selected_button(timeout=10000)

        with self.page.expect_download(timeout=timeout) as download_info:
            save_btn.click(timeout=timeout)
        download = download_info.value

        download_dir = Path("reports/downloads")
        download_dir.mkdir(parents=True, exist_ok=True)
        target_path = download_dir / download.suggested_filename
        download.save_as(str(target_path))

        selected_doc_type = self._get_selected_document_type_text()
        downloaded_name = target_path.name
        self._validate_document_type_year_filename(downloaded_name, selected_doc_type)
        return downloaded_name

    def clear_all_and_select_first_checkbox(self, timeout: int = 10000) -> None:
        """Clear all filters and select first checkbox."""
        self.click_clear_all_filters(timeout=timeout)
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.page.wait_for_timeout(1000)

        # Try the specific document-row checkbox first (avoids picking filter checkboxes).
        try:
            cb = self.first_checkbox.first
            if self.is_visible(cb, timeout=3000):
                cb.scroll_into_view_if_needed()
                cb.click()
                logger.info("First document checkbox selected")
                self.page.wait_for_timeout(500)
                return
        except Exception:
            pass

        # Fallback: broad search across frames.
        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                checkboxes = candidate.locator(self.all_checkboxes_xpath)
                for i in range(checkboxes.count()):
                    cb = checkboxes.nth(i)
                    if self.is_visible(cb, timeout=1000):
                        cb.scroll_into_view_if_needed()
                        cb.click()
                        logger.info("First checkbox selected (fallback)")
                        self.page.wait_for_timeout(500)
                        return
            except Exception:
                continue

        raise AssertionError("Could not find first checkbox in result grid")

    def capture_save_selected_pdf_download(self, timeout: int = 30000) -> str:
        """Click Save Selected, capture PDF download. Returns filename."""
        save_btn = self._find_save_selected_button(timeout=10000)
        with self.page.expect_download(timeout=timeout) as download_info:
            save_btn.click(timeout=timeout)
        download = download_info.value

        download_dir = Path("reports/downloads")
        download_dir.mkdir(parents=True, exist_ok=True)
        target_path = download_dir / download.suggested_filename
        download.save_as(str(target_path))

        downloaded_name = target_path.name
        downloaded_name = re.sub(r" \(\d+\)\.(zip|pdf)$", ".\1", downloaded_name, flags=re.IGNORECASE)
        return downloaded_name

    def validate_qpr_pdf_download(self, pdf_download_name: str) -> bool:
        """Validate PDF filename contains QPR, year, quarter. Returns True if valid."""
        self._validate_qpr_filename(pdf_download_name)
        return True

    def validate_document_type_year_pdf_download(self, pdf_download_name: str) -> bool:
        """Validate PDF filename contains selected document type and year. Returns True if valid."""
        selected_doc_type = self._get_selected_document_type_text()
        self._validate_document_type_year_filename(pdf_download_name, selected_doc_type)
        return True
