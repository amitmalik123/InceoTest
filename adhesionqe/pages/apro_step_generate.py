"""APro Proposal Generate Report step (wizard-6)."""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalGeneratePage(BasePage):
    """Page object for APro proposal Generate Report step (wizard-6).

    Handles proposal summary, template selection, report selection,
    PDF generation, preview, and the Finish workflow.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 7 (Generate Proposal) container
        self.step_generate_proposal: Locator = page.locator("#proposal-wizard-6")

        # Preview and report generation buttons
        # PREVIEW button on Generate Proposal step (opens template selector modal)
        self.preview_button: Locator = page.locator(
            "#btn-preview-report"
        )  # Scoped by ID to avoid strict mode
        # Template report selector modal - use .first to avoid duplicate ID strict mode violation
        self.template_report_selector_modal: Locator = page.locator(
            "#template-selector-modal"
        ).first

        # Generate Preview button - get from visible modal only by using .first to avoid strict mode
        self.generate_preview_button: Locator = page.locator(
            ".k-window:has(#template-selector-modal) .k-dialog-actions button:has-text('GENERATE PREVIEW')"
        ).first

        self.template_report_selector_input: Locator = self.template_report_selector_modal.locator(
            'input[name="template-selector-dropdown_input"]'
        )
        self.template_report_selector_combobox: Locator = (
            self.template_report_selector_modal.locator("#template-selector-dropdown")
        )

        # Available / Selected reports listboxes
        self.available_reports_list_items: Locator = self.template_report_selector_modal.locator(
            ".report-listbox-container .listbox-section:nth-of-type(1) .k-list-ul li.k-list-item"
        )
        self.available_reports_select: Locator = self.template_report_selector_modal.locator(
            "#available-reports"
        )
        self.selected_reports_select: Locator = self.template_report_selector_modal.locator(
            "#selected-reports"
        )

        # Modal locators for close buttons
        self.proposal_wizard_modal: Locator = page.locator(
            'div.k-window:has(div[id^="proposal-wizard-"])'
        ).first
        self.preview_proposal_modal: Locator = page.locator(
            "div.k-window:has(button:has-text('Preview Proposal'))"
        ).first
        self.preview_proposal_titlebar_close: Locator = self.preview_proposal_modal.locator(
            "div.k-window-titlebar-actions button.k-dialog-close"
        ).first
        self.preview_proposal_titlebar_close_svg: Locator = self.preview_proposal_modal.locator(
            "div.k-window-titlebar-actions button:has(svg)"
        ).first

        self.template_report_modal_scoped: Locator = page.locator(
            "div.k-window:has(#template-selector-modal)"
        ).first
        self.template_report_titlebar_close: Locator = self.template_report_modal_scoped.locator(
            "div.k-window-titlebar-actions button.k-dialog-close"
        ).first
        self.template_report_titlebar_close_svg: Locator = (
            self.template_report_modal_scoped.locator(
                "div.k-window-titlebar-actions button:has(svg)"
            ).first
        )

        # PREVIEW/GENERATE PROPOSAL modal - appears after GenerateReport API completes
        # Contains the button to download/preview the generated PDF
        self.preview_proposal_modal_dialog: Locator = page.locator(
            "div.k-window:has-text('PREVIEW/GENERATE PROPOSAL')"
        ).first

        # Preview/View Proposal button - both original and copied proposals use the same button
        self.preview_proposal_button: Locator = page.locator("button#btn-view-proposal").first

        # Finish button locators
        self.finish_primary_button: Locator = self.step_generate_proposal.locator(
            "button:has-text('Finish')"
        ).first
        self.finish_confirm_modal: Locator = page.locator(
            "div.k-window:has(button:has-text('Finish'))"
        ).first
        self.finish_confirm_button: Locator = self.finish_confirm_modal.locator(
            "button:has-text('Finish')"
        ).first

        # State tracking
        self._preview_clicked: bool = False
        self._generated_file_id: str | None = None
        self.last_selected_reports: dict | None = None
        self._modal_type: str | None = None  # Track which modal is open: 'report' or 'proposal'

    def wait_for_summary_step(self, timeout: int = 10000) -> None:
        """Wait for the Generate Proposal (wizard step 7, proposal-wizard-6) to be visible."""
        logger.info("Waiting for Generate Proposal step to be visible")
        self.wait_for_element(self.step_generate_proposal, state="visible", timeout=timeout)

    def get_summary_details(self, timeout: int = 10000) -> dict:
        """Extract proposal summary details from the current step.

        Returns:
            Dict with keys: visible, client, strategy, composite, investment_amount, investment_raw
        """
        logger.info("Getting proposal summary details")

        self.wait_for_element(self.step_generate_proposal, state="visible", timeout=timeout)

        # Wait for summary content to be populated (not empty)
        summary_content = self.step_generate_proposal.locator(
            ".summary-content, .proposal-summary, [id*='summary']"
        ).first
        try:
            summary_content.wait_for(state="visible", timeout=timeout)
            self.page.wait_for_timeout(1000)  # Give it an extra moment to populate
        except Exception:
            logger.warning(
                "Could not find explicit summary content locator, proceeding with inner_text"
            )

        # Parse the summary panel text
        summary_text = self.step_generate_proposal.inner_text()
        logger.info(
            f"Raw summary text: {summary_text[:200]}..."
        )  # Log first 200 chars for debugging

        details: dict[str, bool | str | None | float] = {
            "visible": True,
            "client": self._extract_field(summary_text, "client", "name"),
            "strategy": self._extract_field(summary_text, "strategy"),
            "composite": self._extract_field(summary_text, "composite", "allocation"),
            "investment_raw": self._extract_field(summary_text, "investment"),
            "investment_amount": None,
        }

        # Parse investment amount
        if details["investment_raw"] and isinstance(details["investment_raw"], str):
            try:
                # Remove currency symbols and commas
                amount_str = details["investment_raw"].replace("$", "").replace(",", "")
                details["investment_amount"] = float(amount_str)
            except ValueError:
                logger.warning(f"Could not parse investment amount: {details['investment_raw']}")

        logger.info(f"Summary details: {details}")
        return details

    def _extract_field(self, text: str, *keywords) -> str | None:
        """Extract field value by searching for keywords in text.

        Handles both formats:
        - Inline: "Client: Guy Apro"
        - Multi-line: "Client:\nGuy Apro"
        """
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(kw.lower() in line.lower() for kw in keywords):
                # Try inline format first (value after colon)
                if ":" in line:
                    value = line.split(":", 1)[1].strip()
                    if value:
                        return value

                # Try next line format (value on next line)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and ":" not in next_line:
                        return next_line

                return line.strip()
        return None

    def click_preview(
        self, times: int = 1, pause_ms: int = 250, wait_for_modal: bool = True
    ) -> None:
        """Click the PREVIEW button and wait for modal to appear.

        Args:
            times: Number of times to click
            pause_ms: Pause between clicks
            wait_for_modal: Whether to wait for modal after clicking
        """
        logger.info(f"Clicking PREVIEW button {times} times")

        for i in range(times):
            self.click(self.preview_button)
            if i < times - 1:
                self.page.wait_for_timeout(pause_ms)

        # Wait for modal to appear after clicking
        if wait_for_modal:
            self.wait_for_template_report_modal(timeout=10000)

    def wait_for_template_report_modal(self, timeout: int = 10000) -> None:
        """Wait for the template selector modal to appear."""
        logger.info("Waiting for template report selector modal")

        # Wait for the template selector modal to become visible
        self.template_report_selector_modal.wait_for(state="visible", timeout=timeout)

        logger.info("Template report selector modal appeared")

    def open_template_report_dropdown(self) -> None:
        """Open the template name dropdown."""
        logger.info("Opening template report dropdown")
        self.click(self.template_report_selector_input)
        self.page.wait_for_timeout(500)

    def select_template_name_by_text(self, name: str) -> bool:
        """Select a template by name using Kendo ComboBox API.

        Args:
            name: Template name to select

        Returns:
            True if selected, False if not found
        """

        try:
            # Wait for combobox data to load
            self.page.wait_for_timeout(1000)

            # Use Kendo ComboBox API to set value by text
            result = self.page.evaluate(
                f"""
                (function() {{
                    const comboBox = $('#template-selector-dropdown').data('kendoComboBox');
                    if (!comboBox) {{
                        console.error('ComboBox not initialized');
                        return false;
                    }}

                    // Get the data source
                    const dataSource = comboBox.dataSource;
                    if (!dataSource) {{
                        console.error('DataSource not available');
                        return false;
                    }}

                    // Read/fetch the data if needed
                    dataSource.read();
                    const items = dataSource.data();

                    console.log('Available templates:', items.map(i => i.TemplateName));

                    // Find the item by text
                    for (let i = 0; i < items.length; i++) {{
                        if (items[i].TemplateName === '{name}') {{
                            // Select the item
                            comboBox.select(function(data) {{
                                return data.TemplateID === items[i].TemplateID;
                            }});

                            // Trigger the select event to load reports
                            comboBox.trigger('select', {{ dataItem: items[i] }});

                            return true;
                        }}
                    }}

                    console.error('Template not found: {name}');
                    return false;
                }})()
                """
            )

            if result:
                self.page.wait_for_timeout(1000)  # Wait for reports to load
                return True
            else:
                logger.warning(f"Could not select template '{name}'")
                return False
        except Exception as exc:
            logger.warning(f"Error selecting template '{name}': {exc}")
            return False

    def get_available_reports(self) -> list:
        """Get list of available reports in the left listbox."""
        logger.info("Retrieving available reports")

        reports = []
        try:
            items = self.available_reports_list_items
            count = items.count()

            for i in range(count):
                text = items.nth(i).inner_text().strip()
                reports.append(text)

            logger.info(f"Found {len(reports)} available reports")
        except Exception as exc:
            logger.error(f"Error getting available reports: {exc}")

        return reports

    def select_report_by_name_using_kendo(self, name: str) -> bool:
        """Transfer a report from available to selected using Kendo ListBox API.

        Args:
            name: Exact report name to select

        Returns:
            True if transferred, False otherwise
        """

        try:
            # Use Kendo ListBox API to find and transfer the item
            result = self.page.evaluate(
                f"""
                (function() {{
                    const availableLb = $('#available-reports').data('kendoListBox');
                    const selectedLb = $('#selected-reports').data('kendoListBox');

                    if (!availableLb || !selectedLb) {{
                        console.error('ListBoxes not initialized');
                        return false;
                    }}

                    // Find the item in available list
                    const items = availableLb.items();
                    let targetItem = null;

                    for (let i = 0; i < items.length; i++) {{
                        if ($(items[i]).text().trim() === '{name}') {{
                            targetItem = items[i];
                            break;
                        }}
                    }}

                    if (!targetItem) {{
                        console.error('Item not found: {name}');
                        return false;
                    }}

                    // Select the item
                    availableLb.select(targetItem);

                    // Transfer using button or direct move
                    try {{
                        // Try to find and click the transfer button (chevron/arrow)
                        const transferBtn = $('.report-listbox-container button[data-icon="arrow-right"]').first();
                        if (transferBtn.length > 0) {{
                            transferBtn.click();
                        }} else {{
                            // Fallback: manually transfer using Kendo API
                            const dataSource = availableLb.dataSource;
                            const item = dataSource.getByUid(availableLb.select().attr('data-uid'));
                            if (item) {{
                                dataSource.remove(item);
                                selectedLb.dataSource.add(item);
                            }}
                        }}
                    }} catch (e) {{
                        console.error('Transfer error:', e);
                        return false;
                    }}

                    return true;
                }})();
                """
            )

            if result:
                return True
            else:
                logger.warning(f"✗ Failed to transfer report '{name}'")
                return False
        except Exception as exc:
            logger.warning(f"Could not transfer report '{name}': {exc}")
            return False

    def select_all_reports(self, reports: list | None = None, wait: bool = True) -> dict:
        """Select all or a specific set of reports.

        Args:
            reports: List of report names to select (None = all)
            wait: Whether to wait for default reports

        Returns:
            Dict mapping report name -> bool (selected)
        """
        logger.info(f"Selecting reports: {reports or 'all'}")

        # Verify reports are available
        try:
            self.available_reports_list_items.first.wait_for(state="visible", timeout=5000)
            logger.info("Available reports loaded")
        except Exception as exc:
            logger.warning(f"Timeout waiting for available reports to load: {exc}")

        default_reports = [
            "Cover Page",
            "Table of Contents",
            "Proposal Summary",
            "Projected Fees Report",
            "Manager Performance Review",
            "Manager Transition Summary",
            "Fee Detail Report",
            "Strategy Performance Review",
            "Composite Fact Sheet",
            "Proposal Agreement",
            "Holdings Transition Report",
        ]

        reports_to_select = reports or default_reports
        results = {}

        for report_name in reports_to_select:
            success = self.select_report_by_name_using_kendo(report_name)
            results[report_name] = success
            if not success:
                logger.warning(f"Failed to select: {report_name}")

        self.last_selected_reports = results
        return results

    def wait_for_preview_generate_modal(self, timeout: int = 10000) -> None:
        """Wait for the preview/generate modal to appear."""
        logger.info("Waiting for preview/generate modal")
        self.wait_for_element(self.template_report_selector_modal, state="visible", timeout=timeout)

    def click_generate_preview(self) -> None:
        """Click the GENERATE PREVIEW button inside the template selector modal.

        Both original and copied proposals use the same template selection flow.
        The difference appears AFTER this click, when the PREVIEW/GENERATE PROPOSAL
        modal shows different button content (Preview Proposal vs View Proposal).
        """
        logger.info("Clicking GENERATE PREVIEW button in template selector modal")
        # Wait for button to be visible and clickable
        self.generate_preview_button.wait_for(state="visible", timeout=5000)
        self.page.wait_for_timeout(500)  # Brief pause before click
        self.click(self.generate_preview_button)

    def click_preview_proposal_button(self) -> None:
        """Click the 'Preview Proposal' button (opens PDF tab).

        Detects which button is available:
        - Original: "Preview Proposal" button
        - Copied: "View Proposal" button
        """
        logger.info("Clicking proposal preview button (detecting type first)")

        # Try to detect which proposal type
        try:
            proposal_type = self.detect_generate_modal_type(timeout=2000)  # type: ignore[attr-defined]
            if proposal_type == "copied":
                logger.info("Detected copied proposal - clicking 'View Proposal' button")
                self.click(self.view_proposal_button)  # type: ignore[attr-defined]
                return
        except Exception:
            pass

        # Default to Preview Proposal button (original proposal)
        logger.info("Using 'Preview Proposal' button (original proposal)")
        self.click(self.preview_proposal_button)

    def click_preview_proposal_and_verify_tab(  # noqa: C901
        self, timeout: int = 20000
    ) -> str | None:
        """Click Preview Proposal button and download the PDF.

        Detects headed vs headless mode and uses appropriate strategy:
        - Headless: CDP forces download to disk, polls filesystem with size stability check
        - Headed: Makes direct HTTP request to PDF URL and saves to disk

        Args:
            timeout: max wait time in ms for the preview button / download.

        Returns:
            The path to the downloaded PDF file, or None if download failed.
        """
        import time
        from pathlib import Path

        from utils.pdf_utils import PDFValidator

        logger.info("Clicking PREVIEW/VIEW Proposal button and downloading PDF")

        preview_proposal_btn = self.preview_proposal_button

        try:
            wait_timeout = max(timeout, 60000)
            self.wait_for_element(preview_proposal_btn, state="visible", timeout=wait_timeout)
        except Exception as exc:
            raise TimeoutError(
                f"Preview/View Proposal button did not appear after GENERATE PREVIEW: {exc}"
            )

        if not preview_proposal_btn.is_visible():
            raise RuntimeError("Preview/View Proposal locator is not visible")
        dis = preview_proposal_btn.get_attribute("disabled")
        aria = preview_proposal_btn.get_attribute("aria-disabled")
        if dis is not None or (aria is not None and str(aria).strip().lower() == "true"):
            raise RuntimeError("Preview/View Proposal locator is disabled/aria-disabled")

        downloads_dir = Path("tmp").absolute()
        downloads_dir.mkdir(parents=True, exist_ok=True)

        # Configure CDP on the MAIN page to force PDF downloads to disk (headless mode)
        try:
            cdp_session = self.page.context.new_cdp_session(self.page)
            cdp_session.send(
                "Page.setDownloadBehavior",
                {"behavior": "allow", "downloadPath": str(downloads_dir)},
            )
            logger.info(f"CDP configured to download PDFs to: {downloads_dir}")
        except Exception as e:
            logger.warning(f"Could not configure CDP download behavior: {e}")

        pdf_path = None

        try:
            # Listen for new page/popup event
            with self.page.context.expect_event("page", timeout=timeout) as new_page_context:
                # Record start time
                start_time = time.time()

                preview_proposal_btn.click()
                logger.info("Preview button clicked")

                # Get the new page
                new_page = new_page_context.value
                logger.info(f"New page created: {new_page.url}")

                # Detect if headed or headless based on new page URL
                # Headless: URL is ":" (stuck at initial state)
                # Headed: URL is the full DownloadReport URL with fileId
                is_headed = new_page.url.startswith("http")

                if is_headed:
                    logger.info("Headed mode detected - waiting for URL to load...")
                    # Wait for the URL to stabilize (may take time to navigate)
                    url_wait_timeout = 10  # seconds
                    url_wait_start = time.time()
                    final_url = None

                    while time.time() - url_wait_start < url_wait_timeout:
                        current_url = new_page.url
                        if current_url.startswith("http") and "DownloadReport" in current_url:
                            final_url = current_url
                            logger.info(f"URL loaded: {final_url}")
                            break
                        time.sleep(0.5)

                    if not final_url:
                        logger.warning(
                            f"URL did not load properly after {url_wait_timeout}s, last URL: {new_page.url}"
                        )
                    else:
                        try:
                            # Make a direct HTTP request to get the PDF from the URL
                            pdf_response = new_page.context.request.get(final_url)
                            if pdf_response.ok and "application/pdf" in pdf_response.headers.get(
                                "content-type", ""
                            ):
                                pdf_data = pdf_response.body()
                                pdf_path = str(downloads_dir / "DownloadReport.pdf")
                                with open(pdf_path, "wb") as f:
                                    f.write(pdf_data)
                                logger.info(f"PDF downloaded from URL ({len(pdf_data)} bytes)")
                            else:
                                logger.warning(
                                    f"PDF response not OK or wrong content-type: {pdf_response.status}"
                                )
                        except Exception as e:
                            logger.warning(f"Failed to download PDF from URL: {e}")

                    from contextlib import suppress

                    with suppress(Exception):
                        new_page.close()
                else:
                    logger.info("Headless mode detected - using filesystem polling")
                    # Close the new page
                    with suppress(Exception):
                        new_page.close()

                    # Poll the downloads folder for a PDF file with size stability check
                    # CDP should have downloaded it instead of opening it in the viewer
                    logger.info(f"Polling for downloaded PDF in: {downloads_dir}")
                    poll_timeout = max(30, timeout / 1000)  # Convert ms to seconds, min 30s
                    poll_interval = 0.5
                    size_stability_duration = 2.0  # File must be stable for 2 seconds
                    last_stable_time = None

                    while time.time() - start_time < poll_timeout:
                        try:
                            # Look for any .pdf file in the downloads directory
                            pdf_files = list(downloads_dir.glob("*.pdf"))
                            if pdf_files:
                                candidate = pdf_files[0]  # Get first PDF
                                candidate_size = candidate.stat().st_size

                                # Verify it's a complete PDF (has proper header and trailer)
                                if candidate_size > 1000:  # Minimum reasonable PDF size
                                    with open(candidate, "rb") as f:
                                        header = f.read(4)
                                        f.seek(-100, 2)  # Seek to near end
                                        trailer = f.read()

                                    if header == b"%PDF" and b"%%EOF" in trailer:
                                        # Check size stability - has file size stayed the same?
                                        if last_stable_time is None:
                                            last_stable_time = time.time()
                                            last_stable_size = candidate_size
                                        elif candidate_size == last_stable_size:
                                            # Size hasn't changed - check if stable long enough
                                            if (
                                                time.time() - last_stable_time
                                                >= size_stability_duration
                                            ):
                                                logger.info(
                                                    f"Found PDF: {candidate.name} ({candidate_size} bytes)"
                                                )
                                                logger.info("Valid PDF detected")
                                                pdf_path = str(candidate)
                                                break
                                        else:
                                            # Size changed - reset stability timer
                                            last_stable_time = time.time()
                                            last_stable_size = candidate_size
                        except Exception as e:
                            logger.debug(f"Poll iteration error: {e}")

                        time.sleep(poll_interval)

                    if not pdf_path:
                        logger.warning(
                            f"No valid PDF found in {downloads_dir} after {poll_timeout}s"
                        )

        except Exception as e:
            logger.warning(f"Error during page creation: {e}")

        # If PDF was found, validate it
        if pdf_path:
            try:
                logger.info(f"PDF located at: {pdf_path}")

                # Validate PDF
                validator = PDFValidator(Path(pdf_path))
                page_count = validator.get_page_count()
                file_size_mb = validator.get_file_size_mb()
                logger.info(f"PDF validated: {page_count} pages, {file_size_mb:.2f}MB")
                return pdf_path
            except Exception as exc:
                logger.error(f"PDF validation failed: {exc}")
                return None

        # No PDF captured
        logger.error("No PDF file downloaded to disk")
        return None

    def get_finish_primary_locator(self) -> Locator:
        """Return the primary Finish button locator."""
        return self.finish_primary_button

    def get_finish_confirm_locator(self) -> Locator:
        """Return the confirmation modal Finish button locator."""
        return self.finish_confirm_button

    def click_finish_primary(self) -> bool:
        """Click the primary Finish button in the wizard.

        Returns:
            True if click succeeded, False otherwise
        """
        logger.info("Clicking primary Finish button")
        try:
            self.click(self.finish_primary_button)
            return True
        except Exception as exc:
            logger.error(f"Failed to click primary Finish: {exc}")
            return False

    def click_finish_confirm(self, timeout: int = 5000) -> bool:
        """Click the Finish button in the confirmation modal.

        Returns:
            True if click succeeded, False otherwise
        """
        logger.info("Clicking confirmation Finish button")
        try:
            self.finish_confirm_button.wait_for(state="visible", timeout=timeout)
            self.click(self.finish_confirm_button)
            logger.info("Clicked confirmation Finish button (nth=1)")
            return True
        except Exception as exc:
            logger.error(f"Failed to click confirmation Finish: {exc}")
            return False

    def click_finish(self, timeout: int = 10000) -> bool:
        """Orchestrate the full Finish workflow.

        Clicks primary Finish, waits for confirmation modal, clicks confirm.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting Finish workflow")

        # Click primary Finish button
        if not self.click_finish_primary():
            return False

        # Check for confirmation modal
        try:
            self.finish_confirm_modal.wait_for(state="visible", timeout=timeout)
            logger.info("Confirmation Finish modal detected; attempting confirm click")
            return self.click_finish_confirm(timeout=timeout)
        except Exception:
            # No confirmation modal — primary Finish was sufficient
            logger.info("No confirmation modal; Finish completed")
            return True

    def click_previous(self) -> None:
        """Click Previous button to go back to Fees step."""
        logger.info("Clicking Previous from Generate step")
        prev_button = self.step_generate_panel.locator("button[data-wizard-previous]")  # type: ignore[attr-defined]
        prev_button.click()

    def click_preview_proposal_close(self) -> bool:
        """Close the Preview Proposal modal via titlebar X button."""
        logger.info("Clicked Preview Proposal modal titlebar close")
        try:
            self.click(self.preview_proposal_titlebar_close_svg)
            self.preview_proposal_modal.wait_for(state="hidden", timeout=5000)
            return True
        except Exception:
            try:
                self.click(self.preview_proposal_titlebar_close)
                self.preview_proposal_modal.wait_for(state="hidden", timeout=5000)
                return True
            except Exception as exc:
                logger.error(f"Failed to close preview modal: {exc}")
                return False

    def click_preview_report_close(self) -> bool:
        """Close the Template/Generate Report modal via titlebar X button."""
        logger.info("Clicked Template/Generate Report modal titlebar close")
        try:
            self.click(self.template_report_titlebar_close_svg)
            self.template_report_modal_scoped.wait_for(state="hidden", timeout=5000)
            return True
        except Exception:
            try:
                self.click(self.template_report_titlebar_close)
                self.template_report_modal_scoped.wait_for(state="hidden", timeout=5000)
                return True
            except Exception as exc:
                logger.error(f"Failed to close template modal: {exc}")
                return False

    def get_preview_proposal_close_locator(self):
        """Return the Preview Proposal modal close button locator."""
        return self.preview_proposal_titlebar_close

    def get_preview_report_close_locator(self):
        """Return the Template modal close button locator."""
        return self.template_report_titlebar_close
