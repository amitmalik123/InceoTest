from playwright.sync_api import FrameLocator, Locator, Page
from typing import Callable

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.helpers import random_alpha, random_number

logger = get_allure_logger(__name__)


class TransferAttributesPage(BasePage):
    """Transfer Attributes Page - handles transfer request and destination accounts."""

    PAGE_NAME = "Transfer Attributes Page"

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        self._frame: FrameLocator = page.frame_locator("iframe[title='Coach']")
        f = self._frame  # short alias for locator definitions
    
        # Transfer request locators
        self.full_checkbox: Locator = f.get_by_role("radio", name="Full")
        self.partial_checkbox: Locator = f.get_by_role("radio", name="Partial")
        self.non_acat_checkbox: Locator = f.get_by_role("checkbox", name="non-ACAT")
        self.contribution_code: Locator = f.get_by_role("combobox", name="Contribution Code")
        self.contra_firm_account: Locator = f.get_by_role("textbox", name="Contra Firm Account")
        self.contra_firm_name_line1: Locator = f.get_by_role("textbox", name="Contra Firm Name Line 1")
        self.contra_firm_name_line2: Locator = f.get_by_role("textbox", name="Contra Firm Name Line 2")
        self.amount: Locator = f.get_by_role("textbox", name="Amount", exact=True)
        self.estimated_checkbox: Locator = f.get_by_role("radio", name="Estimated")
        self.special_instructions: Locator = f.get_by_role("textbox", name="Special Instructions")
        # No semantic role available for chosen.js widget
        self.clearing_firm_chosen: Locator = f.locator("#singleselect_TransferAttributesCV_ClearingFirm_chosen")
        self.clearing_firm_chosen_link: Locator = f.locator("//div[@id='singleselect_TransferAttributesCV_ClearingFirm_chosen']/a")
        self.contra_firm_chosen: Locator = f.locator("//div[@id='singleselect_TransferAttributesCV_ContraFirm_chosen']/a/div")
        self.contra_firm_registration_chosen: Locator = f.locator("//div[@id='singleselect_TransferAttributesCV_ContraFirmRegistration_chosen']/a/div")
        self.contra_firm_results: Locator = f.locator("#singleselect_TransferAttributesCV_ContraFirm_chosen .chosen-results li")
        self.clearing_firm_results: Locator = f.locator("#singleselect_TransferAttributesCV_ClearingFirm_chosen .chosen-results li")
        self.contra_firm_registration_results: Locator = f.locator("#singleselect_TransferAttributesCV_ContraFirmRegistration_chosen .chosen-results li")

        # Destination account locators
        self.header_account: Locator = f.locator("div", has_text="Account #").locator("p").first
        self.destination_account: Locator = f.locator("[id=\"singleselect-TransferAttributesCV\\:AccountNumberSelect\"]").first
        self.destination_amount: Locator = f.get_by_role("textbox", name="Destination Amount")
        self.add_button: Locator = f.get_by_role("button", name="Add")
        self.create_funding_account: Locator = f.get_by_role("button", name="Create Funding Account")
        self.create_funding_account_input: Locator = f.get_by_role("textbox", name="Funding Account #")
        self.create_toar_button: Locator = f.get_by_role("button", name="Create TOAR Record")
        self.eds_confirmation_number: Locator = f.get_by_role("textbox", name="EDS Confirmation Number")
        self.submitted_to_fidelity: Locator = f.get_by_role("radio", name="Submitted to Fidelity")
        self.save_close_button: Locator = f.get_by_role("button", name="Save & Close")
        self.warning_checkboxes: Locator = f.locator("input[id*='WarningCheckboxes']")
        self.warning_proceed_button: Locator = f.locator("[id*='WarningPopupProceedButton']")
        self.destination_accounts_table: Locator = f.locator('[data-viewid="DestinationAccountsTable"]')
        self.error_msg: Locator = f.locator(".error-message")  # TODO: verify selector
        self.alert_indicator: Locator = f.locator("[role='alert']")
        self.iwr_complete: Locator = f.get_by_role("button", name="IWR Complete")
        self.create_toad_button: Locator = f.get_by_role("button", name="Create TOAD Record")
        self.create_checklist_button: Locator = f.get_by_role("button", name="Create Checklist")
        self.checklist_table: Locator = f.locator("[data-viewid='CreateChecklistTable']")
        self.toad_success_alert: Locator = f.locator(".alert-success")
        self.transfer_records_panels: Locator = f.locator("[data-viewid='TransferRecordsPanel']")

        self.question_check: Locator = f.locator("//table[@class='table table-striped']//tr//div[contains(@class,'_style CPP CoachView_show')]//textarea[not(@disabled)]")
        self.cost_basis: Locator = f.locator("select[id*='CostBasis']")
        self.cost_basis_disabled: Locator = f.locator("select[id*='CostBasis'][disabled]")

    def enter_transfer_request(self, transfer_request: str, work_item_type: str) -> None:
        """Enter transfer request section info based on work item type.

        Args:
            transfer_request: Comma-separated transfer data string from Excel
            work_item_type: e.g. "Transfer In Request", "Custodian Change Request"
        """
        Assertions.assert_true("TransferAttributes" in self.page.url, "Transfer page should be loaded before entering transfer request details")
        logger.info(f"Validated Transfer Attributes page is loaded. Current URL: {self.page.url}")

        transfer_data = [item.strip() for item in transfer_request.split(",")]

        if work_item_type in ("Transfer In Request", "Custodian Change Request", "Full Transfer Out In Kind", "Partial Transfer Out In Kind"):
            self._common_transfer_request_steps(transfer_data, work_item_type)
        else:
            logger.info(f"No transfer request steps for work item type: {work_item_type}")

        logger.info("Entered transfer request section")
    def _common_transfer_request_steps(self, transfer_data: list[str], work_item_type: str) -> None:
        """Fill common transfer request fields from parsed data.

        Args:
            transfer_data: List of transfer field values
        """
        self.wait_for_loading_data()

        # Validate amount-type radio based on work item type.
        if work_item_type == "Full Transfer Out In Kind":
            amount_type_checkbox = self.full_checkbox
            amount_type_label = "Full"
        elif work_item_type == "Partial Transfer Out In Kind":
            amount_type_checkbox = self.partial_checkbox
            amount_type_label = "Partial"
        else:
            amount_type_checkbox = self.full_checkbox
            amount_type_label = "Full"

        # Wait for the Coach iframe content to be fully rendered before interacting.
        # The iframe loads asynchronously after the outer page is ready, so we
        # wait for a known stable element inside the frame before proceeding.
        amount_type_checkbox.wait_for(state="visible", timeout=30000)

        transfer_type = transfer_data[9].strip()
        # Normalise test-data values to the actual radio-button labels on the BAW page
        _TRANSFER_TYPE_LABELS: dict[str, str] = {
            "inkind": "In Kind",
            "in kind": "In Kind",
            "cash": "Cash",
            "partial": "Partial",
        }
        transfer_type_label = _TRANSFER_TYPE_LABELS.get(transfer_type.lower(), transfer_type)
        transfer_type_checkbox = self._frame.get_by_role("radio", name=transfer_type_label)

        self.check(amount_type_checkbox, timeout=30000)
        logger.info(f"Checked amount type: {amount_type_label}")

        # Check transfer type radio
        self.check(transfer_type_checkbox)
        logger.info(f"Checked transfer type: {transfer_type}")

        if transfer_type.lower() == "cash":
            self.select_option(self.contribution_code, value=transfer_data[0])
        else:
            self.check(self.non_acat_checkbox)
            logger.info("Checked non-ACAT checkbox")
            self.wait_for_loading_data()

        # Select contra firm
        self._select_contra_firm()

        if transfer_type.lower() != "cash":
            chosen_classes = self.clearing_firm_chosen.get_attribute("class") or ""
            if "chosen-disabled" not in chosen_classes:
                self._select_clearing_firm()
                if self.get_text(self.clearing_firm_chosen).strip().lower() == "select":
                    self._select_clearing_firm()

        # Enter contra firm account
        self.fill(self.contra_firm_account, random_number(9))
        self.tab_out()
        self.wait_for_loading_data()

        try:
            self.accept_alert()
        except Exception as e:
            logger.info(f"Alert handling: {e}")

        if transfer_type.lower() != "cash":
            self.fill(self.contra_firm_name_line1, random_alpha(5))
            self.tab_out()
            self.fill(self.contra_firm_name_line2, random_alpha(5))
            self.tab_out()
            self._select_contra_firm_registration()

        if transfer_type.lower() == "cash":
            delivery_method = transfer_data[10].strip()
            mail_checkbox = self._frame.locator(f"input[value='{delivery_method}']")
            self.click(mail_checkbox)

        # Enter amount
        self.fill(self.amount.first, random_number(2))
        self.check(self.estimated_checkbox)
        logger.info("Checked amount expectation: Estimated")

        # Enter special instructions
        self.fill(self.special_instructions, random_alpha(20)) 
        self.tab_out()       
        logger.info("Common transfer request steps completed")

    def _select_contra_firm(self) -> None:
        """Select contra firm from chosen.js dropdown by index."""
        self.click(self.contra_firm_chosen, timeout=5000)
        self.contra_firm_results.nth(3).click()
        logger.info("Selected contra firm")

    def _select_clearing_firm(self) -> None:
        """Select clearing firm."""
        self.click(self.clearing_firm_chosen_link, timeout=5000)
        self.clearing_firm_results.nth(3).click()
        logger.info("Selected clearing firm")

    def _select_contra_firm_registration(self) -> None:
        """Select contra firm registration."""
        self.click(self.contra_firm_registration_chosen, timeout=5000)
        self.contra_firm_registration_results.nth(3).click()
        logger.info("Selected contra firm registration")

    def enter_destination_accounts(self, work_item_type: str, allocation_unit: str, account_number: str = "") -> None:
        """Enter destination account details.

        Args:
            work_item_type: e.g. "Transfer In Request", "Custodian Change Request"
            allocation_unit: Allocation type (e.g. "percentage", "dollar", "multiple", "multipleAR")
            account_number: Fallback account number if header account is empty
        """
        account = self.get_text(self.header_account).strip()
        self.select_option(self.destination_account, value=account)

        self.check(self._frame.locator(f"input[value='{allocation_unit}']"))

        if allocation_unit == "Percent" or allocation_unit == "USDollar":            
            self.fill(self.amount.last, "100")
        
        self.click(self.add_button)
        logger.info("Clicked on add button")
      
        Assertions.assert_true(self.destination_accounts_table.locator('td').count()>2, "Destination accounts table should be visible after adding an account")
        logger.info(f"Validated destination accounts table has data. TD count: {self.destination_accounts_table.locator('td').count()}")
        self.click(self.create_funding_account)
        logger.info("Clicked on create funding account button")
        self.wait_for_loading_data()
        Assertions.assert_true(self.create_funding_account_input.is_disabled() and self.create_funding_account_input.is_visible(), "Funding account textbox should be visible and disabled after clicking create funding account")
        logger.info(f"Validated funding account textbox is visible and disabled. Disabled: {self.create_funding_account_input.is_disabled()}, Visible: {self.create_funding_account_input.is_visible()}")    

        if work_item_type == "Custodian Change Request":
            self.alert_indicator.wait_for(state="hidden", timeout=30000)
            self.click(self.create_toar_button)
            logger.info("Clicked on create TOAR Record button")

            # if self.eds_confirmation_number.is_visible(timeout=1000):
            #     self.check(self.submitted_to_fidelity)
            #     self.fill(self.eds_confirmation_number, "546456")
            #     self.wait_for_loading_data()

            self._click_save_close_button()
            self._handle_warning_checkboxes()
        else:
            self._iwr_complete()

        # if self.error_msg.is_visible(timeout=4000):
        #     error_text = self.get_text(self.error_msg)
        #     raise RuntimeError(f"Getting error message: {error_text}")

        logger.info(f"Entered destination accounts - type: {work_item_type}, allocation: {allocation_unit}")

    def _select_different_destination_account(self, current_account: str) -> None:
        """Select a different destination account from the dropdown."""
        options = self.destination_account.locator("option").all()
        for option in options:
            text = (option.text_content() or "").strip()
            if text and text != current_account and text != "Select":
                self.select_option(self.destination_account, label=text)
                self.wait_for_timeout(500)
                break

    def _click_save_close_button(self) -> None:
        """Click the Save & Close button."""
        self.click(self.save_close_button)
        logger.info("Clicked on Save & Close button")

    def _handle_warning_checkboxes(self) -> None:
        """Check all warning checkboxes and click proceed if present."""
        try:
            checkboxes = self.warning_checkboxes.all()
            if checkboxes:
                for checkbox in checkboxes:                    
                    checkbox.click()
                self.warning_proceed_button.click()
        except Exception:
            logger.info("No warning checkboxes found")

    def _iwr_complete(self) -> None:
        """Complete IWR flow."""
        self._answer_checklist_questions()
        self._update_cost_basis()
        self.click(self.iwr_complete)
        logger.info("Clicked on IWR complete button")

    def _answer_checklist_questions(self) -> None:
        """Answer all visible checklist questions with placeholder text."""
        if self.question_check.first.is_visible(timeout=1000):
            elements = self.question_check.all()
            for element in elements:
                element.fill("abcde")
                self.tab_out()

    def _update_cost_basis(self) -> None:
        """Update cost basis to Waived if enabled."""
        if self.cost_basis.is_visible(timeout=1000) and not self.cost_basis_disabled.is_visible(timeout=500):
            self.select_option(self.cost_basis, value="Waived")

    def _fill_full_transfer_out_in_kind_radios(self) -> None:
        """Fill transfer-request radios specific to Full Transfer Out In Kind."""
        logger.info("Panel: Transfer Request - validating and selecting radio options")

        custodian_change_no = self._frame.locator("input[id*='CustodianChange'][value='No']")
        what_transferred_both = self._frame.locator("input[id*='WhatIsBeingTransferred'][value='Both']")
        ptd_eligibility_no = self._frame.locator("input[id*='PTDEligibility'][value='No']")
        bonds_in_account_no = self._frame.locator("input[id*='BondsInAccount'][value='No']")

        self.check(custodian_change_no)
        logger.info("Transfer Request radio selected: Custodian Change = No")
        self.check(what_transferred_both)
        logger.info("Transfer Request radio selected: What is being transferred = Both")
        self.check(ptd_eligibility_no)
        logger.info("Transfer Request radio selected: PTD eligibility = No")
        self.check(bonds_in_account_no)
        logger.info("Transfer Request radio selected: Bonds in Account = No")

    def _fill_partial_transfer_out_in_kind_radios(self) -> None:
        """Fill transfer-request radios specific to Partial Transfer Out In Kind."""
        logger.info("Panel: Transfer Request (Partial) - validating and selecting radio options")

        what_transferred_both = self._frame.locator("input[id*='WhatIsBeingTransferred'][value='Both']")
        ptd_eligibility_no = self._frame.locator("input[id*='PTDEligibility'][value='No']")
        bonds_in_account_no = self._frame.locator("input[id*='BondsInAccount'][value='No']")

        # Partial path can hide some radios depending on UI state, so select only visible options.
        partial_radios = [
            (what_transferred_both, "What is being transferred = Both"),
            (ptd_eligibility_no, "PTD eligibility = No"),
            (bonds_in_account_no, "Bonds in Account = No"),
        ]

        for locator, label in partial_radios:
            if locator.count() > 0 and locator.first.is_visible(timeout=1000):
                self.check(locator.first)
                logger.info(f"Transfer Request radio selected (Partial): {label}")
            else:
                logger.info(f"Transfer Request radio not applicable (Partial): {label}")

    def _fill_non_transferable_securities_section(self) -> None:
        """Set Non-Transferable Securities defaults to No."""
        logger.info("Panel: Non-Transferable Securities - validating and selecting radio options")

        options_no_options = self._frame.locator("input[id*='Options'][value='NoOptions']")
        securities_to_exclude_no = self._frame.locator("input[id*='SecuritiesToExclude'][value='No']")

        self.check(options_no_options)
        logger.info("Non-Transferable Securities radio selected: Options = NoOptions")
        self.check(securities_to_exclude_no)
        logger.info("Non-Transferable Securities radio selected: Securities To Exclude = No")
        securities_to_sell_no = self._frame.locator("input[id*='SecuritiesToSell'][value='No']")
        if securities_to_sell_no.count() > 0 and securities_to_sell_no.first.is_visible(timeout=1000):
            self.check(securities_to_sell_no.first)
            logger.info("Non-Transferable Securities radio selected: Securities To Sell = No")
        logger.info("Panel validated: Non-Transferable Securities")

    def _get_transfer_out_config(self, work_item_type: str) -> dict[str, str | bool]:
        """Return workflow configuration for Full/Partial Transfer Out In Kind."""
        if work_item_type == "Partial Transfer Out In Kind":
            return {
                "run_non_transferable_section": False,
                "populate_toad_securities": True,
                "toad_security_quantity": "1",
                "checklist_contra_row": "Contra account number matches Transfer coach",
            }

        return {
            "run_non_transferable_section": True,
            "populate_toad_securities": False,
            "checklist_contra_row": "Contra account number matches all three coaches",
        }

    def _populate_toad_securities_row(self, quantity: str = "1") -> None:
        """Add one security row in TOAD panel, select first security, set quantity, and tab out."""
        add_security_button = self._frame.locator(
            '[id="button-button-TransferAttributesCV:AddSecuritiesToTransferButton"]'
        )

        if not (add_security_button.count() > 0 and add_security_button.first.is_visible(timeout=5000)):
            logger.info("TOAD Securities Add button not visible")
            return

        self.click(add_security_button.first)
        logger.info("Clicked TOAD Securities Add button")
        self.wait_for_loading_data()

        security_dropdown = self._frame.locator(
            "#singleselect_TransferAttributesCV_SecuritiesToTransferTable_TransferSecurityCell_0__TransferSecurity_chosen"
        )
        if not (security_dropdown.count() > 0 and security_dropdown.first.is_visible(timeout=5000)):
            logger.info("TOAD security dropdown container not visible")
            return

        security_dropdown_toggle = security_dropdown.locator("a").first
        if not (security_dropdown_toggle.count() > 0 and security_dropdown_toggle.is_visible(timeout=5000)):
            logger.info("TOAD security dropdown toggle not visible")
            return

        self.click(security_dropdown_toggle)
        logger.info("Opened TOAD security dropdown")

        security_options = security_dropdown.locator(
            ".chosen-results li.active-result"
        )
        option_count = security_options.count()
        if option_count == 0:
            logger.info("No selectable option found in TOAD security dropdown")
            return

        # First active result is a placeholder in this widget; choose the second option.
        target_security_option = security_options.nth(1) if option_count > 1 else security_options.first
        if not target_security_option.is_visible(timeout=5000):
            logger.info("Target TOAD security option is not visible")
            return

        option_text = (target_security_option.inner_text() or "").strip()
        self.click(target_security_option)
        logger.info(f"Selected TOAD security dropdown option: {option_text}")

        quantity_input = self._frame.locator(
            '[id="decimal-input-TransferAttributesCV:SecuritiesToTransferTable:TransferQuantityCell[0]:TransferQuantity"]'
        )
        Assertions.assert_true(
            quantity_input.count() > 0 and quantity_input.first.is_visible(timeout=5000),
            "TOAD quantity field should be visible",
        )
        self.click(quantity_input.first)
        self.fill(quantity_input.first, quantity)
        self.tab_out()
        logger.info(f"Entered TOAD security quantity: {quantity}")

    def _create_toad_record_and_validate(self, work_item_type: str) -> None:
        """Create TOAD record and validate success banner."""
        logger.info("Panel: Create TOAD Record - validating and selecting options")
        config = self._get_transfer_out_config(work_item_type)
        self.scroll_into_view(self.create_toad_button)

        pending_trades_no = self._frame.locator("input[id*='PendingTrades'][value='No']")
        self.check(pending_trades_no)
        logger.info("Create TOAD Record radio selected: Pending Trades = No")

        ack_checkbox = self._frame.locator("input[id*='Implication_Ack_Checkbox']")
        if ack_checkbox.count() > 0 and ack_checkbox.first.is_visible(timeout=1000):
            self.check(ack_checkbox.first)
            logger.info("Create TOAD Record checkbox selected: Implication Acknowledgement = checked")
        else:
            logger.info("Create TOAD Record implication acknowledgement checkbox not visible")

        if config["populate_toad_securities"]:
            self._populate_toad_securities_row(quantity=str(config["toad_security_quantity"]))
        else:
            logger.info("Skipping TOAD securities row population based on workflow config")

        self.click(self.create_toad_button)
        logger.info("Clicked button: Create TOAD Record")
        self.wait_for_loading_data()
        logger.info("Loading completed after clicking Create TOAD Record")

        expected_text = "TOAD Record created successfully"

        # Strict validation: after loader completes, the visible success alert must contain exact expected text.
        success_banner = self._frame.locator(".alert-success").filter(has_text=expected_text).first
        success_banner.wait_for(state="visible", timeout=30000)
        # self.scroll_into_view(success_banner)
        success_text = (success_banner.inner_text() or "").strip()

        Assertions.assert_true(
            expected_text in success_text,
            "TOAD success banner should be visible after creating TOAD record",
        )
        logger.info(f"Validated TOAD success banner: {success_text}")

    def _log_toad_record_panels(self) -> None:
        """Capture and log TOAD record panel content in a readable format."""
        panel_count = self.transfer_records_panels.count()
        Assertions.assert_true(panel_count > 0, "At least one TOAD record panel should be visible")

        visible_indexes: list[int] = []
        for idx in range(panel_count):
            panel = self.transfer_records_panels.nth(idx)
            if panel.is_visible(timeout=500):
                visible_indexes.append(idx)
            if len(visible_indexes) >= 5:
                break

        Assertions.assert_true(
            len(visible_indexes) > 0,
            "At least one visible TOAD record panel should be present",
        )

        logger.info(f"Panel validated: TOAD Record Panel(s). Found {panel_count} panel(s)")

        for idx in visible_indexes:
            panel = self.transfer_records_panels.nth(idx)
            heading = panel.locator(".panel-title").first.inner_text().strip()
            body_text = panel.locator(".panel-body").first.inner_text().strip()
            condensed = " | ".join([line.strip() for line in body_text.splitlines() if line.strip()])
            logger.info(f"{heading}: {condensed}")
        if panel_count > len(visible_indexes):
            logger.info(f"Additional TOAD record panels not logged: {panel_count - len(visible_indexes)}")

    def _validate_and_complete_submission_checklist(self, work_item_type: str) -> None:
        """Create checklist, validate defaults, collect alert text, and set all responses to Yes."""
        logger.info("Panel: Submission Checklist - creating and validating checklist")
        config = self._get_transfer_out_config(work_item_type)
        self.scroll_into_view(self.create_checklist_button)
        self.click(self.create_checklist_button)
        logger.info("Clicked button: Create Checklist")
        self.wait_for_loading_data()
        self.checklist_table.wait_for(state="visible", timeout=15000)
        self.scroll_into_view(self.checklist_table)
        logger.info("Panel validated: ChecklistPanel/CreateChecklistTable is visible")

        required_rows = [
            "Client name and Account",
            str(config["checklist_contra_row"]),
            "Appropriate OA has been added",
            "Open work items have been",
            "Reviewed for Pending Trades",
        ]
        for row in required_rows:
            Assertions.assert_true(
                self._frame.get_by_role("cell", name=row).first.is_visible(timeout=5000),
                f"Checklist row should be visible: {row}",
            )
        logger.info(f"Checklist row texts validated: {required_rows}")

        for idx in range(5):
            no_radio = self._frame.locator(
                f"input[id*='CreateChecklistRadioGroup[{idx}][1]']"
            )
            if no_radio.count() > 0 and no_radio.first.is_visible(timeout=1000):
                Assertions.assert_true(no_radio.first.is_checked(), f"Checklist row {idx + 1} should default to No")
                logger.info(f"Checklist default validated: row {idx + 1} = No")

        # Keep one row as 'No', click IWR Complete, and validate checklist error alert.
        for idx in range(4):
            yes_radio = self._frame.locator(
                f"input[id*='CreateChecklistRadioGroup[{idx}][0]']"
            )
            if yes_radio.count() > 0 and yes_radio.first.is_visible(timeout=1000):
                self.check(yes_radio.first)
                logger.info(f"Checklist radio selected for negative validation: row {idx + 1} = Yes")
        logger.info("Checklist radio kept as No for negative validation: row 5 = No")
        self.scroll_into_view(self.iwr_complete)
        self.click(self.iwr_complete)
        logger.info("Clicked button: IWR Complete (with one checklist row = No)")
        self.wait_for_loading_data()

        checklist_error_alert = self.page.locator("iframe[title=\"Coach\"]").content_frame.get_by_text("1. Checklist not complete - a")
        checklist_error_alert.wait_for(state="visible", timeout=10000)
        alert_text = (checklist_error_alert.inner_text() or "").strip()
        Assertions.assert_true(
            len(alert_text) > 0,
            "Checklist error message should be visible when at least one checklist answer is No",
        )
        logger.info(f"Checklist error validated with one remaining No: {alert_text}")

        # Ensure all rows are Yes before final completion.
        for idx in range(5):
            yes_radio = self._frame.locator(f"input[id*='CreateChecklistRadioGroup[{idx}][0]']")
            if yes_radio.count() > 0 and yes_radio.first.is_visible(timeout=1000):
                if not yes_radio.first.is_checked():
                    self.check(yes_radio.first)
                    logger.info(f"Checklist radio corrected to Yes: row {idx + 1}")
                else:
                    logger.info(f"Checklist radio already Yes: row {idx + 1}")

        self.scroll_into_view(self.iwr_complete)
        self.click(self.iwr_complete)
        logger.info("Clicked button: IWR Complete (all checklist rows = Yes)")
        self.wait_for_loading_data()

        logger.info("Validated checklist error path and completed checklist with all rows set to Yes")

    def _complete_transfer_out_in_kind_flow(self, work_item_type: str, radio_filler: Callable[[], None]) -> None:
        """Execute Transfer Out In Kind flow using a config-driven shared sequence."""
        config = self._get_transfer_out_config(work_item_type)

        radio_filler()
        if config["run_non_transferable_section"]:
            self._fill_non_transferable_securities_section()
        else:
            logger.info("Skipping Non-Transferable Securities section based on workflow config")
        self._create_toad_record_and_validate(work_item_type)
        self._log_toad_record_panels()
        self._validate_and_complete_submission_checklist(work_item_type)
        logger.info(f"Completed {work_item_type} workflow")

    def _complete_full_transfer_out_in_kind_flow(self, work_item_type: str) -> None:
        """Execute Full Transfer Out In Kind flow in shared order."""
        self._complete_transfer_out_in_kind_flow(work_item_type, self._fill_full_transfer_out_in_kind_radios)

    def _complete_partial_transfer_out_in_kind_flow(self, work_item_type: str) -> None:
        """Execute Partial Transfer Out In Kind flow in shared order."""
        self._complete_transfer_out_in_kind_flow(work_item_type, self._fill_partial_transfer_out_in_kind_radios)

    def enter_details_for_full_transfer_out_in_kind(self, transfer_request: str, work_item_type: str) -> None:
        """Convenience method to enter transfer request and execute workflow based on work item type."""
        if work_item_type == "Full Transfer Out In Kind":
            self._complete_full_transfer_out_in_kind_flow(work_item_type)
            return

    def enter_details_for_partial_transfer_out_in_kind(self, transfer_request: str, work_item_type: str) -> None:
        """Convenience method to execute Partial Transfer Out In Kind workflow."""
        if work_item_type == "Partial Transfer Out In Kind":
            self._complete_partial_transfer_out_in_kind_flow(work_item_type)
            return

       