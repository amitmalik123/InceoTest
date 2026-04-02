"""APro Proposals page."""

# flake8: noqa: SIM105
import contextlib
import time
from typing import Union

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AproProposalsPage(BasePage):
    """Page object for the APro proposals actions dropdown and related items.

    Locators:
      - actions_button: the button that opens the actions dropdown (id `btnMainActionButton`)
      - items_container: the dropdown container (id `items`)
      - create_prospect_item: the menu item text 'Create Prospect'
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        self.actions_button: Locator = page.locator("#btnMainActionButton")
        self.items_container: Locator = page.locator("#items")
        self.create_prospect_item: Locator = page.get_by_text("Create Prospect", exact=True)
        # Overlay that appears behind modal dialogs (e.g., after starting a proposal)
        self.overlay: Locator = page.locator("div.k-overlay")

        # Generic container for the proposal modal steps
        self.proposal_modal: Locator = page.locator("div.k-window")

        # --- Step 1 (Add Details) selectors ---
        self.step_details_panel = page.locator("#proposal-wizard-0")
        self.name_input: Locator = page.locator("#Name")
        self.name_extended_input: Locator = page.locator("#NameExtended")
        self.email_input: Locator = page.locator("#Email")
        self.address_input: Locator = page.locator("#Address")
        self.city_input: Locator = page.locator("#City")
        self.state_input: Locator = page.locator("#State")
        self.zip_input: Locator = page.locator("#Zip")
        self.account_name_input: Locator = page.locator("#AccountName")
        self.account_number_input: Locator = page.locator("#AccountNumber")
        self.investment_amount_input: Locator = page.locator("#InvestmentAmount")
        self.account_type_dropdown: Locator = page.locator(
            'span.k-dropdownlist[aria-controls="AccountTypeID_listbox"]'
        )
        self.custodian_dropdown: Locator = page.locator(
            'span.k-dropdownlist[aria-controls="CustodianID_listbox"]'
        )
        self.advisor_dropdown: Locator = page.locator(
            'span.k-dropdownlist[aria-controls="AdvisorID_listbox"]'
        )
        self.advisor_name_element: Locator = page.locator("div.user div.name")

        # Step navigation buttons scoped to the modal
        self.wizard_next_button: Locator = self.proposal_modal.locator("button[data-wizard-next]")
        self.wizard_previous_button: Locator = self.proposal_modal.locator(
            "button[data-wizard-previous]"
        )
        self.wizard_cancel_button: Locator = self.proposal_modal.locator(
            "button[data-wizard-reset]"
        )

        # Per-step Next button locators to avoid Playwright strict-mode ambiguity
        # Keys are the step container id (e.g., 'proposal-wizard-0')
        self.step_next_buttons: dict = {}
        for i in range(0, 6):
            sid = f"proposal-wizard-{i}"
            try:
                # scope the next button to the specific step container
                self.step_next_buttons[sid] = page.locator(f"#{sid} button[data-wizard-next]")
            except Exception:
                # best-effort: ignore failures during locator creation
                self.step_next_buttons[sid] = page.locator(f"#{sid} button[data-wizard-next]")

        # --- Step 2 (Add Holdings) selectors ---
        self.step_holdings_panel = page.locator("#proposal-wizard-1")
        self.symbol_search_input: Locator = page.locator("#SymbolSearch")
        self.symbol_input: Locator = page.locator("#Symbol")
        self.description_input: Locator = page.locator("#Description")
        self.holding_id_input: Locator = page.locator("#HoldingID")
        self.morningstar_data_id_input: Locator = page.locator("#MorningstarDataID")
        self.asset_type_dropdown: Locator = page.locator("#AssetTypeID")
        self.morningstar_category_dropdown: Locator = page.locator("#MorningstarCategoryID")
        self.benchmark_dropdown: Locator = page.locator("#BenchmarkID")
        self.acquisition_input: Locator = page.locator("#Acquisition")
        self.price_input: Locator = page.locator("#Price")
        # Prefer the visible Kendo wrapper input (input.k-input-inner) over the hidden backing field
        self.shares_input: Locator = page.locator(
            '.form-input-group:has-text("Shares") input.k-input-inner'
        ).first
        self.cost_input: Locator = page.locator(
            '.form-input-group:has-text("Cost") input.k-input-inner'
        ).first
        self.value_input: Locator = page.locator("#Value")
        self.holdings_import_button: Locator = page.locator("#btn-holdings-import")
        self.save_holding_button: Locator = page.get_by_text("SAVE TAX LOT", exact=True)
        self.clear_holding_button: Locator = page.get_by_text("CLEAR", exact=True)
        self.delete_holding_button: Locator = page.get_by_text("DELETE", exact=True)

        # --- Step 3 (Questionnaire) selectors ---
        self.step_questionnaire_panel = page.locator("#proposal-wizard-2")
        self.questionnaire_container: Locator = page.locator("#questionnaire-container")
        self.questionnaire_questions: Locator = page.locator("#questionnaire-questions")
        # Allocation step tabs and grid
        self.filter_tab_objective: Locator = page.locator(
            '.allocation-filters-container .filter-tab[data-tab="objective"]'
        )
        self.filter_tab_performance: Locator = page.locator(
            '.allocation-filters-container .filter-tab[data-tab="performance"]'
        )
        self.filter_tab_fee: Locator = page.locator(
            '.allocation-filters-container .filter-tab[data-tab="fee"]'
        )

        # Allocation grid rows
        self.allocation_grid_rows: Locator = page.locator(
            "#proposal-allocation-grid-wrapper table.k-table tbody.k-table-tbody tr"
        )
        # Selected allocation and risk/performance containers
        self.selected_allocation_card: Locator = page.locator("#proposal-allocation-card")
        self.selected_allocation_details: Locator = page.locator("#proposal-allocation-details")
        self.risk_reward_card: Locator = page.locator("#proposal-risk-reward-card")
        # Generate report / preview button
        self.preview_button: Locator = page.get_by_role("button", name="PREVIEW")
        # Template report selector modal (opened after PREVIEW)
        self.template_report_selector_modal: Locator = page.locator("#template-selector-modal")
        # Visible combobox input for template name and the underlying combobox element
        self.template_report_selector_input: Locator = self.template_report_selector_modal.locator(
            'input[name="template-selector-dropdown_input"]'
        )
        self.template_report_selector_combobox: Locator = (
            self.template_report_selector_modal.locator("#template-selector-dropdown")
        )

        # Available / Selected reports listboxes inside the template modal
        # Available reports list items (visible list)
        self.available_reports_list_items: Locator = self.template_report_selector_modal.locator(
            ".report-listbox-container .listbox-section:nth-of-type(1) .k-list-ul li.k-list-item"
        )
        # Hidden select elements that back the Kendo ListBoxes
        self.available_reports_select: Locator = self.template_report_selector_modal.locator(
            "#available-reports"
        )
        self.selected_reports_select: Locator = self.template_report_selector_modal.locator(
            "#selected-reports"
        )
        # Generate preview action button:
        self.generate_preview_button: Locator = page.get_by_text("GENERATE PREVIEW")
        # Final preview action shown after generation finishes (opens PDF tab)
        self.preview_proposal_button: Locator = page.get_by_role("button", name="Preview Proposal")

        # expected values captured during the flow (used for later verification)
        self.expected_client_name: str | None = None
        self.expected_allocation_name: str | None = None
        self.expected_strategy: str | None = None
        self.expected_investment_amount: float | None = None
        self.expected_advisor_name: str | None = None
        # --- History / Actions (Step 6) selectors ---
        self.step_history_panel: Locator = page.locator("#proposal-wizard-5")
        self.history_client_name: Locator = page.locator("#history-client-name")
        self.history_strategy: Locator = page.locator("#history-strategy")
        self.history_composite: Locator = page.locator("#history-composite")
        self.history_investment_amount: Locator = page.locator("#history-investment-amount")
        self.history_current_status: Locator = page.locator("#history-current-status")
        # Actions dropdown and items
        self.history_actions_button: Locator = page.locator("#btnHistoryActions")
        self.history_actions_items: Locator = page.locator("#historyActionsItems")
        self.history_action_delete: Locator = page.locator("#action-delete")
        self.confirm_delete_button: Locator = page.locator(
            "button.k-button.k-primary", has_text="Delete"
        )
        # Internal guard to avoid clicking PREVIEW more than once per flow
        self._preview_clicked: bool = False
        # Additional Finish variants and titlebar close locators (for helpers)
        # Scoped primary wizard modal (contains proposal-wizard-* steps)
        self.proposal_wizard_modal: Locator = page.locator(
            'div.k-window:has(div[id^="proposal-wizard-"]) '
        ).first
        # Primary Finish button scoped to the wizard modal
        self.finish_primary_button: Locator = self.proposal_wizard_modal.locator(
            "button:has-text('Finish')"
        ).first
        # Confirmation Finish modal (generic modal that may appear after primary Finish)
        self.finish_confirm_modal: Locator = page.locator(
            "div.k-window:has(button:has-text('Finish'))"
        ).first
        self.finish_confirm_button: Locator = self.finish_confirm_modal.locator(
            "button:has-text('Finish')"
        ).first

        # --- Modal-scoped titlebar close locators (avoid hardcoded selectors in methods) ---
        # Modal that contains the final 'Preview Proposal' confirmation button
        self.preview_proposal_modal: Locator = page.locator(
            "div.k-window:has(button:has-text('Preview Proposal'))"
        ).first
        self.preview_proposal_titlebar_close: Locator = self.preview_proposal_modal.locator(
            "div.k-window-titlebar-actions button.k-dialog-close"
        ).first
        self.preview_proposal_titlebar_close_svg: Locator = self.preview_proposal_modal.locator(
            "div.k-window-titlebar-actions button:has(svg)"
        ).first

        # Modal that contains the template selector / generate preview controls
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

        # Wizard popup (create/edit prospect) locator
        self.wizard_popup_modal: Locator = page.locator("div.k-window:has(#wizardPopup)").first
        self.wizard_popup_titlebar_close: Locator = self.wizard_popup_modal.locator(
            "div.k-window-titlebar-actions button.k-dialog-close"
        ).first
        self.wizard_popup_titlebar_close_svg: Locator = self.wizard_popup_modal.locator(
            "div.k-window-titlebar-actions button:has(svg)"
        ).first

    def click_generate_preview(self) -> None:
        """Click the GENERATE PREVIEW button inside the template selector modal."""
        logger.info("Clicking GENERATE PREVIEW")
        try:
            self.generate_preview_button.click()
        except Exception as exc:
            logger.warning(f"Failed to click GENERATE PREVIEW: {exc}")
        # no side-effects here; expected values are set during flow steps

    def click_preview_proposal_button(self) -> None:
        """Click the 'Preview Proposal' button in the confirmation popup (opens PDF tab)."""
        logger.info("Clicking Preview Proposal button")
        try:
            self.click(self.preview_proposal_button)
        except Exception as exc:
            logger.warning(f"Failed to click Preview Proposal: {exc}")

    def open_actions(self) -> None:
        """Open the actions dropdown."""
        logger.info("Opening APro actions dropdown")
        self.click(self.actions_button)

    def wait_for_items(self, timeout: int = 10000) -> None:
        """Wait for the actions items container to be visible."""
        logger.info("Waiting for actions items to be visible")
        self.wait_for_element(self.items_container, state="visible", timeout=timeout)

    def click_create_prospect(self) -> None:
        """Click the 'Create Prospect' item inside the actions dropdown."""
        logger.info("Clicking 'Create Prospect' in APro actions")
        # Ensure dropdown is open and items visible
        try:
            self.wait_for_items()
        except Exception:
            # Attempt to open then wait again
            self.open_actions()
            self.wait_for_items()

        self.click(self.create_prospect_item)

    # -----------------
    # Overlay / modal helpers
    # -----------------
    def wait_for_overlay(self, timeout: int = 10000) -> None:
        """Wait until the overlay is visible (modal shown)."""
        logger.info("Waiting for modal overlay to be visible")
        self.wait_for_element(self.overlay, state="visible", timeout=timeout)

    def wait_for_overlay_to_disappear(self, timeout: int = 10000) -> None:
        """Wait until the overlay is gone/hidden (modal closed)."""
        logger.info("Waiting for modal overlay to disappear")
        self.wait_for_element(self.overlay, state="hidden", timeout=timeout)

    def wait_for_proposal_step(self, step_selector: str, timeout: int = 10000) -> None:
        """Wait for a proposal step element (selector or locator) to be visible.

        Args:
            step_selector: CSS selector or locator expression for the step content
        """
        logger.info(f"Waiting for proposal step selector: {step_selector}")
        locator = self.page.locator(step_selector)
        self.wait_for_element(locator, state="visible", timeout=timeout)

    def _get_visible_wizard_step(self):
        """Return the visible wizard step container Locator (div with id starting proposal-wizard-).

        Falls back to the first matched step if none are visible.
        """
        steps = self.page.locator('div[id^="proposal-wizard-"]')
        try:
            count = steps.count()
        except Exception:
            count = 0

        for i in range(count):
            try:
                s = steps.nth(i)
                if s.is_visible():
                    return s
            except Exception:
                continue

        # fallback: return first step locator (may be hidden)
        return steps.first

    def _wait_for_enabled_in_step(self, selector: str, timeout: int = 10000) -> str | None:
        """Wait until a button matching `selector` inside the visible step is enabled.

        Returns the selector string that matched (for use with visible() scoping),
        or None if nothing became enabled within the timeout.
        """
        logger.info(f"Waiting for enabled element in step: {selector}")
        end = time.time() + (int(timeout) / 1000.0)
        try:
            while time.time() < end:
                try:
                    locs = self.page.locator(selector)
                    cnt = locs.count()
                except Exception:
                    cnt = 0

                for i in range(cnt):
                    try:
                        loc_item = locs.nth(i)
                        # consider visible and not disabled/aria-disabled
                        if loc_item.is_visible():
                            disabled_attr = None
                            with contextlib.suppress(Exception):
                                disabled_attr = loc_item.get_attribute("disabled")
                            aria = None
                            with contextlib.suppress(Exception):
                                aria = loc_item.get_attribute("aria-disabled")
                            is_disabled = False
                            if disabled_attr is not None:
                                is_disabled = True
                            if aria is not None and str(aria).strip().lower() == "true":
                                is_disabled = True
                            if not is_disabled:
                                # return a selector pointing to this element
                                aid = None
                                with contextlib.suppress(Exception):
                                    aid = loc_item.get_attribute("id")
                                if aid:
                                    return f"#{aid}"
                                # fallback to the original selector if no id
                                return selector
                    except Exception:
                        continue
                # small sleep
                self.page.wait_for_timeout(200)
        except Exception:
            pass
        return None

    def wait_for_allocation_step(self, timeout: int = 10000) -> None:
        """Wait for the Allocation (wizard step 3) panel to be visible."""
        logger.info("Waiting for Allocation (proposal-wizard-3) step to be visible")
        self.wait_for_proposal_step("#proposal-wizard-3", timeout=timeout)

    def wait_for_summary_step(self, timeout: int = 10000) -> None:
        """Wait for the Summary/Details (wizard step 4) panel to be visible."""
        logger.info("Waiting for Summary (proposal-wizard-4) step to be visible")
        self.wait_for_proposal_step("#proposal-wizard-4", timeout=timeout)

    # -----------------
    # History / Actions helpers (Step 6)
    # -----------------
    def wait_for_history_step(self, timeout: int = 10000) -> None:
        logger.info("Waiting for History (step 6) to be visible")
        self.wait_for_element(self.step_history_panel, state="visible", timeout=timeout)

    def get_history_details(self) -> dict:
        """Return a dict of visible history details: client, strategy, composite, investment_amount, current_status."""
        try:
            client = self.history_client_name.inner_text().strip()
        except Exception:
            client = ""
        try:
            strategy = self.history_strategy.inner_text().strip()
        except Exception:
            strategy = ""
        try:
            composite = self.history_composite.inner_text().strip()
        except Exception:
            composite = ""
        try:
            inv = self.history_investment_amount.inner_text().strip()
        except Exception:
            inv = ""
        try:
            status = self.history_current_status.inner_text().strip()
        except Exception:
            status = ""
        return {
            "client": client,
            "strategy": strategy,
            "composite": composite,
            "investment": inv,
            "status": status,
        }

    def wait_for_history_details(self, timeout: int = 15000) -> dict:
        """Wait for history step to load and return the details dict once placeholders are resolved."""
        logger.info("Waiting for History/Actions details to populate")
        self.wait_for_history_step(timeout=timeout)

        # Poll until placeholder values ('--') are replaced with real data
        placeholders = {"--", ""}
        end = time.time() + (timeout / 1000.0)
        details = self.get_history_details()
        while time.time() < end:
            if details["client"] not in placeholders:
                break
            time.sleep(0.2)
            details = self.get_history_details()

        return details

    def open_history_actions(self) -> None:
        logger.info("Opening History Actions dropdown")
        self.click(self.history_actions_button)
        # wait for items container to be visible
        self.wait_for_element(self.history_actions_items, state="visible", timeout=5000)

    def click_history_action(self, action: str) -> None:
        """Click a named action in the history actions menu (e.g., 'Delete')."""
        logger.info(f"Clicking history action: {action}")
        # map common actions to ids
        mapping = {
            "Delete": self.history_action_delete,
        }

        locator = mapping.get(action)
        if locator is not None:
            try:
                self.click(locator)
                return
            except Exception as exc:
                logger.warning(f"History action click failed for mapped '{action}': {exc}")

        # fallback: try to click by text inside the history actions items
        try:
            try:
                item = self.history_actions_items.get_by_text(action)
                if item and item.is_visible():
                    item.click()
                    return
            except Exception:
                pass

            # try a general page text match as last resort
            btn = self.page.get_by_text(action)
            if btn and btn.is_visible():
                self.click(btn)
                return
        except Exception as exc:
            logger.warning(f"Failed to click history action '{action}': {exc}")

    def delete_selected_proposal(self, timeout: int = 10000) -> None:
        """Delete the currently selected proposal via the History Actions dropdown."""
        logger.info("Deleting selected proposal")
        self.open_history_actions()
        self.click_history_action("Delete")
        # handle confirmation popup with a second Delete button
        self.confirm_delete_button.wait_for(state="visible", timeout=timeout)
        self.confirm_delete_button.click()
        logger.info("Confirmed proposal deletion")

    def click_next(self) -> None:  # noqa: C901
        """Click the modal 'Next' button scoped to the currently visible wizard step.

        Wait for the visible step's Next button to become enabled, hover briefly
        to trigger UI hover state, then click. Falls back to healing via
        `BasePage.click` if the scoped click fails.
        """
        logger.info("Clicking wizard Next button (with fallbacks)")
        visible_step = None
        try:
            visible_step = self._get_visible_wizard_step()
        except Exception as exc:
            logger.warning(f"Unable to determine visible wizard step: {exc}")

        # primary scoped button handle
        btn = None
        try:
            if visible_step is not None:
                # try to get the step id and use the per-step locator to avoid strict-mode
                try:
                    vid = visible_step.get_attribute("id")
                except Exception:
                    vid = None

                if vid and vid in self.step_next_buttons:
                    try:
                        btn = self.step_next_buttons[vid].first
                    except Exception:
                        btn = None
                else:
                    # fallback: scope to the visible step locator
                    try:
                        btn = visible_step.locator("button[data-wizard-next]").first
                    except Exception:
                        btn = None
        except Exception:
            btn = None

        # Before attempting click strategies, wait for the button in this step to become enabled
        try:
            selector_to_check = None
            try:
                if vid:
                    selector_to_check = f"#{vid} button[data-wizard-next]"
                else:
                    selector_to_check = 'div[id^="proposal-wizard-"] button[data-wizard-next]'
            except Exception:
                selector_to_check = 'div[id^="proposal-wizard-"] button[data-wizard-next]'

            enabled_selector = self._wait_for_enabled_in_step(selector_to_check, timeout=10000)
            if enabled_selector:
                try:
                    btn = self.page.locator(enabled_selector).first
                except Exception:
                    pass
        except Exception:
            pass

        def _log_and_return(method_name: str) -> None:
            logger.info(f"click_next: succeeded using {method_name}")

        # Try hover + force click on the per-step button immediately (no waits)
        tried_methods = []
        try:
            if btn and btn.count() and btn.is_visible():
                try:
                    btn.hover()
                    self.page.wait_for_timeout(150)
                except Exception:
                    pass

                try:
                    btn.click(force=True)
                    _log_and_return("locator.click(force=True)")
                    return
                except Exception as e:
                    tried_methods.append(("locator.click_force", str(e)))
        except Exception:
            pass

        # if we reach here, all scoped attempts failed — record diagnostics and try broader fallbacks
        try:
            # capture diagnostics: screenshot and visible HTML
            try:
                img = "tmp/next-fail.png"
                self.page.screenshot(path=img)
                logger.info(f"click_next diagnostics: screenshot saved to {img}")
            except Exception:
                logger.warning("click_next diagnostics: failed to save screenshot")

            try:
                if btn:
                    h = btn.element_handle()
                    if h:
                        html = self.page.evaluate("(el)=>el.outerHTML", h)
                        logger.info(f"click_next diagnostics: button outerHTML: {html}")
                elif visible_step:
                    try:
                        html = visible_step.inner_html()
                        logger.info(
                            f"click_next diagnostics: visible_step innerHTML length {len(html)}"
                        )
                    except Exception:
                        pass
            except Exception:
                logger.warning("click_next diagnostics: failed to capture element HTML")
        except Exception:
            pass

        # fallback: try modal-scoped first visible next button
        try:
            fbtn = self.wizard_next_button.filter(has=self.proposal_modal).first
        except Exception:
            fbtn = None

        try:
            if fbtn and fbtn.is_visible():
                try:
                    fbtn.hover()
                    self.page.wait_for_timeout(200)
                except Exception:
                    pass
                try:
                    fbtn.click()
                    _log_and_return("modal_scoped_first.click")
                    return
                except Exception as e:
                    tried_methods.append(("modal_scoped_first.click", str(e)))
        except Exception:
            pass

        # final fallback using BasePage click (includes healing)
        try:
            self.click(self.wizard_next_button)
            _log_and_return("BasePage.click(wizard_next_button)")
            return
        except Exception as exc:
            logger.warning(
                f"Final fallback click_next failed: {exc}; tried methods: {tried_methods}"
            )

    def click_previous(self) -> None:
        logger.info("Clicking wizard Previous button")
        self.click(self.wizard_previous_button)

    def wait_for_details_step(self, timeout: int = 10000) -> None:
        """Wait for details step to be visible"""
        logger.info("Waiting for details step to be visible")
        self.wait_for_element(self.step_details_panel, state="visible", timeout=timeout)

    def wait_for_holdings_step(self, timeout: int = 10000) -> None:
        """Wait for holdings step (step 1) to be visible"""
        logger.info("Waiting for holdings step to be visible")
        self.wait_for_element(self.step_holdings_panel, state="visible", timeout=timeout)

    def store_advisor_name(self) -> None:
        logger.info("Storing advisor name from page header")
        self.advisor_name_element.wait_for(state="visible", timeout=5000)
        self.expected_advisor_name = self.advisor_name_element.inner_text().strip()
        logger.info(f"Stored advisor name: {self.expected_advisor_name}")

    def get_advisor_dropdown_value(self) -> str:
        self.advisor_dropdown.wait_for(state="visible", timeout=5000)
        return self.advisor_dropdown.locator("span.k-input-value-text").inner_text().strip()

    def set_client_name(self, name: str) -> None:
        logger.info(f"Setting client name: {name}")
        self.fill(self.name_input, name)
        # trigger change handlers
        try:
            self.page.evaluate("() => { $('#Name').trigger('change'); }")
        except Exception:
            try:
                self.page.evaluate(
                    "() => { document.querySelector('#Name').dispatchEvent(new Event('change')); }"
                )
            except Exception:
                pass
        # store expected client name for later verification in summary
        try:
            self.expected_client_name = name
        except Exception:
            self.expected_client_name = None

    def clear_holding_form(self) -> None:
        logger.info("Clearing holding form")
        self.click(self.clear_holding_button)

    def delete_holding(self) -> None:
        logger.info("Deleting holding via UI")
        self.click(self.delete_holding_button)

    # -----------------
    # Step 3 helpers (Questionnaire)
    # -----------------
    def wait_for_questionnaire_step(self, timeout: int = 10000) -> None:
        logger.info("Waiting for questionnaire step to be visible")
        self.wait_for_element(self.step_questionnaire_panel, state="visible", timeout=timeout)

    def select_question_answer(self, question_id: int | str, value: str) -> None:
        """Select a questionnaire radio button by question id and option value."""
        selector = f'input[name="question_{question_id}"][value="{value}"]'
        logger.info(f"Selecting questionnaire answer: {selector}")
        locator = self.page.locator(selector)
        self.click(locator)

    def select_first_answer_for_question(self, question_id: int | str) -> None:
        # Normalize question name (accepts numeric id or full 'question_1234')
        qname = self._normalize_qname(question_id)
        selector = f'input[name="{qname}"]'
        logger.info(f"Selecting first questionnaire answer for question {qname}")
        locator = self.page.locator(selector).first
        try:
            self.click(locator)
            return
        except Exception:
            # If direct click fails (input may be hidden), try clicking the label inside the question container
            try:
                # click the first label under the questionnaire-question container matching this qname
                script = (
                    "(qn) => {"
                    " const qEl = document.querySelector('#questionnaire-questions .questionnaire-question[data-question-id="
                    "+qn+"
                    "]');"
                    " if(!qEl) return false;"
                    " const lbl = qEl.querySelector('.answer-option label');"
                    " if(lbl){ lbl.click(); return true; }"
                    " return false;"
                    "}"
                )
                ok = self.page.evaluate(script, qname)
                if not ok:
                    raise RuntimeError(f"Could not click first answer label for {qname}")
            except Exception:
                # last resort: try adjacent label selector
                try:
                    label_locator = self.page.locator(f'input[name="{qname}"] ~ label').first
                    self.click(label_locator)
                except Exception:
                    raise

    # -----------------
    # Questionnaire helpers (dynamic)
    # -----------------
    def get_question_ids(self) -> list:
        """Return an ordered list of radio `name` attributes for questionnaire questions."""
        logger.info("Collecting questionnaire question ids")
        try:
            ids = self.page.eval_on_selector_all(
                '#questionnaire-questions input[type="radio"]',
                "els => Array.from(new Set(els.map(e => e.name)))",
            )
            return ids or []
        except Exception:
            return []

    def get_question_meta(self) -> list:
        """Return ordered metadata for each questionnaire question.

        Each item: { index, question_id, text, options: [ {value, label} ] }
        """
        logger.info("Reading questionnaire metadata")
        script = (
            "() => {"
            " const nodes = Array.from(document.querySelectorAll('#questionnaire-questions .questionnaire-question'));"
            " return nodes.map((n,i) => {"
            "   const qid = n.getAttribute('data-question-id') || (n.querySelector('input[type=radio]') && n.querySelector('input[type=radio]').name);"
            "   const qtextEl = n.querySelector('.question-text');"
            "   const qtext = qtextEl ? qtextEl.innerText.trim() : '';"
            "   const opts = Array.from(n.querySelectorAll('.answer-option')).map(opt => { const inp = opt.querySelector('input[type=radio]'); return { value: inp ? inp.value : null, label: opt.innerText.trim() }; });"
            "   return { index: i, question_id: qid, text: qtext, options: opts };"
            " }); }"
        )
        try:
            meta = self.page.evaluate(script)
            return meta or []
        except Exception:
            return []

    def _normalize_qname(self, q: int | str) -> str:
        if isinstance(q, int):
            return f"question_{q}"
        s = str(q)
        if s.startswith("question_"):
            return s
        if s.isdigit():
            return f"question_{s}"
        return s

    def answer_question_by_id(self, question_id: int | str, option_value: str) -> None:
        qname = self._normalize_qname(question_id)
        logger.info(f"Answering question {qname} with value {option_value}")
        selector = f'input[name="{qname}"][value="{option_value}"]'
        locator = self.page.locator(selector)
        self.wait_for_element(locator, state="visible", timeout=5000)
        self.click(locator)

    def answer_question_by_text(self, question_id: int | str, option_text: str) -> None:
        qname = self._normalize_qname(question_id)
        logger.info(f"Answering question {qname} by matching option text '{option_text}'")
        # Use JS to find label containing the text for the question and click its input
        script = (
            "(qn, txt) => {"
            " const qEl = document.querySelector('#questionnaire-questions .questionnaire-question[data-question-id="
            "+qn+"
            "]');"
            " if(!qEl) return false;"
            " const labels = Array.from(qEl.querySelectorAll('.answer-option label'));"
            " const found = labels.find(l => l.innerText && l.innerText.trim().toLowerCase().includes(txt.trim().toLowerCase()));"
            " if(found){ const inp = found.querySelector('input[type=radio]'); if(inp){ inp.click(); return true; } }"
            " return false;"
            "}"
        )
        try:
            ok = self.page.evaluate(script, qname, option_text)
            if not ok:
                raise RuntimeError(f"Option with text '{option_text}' not found for {qname}")
        except Exception:
            raise

    def answer_question_by_index(
        self, idx: int, option_value_or_text: str, by_text: bool = False
    ) -> None:
        ids = self.get_question_ids()
        if not ids:
            raise ValueError("No questionnaire questions found")
        # allow 1-based index for convenience
        if idx <= 0:
            raise ValueError("Index must be >= 1")
        if idx > len(ids):
            raise ValueError(f"Index {idx} out of range (1..{len(ids)})")
        qname = ids[idx - 1]
        if by_text:
            self.answer_question_by_text(qname, option_value_or_text)
        else:
            self.answer_question_by_id(qname, option_value_or_text)

    def answer_all_questions(self, answers: dict | None = None, default: str = "first") -> None:
        """Answer all questionnaire questions.

        `answers` may map question identifiers (question_2110), numeric indices (1-based), or question text
        to an option value or option text. If an answer is not supplied for a question, `default` controls
        behavior: 'first' -> pick first option, or supply a specific option value.
        """
        logger.info("Answering all questionnaire questions")
        self.wait_for_questionnaire_step()
        ids = self.get_question_ids()
        if not ids:
            logger.info("No questions found to answer; retrying briefly for late-loaded questions")
            start = time.time()
            retry_timeout = 8.0
            while time.time() - start < retry_timeout:
                try:
                    self.page.wait_for_timeout(500)
                except Exception:
                    pass
                ids = self.get_question_ids()
                if ids:
                    logger.info(
                        f"Questionnaire appeared after {int((time.time() - start) * 1000)}ms"
                    )
                    break
            if not ids:
                logger.info("No questions found after retry; continuing without answering")
                return

        for idx, qname in enumerate(ids, start=1):
            answered = False
            # check numeric index key
            if answers is not None:
                # direct id key
                if qname in answers:
                    val = answers[qname]
                    # detect if value looks like a label (non-numeric) — try by text first
                    if isinstance(val, str) and not val.isdigit():
                        try:
                            self.answer_question_by_text(qname, val)
                        except Exception:
                            self.answer_question_by_id(qname, val)
                    else:
                        self.answer_question_by_id(qname, str(val))
                    answered = True
                # index key (1-based)
                elif str(idx) in answers:
                    val = answers[str(idx)]
                    if isinstance(val, str) and not val.isdigit():
                        try:
                            self.answer_question_by_text(qname, val)
                        except Exception:
                            self.answer_question_by_id(qname, val)
                    else:
                        self.answer_question_by_id(qname, str(val))
                    answered = True

            if not answered:
                if default == "first":
                    # legacy name compatibility: select the first available answer
                    self.select_first_answer_for_question(qname)
                else:
                    # treat default as option value
                    self.answer_question_by_id(qname, str(default))

    # Backwards-compatible alias for older tests
    def answer_first_option_for_question(self, question_id: int | str) -> None:
        """Alias to `select_first_answer_for_question` kept for backwards compatibility."""
        self.select_first_answer_for_question(question_id)

    # -----------------
    # Allocation step helpers
    # -----------------
    def select_objective_tab(self) -> None:
        logger.info("Selecting Objective tab in allocation filters")
        self.click(self.filter_tab_objective)

    def select_performance_tab(self) -> None:
        logger.info("Selecting Performance tab in allocation filters")
        self.click(self.filter_tab_performance)

    def select_fee_tab(self) -> None:
        logger.info("Selecting Fee tab in allocation filters")
        self.click(self.filter_tab_fee)

    def select_first_allocation(self, timeout: int = 10000) -> str:
        """Click the first row in the allocation grid and return its name."""
        logger.info("Selecting first allocation row")
        try:
            first = self.allocation_grid_rows.first
            self.wait_for_element(first, state="visible", timeout=timeout)
            # read the name from the first cell
            try:
                name = first.locator("td").nth(0).inner_text().strip()
            except Exception:
                name = ""
            first.click()
            # wait for the selected allocation card to appear and populate
            self.wait_for_element(self.selected_allocation_card, state="visible", timeout=timeout)
            # wait for both the details card and the risk/reward card to be populated
            try:
                self._wait_for_card_populated(self.selected_allocation_details, timeout=timeout)
            except Exception:
                logger.warning("Selected allocation details did not populate in time")
            try:
                self._wait_for_card_populated(self.risk_reward_card, timeout=timeout)
            except Exception:
                logger.warning("Risk & Performance card did not populate in time")
            # capture strategy from the details and store expected values
            try:
                # attempt to read the Strategy value from details table
                strategy = ""
                strategy_locator = self.selected_allocation_details.locator(".detail-label")
                value_locator = self.selected_allocation_details.locator(".detail-value")
                # find the Strategy label index
                for i in range(value_locator.count()):
                    try:
                        lbl = strategy_locator.nth(i).inner_text().strip()
                        if lbl == "Strategy":
                            strategy = value_locator.nth(i).inner_text().strip()
                            break
                    except Exception:
                        continue
                self.expected_allocation_name = name
                self.expected_strategy = strategy
            except Exception:
                self.expected_allocation_name = name
                self.expected_strategy = None
            return name
        except Exception as exc:
            logger.warning(f"Failed to select first allocation: {exc}")
            return ""

    def click_preview(self, times: int = 1, pause_ms: int = 250) -> None:
        """Click the PREVIEW button `times` times, with a short pause between clicks.

        Used by the generate report flow where the UI requires repeated clicks.
        """
        # Guard against duplicate PREVIEW clicks in the same flow
        if self._preview_clicked:
            logger.info("Skipping PREVIEW click; already clicked in this flow")
            return

        logger.info(f"Clicking PREVIEW button {times} times")
        for _ in range(max(1, int(times))):
            try:
                self.click(self.preview_button)
                # short pause to allow UI to react
                self.page.wait_for_timeout(pause_ms)
            except Exception as exc:
                logger.warning(f"Failed clicking PREVIEW button: {exc}")
        # mark as clicked so subsequent accidental calls are no-ops
        try:
            self._preview_clicked = True
        except Exception:
            pass

    def _wait_for_card_populated(
        self, locator: Locator, timeout: int = 10000
    ) -> None:  # noqa: C901
        """Wait until the given card locator has non-empty textual content indicating it is populated.

        Elements for cards are often visible before they have their content. This helper polls the
        locator.inner_text() until it contains meaningful content or times out.
        """
        logger.info(f"Waiting for card content to populate for locator: {locator}")
        end = time.time() + (int(timeout) / 1000.0)
        while time.time() < end:
            try:
                # prefer inner_text to capture rendered content
                txt = locator.inner_text().strip()
                if txt and txt not in ("--", "No data", "Loading..."):
                    return
            except Exception:
                pass

            # Special-case heuristics for the Risk & Performance card where
            # content may be rendered as SVG/chart or a Kendo grid rather than
            # plain text. If the locator corresponds to the risk/reward card,
            # ensure the empty-state element is hidden and there is meaningful
            # DOM content (svg or grid rows or non-trivial innerHTML).
            try:
                aid = None
                try:
                    aid = locator.get_attribute("id")
                except Exception:
                    aid = None
                if aid == "proposal-risk-reward-card":
                    # check empty-state visibility
                    try:
                        empty = self.page.locator("#proposal-risk-reward-empty-state")
                        if empty.count():
                            if empty.first.is_visible():
                                # still empty
                                pass
                            else:
                                # empty-state hidden -> look for svg or grid rows
                                try:
                                    if locator.locator("svg").count() > 0:
                                        return
                                except Exception:
                                    pass
                                try:
                                    if locator.locator("table.k-grid-table tbody tr").count() > 0:
                                        return
                                except Exception:
                                    pass
                                # fallback: innerHTML length indicates content
                                try:
                                    h = locator.element_handle()
                                    if h:
                                        length = self.page.evaluate("(el)=>el.innerHTML.length", h)
                                        if length and int(length) > 20:
                                            return
                                except Exception:
                                    pass
                        else:
                            # no explicit empty-state element found; still check for svg/grid
                            try:
                                if locator.locator("svg").count() > 0:
                                    return
                            except Exception:
                                pass
                            try:
                                if locator.locator("table.k-grid-table tbody tr").count() > 0:
                                    return
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                self.page.wait_for_timeout(200)
            except Exception:
                time.sleep(0.2)
        raise TimeoutError("Timed out waiting for card to be populated")

    def select_allocation_by_name(self, name: str, timeout: int = 10000) -> None:
        """Select an allocation row matching the given name (exact match) and wait for panels to load."""
        logger.info(f"Selecting allocation row by name: {name}")
        # find row cell with exact text and click its parent row
        row = self.page.locator(
            f"//div[@id='proposal-allocation-grid-wrapper']//table//tbody//tr/td[normalize-space()='{name}']/parent::tr"
        )
        self.wait_for_element(row, state="visible", timeout=timeout)
        row.click()
        # wait for card and risk/perf to populate
        self.wait_for_element(self.selected_allocation_card, state="visible", timeout=timeout)
        try:
            self._wait_for_card_populated(self.selected_allocation_details, timeout=timeout)
        except Exception:
            logger.warning("Selected allocation details did not populate in time")
        try:
            self._wait_for_card_populated(self.risk_reward_card, timeout=timeout)
        except Exception:
            logger.warning("Risk & Performance card did not populate in time")

    def get_selected_allocation_details(self, timeout: int = 10000) -> dict:
        """Wait for the selected allocation card to populate and return details dict.

        Returns dict with keys: Name, Strategy, Risk Range, Tolerance Band, etc.
        Also includes 'details_populated' (bool), 'risk_populated' (bool),
        and 'risk_contains_name' (bool, set after checking for expected_name if provided).
        """
        logger.info("Getting selected allocation details")
        self.wait_for_element(self.selected_allocation_card, state="visible", timeout=timeout)

        details_populated = True
        risk_populated = True
        try:
            self._wait_for_card_populated(self.selected_allocation_details, timeout=timeout)
        except Exception:
            details_populated = False
        try:
            self._wait_for_card_populated(self.risk_reward_card, timeout=timeout)
        except Exception:
            risk_populated = False

        # read details table labels/values
        labels = self.page.locator("#proposal-allocation-details .detail-label")
        values = self.page.locator("#proposal-allocation-details .detail-value")
        try:
            count = labels.count()
        except Exception:
            count = 0

        details = {}
        for i in range(count):
            try:
                key = labels.nth(i).inner_text().strip()
                val = values.nth(i).inner_text().strip()
                details[key] = val
            except Exception:
                continue

        details["details_populated"] = details_populated
        details["risk_populated"] = risk_populated
        return details

    def is_risk_reward_name_visible(self, expected_name: str, timeout: int = 10000) -> bool:
        """Check whether the risk/reward card contains the expected allocation name."""
        try:
            self.wait_for_element(self.risk_reward_card, state="visible", timeout=timeout)
            name_locator = self.risk_reward_card.locator(f"text={expected_name}")
            self.wait_for_element(name_locator, state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_summary_details(self, timeout: int = 10000) -> dict:
        """Wait for the summary step to populate and return a dict of summary values.

        Returns dict with keys: client, strategy, composite, investment_amount (float or None),
        investment_raw (str), visible (bool).
        """
        logger.info("Getting proposal summary details")
        client_loc = self.page.locator("#summary-client-name")
        strat_loc = self.page.locator("#summary-strategy-name")
        comp_loc = self.page.locator("#summary-composite-name")

        visible = True
        try:
            self.wait_for_element(client_loc, state="visible", timeout=timeout)
        except Exception:
            visible = False

        client = ""
        if visible:
            client = client_loc.inner_text().strip()
            # poll until placeholder is replaced
            if not client or client == "--":
                logger.info("Summary client placeholder detected; waiting for populated value")
                endt = time.time() + (timeout / 1000.0)
                while time.time() < endt:
                    try:
                        client = client_loc.inner_text().strip()
                        if client and client != "--":
                            break
                    except Exception:
                        pass
                    time.sleep(0.2)

        strategy = ""
        composite = ""
        if visible:
            strategy = strat_loc.inner_text().strip()
            composite = comp_loc.inner_text().strip()

        investment_raw = ""
        investment_amount = None
        inv_loc = self.page.locator("#summary-investment-amount")
        try:
            self.wait_for_element(inv_loc, state="visible", timeout=timeout)
            investment_raw = inv_loc.inner_text().strip()
            norm = investment_raw.replace("$", "").replace(",", "").strip()
            investment_amount = float(norm)
        except Exception:
            pass

        return {
            "client": client,
            "strategy": strategy,
            "composite": composite,
            "investment_amount": investment_amount,
            "investment_raw": investment_raw,
            "visible": visible,
        }

    # -----------------
    # Template / Available Reports helpers (preview modal)
    # -----------------
    def wait_for_template_report_modal(self, timeout: int = 10000) -> None:
        """Wait for the PREVIEW/GENERATE REPORT template report selector modal to be visible."""
        logger.info("Waiting for template report selector modal")
        self.wait_for_element(self.template_report_selector_modal, state="visible", timeout=timeout)

    def open_template_report_dropdown(self) -> None:
        """Open the template report combobox (click the visible combobox input)."""
        logger.info("Opening template report selector combobox")
        try:
            self.click(self.template_report_selector_input)
        except Exception:
            # fallback: click underlying hidden combobox
            try:
                self.click(self.template_report_selector_combobox)
            except Exception:
                logger.warning("Failed to open template report selector combobox")

    def select_template_name_by_text(self, name: str) -> bool:
        """Select a template name in the template combobox by visible text.

        Tries the Kendo ComboBox API first, falls back to clicking the listbox item.
        Returns True if selection succeeded.
        """
        logger.info(f"Selecting template name in combobox by text (UI): {name}")
        try:
            # Try to click the combobox expand button first (preferred UI path)
            try:
                btn = self.template_report_selector_modal.locator(
                    'button[aria-label="expand combobox"]'
                ).first
                if btn and btn.is_visible():
                    self.click(btn)
                else:
                    # fallback to clicking the visible input
                    self.open_template_report_dropdown()
            except Exception:
                # fallback: click the combobox input
                try:
                    self.open_template_report_dropdown()
                except Exception:
                    pass

            # wait for the Kendo listbox to appear
            listbox = self.page.locator("#template-selector-dropdown_listbox")
            try:
                self.wait_for_element(listbox, state="visible", timeout=5000)
            except Exception:
                # sometimes the listbox is rendered under a different id or immediately populated
                pass

            # try exact-match first, then contains
            item = listbox.locator("li").filter(has_text=name).first
            if item and item.is_visible():
                self.click(item)
                return True

            item2 = listbox.locator("li").filter(has_text=name, exact=False).first
            if item2 and item2.is_visible():
                self.click(item2)
                return True

            # final fallback: search any visible list item on page
            try:
                any_item = self.page.locator("li.k-list-item").filter(has_text=name).first
                if any_item and any_item.is_visible():
                    self.click(any_item)
                    return True
            except Exception:
                pass

        except Exception as exc:
            logger.warning(f"UI template selection failed for '{name}': {exc}")

        logger.warning(f"Unable to select template name '{name}' via UI")
        return False

    def get_available_reports(self) -> list:
        """Return list of available report items as dicts: {text, id, data_uid} (order preserved)."""
        logger.info("Reading available reports list")
        out: list = []
        try:
            count = self.available_reports_list_items.count()
        except Exception:
            return out
        for i in range(count):
            try:
                item = self.available_reports_list_items.nth(i)
                text = item.inner_text().strip()
                elem_id = item.get_attribute("id")
                data_uid = item.get_attribute("data-uid")
                out.append({"text": text, "id": elem_id, "data_uid": data_uid})
            except Exception:
                continue
        return out

    def select_available_report_by_name(self, name: str, timeout: int = 5000) -> None:
        """Select an available report by visible name by double-clicking its list item.

        If double-clicking doesn't move the item, consider using
        `select_report_by_name_using_kendo` which manipulates the Kendo listbox.
        """
        logger.info(f"Selecting available report by name: {name}")
        try:
            locator = (
                self.template_report_selector_modal.locator(".k-list-ul li.k-list-item")
                .filter(has_text=name)
                .first
            )
            self.wait_for_element(locator, state="visible", timeout=timeout)
            # double-click to move between listboxes (client uses dblclick handler)
            locator.dblclick()
        except Exception as exc:
            logger.warning(f"Failed selecting available report '{name}' via UI: {exc}")

    def select_report_by_name_using_kendo(self, name: str) -> bool:
        """Use the page JS Kendo ListBox API to move an available report with matching Name to Selected.

        Returns True if moved, False otherwise.
        """
        logger.info(f"Selecting report by name using Kendo API: {name}")
        script = (
            "(repName) => {"
            "  var av = $('#available-reports').data('kendoListBox');"
            "  var sel = $('#selected-reports').data('kendoListBox');"
            "  if(!av || !sel) return false;"
            "  var data = av.dataSource.data();"
            "  var item = null;"
            "  for(var i=0;i<data.length;i++){ if(data[i].Name && data[i].Name.trim().toLowerCase() === repName.trim().toLowerCase()){ item = data[i]; break; } }"
            "  if(!item) return false;"
            "  sel.dataSource.add(item);"
            "  av.dataSource.remove(item);"
            "  return true;"
            "}"
        )
        try:
            return bool(self.page.evaluate(script, name))
        except Exception as exc:
            logger.warning(f"Kendo API move failed for '{name}': {exc}")
            return False

    def select_report_by_partial_name_using_kendo(self, name_substr: str) -> bool:
        """Move an available report whose Name contains `name_substr` (case-insensitive)
        using the Kendo ListBox API. Returns True if moved, False otherwise."""
        logger.info(f"Selecting report by partial name using Kendo API: {name_substr}")
        script = (
            "(substr) => {"
            "  var av = $('#available-reports').data('kendoListBox');"
            "  var sel = $('#selected-reports').data('kendoListBox');"
            "  if(!av || !sel) return false;"
            "  var data = av.dataSource.data();"
            "  var item = null;"
            "  var s = substr.trim().toLowerCase();"
            "  for(var i=0;i<data.length;i++){ if(data[i].Name && data[i].Name.toLowerCase().indexOf(s) !== -1){ item = data[i]; break; } }"
            "  if(!item) return false;"
            "  sel.dataSource.add(item);"
            "  av.dataSource.remove(item);"
            "  return true;"
            "}"
        )
        try:
            return bool(self.page.evaluate(script, name_substr))
        except Exception as exc:
            logger.warning(f"Kendo partial-match move failed for '{name_substr}': {exc}")
            return False

    def select_all_reports(
        self, reports: list | None = None, wait: bool = True
    ) -> dict:  # noqa: C901
        """Select all reports in the template report selector modal.

        Tries Kendo API first, falls back to UI dblclick. Handles 'Holdings:' partial entries.
        Returns a mapping {requested_name: moved_bool}.
        """
        if reports is None:
            reports = [
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
                "Holdings:",
            ]

        if wait:
            try:
                self.wait_for_template_report_modal()
            except Exception:
                logger.warning(
                    "Template report modal not visible when attempting to select reports"
                )

        results = {}
        for rpt in reports:
            moved = False
            # try exact name via Kendo API
            try:
                moved = self.select_report_by_name_using_kendo(rpt)
            except Exception:
                moved = False

            # UI dblclick fallback
            if not moved:
                try:
                    self.select_available_report_by_name(rpt)
                    moved = True
                except Exception:
                    moved = False

            # handle Holdings: entries which might include allocation name
            if not moved and rpt.lower().startswith("holdings"):
                try:
                    parts = rpt.split(":", 1)
                    remainder = parts[1].strip() if len(parts) > 1 else ""

                    found = None
                    avail = self.get_available_reports()
                    if remainder:
                        for a in avail:
                            t = a["text"].strip()
                            if remainder.lower() in t.lower() and "holdings" in t.lower():
                                found = t
                                break
                    if not found:
                        for a in avail:
                            if a["text"].strip().lower().startswith("holdings"):
                                found = a["text"]
                                break

                    if found:
                        try:
                            moved = self.select_report_by_name_using_kendo(found)
                        except Exception:
                            moved = False

                        if not moved:
                            moved = self.select_report_by_partial_name_using_kendo(found)

                        if not moved:
                            try:
                                self.select_available_report_by_name(found)
                                moved = True
                            except Exception:
                                moved = False
                except Exception:
                    moved = False

            results[rpt] = bool(moved)

        return results

    # -----------------
    # Preview / Generate modal helpers
    # -----------------
    def wait_for_preview_generate_modal(self, timeout: int = 10000) -> None:
        """Wait for the secondary preview/generate proposal modal to appear.

        The modal contains a single PREVIEW button which opens the generated
        PDF in a new tab; detect the modal by looking for that PREVIEW button.
        """
        logger.info("Waiting for preview/generate modal")
        # Use instance locator so BasePage healing is applied consistently.
        try:
            self.wait_for_element(self.preview_button, state="visible", timeout=timeout)
            return
        except Exception:
            pass
        try:
            # fallback: template modal itself may be visible
            self.wait_for_element(
                self.template_report_selector_modal, state="visible", timeout=timeout
            )
            return
        except Exception:
            raise TimeoutError("Preview/Generate modal not visible")

    def click_preview_proposal_and_verify_tab(  # noqa: C901
        self, timeout: int = 20000, save_pdf_path: str = "tmp/proposal_preview.pdf"
    ) -> str | None:
        """Click the Preview Proposal button, wait for the PDF tab, save the PDF locally, and return focus.

        Args:
            timeout: max wait time in ms for the preview button / new tab.
            save_pdf_path: local file path to save the downloaded PDF.

        Returns:
            The path to the saved PDF file, or None if the PDF could not be saved.
        """
        logger.info("Clicking PREVIEW PROPOSAL button and verifying new tab")
        preview_proposal_btn = self.preview_proposal_button
        try:
            wait_timeout = max(timeout, 60000)
            self.wait_for_element(preview_proposal_btn, state="visible", timeout=wait_timeout)
        except Exception as exc:
            raise TimeoutError(
                f"Preview Proposal button did not appear after GENERATE PREVIEW: {exc}"
            )

        if not preview_proposal_btn.is_visible():
            raise RuntimeError("Preview Proposal locator is not visible")
        dis = preview_proposal_btn.get_attribute("disabled")
        aria = preview_proposal_btn.get_attribute("aria-disabled")
        if dis is not None or (aria is not None and str(aria).strip().lower() == "true"):
            raise RuntimeError("Preview Proposal locator is disabled/aria-disabled")

        new_page = None
        try:
            with self.page.context.expect_page(timeout=15000) as new_page_info:
                preview_proposal_btn.click()
            new_page = new_page_info.value
        except Exception:
            logger.warning(
                "No new tab created by Preview Proposal click; checking for same-tab PDF"
            )

        saved_path: str | None = None

        if new_page:
            wait_deadline = time.time() + max(timeout, 90000) / 1000.0
            try:
                new_page.wait_for_load_state("load", timeout=max(timeout, 60000))
            except Exception:
                pass
            try:
                new_page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            # Poll URL until it stabilizes (no change for 0.5s) or deadline
            prev_url = new_page.url or ""
            last_change = time.time()
            while time.time() < wait_deadline:
                cur_url = new_page.url or ""
                if cur_url != prev_url:
                    prev_url = cur_url
                    last_change = time.time()
                elif time.time() - last_change > 0.5:
                    break
                time.sleep(0.15)

            final_url = new_page.url or ""
            logger.info(f"Preview opened in new tab (final url={final_url})")

            # Download the PDF from the new tab's URL
            try:
                from pathlib import Path

                Path(save_pdf_path).parent.mkdir(parents=True, exist_ok=True)

                response = self.page.context.request.get(final_url)
                if response.ok:
                    with open(save_pdf_path, "wb") as f:
                        f.write(response.body())
                    saved_path = save_pdf_path
                    logger.info(f"PDF saved to {save_pdf_path} ({len(response.body())} bytes)")
                else:
                    logger.warning(f"Failed to download PDF: HTTP {response.status}")
            except Exception as exc:
                logger.warning(f"Failed to save PDF from preview tab: {exc}")

            # Close the preview tab and return focus
            try:
                new_page.close()
            except Exception:
                pass
            try:
                self.page.bring_to_front()
                logger.info("Brought original page to front after preview")
            except Exception:
                logger.warning("Failed to bring original page to front")

        return saved_path

    def click_finish_button(self) -> bool:
        """Click a Finish button"""
        try:
            # legacy text-based Finish locator removed; use scoped helpers instead
            logger.info("click_finish_button legacy removed; use click_finish()")
            return False
        except Exception:
            pass
        logger.warning("Unable to click the finish button")
        return False

    def get_finish_primary_locator(self) -> Locator:
        """Return the primary wizard Finish button locator scoped to the wizard modal."""
        return self.finish_primary_button

    def get_finish_confirm_locator(self) -> Locator:
        """Return the confirmation Finish button locator for any follow-up modal."""
        return self.finish_confirm_button

    def click_finish_primary(self) -> bool:
        """Click the primary wizard Finish button and return True if clicked."""
        try:
            loc = self.get_finish_primary_locator()
            try:
                if loc and loc.count() and loc.first.is_visible():
                    self.click(loc.first)
                    logger.info("Clicked primary wizard Finish")
                    return True
            except Exception:
                pass
        except Exception:
            pass
        logger.warning("Primary wizard Finish not found or click failed")
        return False

    def click_finish_confirm(self, timeout: int = 5000) -> bool:  # noqa: C901
        """If a confirmation Finish modal appears, click its Finish and wait for it to close.

        Returns True if a confirmation Finish was clicked, False otherwise.
        """
        # Prefer locating the confirmation modal content by known id (actionSmallWindow)
        content = None
        try:
            content = self.page.locator("#actionSmallWindow").first
        except Exception:
            content = None

        # fallback to previously discovered confirm modal
        if not content or not getattr(content, "count", lambda: 0)():
            try:
                content = self.finish_confirm_modal.locator("#actionSmallWindow")
            except Exception:
                content = None

        if not content or not getattr(content, "count", lambda: 0)():
            # no identifiable content; fallback to generic confirm modal
            loc = self.get_finish_confirm_locator()
            if not loc or not getattr(loc, "count", lambda: 0)():
                return False
            content = loc.first

        end = time.time() + (int(timeout) / 1000.0)
        while time.time() < end:
            try:
                # find the nearest k-window container for this content
                try:
                    wnd_handle = content.evaluate_handle('(el) => el.closest("div.k-window")')
                except Exception:
                    wnd_handle = None

                is_open = False
                if wnd_handle:
                    try:
                        is_open = self.page.evaluate(
                            """(wnd) => {
                            try {
                                var s = window.getComputedStyle(wnd);
                                if(!s) return false;
                                if(s.display && s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity||1) > 0) return true;
                                if(wnd.classList && wnd.classList.contains && wnd.classList.contains('enhanced-modal')) return true;
                            } catch(e) {}
                            return false;
                        }""",
                            wnd_handle,
                        )
                    except Exception:
                        is_open = False

                # If the window is open, click the Finish button inside the content
                if is_open:
                    try:
                        btn = content.locator("button.k-primary, button:has-text('Finish')").first
                        if btn and btn.count() and btn.first.is_visible():
                            self.click(btn.first)
                            logger.info("Clicked confirmation Finish button")
                            # wait for window to hide or overlay gone
                            try:
                                if wnd_handle:
                                    self.page.wait_for_function(
                                        "(wnd)=>{return window.getComputedStyle(wnd).display==='none' || wnd.classList.contains('k-hidden')}",
                                        wnd_handle,
                                        timeout=5000,
                                    )
                                else:
                                    self.wait_for_overlay_to_disappear(timeout=5000)
                            except Exception:
                                try:
                                    self.wait_for_overlay_to_disappear(timeout=5000)
                                except Exception:
                                    pass
                            return True
                    except Exception:
                        pass

            except Exception:
                pass

            time.sleep(0.12)

        return False

    def click_finish(self, timeout: int = 10000) -> bool:
        """Orchestrate Finish flow: click primary Finish then handle any confirmation modal.

        Returns True if the flow completed (primary clicked and any confirmation handled), False otherwise.
        """
        try:
            clicked = self.click_finish_primary()
            if not clicked:
                return False

            # After clicking primary, wait for either the confirmation modal to appear
            # and be clickable, or for the History step to become visible (flow advanced).
            end = time.time() + (int(timeout) / 1000.0)
            while time.time() < end:
                # 1) check for confirmation modal becoming visible
                try:
                    if (
                        self.finish_confirm_modal.count()
                        and self.finish_confirm_modal.first.is_visible()
                    ):
                        logger.info("Confirmation Finish modal detected; attempting confirm click")
                        ok = self.click_finish_confirm(
                            timeout=min(5000, int((end - time.time()) * 1000))
                        )
                        if ok:
                            try:
                                self.wait_for_overlay_to_disappear(timeout=5000)
                            except Exception:
                                pass
                            return True
                except Exception:
                    pass

                # 2) check if history step appeared (flow completed without confirmation)
                try:
                    if (
                        self.step_history_panel.count()
                        and self.step_history_panel.first.is_visible()
                    ):
                        return True
                except Exception:
                    pass

                try:
                    time.sleep(0.12)
                except Exception:
                    pass
        except Exception as exc:
            logger.warning(f"click_finish orchestration failed: {exc}")
        return False

    # -----------------
    # Scoped titlebar-close helpers for specific modals
    # -----------------
    def get_preview_proposal_close_locator(self):
        """Return the titlebar close button locator for the final Preview Proposal confirmation modal."""
        return self.preview_proposal_titlebar_close

    def click_preview_proposal_close(self) -> bool:  # noqa: C901
        """Click the titlebar close for the Preview Proposal confirmation modal. Returns True if clicked."""
        try:
            loc = self.get_preview_proposal_close_locator()
            try:
                if loc and loc.count() and loc.first.is_visible():
                    self.click(loc.first)
                    logger.info("Clicked Preview Proposal modal titlebar close")
                    # wait for the confirmation modal to hide from view (it remains in DOM with display:none)
                    try:
                        self.wait_for_element(
                            self.preview_proposal_modal, state="hidden", timeout=5000
                        )
                    except Exception:
                        # Not fatal; continue to verify template/overlay state
                        logger.info(
                            "Preview Proposal modal did not hide within timeout (continuing)"
                        )
                    # ensure overlay/template modal state settled before next interactions
                    try:
                        self.wait_for_element(
                            self.template_report_modal_scoped, state="visible", timeout=5000
                        )
                    except Exception:
                        try:
                            self.wait_for_overlay_to_disappear(timeout=5000)
                        except Exception:
                            pass
                    return True
            except Exception:
                pass
            # fallback: use the pre-defined SVG close locator for the same modal
            alt = self.preview_proposal_titlebar_close_svg
            try:
                if alt and alt.count() and alt.first.is_visible():
                    self.click(alt.first)
                    logger.info("Clicked Preview Proposal modal SVG close")
                    try:
                        self.wait_for_element(
                            self.preview_proposal_modal, state="hidden", timeout=5000
                        )
                    except Exception:
                        logger.info(
                            "Preview Proposal modal did not hide within timeout (continuing)"
                        )
                    try:
                        self.wait_for_element(
                            self.template_report_modal_scoped, state="visible", timeout=5000
                        )
                    except Exception:
                        try:
                            self.wait_for_overlay_to_disappear(timeout=5000)
                        except Exception:
                            pass
                    return True
            except Exception:
                pass
        except Exception:
            pass
        logger.warning("Preview Proposal modal close button not found or click failed")
        return False

    def get_preview_report_close_locator(self):
        """Return the titlebar close button locator for the Template/Generate Report modal."""
        return self.template_report_titlebar_close

    def click_preview_report_close(self) -> bool:
        """Click the titlebar close for the Template / Generate Report modal. Returns True if clicked."""
        try:
            loc = self.get_preview_report_close_locator()
            try:
                if loc and loc.count() and loc.first.is_visible():
                    self.click(loc.first)
                    logger.info("Clicked Template/Generate Report modal titlebar close")
                    return True
            except Exception:
                pass
            alt = self.template_report_titlebar_close_svg
            try:
                if alt and alt.count() and alt.first.is_visible():
                    self.click(alt.first)
                    logger.info("Clicked Template/Generate Report modal SVG close")
                    return True
            except Exception:
                pass
        except Exception:
            pass
        logger.warning("Template/Generate Report modal close button not found or click failed")
        return False

    def get_edit_prospect_close_locator(self):
        """Return the titlebar close button locator for the Edit/Create Prospect wizard modal."""
        # wizard popup is rendered into a k-window with #wizardPopup content
        return self.page.locator(
            "div.k-window:has(#wizardPopup) div.k-window-titlebar-actions button.k-dialog-close"
        ).first

    def click_edit_prospect_close(self) -> bool:
        """Click the titlebar close for the Edit/Create Prospect wizard modal. Returns True if clicked."""
        try:
            loc = self.get_edit_prospect_close_locator()
            try:
                if loc.count() and loc.first.is_visible():
                    self.click(loc.first)
                    logger.info("Clicked Edit/Create Prospect modal titlebar close")
                    return True
            except Exception:
                pass
            alt = self.page.locator(
                "div.k-window:has(#wizardPopup) div.k-window-titlebar-actions button:has(svg)"
            ).first
            try:
                if alt.count() and alt.first.is_visible():
                    self.click(alt.first)
                    logger.info("Clicked Edit/Create Prospect modal SVG close")
                    return True
            except Exception:
                pass
        except Exception:
            pass
        logger.warning("Edit/Create Prospect modal close button not found or click failed")
        return False

    # -----------------
    # Step 1 - detailed field setters
    # -----------------
    def set_proposal_email(self, email: str) -> None:
        logger.info(f"Setting proposal email: {email}")
        self.fill(self.email_input, email)
        # trigger any change/validation handlers
        self.page.evaluate("() => { $('#Email').trigger('change'); }")

    def set_name_extended(self, value: str) -> None:
        logger.info(f"Setting NameExtended: {value}")
        self.fill(self.name_extended_input, value)

    def set_address(self, value: str) -> None:
        logger.info(f"Setting Address: {value}")
        self.fill(self.address_input, value)

    def set_city(self, value: str) -> None:
        logger.info(f"Setting City: {value}")
        self.fill(self.city_input, value)

    def set_zip(self, value: str) -> None:
        logger.info(f"Setting Zip: {value}")
        self.fill(self.zip_input, value)

    def set_account_name(self, value: str) -> None:
        logger.info(f"Setting AccountName: {value}")
        self.fill(self.account_name_input, value)

    def set_account_number(self, value: str) -> None:
        logger.info(f"Setting AccountNumber: {value}")
        self.fill(self.account_number_input, value)

    def set_investment_amount(self, value: Union[str, float, int]) -> None:
        """Set the Investment Amount field. Accepts numeric or string input; stores as float."""
        logger.info(f"Setting InvestmentAmount: {value}")
        # normalize to a numeric string for input
        try:
            if isinstance(value, str):
                v = value.strip().replace("$", "").replace(",", "")
            else:
                v = str(value)
            num = float(v)
            # set numeric value via JS to ensure the field receives a numeric type
            try:
                self.page.evaluate(
                    "(v) => { $('#InvestmentAmount').val(v); $('#InvestmentAmount').trigger('change'); }",
                    num,
                )
            except Exception:
                # fallback to fill if JS fails
                self.fill(self.investment_amount_input, str(num))
            self.expected_investment_amount = num
        except Exception:
            logger.warning(f"Unable to parse investment amount '{value}' as number")
            # fallback: fill as provided and clear expected
            try:
                self.fill(self.investment_amount_input, str(value))
            except Exception:
                pass
            self.expected_investment_amount = None

    def set_account_type(self, value: str) -> None:
        logger.info(f"Setting AccountTypeID: {value}")
        self.account_type_dropdown.click()
        option = self.page.locator("#AccountTypeID_listbox li").filter(has_text=value).first
        option.wait_for(state="visible", timeout=8000)
        option.click()

    def set_custodian(self, value: str) -> None:
        logger.info(f"Setting CustodianID: {value}")
        self.custodian_dropdown.click()
        option = self.page.locator("#CustodianID_listbox li").filter(has_text=value).first
        option.wait_for(state="visible", timeout=8000)
        option.click()

    def set_advisor(self, value: str) -> None:
        logger.info(f"Setting AdvisorID: {value}")
        self.set_dropdown_value("AdvisorID", value)

    def set_dropdown_value(
        self, field_id: str, value: str, timeout: int = 8000
    ) -> None:  # noqa: C901
        """
        Robustly set a dropdown value by field id.

        Supports native <select> (uses select_option by label/value), Kendo-style
        dropdowns/comboboxes (opens wrapper and clicks matching list item), and
        a last-resort visible-text click.

        Args:
            field_id: the HTML id attribute of the control (without '#')
            value: the visible label text to select
            timeout: wait timeout in milliseconds for visible elements
        """
        logger.info(f"Setting dropdown {field_id} -> '{value}'")

        selector = f"#{field_id}"
        # UI-driven path: click the visible dropdown/combobox wrapper then click the option by visible text
        tried = []
        opened = False
        try:
            # common wrappers: #{id}_wrapper, and internal dropdown/combobox elements
            wrapper = self.page.locator(
                f"#{field_id}_wrapper .k-dropdown-wrap, #{field_id}_wrapper .k-combobox, #{field_id}_wrapper, {selector} .k-dropdown-wrap, {selector} .k-combobox, {selector}"
            )
            if wrapper.count() > 0:
                try:
                    wrapper.first.click()
                    opened = True
                except Exception as e:
                    tried.append(("wrapper.click", str(e)))
        except Exception as e:
            tried.append(("wrapper.locator", str(e)))

        # If wrapper click didn't happen, try clicking the base selector directly
        if not opened:
            try:
                base = self.page.locator(selector)
                if base.count() > 0:
                    try:
                        base.first.click()
                        opened = True
                    except Exception as e:
                        tried.append(("base.click", str(e)))
            except Exception as e:
                tried.append(("base.locator", str(e)))

        # Wait up to timeout for candidate option elements to appear, then match by text
        start = time.time()
        end = start + (int(timeout) / 1000.0)
        candidate_selectors = [
            f"#{field_id}_listbox li",
            'ul[role="listbox"] li',
            ".k-list-ul li.k-list-item",
            ".k-list-item",
            'li[role="option"]',
            "li",
        ]

        while time.time() < end:
            try:
                # try each candidate selector and look for a text match
                for cs in candidate_selectors:
                    try:
                        loc = self.page.locator(cs)
                        cnt = 0
                        try:
                            cnt = loc.count()
                        except Exception:
                            cnt = 0
                        for i in range(cnt):
                            try:
                                item = loc.nth(i)
                                if not item.is_visible():
                                    continue
                                txt = item.inner_text().strip()
                                if not txt:
                                    continue
                                # exact (case-insensitive) or contains
                                if (
                                    txt.strip().lower() == value.strip().lower()
                                    or value.strip().lower() in txt.strip().lower()
                                ):
                                    try:
                                        item.click()
                                        logger.info(
                                            f"Selected '{value}' using UI list item '{txt}' for {field_id}"
                                        )
                                        return
                                    except Exception as e:
                                        tried.append(("item.click", str(e)))
                                        # continue searching other items
                            except Exception:
                                continue
                    except Exception:
                        continue
                # small sleep before retrying
                try:
                    self.page.wait_for_timeout(150)
                except Exception:
                    time.sleep(0.15)
            except Exception:
                break
        logger.warning(f"Unable to set dropdown {field_id} to '{value}' - tried: {tried}")
        raise Exception(f"Unable to select '{value}' for dropdown '{field_id}'")

    # -----------------
    # Step 2 - holdings field setters
    # -----------------
    def set_holding_id(self, value: str) -> None:
        logger.info(f"Setting HoldingID: {value}")
        # hidden input
        self.page.evaluate("(v) => { $('#HoldingID').val(v); }", value)

    def set_morningstar_data_id(self, value: str) -> None:
        logger.info(f"Setting MorningstarDataID: {value}")
        self.page.evaluate("(v) => { $('#MorningstarDataID').val(v); }", value)

    def set_symbol(self, symbol: str) -> None:
        logger.info(f"Setting Symbol: {symbol}")
        self.fill(self.symbol_input, symbol)
        self.page.evaluate("() => { $('#Symbol').trigger('change'); }")

    def set_description(self, text: str) -> None:
        logger.info(f"Setting Description: {text}")
        self.fill(self.description_input, text)

    def set_asset_type(self, value: str) -> None:
        logger.info(f"Setting AssetTypeID: {value}")
        self.set_dropdown_value("AssetTypeID", value)

    def set_morningstar_category(self, value: str) -> None:
        logger.info(f"Setting MorningstarCategoryID: {value}")
        self.set_dropdown_value("MorningstarCategoryID", value)

    def set_benchmark(self, value: str) -> None:
        logger.info(f"Setting BenchmarkID: {value}")
        self.set_dropdown_value("BenchmarkID", value)

    def set_acquisition(self, date_str: str) -> None:
        logger.info(f"Setting Acquisition date: {date_str}")
        # set raw value then trigger datepicker change
        self.fill(self.acquisition_input, date_str)
        self.page.evaluate("() => { $('#Acquisition').trigger('change'); }")

    def set_price(self, value: str) -> None:
        logger.info(f"Setting Price: {value}")
        self.fill(self.price_input, value)
        # recalc value on page
        self.page.evaluate(
            "() => { if(typeof proposalEditor_calculateValue === 'function') proposalEditor_calculateValue(); }"
        )

    def set_shares(self, value: str) -> None:
        logger.info(f"Setting Shares: {value}")
        # Wait for field to be enabled before attempting to fill
        self.wait_for_element(self.shares_input, state="visible", timeout=8000)
        # Type the provided value as-is (numbers from JSON are accepted)
        digits = str(value)
        # focus, select-all, type digits, then commit with Enter
        self.shares_input.hover()
        self.shares_input.click()
        with contextlib.suppress(Exception):
            self.page.keyboard.press("Control+A")
        self.page.keyboard.type(digits)
        with contextlib.suppress(Exception):
            self.page.keyboard.press("Enter")
        self.page.evaluate(
            "() => { if(typeof proposalEditor_calculateValue === 'function') proposalEditor_calculateValue(); }"
        )

    def set_cost(self, value: str) -> None:
        logger.info(f"Setting Cost: {value}")
        # Wait for field to be enabled before attempting to fill
        self.wait_for_element(self.cost_input, state="visible", timeout=8000)
        # Type the provided value as-is (numbers from JSON are accepted)
        digits = str(value)
        self.cost_input.hover()
        self.cost_input.click()
        with contextlib.suppress(Exception):
            self.page.keyboard.press("Control+A")
        self.page.keyboard.type(digits)
        with contextlib.suppress(Exception):
            self.page.keyboard.press("Enter")
        self.page.evaluate(
            "() => { if(typeof proposalEditor_calculateValue === 'function') proposalEditor_calculateValue(); }"
        )

    def get_value(self) -> str:
        logger.info("Reading Value field")
        return self.value_input.input_value()

    def add_holdings_from_tickers(self, entries: list, timeout: int = 10000) -> None:
        """Add holdings by searching each ticker and saving tax lots.

        Entries may be:
          - list/tuple: [ticker, shares, cost]
          - dict: {'ticker':..., 'shares':..., 'cost':...}
          - string: 'VTI' (shares/cost will be skipped)
        """
        logger.info(f"Adding holdings for entries: {entries}")
        list_selector = "#SymbolSearch_listbox li, #SymbolSearch_listbox .k-item"

        for entry in entries:
            # normalize
            ticker: str | None
            shares: int | str | None
            cost: int | str | None
            if isinstance(entry, str):
                ticker = entry
                shares = None
                cost = None
            elif isinstance(entry, dict):
                ticker = entry.get("ticker") or entry.get("symbol")
                shares = entry.get("shares")
                cost = entry.get("cost")
            else:
                try:
                    ticker, shares, cost = entry
                except Exception:
                    logger.warning(f"Invalid holding entry format: {entry}")
                    continue

            if not ticker:
                logger.warning(f"Skipping empty ticker entry: {entry}")
                continue

            # type into the autocomplete input
            self.fill(self.symbol_search_input, ticker)

            # wait for and click the first autocomplete suggestion
            first_item = self.page.locator(list_selector).first
            try:
                self.wait_for_element(first_item, state="visible", timeout=timeout)
                first_item.click()
            except Exception:
                logger.warning(f"No autocomplete suggestion visible for {ticker}")
                continue

            # wait for symbol details to populate
            try:
                self.page.wait_for_function(
                    "() => ($('#Symbol').val() || '').length > 0", timeout=timeout
                )
            except Exception:
                logger.warning(f"Timed out waiting for symbol details to load for {ticker}")

            # set acquisition date (optional fourth field) or default
            acquisition = None
            if isinstance(entry, dict):
                acquisition = entry.get("acquisition") or entry.get("date")
            else:
                # entry may be [ticker, shares, cost, acquisition]
                if not isinstance(entry, str) and len(entry) >= 4:
                    acquisition = entry[3]

            if not acquisition:
                acquisition = "01/01/2025"

            # set acquisition date before numeric fields
            try:
                self.set_acquisition(acquisition)
            except Exception:
                logger.warning(f"Failed to set acquisition date '{acquisition}' for {ticker}")

            # set numeric fields if provided
            if shares is not None:
                self.set_shares(str(shares))

            if cost is not None:
                self.set_cost(str(cost))

            # save the tax lot (per-entry verification is handled by the final step)
            self.save_current_holding()

    def save_current_holding(self, timeout: int = 5000) -> None:
        """Save the currently-entered tax lot using the SAVE TAX LOT button.

        This is a best-effort click with a small wait for the UI to process.
        """
        logger.info("Saving current tax lot")
        try:
            # prefer the explicit locator
            self.click(self.save_holding_button)
        except Exception:
            logger.warning("Failed to click SAVE TAX LOT button")

        # small pause to let the UI catch up
        with contextlib.suppress(Exception):
            self.page.wait_for_timeout(1000)

    def verify_saved_holding(self, holdings: list, timeout: int = 10000) -> None:
        """Verify that each holding in `holdings` (list of [ticker, shares, cost]) appears in the UI.

        This helper is forgiving: it logs warnings if a ticker cannot be confirmed but does not raise.
        """
        logger.info(f"Verifying saved holdings list of {len(holdings)} entries")
        for entry in holdings:
            try:
                ticker = entry[0]
            except Exception:
                logger.warning(f"Invalid holding entry for verification: {entry}")
                continue

            try:
                # Wait for the ticker text to appear somewhere in the proposal holdings area
                self.page.wait_for_selector(
                    f'#proposal-wizard-1 :text("{ticker}")', timeout=timeout
                )
            except Exception:
                try:
                    self.page.wait_for_selector(f'text="{ticker}"', timeout=timeout)
                except Exception:
                    logger.warning(f"Could not confirm presence of holding ticker '{ticker}' in UI")
