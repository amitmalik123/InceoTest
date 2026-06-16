from playwright.sync_api import Locator, Page, expect

from config.settings import get_settings
from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)

TRACKING_CENTER_PATH = "AccountsAnalysis/TrackingCenter/TrackingCenter"

class TrackingCenterPage(BasePage):
    
    PAGE_URL = "AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail"    

    def __init__(self, page: Page):
        super().__init__(page)
        self.form_root = self.active_root()
        self.search_box: Locator = self.form_root.locator("#client_search_input")
        self.search_button: Locator = self.form_root.locator("#searchbutton")
        self.work_item_description_label: Locator = self.form_root.locator(
            "xpath=//span[normalize-space(text())='Description:']/following-sibling::label"
        )
        self.detail_descriptions: Locator = self.form_root.locator(
            "xpath=//*[@id='TrackingCenterItemDetailNotesGrid']/tbody/tr/td[4]"
        )
        self.tracking_center_tab: Locator = self.form_root.locator(
            "xpath=(//a[@id='ctl00_rItems_hLink_2'] | //a[normalize-space()='Tracking Center' and not(@id)] | //a[@id='header_0_content_0_rItems_hLink_2' and contains(normalize-space(),'Tracking Center')])[1]"
        )
        self.action_items_tab: Locator = self.form_root.locator("a[href='/action-items']")
        self.tracking_center_grid: Locator = self.form_root.locator("#TrackingCenterGrid")
        self.tracking_center_rows: Locator = self.form_root.locator(
            "#TrackingCenterGrid tr:has(td[aria-describedby])"
        )
        self.esignature_link: Locator = self.page.get_by_role("link", name="eSignature")
        self.sign_buttons: Locator = self.page.locator("input[id^='btnSign']")
        self.account_src_label: Locator = None  # Will be set dynamically
        self.roth_str_label: Locator = page.get_by_text('Roth Conversion')
        self.logout_link: Locator = page.get_by_role('link', name='Logout')
        self.bodycontent_div: Locator = page.locator('div#BodyContent')

    def navigate(self) -> None:
        base_url = get_settings().base_url.rstrip("/")
        full_url = f"{base_url}/{TRACKING_CENTER_PATH}"
        logger.info(f"Navigating to tracking center page: {full_url}")
        self.page.goto(full_url, wait_until='domcontentloaded')
        self.page.wait_for_load_state('networkidle', timeout=30000)
        logger.info("Tracking center page loaded")

    def _resolve_tracking_center_root(self):
        """Resolve whether Tracking Center is rendered in iframe root or top page."""
        current_root = self.active_root()
        for root_name, root in (("active_root", current_root), ("page", self.page)):
            try:
                grid = root.locator("#TrackingCenterGrid")
                grid.first.wait_for(state="attached", timeout=30000)
                logger.info(f"Tracking Center grid found in {root_name}")
                return root
            except Exception:
                continue
        raise Exception("Tracking Center grid not found in active_root or page")

    def _get_matching_item_row(self, root, search_text: str) -> Locator:
        """Get the tracking center grid row matching the Sort Name text."""
        return root.locator(
            "#TrackingCenterGrid tr:has(td[aria-describedby='TrackingCenterGrid_SortName'])",
            has=root.locator(
                "td[aria-describedby='TrackingCenterGrid_SortName']",
                has_text=search_text,
            ),
        ).first

    def click_tracking_center_tab(self) -> None:
        logger.info("Clicking on tracking center tab")
        self.page.bring_to_front()
        base_url = get_settings().base_url.rstrip("/")
        expected_url = f"{base_url}/{TRACKING_CENTER_PATH}"

        root = self.active_root()
        tracking_center_tab = root.locator(
            "xpath=(//a[@id='ctl00_rItems_hLink_2'] | //a[normalize-space()='Tracking Center' and not(@id)] | //a[@id='header_0_content_0_rItems_hLink_2' and contains(normalize-space(),'Tracking Center')])[1]"
        )
        try:
            tracking_center_tab.wait_for(state="visible", timeout=10000)
            self.click(tracking_center_tab)
            logger.info("Tracking center tab clicked")
        except Exception:
            logger.warning("Tracking center tab not found, navigating directly to tracking center URL")
            self.page.goto(expected_url, wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        current_url = self.page.url
        if TRACKING_CENTER_PATH not in current_url:
            logger.warning(f"Wrong URL after tracking center click: {current_url}")
            logger.info(f"Force-redirecting to: {expected_url}")
            self.page.goto(expected_url, wait_until="domcontentloaded", timeout=30000)
        else:
            logger.info(f"Tracking center URL verified: {current_url}")

    def search_for_item_number(self, search_text: str) -> str:
        logger.info(f"Searching for item: {search_text}")
        root = self.active_root()
        search_box = root.locator("#client_search_input")
        search_button = root.locator("#searchbutton")

        max_retries = 3
        matching_row = None

        for attempt in range(1, max_retries + 1):
            logger.info(f"Search attempt {attempt}/{max_retries} for: {search_text}")
            search_box.wait_for(state="visible", timeout=30000)
            search_box.fill("")
            search_box.fill(search_text)
            self.click(search_button)
            self.page.wait_for_load_state("domcontentloaded", timeout=60000)
            self.page.wait_for_timeout(5000)

            root = self._resolve_tracking_center_root()
            tracking_center_grid = root.locator("#TrackingCenterGrid")
            tracking_center_grid.wait_for(state="attached", timeout=90000)
            self.page.wait_for_timeout(2000)

            matching_row = self._get_matching_item_row(root, search_text)
            try:
                matching_row.wait_for(state="visible", timeout=30000)
                break
            except Exception:
                if attempt < max_retries:
                    logger.warning(
                        f"Matching row not found on attempt {attempt}, retrying search..."
                    )
                else:
                    raise

        item_number_cell = matching_row.locator(
            "td[aria-describedby='TrackingCenterGrid_ExternalId']"
        )
        sort_name_cell = matching_row.locator(
            "td[aria-describedby='TrackingCenterGrid_SortName']"
        )

        item_number = (item_number_cell.inner_text() or "").strip()
        self.page.wait_for_timeout(3000)
        self.click(sort_name_cell)
        logger.info(f"Searched and opened item details for: {search_text} | Item Number: {item_number}")
        return item_number

    def get_work_item_description(self) -> str:
        self.work_item_description_label.wait_for(state="visible", timeout=30000)
        work_item_description = (self.work_item_description_label.inner_text() or "").strip()
        logger.info(f"Work Item Description: {work_item_description}")
        return work_item_description

    def fetch_description(self) -> str:
        descriptions = self.detail_descriptions.all()
        lines = []

        for index, description in enumerate(descriptions, start=1):
            text = (description.inner_text() or "").strip()
            if text:
                lines.append(f"{index}. {text}")

        result = "\n".join(lines)
        logger.info(f"Fetched Description(s):\n{result}")
        return result

    def navigate_to_item_detail(self, parent_b_number: str) -> None:
        """Navigate directly to the Tracking Center Item Detail page for the given parent B number."""
        logger.info(f"Navigating to item detail page for: {parent_b_number}")
        self.page.bring_to_front()
        base_url = get_settings().base_url.rstrip("/")
        item_detail_url = f"{base_url}/AccountsAnalysis/TrackingCenter/TrackingCenterItemDetail/{parent_b_number}?isParent=True"
        self.page.goto(item_detail_url, wait_until="domcontentloaded", timeout=60000)
        logger.info(f"Navigated to item detail: {self.page.url}")

    def validate_item_detail(self, expected_parent_b: str, expected_account_number: str) -> dict:
        """Validate Item Detail page: item number, description, and account in child grid."""
        logger.info("Validating Tracking Center Item Detail page")
        root = self.active_root()

        item_number_el = root.locator(".item-number .value")
        item_number_el.wait_for(state="visible", timeout=30000)
        actual_item_number = (item_number_el.text_content() or "").strip()
        logger.info(f"Item Number: expected={expected_parent_b}, actual={actual_item_number}")
        assert actual_item_number == expected_parent_b, (
            f"Item Number mismatch: expected '{expected_parent_b}', got '{actual_item_number}'"
        )

        description_el = root.locator(".description .label")
        description_el.wait_for(state="visible", timeout=15000)
        actual_description = (description_el.text_content() or "").strip()
        logger.info(f"Description text: {actual_description}")
        assert "New Account Bundle" in actual_description, (
            f"Description mismatch: expected 'New Account Bundle' in '{actual_description}'"
        )

        naa_row = root.locator(
            "#TrackingCenterChildItemDetailsGrid tr",
            has=root.locator("td.ui-td-externalDesc", has_text="New Account Application"),
        ).first
        naa_row.wait_for(state="visible", timeout=30000)
        account_cell = naa_row.locator("td.ui-td-account")
        actual_account = (account_cell.text_content() or "").strip()
        if expected_account_number:
            logger.info(f"Account #: expected={expected_account_number}, actual={actual_account}")
            assert expected_account_number in actual_account, (
                f"Account # mismatch: expected '{expected_account_number}' in '{actual_account}'"
            )
        else:
            logger.info(f"Account # check skipped (no activation). Actual: {actual_account}")

        logger.info("Item Detail validation PASSED")
        return {
            "item_number": actual_item_number,
            "description": actual_description,
            "account_number": actual_account,
        }

    def validate_description_text(self, expected_text: str, validation_name: str) -> None:
        """Assert that expected text exists in the item detail notes grid."""
        root = self.active_root()
        description_cells = root.locator(
            "td[aria-describedby='TrackingCenterItemDetailNotesGrid_description']"
        )
        description_cells.first.wait_for(state="visible", timeout=15000)

        matching_cell = description_cells.filter(has_text=expected_text)
        assert matching_cell.count() > 0, (
            f"Expected description text '{expected_text}' not found in notes grid"
        )

        self.highlight_and_screenshot(matching_cell.first, validation_name, color="green")
        logger.info(f"Validated '{expected_text}' present in notes grid - {validation_name}")

    def clickESignatureLink(self, role: str = "Agent") -> None:
        """Click the eSignature link on the Tracking Center page."""
        logger.info(f"[tracking-center] Clicking 'eSignature' link for role={role}")
        self.capture_additional_screenshot(name=f"esignature_link_before_{role}")

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

        try:
            self.esignature_link.wait_for(state="visible", timeout=30000)
        except Exception:
            logger.warning("[tracking-center] eSignature link not visible after 30s, reloading page and retrying")
            self.capture_additional_screenshot(name=f"esignature_link_not_found_{role}")
            self.page.reload(wait_until="domcontentloaded", timeout=30000)
            self.wait_for_timeout(3000)
            self.esignature_link.wait_for(state="visible", timeout=30000)

        try:
            self._heal_and_retry(self.esignature_link, lambda loc: loc.click())
        except Exception:
            logger.warning("[tracking-center] eSignature link click failed, falling back to JS click")
            self.esignature_link.evaluate("el => el.click()")
        self.wait_for_timeout(5000)

        self.sign_buttons.last.wait_for(state="visible", timeout=15000)
        sign_button = self.sign_buttons.last
        logger.info(f"[tracking-center] Clicking '{role}' Sign button")
        try:
            self._heal_and_retry(sign_button, lambda loc: loc.click())
        except Exception:
            logger.warning(f"[tracking-center] {role} Sign button click failed, falling back to JS click")
            sign_button.evaluate("el => el.click()")
        self.wait_for_timeout(5000)
        logger.info(f"[tracking-center] Clicked '{role}' Sign button successfully")

    def verify_account_src(self, expected: str) -> None:
        logger.info(f"Verifying account source: {expected}")
        self.account_src_label = self.page.get_by_text(expected)
        expect(self.account_src_label).to_have_text(expected)
        logger.info(f"Account source {expected} verified")

    def verify_roth_str(self, expected: str) -> None:
        logger.info(f"Verifying Roth STR: {expected}")
        expect(self.roth_str_label).to_have_text(expected)
        logger.info(f"Roth STR {expected} verified")

    def click_logout(self) -> None:
        logger.info("Clicking logout")
        self.logout_link.click()
        logger.info("Logout clicked")

    def click_bodycontent(self) -> None:
        logger.info("Clicking body content")
        self.bodycontent_div.click()

    def search_and_open_d_number(self, d_number: str, timeout: int = 30000) -> None:
        """Search for D-number and open the item details page."""
        logger.info(f"Searching for D-number: {d_number}")
        root = self.active_root()
        search_input = root.locator("#client_search_input")
        search_button = root.locator("#searchbutton")
        d_number_row = root.locator(f"tr:has-text('{d_number}')")

        # Enter D-number in search input
        search_input.wait_for(state="visible", timeout=timeout)
        search_input.fill(d_number)
        logger.info(f"D-number entered in search input: {d_number}")

        # Click search button
        search_button.click(timeout=timeout)
        logger.info("Search button clicked")

        # Wait for table row with D-number
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        try:
            d_number_row.wait_for(state="visible", timeout=timeout)
            logger.info(f"D-number table row visible: {d_number}")
        except Exception:
            logger.warning("D-number row not found, checking for single row fallback")
            all_rows = root.locator("tr").all()
            if len(all_rows) == 1:
                d_number_row = root.locator("tr").first
                logger.info("Using single table row as D-number row")
            else:
                raise AssertionError(f"Failed to find table row for D-number '{d_number}'")

        # Click row to open item details
        d_number_row.click(timeout=timeout)
        logger.info(f"D-number table row clicked: {d_number}")

        self.page.wait_for_load_state("networkidle", timeout=timeout)
        logger.info(f"D-Number search and open completed: {d_number}")

    def search_d_number(self, d_number: str, timeout: int = 30000) -> None:
        """Search for a D-number in Tracking Center and wait for search results."""
        logger.info(f"Searching for D-number: {d_number}")
        root = self.active_root()
        search_box = root.locator("#client_search_input")
        search_button = root.locator("#searchbutton")

        search_box.wait_for(state="visible", timeout=timeout)
        search_box.fill(d_number)
        self.click(search_button)
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        logger.info(f"D-number search completed: {d_number}")

    def get_no_search_results_message(self, timeout: int = 10000) -> str:
        """Get the 'No search results' message text from the Tracking Center grid."""
        logger.info("Retrieving no search results message...")
        root = self.active_root()
        no_results_locator = root.locator("#noresults_TrackingCenterGrid")
        
        no_results_locator.wait_for(state="visible", timeout=timeout)
        message_text = (no_results_locator.text_content() or "").strip()
        logger.info(f"No search results message: {message_text}")
        return message_text

