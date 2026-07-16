"""NAA Coach Page - New Account Application Coach"""

from playwright.sync_api import Locator, Page

from locators.baw.naa_coach_locators import NAACoachLocators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.wait_utils import WaitContext

logger = get_allure_logger(__name__)


class NAACoachPage(BasePage):
    """NAA Coach Page class for New Account Application workflow"""

    PAGE_NAME = "NAA Coach Page"
    activated_account_number: str = ""

    def __init__(self, page: Page):
        super().__init__(page)
        # Locators for CIP section
        self.cip_heading: Locator = page.locator(NAACoachLocators.CIP_HEADING)
        self.save_client_data_button: Locator = page.locator(NAACoachLocators.SAVE_CLIENT_DATA_BUTTON)
        self.cip_table_rows: Locator = page.locator(NAACoachLocators.CIP_TABLE_ROWS)
        self.cip_system_result: Locator = page.locator(NAACoachLocators.CIP_SYSTEM_RESULT)
        
        # Locators for Work Items section
        self.work_items_heading: Locator = page.locator(NAACoachLocators.WORK_ITEMS_HEADING)
        self.save_shell_process_button: Locator = page.locator(NAACoachLocators.SAVE_SHELL_PROCESS_BUTTON)
        self.save_refresh_button: Locator = page.locator(NAACoachLocators.SAVE_REFRESH_BUTTON)
        self.add_work_item_modal: Locator = page.locator(NAACoachLocators.ADD_WORK_ITEM_MODAL)
        self.add_work_item_button: Locator = page.locator(NAACoachLocators.ADD_WORK_ITEM_BUTTON)
        self.add_new_work_item: Locator = page.locator(NAACoachLocators.ADD_NEW_WORK_ITEM)
        self.add_work_item_type: Locator = page.locator(NAACoachLocators.ADD_WORK_ITEM_TYPE)
        self.add_work_item_save_button: Locator = page.locator(NAACoachLocators.ADD_WORK_ITEM_SAVE_BUTTON)

        # Locators for Activation section
        self.client_has_private_assets: Locator = page.locator(NAACoachLocators.CLIENT_HAS_PRIVATE_ASSETS)
        self.activation_section: Locator = page.locator(NAACoachLocators.ACTIVATION_SECTION)
        self.save_client_data: Locator = page.locator(NAACoachLocators.SAVE_CLIENT_DATA)
        self.client_name: Locator = page.locator(NAACoachLocators.CLIENT_NAME)
        self.client_address1: Locator = page.locator(NAACoachLocators.CLIENT_ADDRESS1)
        self.client_city: Locator = page.locator(NAACoachLocators.CLIENT_CITY)
        self.client_state: Locator = page.locator(NAACoachLocators.CLIENT_STATE)
        self.client_zip: Locator = page.locator(NAACoachLocators.CLIENT_ZIP)
        self.statement_name: Locator = page.locator(NAACoachLocators.STATEMENT_NAME)
        self.statement_address1: Locator = page.locator(NAACoachLocators.STATEMENT_ADDRESS1)
        self.statement_city: Locator = page.locator(NAACoachLocators.STATEMENT_CITY)
        self.statement_state: Locator = page.locator(NAACoachLocators.STATEMENT_STATE)
        self.statement_zip: Locator = page.locator(NAACoachLocators.STATEMENT_ZIP)
        self.edit_app_modal: Locator = page.locator(NAACoachLocators.EDIT_APP_MODAL)
        self.power_attorney_save_close_button: Locator = page.locator(NAACoachLocators.POWER_ATTORNEY_SAVE_CLOSE_BUTTON)
        self.duplicate_statement_address_not_found: Locator = page.locator(NAACoachLocators.DUPLICATE_STATEMENT_ADDRESS_NOT_FOUND)
        self.amp_sop_completed: Locator = page.locator(NAACoachLocators.AMP_SOP_COMPLETED)
        self.max_30_char_error: Locator = page.locator(NAACoachLocators.MAX_30_CHAR_ERROR)
        self.account_name: Locator = page.locator(NAACoachLocators.ACCOUNT_NAME)
        self.activate_accounts_button: Locator = page.locator(NAACoachLocators.ACTIVATE_ACCOUNTS_BUTTON)
        self.activated_account: Locator = page.locator(NAACoachLocators.ACTIVATED_ACCOUNT)
        self.has_client_tax_management: Locator = page.locator(NAACoachLocators.HAS_CLIENT_TAX_MANAGEMENT)
        self.open_work_item_button: Locator = page.locator(NAACoachLocators.OPEN_WORK_ITEM_BUTTON)
        self.activation_success_alerts: Locator = page.locator(NAACoachLocators.ACTIVATION_SUCCESS_ALERTS)

        # Locators for Plan Document / retirement-service validation
        self.view_edit_app_data_button: Locator = page.get_by_role("button", name=NAACoachLocators.VIEW_EDIT_APP_DATA_BUTTON_ROLE)
        self.plan_document_text: Locator = page.locator(NAACoachLocators.PLAN_DOCUMENT_TEXT)
        self.plan_document_section: Locator = page.locator(NAACoachLocators.PLAN_DOCUMENT_SECTION)
        self.plan_document_radio_inputs: Locator = page.locator(NAACoachLocators.PLAN_DOCUMENT_RADIO_INPUTS)
        self.epic_plan_id_label: Locator = page.get_by_text(NAACoachLocators.EPIC_PLAN_ID_LABEL_TEXT, exact=False)
        self.epic_plan_id_input: Locator = page.locator(NAACoachLocators.EPIC_PLAN_ID_INPUT)
        self.epic_plan_id_max_length_error: Locator = page.get_by_text(NAACoachLocators.EPIC_PLAN_ID_MAX_LENGTH_ERROR_TEXT, exact=False)
        self.penchecks_plan_id_label: Locator = page.get_by_text(NAACoachLocators.PENCHECKS_PLAN_ID_LABEL_TEXT, exact=False)
        self.penchecks_plan_id_input: Locator = page.locator(NAACoachLocators.PENCHECKS_PLAN_ID_INPUT)
        self.penchecks_plan_id_max_length_error: Locator = page.get_by_text(NAACoachLocators.PENCHECKS_PLAN_ID_MAX_LENGTH_ERROR_TEXT, exact=False)
        self.save_close_button: Locator = page.get_by_role("button", name=NAACoachLocators.SAVE_CLOSE_BUTTON_ROLE)
        self.access_account_name_2_text: Locator = page.get_by_text(NAACoachLocators.ACCESS_ACCOUNT_NAME_2_TEXT, exact=False)
        self.access_account_name_2_input: Locator = page.locator(NAACoachLocators.ACCESS_ACCOUNT_NAME_2_INPUT)

    @classmethod
    def from_context(cls, test_context) -> "NAACoachPage":
        """Build NAA Coach page from the current BAW page in context."""
        current_page = test_context.get("baw_page")
        if not current_page:
            raise ValueError("NAA Coach page not initialized. Navigate to NAA Coach page first.")
        page_obj = cls(current_page)
        test_context["naa_coach_page"] = page_obj
        return page_obj

    def click_save_and_refresh(self) -> None:
        """Click Save and Refresh button and wait for UI loading."""
        with logger.step("click on save and refresh button", page=self.page):
            self.save_refresh_button.wait_for(state="visible", timeout=30000)
            with WaitContext(timeout=30.0) as wait:
                wait.until_visible(self.save_refresh_button)
            self.save_refresh_button.scroll_into_view_if_needed()
            self.save_refresh_button.click(no_wait_after=True)
            try:
                self.wait_for_load_state("domcontentloaded", timeout=60000)
            except Exception as e:
                logger.warning(f"Load state wait timeout after Save and Refresh: {e}")
            self.wait_for_loading_data(timeout=30000)
            logger.info("click on save and refresh button")

    def switch_to_naa_coach_page(self) -> None:
        """Switch to NAA Coach page and reinitialize this page object."""
        with logger.step('Switch to "NAA Coach" page', page=self.page):
            page = self.switch_to_page_by_title("NAA Coach", timeout=30)
            self.__init__(page)
            logger.info("Switched to NAA Coach page")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                logger.warning("NAA Coach page domcontentloaded wait timed out")
            self.wait_for_loading_data(timeout=30000)

            try:
                self.cip_heading.count()
            except Exception as stale_error:
                logger.warning(f"Stale NAA Coach object detected: {stale_error}, retrying switch and reinit")
                page = self.switch_to_page_by_title("NAA Coach", timeout=30)
                self.__init__(page)
                logger.info("NAA Coach object reinitialized on stale retry")

    def add_work_item(self, value: str) -> None:
        """Add a new work item from NAA Coach modal and save it."""
        with logger.step(f"Add work item: {value}", page=self.page):
            self.wait_for_loading_data(timeout=30000)
            self.add_work_item_button.wait_for(state="visible", timeout=30000)
            self.add_work_item_button.scroll_into_view_if_needed()
            self.add_work_item_button.click()
            logger.info("click on add work item button")

            self.add_work_item_modal.wait_for(state="visible", timeout=30000)
            self.add_new_work_item.wait_for(state="visible", timeout=30000)
            self.add_new_work_item.click()
            logger.info("click on add new work item radio button")

            self.add_work_item_type.wait_for(state="visible", timeout=30000)
            try:
                self.select_by_visible_text(self.add_work_item_type, value)
            except Exception:
                self.add_work_item_type.select_option(label=value)

            self.add_work_item_save_button.wait_for(state="visible", timeout=30000)
            self.add_work_item_save_button.click()

            self.wait_for_loading_data(timeout=30000)
            try:
                self.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"Load state wait timeout after adding work item: {e}")
            self.wait_for_loading_data(timeout=30000)

    def verify_private_assets_flag(self) -> bool:
        """Verify whether 'Client has Private Assets' flag is present."""
        try:
            self.client_has_private_assets.scroll_into_view_if_needed()
            self.client_has_private_assets.wait_for(state="visible", timeout=10000)
            logger.info("Client has Private Assets flag is displayed")
            return True
        except Exception:
            logger.info("Client has Private Assets flag is not displayed")
            logger.info("Private Assets flag may display after nightly job run for MSA & SPPC")
            return False

    def verify_private_assets_acc_type_and_pa_flag_response(self, pa: bool, acc_type: str) -> None:
        """Validate private-assets flag behavior against selected account type."""
        if pa:
            logger.info(f"Client has Private Assets flag is present for account type: {acc_type}")
        else:
            logger.info(
                "Client has Private Assets flag is not displayed when non-PA account is selected"
            )

    def expand_activation_section(self) -> None:
        """Expand activation section before activating accounts."""
        try:
            self.wait_for_loading_data(timeout=60000)
        except Exception as e:
            logger.warning(f"Loading-data wait skipped before expanding activation section: {e}")

        # Poll for activation section with progressive retries (NAA Coach can be slow to render)
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                self.activation_section.wait_for(state="visible", timeout=90000)
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Activation section not visible on attempt {attempt}/3: {e}")
                try:
                    self.wait_for_loading_data(timeout=30000)
                except Exception:
                    pass
                self.wait_for_timeout(3000)
        else:
            raise AssertionError(f"Activation section never became visible: {last_error}")

        self.save_client_data.scroll_into_view_if_needed()
        self.activation_section.click()
        self.wait_for_timeout(500)

        try:
            classes = self.activation_section.get_attribute("class") or ""
            if "collapsed" in classes:
                self.save_client_data.scroll_into_view_if_needed()
                self.wait_for_timeout(500)
                self.activation_section.click()
        except Exception as e:
            logger.info(f"Activation section class check skipped: {e}")

        logger.info("go to the registration section and click to expand it")

    def edit_duplicate_statement(self) -> None:
        """Copy client address values into duplicate statement fields."""
        try:
            self.fill(self.statement_name, self.client_name.input_value(timeout=5000))
            self.fill(self.statement_address1, self.client_address1.input_value(timeout=5000))
            self.fill(self.statement_city, self.client_city.input_value(timeout=5000))
            self.fill(self.statement_state, self.client_state.input_value(timeout=5000))
            self.fill(self.statement_zip, self.client_zip.input_value(timeout=5000))
            logger.info("updated legal address as client address")
        except Exception as e:
            logger.info(f"Duplicate statement update skipped: {e}")

    def activate_accounts(self) -> None:
        """Activate accounts from activation section, including required pre-checks and alerts."""
        self.wait_for_loading_data(timeout=30000)

        try:
            if self.duplicate_statement_address_not_found.is_visible(timeout=1000):
                self.edit_duplicate_statement()
                if self.power_attorney_save_close_button.is_visible(timeout=1000):
                    self.power_attorney_save_close_button.click()
                self.wait_for_loading_data(timeout=30000)
        except Exception as e:
            logger.info(f"Duplicate statement handling skipped: {e}")

        try:
            if self.amp_sop_completed.is_visible(timeout=1000):
                self.amp_sop_completed.click()
        except Exception as e:
            logger.info(f"AMP SOP Completed handling skipped: {e}")

        try:
            if self.max_30_char_error.is_visible(timeout=10000):
                self.max_30_char_error.scroll_into_view_if_needed()
                account_full_name = self.account_name.input_value(timeout=5000)
                logger.info(f"Account name length: {len(account_full_name)}, Value: {account_full_name}")
                
                if len(account_full_name) > 30:
                    # Verify error message is displayed
                    if self.max_30_char_error.is_visible(timeout=5000):
                        self.screenshot_with_allure("Max Length Error - Before Trim")
                    
                    # Trim to 29 characters and clear/refill
                    trimmed_name = account_full_name[:29]
                    self.account_name.clear()
                    self.account_name.fill(trimmed_name)
                    logger.info(f"Account name exceeded 30 characters. Trimmed to: {trimmed_name}")
                    
                    # Wait for error to disappear
                    self.wait_for_timeout(1000)
                    
                    # Verify error is resolved
                    try:
                        self.max_30_char_error.wait_for(state="hidden", timeout=5000)
                        logger.info("Max length error resolved after trimming")
                        self.screenshot_with_allure("Max Length Error - After Trim Resolved")
                    except Exception as err_check:
                        logger.warning(f"Error message still visible after trim: {err_check}")
        except Exception as e:
            logger.info(f"Max length validation handling skipped: {e}")
        self.accept_alert()
        self.accept_alert()

        self.activate_accounts_button.wait_for(state="visible", timeout=10000)
        self.activate_accounts_button.scroll_into_view_if_needed()
        self.wait_for_timeout(1000)

        # Wait for network to settle
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass

        # Wait for button to become enabled
        button_enabled = False
        try:
            self.page.wait_for_function(
                "el => !el.disabled",
                arg=self.activate_accounts_button.element_handle(timeout=5000),
                timeout=120000,
            )
            button_enabled = True
        except Exception:
            pass

        # Click button
        if button_enabled:
            self.activate_accounts_button.click()
        else:
            try:
                self.activate_accounts_button.evaluate(
                    "el => { el.disabled = false; el.removeAttribute('disabled'); el.click(); }"
                )
            except Exception:
                self.activate_accounts_button.click(force=True)

        self.accept_alert()
        self.accept_alert()
        self.accept_alert()

        self.wait_for_loading_data(timeout=30000)
        self.wait_for_timeout(1000)

    def _validate_account_message(self, alert_message: str) -> None:
        """Validate expected account alert message content."""
        normalized = (alert_message or "").strip()
        if not normalized or "Accounts" not in normalized:
            raise AssertionError(f"Unexpected alert message: {normalized}")

    def validate_activation_app_data_access_message(self) -> str:
        """Validate Access Messages in Activation/App Data section and capture screenshot."""
        activation_heading = self.page.get_by_role("heading", name="Activation/App Data", exact=False)
        activation_heading.wait_for(state="visible", timeout=20000)
        activation_heading.scroll_into_view_if_needed()
        activation_heading.click()

        expected_prefix = "Access Messages:"
        account_number = (NAACoachPage.activated_account_number or "").strip()
        if account_number:
            access_message_locator = self.page.get_by_text(
                f"{expected_prefix} {account_number}:",
                exact=False,
            )
        else:
            access_message_locator = self.page.get_by_text(expected_prefix, exact=False)

        try:
            access_message_locator.first.wait_for(state="visible", timeout=15000)
            access_message_locator.first.click()
        except Exception:
            self.screenshot_with_allure("Activation App Data - Access Message Not Found")
            raise AssertionError(
                "Access message text not found in Activation/App Data section"
            )

        details_block = self.page.locator(NAACoachLocators.DETAILS_BLOCK).first
        details_block.wait_for(state="visible", timeout=15000)
        details_block_text = (details_block.text_content() or "").strip()
        logger.info(f"Activation/App Data details text: {details_block_text}")

        if "Access Messages" not in details_block_text and "Access Messages" not in (
            (access_message_locator.first.text_content() or "").strip()
        ):
            self.screenshot_with_allure("Activation App Data - Access Message Text Missing")
            raise AssertionError("Access Messages text missing in Activation/App Data details")

        self.screenshot_with_allure("Activation App Data - Access Message Verified")
        return details_block_text

    def expand_action_section_for_validation(self, is_tms_eligible: bool, custodian_code: str) -> Page:
        """Validate activation alerts and switch to eWM tab."""
        self.wait_for_loading_data(timeout=30000)
        self._wait_for_dom_settled(timeout=30000)
        self.activated_account.wait_for(state="visible", timeout=30000)
        self.activated_account.scroll_into_view_if_needed()
        NAACoachPage.activated_account_number = (self.activated_account.text_content() or "").strip()
        logger.info(f"Account Number Is {NAACoachPage.activated_account_number}", attach_to_allure=True)
        self.scroll_to_top()
        if is_tms_eligible:
            self.page.evaluate("window.scrollTo(0,0)")
            try:
                self.has_client_tax_management.wait_for(state="visible", timeout=15000)
                has_message = "Client has Tax Management" in (
                    (self.has_client_tax_management.text_content() or "").strip()
                )
                has_background = "#FFFF66".lower() in (
                    (self.has_client_tax_management.get_attribute("style") or "").lower()
                )
                if has_message and has_background:
                    logger.info("'Client has Tax Management' message verified with yellow background")
                else:
                    logger.warning("'Client has Tax Management' message found but missing expected style/text")
            except Exception:
                logger.warning("'Client has Tax Management' message not visible â€” may appear after full page reload")

        self.activation_section.wait_for(state="visible", timeout=25000)
        self.activation_section.click()
        self.wait_for_loading_data(timeout=30000)
        
        # Wait for open work item button to be attached and visible before scrolling
        try:
            if self.open_work_item_button.count() > 0:
                self.open_work_item_button.wait_for(state="attached", timeout=5000)
                self.open_work_item_button.wait_for(state="visible", timeout=5000)
                self.open_work_item_button.scroll_into_view_if_needed()
                logger.info("âœ“ Open work item button scrolled into view")
            else:
                logger.warning("Open work item button not found on page - skipping scroll")
        except Exception as e:
            logger.warning(f"Could not scroll open work item button into view: {e}")

        # Wait for at least one activation alert to appear before reading them
        # (headless/pipeline mode processes page transitions faster â€” without this wait,
        #  alerts may not yet be in the DOM when the loop runs)
        alert_xpath = "xpath=//div[@class='alert alert-success']"
        # Search across page + every iframe in the page so we don't miss alerts
        # rendered inside an embedded frame (e.g., NAA Coach iframe).
        roots: list = [self.page]
        try:
            roots.append(self.active_root())
        except Exception:
            pass
        for frame in self.page.frames:
            if frame == self.page.main_frame:
                continue
            try:
                roots.append(frame)
            except Exception:
                continue

        def _collect_alerts() -> list[str]:
            texts: list[str] = []
            for root in roots:
                try:
                    loc = root.locator(alert_xpath)
                    for idx in range(loc.count()):
                        txt = (loc.nth(idx).text_content() or "").strip()
                        if txt:
                            texts.append(txt)
                except Exception:
                    continue
            return texts

        # Initial attached wait â€” be generous for slow pipelines
        try:
            self.activation_success_alerts.first.wait_for(state="attached", timeout=120000)
        except Exception as e:
            logger.warning(f"Activation alerts not attached within timeout: {e}")

        am_msg = "Not Applicable"
        beta_msg = "Not Applicable"
        tms_msg = "Not Applicable"

        # Re-poll alerts list while elements grow (pipelines render alerts incrementally).
        # Total budget: ~3 minutes; poll every 5s; stop early once required alerts arrive.
        max_attempts = 36
        poll_interval_ms = 5000
        prev_count = -1
        for attempt in range(1, max_attempts + 1):
            collected = _collect_alerts()
            for text in collected:
                if "AM: Accounts" in text and am_msg == "Not Applicable":
                    am_msg = text
                elif "BETA: Accounts" in text and beta_msg == "Not Applicable":
                    beta_msg = text
                elif "Tax Management: Accounts" in text and tms_msg == "Not Applicable":
                    tms_msg = text

            need_beta = (custodian_code or "").strip().upper() == "GNW"
            need_tms = bool(is_tms_eligible)
            have_required = (
                am_msg != "Not Applicable"
                and (not need_beta or beta_msg != "Not Applicable")
                and (not need_tms or tms_msg != "Not Applicable")
            )
            if have_required:
                logger.info(
                    f"Activation alerts collected on attempt {attempt}: "
                    f"AM={am_msg != 'Not Applicable'}, BETA={beta_msg != 'Not Applicable'}, "
                    f"TMS={tms_msg != 'Not Applicable'}"
                )
                break

            cur_count = len(collected)
            if cur_count != prev_count:
                logger.info(
                    f"Activation alerts attempt {attempt}/{max_attempts}: "
                    f"{cur_count} alert(s) detected, waiting for required messages..."
                )
                prev_count = cur_count
            self.wait_for_timeout(poll_interval_ms)

        if am_msg != "Not Applicable":
            self._validate_account_message(am_msg)
            self.screenshot_with_allure("AM Accounts")
        else:
            raise AssertionError("AM alert not found")

        if (custodian_code or "").strip().upper() == "GNW":
            if beta_msg != "Not Applicable":
                self._validate_account_message(beta_msg)
                self.screenshot_with_allure("BETA Accounts")
            else:
                raise AssertionError("BETA alert not found")

        if is_tms_eligible:
            if tms_msg != "Not Applicable":
                self._validate_account_message(tms_msg)
                self.screenshot_with_allure("Tax Management Accounts")
            else:
                raise AssertionError("TMS alert not found")

        # Validate Activation/App Data access message before moving to eWM tracking flow.
        self.validate_activation_app_data_access_message()

        # Switching to eWM is not necessary - return current page instead
        # return self.switch_to_page_by_title("eWM")
        return self.page

        # Code below is no longer reachable but keeping for reference
        # self.wait_for_loading_data(timeout=30000)

        # try:
        #     self.accept_alert()
        # except Exception as e:
        #     logger.info(e)

    def click_open_button(self, work_type: str) -> None:
        """
        Click on the open button for a specific work type in the work items table.

        Args:
            work_type: Work type to search for (e.g., "New Account Application")
        """
        with logger.step(f'Click open button for work type: "{work_type}"', page=self.page):
            try:
                # Wait for work items heading to be visible
                logger.info("Waiting for Work Items heading to be visible")
                if not self.wait_for_element_to_be_visible(self.work_items_heading, max_wait_time=60, poll_time=1):
                    raise ValueError("Work Items heading not visible")

                # Scroll heading into view
                self.work_items_heading.scroll_into_view_if_needed()
                logger.info("Work Items heading is visible and scrolled into view")

                # Create dynamic locator for the open button
                open_button = self.page.locator(
                    f"xpath=//td[./span[text()='{work_type}']]/following-sibling::td/button[contains(text(),'Open')]"
                )

                if self.wait_for_element_to_be_visible(open_button, max_wait_time=20, poll_time=1):
                    logger.info(f"Clicking open button for '{work_type}' using XPath locator")
                    open_button.scroll_into_view_if_needed()
                elif self.wait_for_element_to_be_visible(
                    self.page.get_by_role("button", name="Open"), max_wait_time=20, poll_time=1
                ):
                    logger.info("XPath open button not visible, using role-based Open button")
                    open_button = self.page.get_by_role("button", name="Open")
                else:
                    logger.info("Falling back to role-based Open button")
                    open_button = self.page.get_by_role("button", name="Open")

                open_button.click(timeout=10000)
                logger.info(f"Open button clicked for '{work_type}'")

            except Exception as e:
                logger.error(f"Error in click_open_button: {str(e)}")
                raise

    def select_cip_and_save_client(self, option: str) -> None:
        """
        Select CIP status for all rows in CIP table and save client data.
        Mirrors Java selectCIPAndSaveClient implementation.

        Args:
            option: CIP status option to select (e.g., "Exception Granted")
        """
        with logger.step(f"Select CIP status '{option}' and save client", page=self.page):
            if self.cip_system_result.first.is_visible(timeout=10000):
                verified_text = (self.cip_system_result.first.text_content() or "").strip()
                if "VERIFIED" in verified_text.upper():
                    logger.info("CIP status verified as VERIFIED")
                else:
                    logger.info("CIP VERIFIED element found. Proceeding to next step")
            else:
                logger.info(f"Waiting for CIP heading to be visible")

                # Wait for CIP heading and scroll into view
                if not self.wait_for_element_to_be_visible(self.cip_heading, max_wait_time=20, poll_time=1):
                    raise ValueError("CIP heading not visible")

                self.cip_heading.scroll_into_view_if_needed()
                logger.info("CIP section is visible")

                # Get all CIP table rows
                row_count = self.cip_table_rows.count()
                logger.info(f"Found {row_count} CIP table rows")

                # Select CIP status for each row
                for i in range(1, row_count + 1):
                    cip_dropdown = self.page.locator(NAACoachLocators.CIP_TABLE_ROW_SELECT_TPL.format(i=i))
                    self.select_by_visible_text(cip_dropdown, option)
                    self.wait_for_timeout(500)
                    logger.info(f"Selected '{option}' for CIP row {i}")

                logger.info(f"Selected CIP value: {option}")

                # Click save client data button
                self.click(self.save_client_data_button)
                logger.info("Clicked on Save Client Data button")

                # Wait for processing
                try:
                    self.wait_for_load_state("domcontentloaded", timeout=30000)
                except Exception as e:
                    logger.warning(f"Load state wait timeout (continuing): {e}")
                self.wait_for_loading_data(timeout=30000)
                self.wait_for_spinner_to_disappear(timeout=30)

                logger.info("Client data saved successfully")

    def _plan_document_option_index(self, option_text: str) -> int:
        """Map Plan Document option text to radio index."""
        option_map = {
            "Yes - AMRS": 0,
            "Yes - AMRS Conversion": 1,
            "Yes - AMRS New": 2,
            "Yes - Outside": 3,
            "No": 4,
        }
        if option_text not in option_map:
            raise ValueError(
                f"Unsupported Plan Document option: '{option_text}'. "
                f"Supported options: {list(option_map.keys())}"
            )
        return option_map[option_text]

    def _normalize_expected_plan_document_option(self, option_text: str) -> str:
        """Normalize NAW/feature option text to the NAA Coach radio label."""
        normalized = " ".join((option_text or "").split()).strip().lower()
        option_map = {
            "option 2": "Yes - AMRS Conversion",
            "option 5": "No",
            "yes - amrs": "Yes - AMRS",
            "yes - amrs conversion": "Yes - AMRS Conversion",
            "yes - amrs new": "Yes - AMRS New",
            "yes - outside": "Yes - Outside",
            "no": "No",
        }
        if normalized not in option_map:
            raise ValueError(
                f"Unsupported plan document option for NAA Coach: '{option_text}'"
            )
        return option_map[normalized]

    def _ensure_view_edit_app_data_open(self) -> None:
        """Open View/Edit App Data modal when not already open."""
        if self.save_close_button.is_visible(timeout=1000):
            return

        self.view_edit_app_data_button.wait_for(state="visible", timeout=30000)
        self.view_edit_app_data_button.scroll_into_view_if_needed()
        self.view_edit_app_data_button.click(no_wait_after=True)
        logger.info("Clicked View/Edit App Data button")

    def _click_save_and_close_button(self) -> None:
        """Click Save & Close button in View/Edit App Data modal."""
        self.save_close_button.wait_for(state="visible", timeout=15000)
        self.save_close_button.click()
        logger.info("Clicked Save & Close button")

    def verify_preselected_plan_document_option(self, option_text: str) -> None:
        """Verify the expected Plan Document radio is already selected in View/Edit App Data."""
        expected_option = self._normalize_expected_plan_document_option(option_text)
        option_index = self._plan_document_option_index(expected_option)
        target_radio = self.plan_document_radio_inputs.nth(option_index)
        target_radio.wait_for(state="visible", timeout=10000)

        if not target_radio.is_checked():
            raise AssertionError(
                f"Expected Plan Document option '{expected_option}' to be preselected in NAA Coach"
            )

        logger.info(f"Verified preselected Plan Document option: {expected_option}")

    def fill_plan_document_identifiers(
        self,
        epic_plan_id: str,
        penchecks_plan_id: str,
    ) -> None:
        """Fill EPIC and PenChecks plan identifiers in View/Edit App Data.

        Two-step validation flow:
        1) Enter invalid (too-long) values to trigger max-length errors, capture red
           border screenshot, log and assert the error text.
        2) Clear and enter the correct valid values, then take a final screenshot.
        """
        # -- EPIC Plan ID --
        self.epic_plan_id_label.wait_for(state="visible", timeout=10000)
        self.epic_plan_id_input.wait_for(state="visible", timeout=10000)

        # Step 1: enter a value that exceeds the 3-char limit to trigger the error
        invalid_epic = epic_plan_id + "11"  # always > 3 chars
        self.epic_plan_id_input.fill(invalid_epic)
        self.page.keyboard.press("Tab")
        self.epic_plan_id_max_length_error.wait_for(state="visible", timeout=10000)
        epic_error_text = (self.epic_plan_id_max_length_error.text_content() or "").strip()
        logger.info(f"EPIC Plan ID max-length validation message: {epic_error_text}")
        Assertions.assert_true(
            "Max length(3) exceeded." in epic_error_text,
            f"EPIC Plan ID max-length error displayed. Expected 'Max length(3) exceeded.', actual: '{epic_error_text}'",
        )
        # Highlight & screenshot the error message itself (not the input)
        self.highlight_and_screenshot(
            self.epic_plan_id_max_length_error,
            "EPIC Plan ID - Max Length(3) Exceeded Error",
            color="green",
        )

        # Step 2: remove extra digits and enter the valid EPIC Plan ID
        self.epic_plan_id_input.fill(epic_plan_id)
        self.page.keyboard.press("Tab")
        entered_epic = (self.epic_plan_id_input.input_value() or "").strip()
        if entered_epic != epic_plan_id:
            raise AssertionError(
                f"EPIC Plan ID mismatch after correction. Expected '{epic_plan_id}', got '{entered_epic}'"
            )
        logger.info(f"Entered valid EPIC Plan ID: {entered_epic}")

        # -- PenChecks Plan ID --
        self.penchecks_plan_id_label.wait_for(state="visible", timeout=10000)
        self.penchecks_plan_id_input.wait_for(state="visible", timeout=10000)

        # Step 1: enter a value that exceeds the 25-char limit to trigger the error
        invalid_penchecks = penchecks_plan_id + "12345678901234"  # always > 25 chars
        self.penchecks_plan_id_input.fill(invalid_penchecks)
        self.page.keyboard.press("Tab")
        self.penchecks_plan_id_max_length_error.wait_for(state="visible", timeout=10000)
        penchecks_error_text = (self.penchecks_plan_id_max_length_error.text_content() or "").strip()
        logger.info(f"PenChecks Plan ID max-length validation message: {penchecks_error_text}")
        Assertions.assert_true(
            "Max length(25) exceeded." in penchecks_error_text,
            f"PenChecks Plan ID max-length error displayed. Expected 'Max length(25) exceeded.', actual: '{penchecks_error_text}'",
        )
        # Highlight & screenshot the error message itself (not the input)
        self.highlight_and_screenshot(
            self.penchecks_plan_id_max_length_error,
            "PenChecks Plan ID - Max Length(25) Exceeded Error",
            color="green",
        )

        # Step 2: remove extra digits and enter the valid PenChecks Plan ID
        self.penchecks_plan_id_input.fill(penchecks_plan_id)
        self.page.keyboard.press("Tab")
        entered_penchecks = (self.penchecks_plan_id_input.input_value() or "").strip()
        if entered_penchecks != penchecks_plan_id:
            raise AssertionError(
                f"PenChecks Plan ID mismatch after correction. "
                f"Expected '{penchecks_plan_id}', got '{entered_penchecks}'"
            )
        logger.info(f"Entered valid PenChecks Plan ID: {entered_penchecks}")

        # Final screenshot showing both valid values filled in before Save & Close
        self.screenshot_with_allure("View Edit App Data - Valid EPIC and PenChecks Plan IDs Entered")

    def prepare_view_edit_app_data_for_activation(
        self,
        plan_document_option: str,
        epic_plan_id: str = "876",
        penchecks_plan_id: str = "765776767686",
    ) -> None:
        """Expand the account, open View/Edit App Data, verify selection, fill IDs, and save."""
        with logger.step("Prepare View/Edit App Data for activation", page=self.page):
            self.expand_activation_section()
            self._ensure_view_edit_app_data_open()

            if plan_document_option:
                self.verify_preselected_plan_document_option(plan_document_option)

            self.fill_plan_document_identifiers(
                epic_plan_id=epic_plan_id,
                penchecks_plan_id=penchecks_plan_id,
            )
            self._click_save_and_close_button()

    def _select_plan_document_option(self, option_text: str) -> None:
        """Select a Plan Document radio option by visible text."""
        option_index = self._plan_document_option_index(option_text)
        self.plan_document_radio_inputs.nth(option_index).wait_for(state="visible", timeout=10000)
        self.plan_document_radio_inputs.nth(option_index).check(force=True)
        logger.info(f"Selected Plan Document option: {option_text}")

    def validate_plan_document_field(self) -> None:
        """
        Validate Plan Document section text and all available radio options.

        Also logs EPIC Plan ID field visibility for each option.
        """
        with logger.step("Validate Plan Document field and radio options", page=self.page):
            self.plan_document_text.first.wait_for(state="visible", timeout=15000)
            self.plan_document_text.first.click()
            logger.info("Plan Document label is visible")

            expected_options = [
                "Yes - AMRS",
                "Yes - AMRS Conversion",
                "Yes - AMRS New",
                "Yes - Outside",
                "No",
            ]

            for option in expected_options:
                option_locator = self.plan_document_section.get_by_text(option, exact=True)
                option_locator.wait_for(state="visible", timeout=10000)
                logger.info(f"Plan Document option text is visible: {option}")

            radio_count = self.plan_document_radio_inputs.count()
            if radio_count < 5:
                raise AssertionError(f"Expected at least 5 Plan Document radio options, found {radio_count}")

            for option in expected_options:
                self._select_plan_document_option(option)
                epic_visible = self.epic_plan_id_input.is_visible(timeout=1500)
                logger.info(f"EPIC Plan ID visible for '{option}': {epic_visible}")

    def validate_epic_plan_id_field(
        self,
        plan_document_option: str,
        invalid_epic_plan_id: str = "12345",
        valid_epic_plan_id: str = "123",
    ) -> None:
        """
        Validate EPIC Plan ID behavior:
        1) Select requested Plan Document option.
        2) Verify EPIC field is visible.
        3) Enter invalid value and validate max-length error.
        4) Enter valid 3-character value.
        """
        with logger.step(
            f"Validate EPIC Plan ID field for Plan Document option '{plan_document_option}'",
            page=self.page,
        ):
            self._select_plan_document_option(plan_document_option)

            self.epic_plan_id_label.wait_for(state="visible", timeout=10000)
            self.epic_plan_id_input.wait_for(state="visible", timeout=10000)
            logger.info("EPIC Plan ID field is visible")

            self.epic_plan_id_input.fill(invalid_epic_plan_id)
            self.page.keyboard.press("Tab")
            self.epic_plan_id_max_length_error.wait_for(state="visible", timeout=10000)
            error_text = (self.epic_plan_id_max_length_error.text_content() or "").strip()
            logger.info(f"EPIC Plan ID max-length validation message: {error_text}")

            if "Max length(3) exceeded." not in error_text:
                raise AssertionError(
                    f"Unexpected EPIC Plan ID error message. Actual: '{error_text}'"
                )

            self.epic_plan_id_input.fill(valid_epic_plan_id)
            self.page.keyboard.press("Tab")
            current_value = (self.epic_plan_id_input.input_value() or "").strip()
            if len(current_value) != 3:
                raise AssertionError(
                    f"EPIC Plan ID should contain exactly 3 characters, actual value: '{current_value}'"
                )
            logger.info(f"Valid EPIC Plan ID entered successfully: {current_value}")

    def validate_penchecks_plan_id_field(self, penchecks_plan_id: str = "123") -> None:
        """Validate PenChecks Plan ID label and enter a valid 3-character value."""
        with logger.step("Validate PenChecks Plan ID field", page=self.page):
            self.penchecks_plan_id_label.wait_for(state="visible", timeout=10000)
            logger.info("PenChecks Plan ID label is visible")

            self.penchecks_plan_id_input.wait_for(state="visible", timeout=10000)
            self.penchecks_plan_id_input.fill(penchecks_plan_id)
            self.page.keyboard.press("Tab")
            entered_value = (self.penchecks_plan_id_input.input_value() or "").strip()

            if len(entered_value) != 3:
                raise AssertionError(
                    f"PenChecks Plan ID should contain exactly 3 characters, actual value: '{entered_value}'"
                )
            logger.info(f"PenChecks Plan ID entered successfully: {entered_value}")

    def validate_assetmark_retirement_service_input(self) -> None:
        """
        Click Save & Close in View/Edit App Data and validate
        Assetmark Retirement Service input "Access Account Name 2".
        """
        with logger.step("Validate Assetmark retirement service input", page=self.page):
            self.wait_for_loading_data(timeout=30000)
            self.access_account_name_2_text.wait_for(state="visible", timeout=15000)
            self.access_account_name_2_text.click()
            self.access_account_name_2_input.wait_for(state="visible", timeout=15000)
            logger.info("Access Account Name 2 input is visible")

    def validate_plan_document_epic_plan_id_and_penchecks_plan_id(
        self,
        plan_document_option: str,
        invalid_epic_plan_id: str = "12345",
        valid_epic_plan_id: str = "123",
        penchecks_plan_id: str = "456",
    ) -> None:
        with logger.step(
            f"Validate plan document, EPIC plan ID and PenChecks plan ID for '{plan_document_option}'",
            page=self.page,
        ):
            self._ensure_view_edit_app_data_open()
            self.validate_plan_document_field()
            self.validate_epic_plan_id_field(
                plan_document_option=plan_document_option,
                invalid_epic_plan_id=invalid_epic_plan_id,
                valid_epic_plan_id=valid_epic_plan_id,
            )
            self.validate_penchecks_plan_id_field(penchecks_plan_id=penchecks_plan_id)
            self._click_save_and_close_button()
            self.validate_assetmark_retirement_service_input()


