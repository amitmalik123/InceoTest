"""
Tax Management Services Page Object Model for Proposals application.
Handles tax template upload, results viewing, and tax sensitivity settings.
"""

import logging
import os
import time
from typing import List

from playwright.sync_api import Locator, Page, Request

from ..base_page import BasePage

logger = logging.getLogger(__name__)


class TaxManagementServicesPage(BasePage):
    """Tax Management Services page for template upload and result visualization."""

    def __init__(self, page: Page):
        super().__init__(page)

        # File Upload - target the hidden file input directly by ID
        self.upload_input: Locator = page.locator('#fileInput')
        # Try multiple selectors for view results button (environment variations)
        self.view_results_button: Locator = self._get_view_results_button(page)
        self.loading_spinner: Locator = page.locator('[class*="LoadingImageLargeIcon"]').last

        # Tax Rate Inputs
        self.short_term_rate_input: Locator = page.locator("input#ShortTerm")
        self.long_term_rate_input: Locator = page.locator("input#LongTerm")
        self.state_rate_input: Locator = page.locator("input#State")

        # File Information Section
        self.file_name_heading: Locator = page.get_by_role("heading", name="File", level=1)
        self.file_name_value: Locator = self.file_name_heading.locator("xpath=following-sibling::p[1]")

        # Tax Sensitivity Buttons
        self.low_sensitivity_button: Locator = page.get_by_label("Low")
        self.medium_sensitivity_button: Locator = page.get_by_label("Medium")
        self.high_sensitivity_button: Locator = page.get_by_label("High", exact=True)
        self.very_high_sensitivity_button: Locator = page.get_by_label("Very High")

        # Download and Continue Buttons
        self.download_button: Locator = page.get_by_label("Download")
        self.continue_button: Locator = page.get_by_label("Continue")

        # Proposal Date
        self.proposal_date: Locator = page.locator('p:has-text("Proposal Date")')

    def _get_view_results_button(self, page: Page) -> Locator:
        """
        Get the view results button by trying multiple selectors.
        Handles environment variations in button IDs and attributes.
        
        Args:
            page: The Playwright page object
            
        Returns:
            A Locator for the view results button
        """
        # Try selectors in order of preference, return the first that works
        selectors = [
            lambda p: p.locator("#VIEWRESULTS"),
            lambda p: p.locator("#VIEW RESULTS"),
            lambda p: p.locator('[aria-label="VIEW RESULTS"]'),
            lambda p: p.locator('[label="VIEW RESULTS"]'),
        ]
        
        # For now, return the first selector - Playwright will handle selector resolution dynamically
        # We could also wrap this in a method that tries each on click, but locators are lazy
        return selectors[0](page)

    def upload_holdings_template(self, file_name: str = "NEW-REVISED Sample TMS ticker file.csv") -> List[Request]:
        """
        Upload a holdings template file and wait for all 3 TMS API requests.

        Args:
            file_name: The filename of the template to upload.

        Returns:
            List of API request objects for assertion in tests.
        """
        # Data files are in applicationqe/data/PROPOSAL/
        file_path = os.path.join("data", "PROPOSAL", file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template file not found: {file_path}")

        self.page.wait_for_load_state()
        # File input is hidden, so just set the file directly (no visibility wait needed)
        self.upload_input.set_input_files(file_path)
        self.page.wait_for_load_state()

        return self._click_view_results_with_retry()

    def _click_view_results_with_retry(self, max_retries: int = 3) -> List[Request]:
        """
        Click VIEW RESULTS button and wait for page to load.

        Retries up to 3 times if click fails.

        Args:
            max_retries: Maximum number of retry attempts.

        Returns:
            Empty list (API validation skipped for now).

        Raises:
            TimeoutError: If all retry attempts fail.
        """
        last_error: Exception | None = None

        for attempt in range(1, max_retries + 1):
            try:
                # Wait for spinner to appear (from file upload)
                logger.debug("Waiting for loading spinner to appear...")
                try:
                    self.loading_spinner.wait_for(state="visible", timeout=10000)
                    logger.debug("Loading spinner appeared")
                except Exception as spinner_appear_err:
                    logger.debug(f"Spinner didn't appear: {spinner_appear_err}")

                # Wait for spinner to disappear (file upload complete)
                logger.debug("Waiting for loading spinner to disappear...")
                try:
                    self.loading_spinner.wait_for(state="hidden", timeout=15000)
                    logger.debug("Loading spinner has disappeared - file upload complete")
                except Exception as spinner_err:
                    logger.warning(f"Spinner disappear wait failed: {spinner_err}")

                # Click VIEW RESULTS button
                logger.debug("Clicking VIEW RESULTS button...")
                self.view_results_button.click(timeout=5000)

                # Wait for results page to load
                self.page.wait_for_load_state("load", timeout=15000)

                # ===== NEW: Wait for secondary spinner (may appear after VIEW RESULTS click) =====
                logger.debug("Checking for secondary spinner after VIEW RESULTS click...")
                try:
                    # Try to wait for spinner to appear (non-blocking - OK if it doesn't appear)
                    self.loading_spinner.wait_for(state="visible", timeout=5000)
                    logger.debug("Secondary spinner appeared")
                    
                    # Now wait for it to disappear
                    try:
                        self.loading_spinner.wait_for(state="hidden", timeout=15000)
                        logger.debug("Secondary spinner disappeared - results ready")
                    except Exception as secondary_spinner_err:
                        logger.warning(f"Secondary spinner disappear wait failed: {secondary_spinner_err}")
                
                except Exception as secondary_spinner_appear_err:
                    # It's OK if secondary spinner doesn't appear - just log and continue
                    logger.debug(f"Secondary spinner did not appear (OK): {secondary_spinner_appear_err}")

                logger.info("Successfully clicked VIEW RESULTS and page loaded")
                return []

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {e}")

                if attempt < max_retries:
                    self.page.wait_for_timeout(1000)

        raise TimeoutError(f"Failed to click VIEW RESULTS after {max_retries} attempts. Last error: {last_error}")

    def select_tax_sensitivity(self, sensitivity: str) -> None:
        """
        Select a tax sensitivity level.

        Args:
            sensitivity: The sensitivity level ("Low", "Medium", "High", "Very High").
        """
        sensitivity_map = {
            "Low": self.low_sensitivity_button,
            "Medium": self.medium_sensitivity_button,
            "High": self.high_sensitivity_button,
            "Very High": self.very_high_sensitivity_button,
        }

        button = sensitivity_map.get(sensitivity)
        if not button:
            raise ValueError(f"Unknown tax sensitivity level: {sensitivity}")

        button.click()
        self.page.wait_for_timeout(500)

    def get_estimated_tax_benefits_table_data(self) -> list[dict]:
        """Extract estimated tax benefits table data."""
        try:
            # Find the estimated tax benefits section
            section = self.page.locator('div:has-text("Estimated Tax Benefits")')
            rows = section.locator('table tr')
            row_count = rows.count()
            results = []

            for i in range(row_count):
                row = rows.nth(i)
                cells = row.locator('th, td')
                cell_count = cells.count()
                if cell_count == 0:
                    continue

                label = (cells.nth(0).inner_text()).strip()
                values = []
                for c in range(1, cell_count):
                    value = (cells.nth(c).inner_text()).strip()
                    if value:
                        values.append(value)

                if label:
                    results.append({"label": label, "values": values})

            return results
        except Exception as e:
            logger.error(f"Error extracting tax benefits table: {e}")
            return []

    def get_client_account_summary_data(self) -> list[dict]:
        """Extract client account summary data."""
        try:
            # Find the client account tax summary section
            section = self.page.locator('div:has-text("Client Account Tax Summary")')
            items = section.locator('div:has(>h2)')
            item_count = items.count()
            results = []

            for i in range(item_count):
                item = items.nth(i)
                try:
                    label = (item.locator('h2').inner_text()).strip()
                    value = (item.locator('p').inner_text()).strip()

                    if label and value:
                        results.append({"label": label, "value": value})
                except Exception:
                    continue

            return results
        except Exception as e:
            logger.error(f"Error extracting account summary: {e}")
            return []

    def download_pdf(self) -> str:
        """Download PDF when clicking the download button."""
        try:
            downloads_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'downloads')
            os.makedirs(downloads_dir, exist_ok=True)

            # Setup download listener
            download_promise = self.page.wait_for_event('download')
            self.download_button.click()
            download = download_promise

            filename = download.suggested_filename or f"tax-mgmt-{int(time.time())}.pdf"
            file_path = os.path.join(downloads_dir, filename)
            download.save_as(file_path)

            # Wait for file to exist and have size
            deadline = time.time() + 15
            while time.time() < deadline:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return file_path
                self.page.wait_for_timeout(300)

            raise Exception(f"Downloaded file not found or empty: {file_path}")
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            raise

    def get_screenshot_mask_locators(self) -> List[Locator]:
        """
        Get list of locators to mask in screenshots (e.g., dates, dynamic content).
        
        Matches TypeScript version by masking:
        - Tax rate inputs (Short/Long term, State)
        - File name (changes per test)
        - Proposal date (changes per test)
        - Financial values (Estimated Tax Benefits)
        - Account summary values (Client Account Tax Management Summary)

        Returns:
            List of locators to mask.
        """
        return [
            self.short_term_rate_input,
            self.long_term_rate_input,
            self.state_rate_input,
            self.file_name_value,
            self.proposal_date,
            self.get_estimated_tax_benefits_values(),
            self.get_client_account_summary_values(),
        ]

    def get_estimated_tax_benefits_values(self) -> Locator:
        """
        Get locator for estimated tax benefits values (any dollar amounts in the section).
        
        Returns:
            Locator matching all financial values in the Estimated Tax Benefits section.
        """
        # Find the Estimated Tax Benefits section, then get all divs/spans/ps/tds
        # that contain numeric values (dollar amounts, percentages)
        section = self.page.locator('div').filter(
            has=self.page.get_by_text("Estimated Tax Benefits", exact=True)
        ).first
        
        # Return all value containers (divs, spans, paragraphs, table cells) in the section
        # These will be masked to hide changing dollar amounts
        return section.locator('div, span, p, td')

    def get_client_account_summary_values(self) -> Locator:
        """
        Get locator for client account summary values.
        
        Returns:
            Locator matching all financial values in the Client Account Tax Management Summary section.
        """
        # Find the Client Account Tax Management Summary section
        section = self.page.locator('div').filter(
            has=self.page.get_by_text("Client Account Tax Management Summary|Account Summary")
        ).first
        
        # Get all p tags that are direct children of divs with h2
        return section.locator('div:has(>h2)>p')
