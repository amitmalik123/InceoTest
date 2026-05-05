import re
from pathlib import Path

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class DocumentVaultPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._init_locators()

    def _init_locators(self) -> None:
        self.form_root = self.active_root()

        # New navbar top-level navigation element
        self.statements_reports_link: Locator = self.page.locator('//a[text()="Statements & Reports"]')
        self.service_center_link: Locator = self.page.locator('//a[text()="Service Center"]')
        self.tax_and_reporting_link: Locator = self.page.locator('//a[text()="Tax and Reporting"]')
        self.document_vault_nav_link: Locator = self.page.locator('//a[text()="Document Vault"]')
        self.document_type_dropdown: Locator = self.form_root.locator('//span[text()="Select a document type"]')
        self.qpr_document_type_option: Locator = self.form_root.locator(
            '//span[text()="Quarterly Performance Reports (QPR)"]'
        )
        self.year_dropdown: Locator = self.form_root.locator('//select[@name="ddYear"]')
        self.quarter_dropdown: Locator = self.form_root.locator('//select[@name="ddQtrMonth"]')
        self.document_dropdown: Locator = self.form_root.locator('//select[@name="ddDocument"]')
        self.find_button: Locator = self.form_root.locator("//input[@name='btSearch']")

        self.clients_tab: Locator = self.form_root.locator("//a[text()='Clients']")
        self.client_list_search_input: Locator = self.form_root.locator("//input[@name='search_input']")
        self.search_button: Locator = self.form_root.locator("//button[@class='searchbutton']")
        self.document_vault_link: Locator = self.form_root.locator("//li//a[text()='Document Vault']")
        self.document_vault_dropdown: Locator = self.form_root.locator(
            "//div[@class='ui-genworthdropdownpanel-buttonContent']"
        )
        self.date_filter_all_option: Locator = self.form_root.locator(
            "//div[@class='ui-genworthdropdownpanel-dropdownContent']//div[text()='All']"
        )
        self.list_of_headers: Locator = self.form_root.locator(
            "//*[@role='tab' and not(ancestor-or-self::*[contains(@style, 'display: none')])]/a"
        )
        self.header_expander: Locator = self.form_root.locator(
            "//div[@aria-disabled='false']//h3[@aria-expanded='false']"
            "//span[@class='ui-accordion-header-icon ui-icon ui-icon-triangle-1-e'"
            " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
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
            "//h3[@aria-expanded='true']//span[contains(@class,'ui-accordion-header-icon')"
            " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
        )
        self.all_checkboxes: Locator = self.form_root.locator('//input[@type="checkbox"]')
        self.select_all_button: Locator = self.form_root.locator('//a[text()="Select All"]')
        self.clear_all_button: Locator = self.form_root.locator('//a[text()="Clear All"]')
        self.view_selected_as_one_button: Locator = self.form_root.locator('//input[@id="btSelectOneUp"]')
        self.save_selected_button: Locator = self.form_root.locator('//input[@id="btDownloadUp"]')
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
        heading_xpath = '//span[normalize-space()="Client Document and Reports Vault"]'

        candidates = [self.active_root(), self.page] + [
            frame for frame in self.page.frames if frame != self.page.main_frame
        ]
        for candidate in candidates:
            try:
                if self.is_visible(candidate.locator(heading_xpath), timeout=5000):
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
            ("DocumentTypeDropdown", '//span[text()="Select a document type"]'),
            ("yeardropdown",         '//select[@name="ddYear"]'),
            ("quarterdropdown",      '//select[@name="ddQtrMonth"]'),
            ("documentdropdown",     '//select[@name="ddDocument"]'),
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

    def select_document_type_quarterly_performance_reports(self, timeout: int = 15000) -> None:
        """Select Quarterly Performance Reports (QPR) from the Document Type dropdown."""
        logger.info("Selecting Document Type: Quarterly Performance Reports (QPR)")

        candidates = [self.page] + list(self.page.frames)
        document_type_select = None
        for candidate in candidates:
            try:
                locator = candidate.locator('//select[@name="ddDocType"]').first
                if self.is_visible(locator, timeout=1200):
                    document_type_select = locator
                    break
            except Exception:
                continue

        if document_type_select is None:
            raise AssertionError("Document Type select ddDocType is not visible")

        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        self.wait_for_element(document_type_select, timeout=timeout)
        logger.info("Document Type dropdown is ready, waiting 2 seconds for visibility...")
        self.page.wait_for_timeout(2000)  # Slow down to show the dropdown
        
        logger.info("Clicking on Document Type dropdown...")
        self.select_option(
            document_type_select,
            value="QPR",
            timeout=timeout,
        )
        logger.info("Selection executed, waiting 3 seconds to show the selected value...")
        self.page.wait_for_timeout(3000)  # Extended wait to show selected value
        
        self.wait_for_all_spinners_to_disappear(timeout=timeout)
        logger.info("Additional 2 second wait for final confirmation...")
        self.page.wait_for_timeout(2000)  # Final wait for visual confirmation
        
        logger.info("Document Type selected: Quarterly Performance Reports (QPR)")

    def validate_find_button_enabled(self, timeout: int = 10000) -> bool:
        """Validate that the Find/Search button is enabled after document selection."""
        logger.info("Validating Find button is enabled for user interaction")

        candidates = [self.page] + list(self.page.frames)
        find_button = None
        for candidate in candidates:
            try:
                locator = candidate.locator("//input[@name='btSearch']").first
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

        # Assertion 2: Button must not be disabled.
        is_disabled = find_button.evaluate("element => element.hasAttribute('disabled') || element.disabled")
        if is_disabled:
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

        # Grid actions are lower on the page; scroll first so Select All can render.
        self.page.mouse.wheel(0, 700)

        xpaths = [
            "//a[normalize-space()='Select All']",
            "//a[contains(normalize-space(), 'Select All')]",
        ]
        candidates = [self.page] + list(self.page.frames)

        for candidate in candidates:
            for xpath in xpaths:
                try:
                    locator = candidate.locator(xpath).first
                    if self.is_visible(locator, timeout=1500):
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
            "//a[normalize-space()='Clear All']",
            "//a[contains(normalize-space(), 'Clear All')]",
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
        total_xpath = "//div[contains(@class,'checker')]/span"
        checked_xpath = "//div[contains(@class,'checker')]/span[contains(@class,'checked')]"

        candidates = [self.page] + list(self.page.frames)
        for candidate in candidates:
            try:
                total_locator = candidate.locator(total_xpath)
                total_count = total_locator.count()
                if total_count > 0:
                    checked_count = candidate.locator(checked_xpath).count()
                    return total_count, checked_count
            except Exception:
                continue

        raise AssertionError("No filter checkboxes found")

    def validate_button_states_based_on_filter_selection(self, timeout: int = 10000) -> bool:
        """Validate View selected as one and Save selected buttons are enabled when filters are selected."""
        self.click_select_all_filters(timeout=timeout)

        candidates = [self.page] + list(self.page.frames)
        view_btn = None
        save_btn = None
        for candidate in candidates:
            try:
                v = candidate.locator('//input[@id="btSelectOneUp"]').first
                s = candidate.locator('//input[@id="btDownloadUp"]').first
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
