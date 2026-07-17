"""Shell Process Page - BAW Work Item actions"""

import re
from typing import TYPE_CHECKING, Dict, Optional

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.wait_utils import WaitContext

if TYPE_CHECKING:
    from pages.baw.transfer_attributes_page import TransferAttributesPage

logger = get_allure_logger(__name__)


class ShellProcessPage(BasePage):
    """Shell Process Page class for work item selections"""

    PAGE_NAME = "Shell Process Page"

    def __init__(self, page: Page):
        super().__init__(page)
        self.work_item_type_select: Locator = page.locator("select#InputText3")
        self.custodian_select: Locator = page.locator("select#InputText0")
        self.team_name: Locator = page.locator("#ComboBox0")
        self.individual_owner: Locator = page.locator("select#ComboBox1")
        self.run_now_button: Locator = page.locator("#ButtonGroup0_RunNow")
        self.b_number: Locator = page.locator("xpath=//*[normalize-space()='B #']/following-sibling::td[1]")
        self.hrc_textbox: Locator = page.locator("#InputText32")
        self.hrc_submit_button: Locator = page.locator("#ButtonGroup21_SubmitHRC")
        self.save_shell_process_button: Locator = page.locator("#ButtonGroup0_Save")
        self.select_account_button: Locator = page.locator("button#ButtonGroup19_SelectAccount")
        self.remove_association_button: Locator = page.locator("xpath=//button[normalize-space()='Remove']")
        self.add_account_association_button: Locator = page.locator("xpath=//button[normalize-space()='Add']")
        self.added_account_number: Locator = page.locator("#TableCellCustodialAccountNumber0_0")
        self.added_account_name: Locator = page.locator("#TableCellItemName0_0")
        self.save_exit_button: Locator = page.locator("button#ButtonGroup0_Button2")
        self.baw_loading_spinner: Locator = page.locator("img[src*='loading_msg.gif']")
        self.internal_status_label: Locator = page.locator("label#combo_Label")
        self.internal_status_dropdown: Locator = page.locator("select#combo")
        self.custodial_account: Locator = page.get_by_role("textbox", name="Custodial Account")
        self.update_transfer_details_button: Locator = page.get_by_role("button", name="Update Transfer details")
        self.notes_table: Locator = page.locator("//table[@id='Table4']")
        self.internal_status: Locator = page.get_by_role("combobox", name="Internal Status")
        self.custodian_acc: Locator = page.locator('td.LabelFontStyle').filter(has_text='Custodian Acc #').locator('xpath=following-sibling::td').first
        self.add_update_button: Locator = page.get_by_role("button", name=re.compile(r"Add.?Update OA"))

    def switch_to_shell_process_page(self, source_page: Optional[Page] = None) -> None:
        """Switch to Shell Process page and reinitialize this page object."""
        with logger.step('Switch to "Shell Process" page', page=source_page or self.page):
            if source_page is not None:
                self.page = source_page

            if self.page.is_closed():
                open_pages = [p for p in self.page.context.pages if not p.is_closed()]
                if not open_pages:
                    raise RuntimeError("No open browser pages available to switch to Shell Process")
                self.page = open_pages[-1]
                logger.info("Current page was closed; rebound to an open page before switching")

            page = self.switch_to_page_by_title("Shell Process", timeout=30)
            self.__init__(page)
            logger.info("Switched to Shell Process page")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                logger.warning("Shell Process page domcontentloaded wait timed out")
            self.wait_for_loading_data(timeout=30000)

    def select_work_item_type(self, value: str) -> None:
        """
        Select work item type by visible text.

        Args:
            value: Work item type option text
        """
        with logger.step(f"Select work item type: {value}", page=self.page):
            page = self.switch_to_page_by_title("Shell Process", timeout=30)
            # Refresh all locators so they bind to the active Shell Process page.
            self.__init__(page)
            logger.info("Switched to new window after clicking Open New WorkItem button")
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                logger.warning("New window domcontentloaded wait timed out")
            self.wait_for_loading_data()

            try:
                # Re-resolve locator from current page/frame after switching windows.
                work_item_type_dropdown = self.active_root().get_by_label("Work Item Type")
                work_item_type_dropdown.wait_for(state="visible", timeout=20000)
                with WaitContext(timeout=20.0) as wait:
                    wait.until_visible(work_item_type_dropdown)
                work_item_type_dropdown.select_option(label=value)
            except Exception as primary_error:
                logger.warning(f"Work Item Type by label failed: {primary_error}; trying InputText3 fallback")
                self.work_item_type_select = self.page.locator("select#InputText3")
                self.work_item_type_select.wait_for(state="visible", timeout=20000)
                with WaitContext(timeout=20.0) as wait:
                    wait.until_visible(self.work_item_type_select)
                self.work_item_type_select.select_option(label=value)

            logger.info(f"Work item type selected: {value}")
            self.wait_for_loading_data()
            self.tab_out()

    def select_custodian_type(self, value: str) -> None:
        """
        Select custodian type by visible text.

        Args:
            value: Custodian option text
        """
        with logger.step(f"Select custodian type: {value}", page=self.page):
            self.custodian_select.wait_for(state="visible", timeout=20000)
            with WaitContext(timeout=20.0) as wait:
                wait.until_visible(self.custodian_select)
            self.custodian_select.select_option(label=value)
            self.team_name.wait_for(state="visible", timeout=30000)
            with WaitContext(timeout=30.0) as wait:
                wait.until_visible(self.team_name)
            logger.info(f"Custodian selected: {value}")

    def select_individual_owner_and_click_run_now(self, value: str) -> None:
        """
        Select individual owner and click run now button.
        Mirrors Java implementation: waitForUILoading -> selectByValue -> click runNow

        Args:
            value: Individual owner option text
        """
        with logger.step(f"Select individual owner: {value} and click Run Now", page=self.page):
            # Wait for UI loading (5000ms as per Java)
            self.wait_for_timeout(5000)
            
            # Select individual owner using base reusable function
            self.select_by_visible_text(self.individual_owner, value)
            
            # Click run now button — use no_wait_after because the form POST
            # triggers a long server-side navigation that exceeds Playwright's
            # default 30s actionability timeout; spinner waits below handle loading.
            try:
                self.run_now_button.click(no_wait_after=True)
            except Exception:
                logger.warning("Run Now normal click failed, trying JS click")
                self.run_now_button.evaluate("el => el.click()")
            logger.info(f"Individual owner has been selected as {value}")
            logger.info("Run Now button clicked")
            try:
                self.wait_for_spinner(self.baw_loading_spinner, timeout=60000)
            except Exception as spinner_error:
                logger.warning(f"Spinner wait failed after Run Now click (spinner may have already disappeared): {spinner_error}")
                logger.info("Continuing with next step despite spinner check failure")
            try:
                self.wait_for_spinner_to_disappear(timeout=60000)
            except Exception as spinner_disappear_error:
                logger.warning(f"Spinner did not disappear within timeout after Run Now click: {spinner_disappear_error}")
                logger.info("Continuing with next step despite spinner disappearance check failure")
            

    def fetch_b_number(self) -> str:
        """Fetch B number from Shell Process page."""
        with logger.step("Fetch B number from Shell Process page", page=self.page):
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=60000)
            except Exception:
                pass
            self.wait_for_loading_data()
            self.b_number.wait_for(state="visible", timeout=60000)

            for attempt in range(1, 4):
                b_num = self.get_text(self.b_number, timeout=30000).strip()
                if b_num:
                    logger.info(f"Fetched B number: {b_num}")
                    return b_num
                if attempt < 3:
                    self.wait_for_timeout(1000)

            Assertions.fail("Could not fetch B number after 3 attempts (text was empty)")

    def enter_hrc(self, hrc_number: str) -> None:
        """
        Enter HRC number in the HRC textbox.
        Mirrors Java implementation with additional render-safe checks.

        Args:
            hrc_number: The HRC number to enter (7-digit string)
        """
        with logger.step("Enter HRC number", page=self.page):
            # Render-safe readiness: ensure element is in DOM and visible before interacting.
            self.hrc_textbox.wait_for(state="attached", timeout=20000)
            self.hrc_textbox.wait_for(state="visible", timeout=20000)
            with WaitContext(timeout=20.0) as wait:
                wait.until_visible(self.hrc_textbox)
                wait.until_enabled(self.hrc_textbox)
            
            # Fill HRC textbox with the number
            self.fill(self.hrc_textbox, hrc_number)
            logger.info(f"Entered HRC number: {hrc_number}")

    def submit_hrc(self) -> None:
        """
        Click HRC submit button and wait for spinner to appear then disappear.
        """
        with logger.step("Submit HRC", page=self.page):
            self.wait_for_timeout(1000)
            baw_url = self.page.url
            try:
                self.hrc_submit_button.click(no_wait_after=True)
            except Exception:
                logger.warning("HRC Submit normal click failed, trying JS click")
                self.hrc_submit_button.evaluate("el => el.click()")
            logger.info("HRC submit button clicked")
            try:
                self.wait_for_timeout(1000)
            except Exception as e:
                if "closed" in str(e).lower():
                    logger.warning("BAW page crashed after HRC submit — recovering")
                    new_page = self.page.context.new_page()
                    new_page.goto(baw_url, wait_until="domcontentloaded", timeout=30000)
                    self.page = new_page
                    self.__init__(new_page)
                    return
                raise
            try:
                self.wait_for_spinner_to_disappear(timeout=60000)
            except Exception as spinner_disappear_error:
                logger.warning(f"Spinner did not disappear within timeout after HRC submit click: {spinner_disappear_error}")
                logger.info("Continuing with next step despite spinner disappearance check failure")

    def click_select_button(self, button_type: str) -> None:
        """
        Click button under account number association section.
        Mirrors Java behavior for select/remove/add options.

        Args:
            button_type: Button type (select/remove/add)
        """
        with logger.step(f"Click on {button_type} button under account number association", page=self.page):
            self.wait_for_loading_data()
            try:
                self.page.wait_for_url("**WorkflowState**", timeout=10000)
            except Exception:
                logger.info("WorkflowState not detected in URL within timeout")

            action = (button_type or "").strip().lower()

            if action == "select":
                try:
                    self.page.keyboard.press("Enter")
                except Exception as enter_error:
                    logger.info(f"Enter key action failed: {enter_error}")

                try:
                    self.accept_alert()
                except Exception as alert_error:
                    logger.info(f"Alert handling in previous step: {alert_error}")

                select_clicked = False
                for attempt in range(1, 4):
                    logger.info(f"Waiting for Select button attempt {attempt}/3")

                    try:
                        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                    except Exception as e:
                        logger.warning(f"domcontentloaded wait timeout on Select attempt {attempt}: {e}")

                    self.wait_for_loading_data(timeout=45000)
                    self.wait_for_timeout(1000 * attempt)

                    try:
                        self.select_account_button.wait_for(state="visible", timeout=30000)
                        with WaitContext(timeout=30.0) as wait:
                            wait.until_visible(self.select_account_button)
                        self.select_account_button.scroll_into_view_if_needed()
                        self.select_account_button.click(timeout=15000, force=True)
                        logger.info("Click on select button under account number association")
                        select_clicked = True
                        break
                    except Exception as click_error:
                        logger.warning(f"Select button attempt {attempt} failed: {click_error}")

                if not select_clicked:
                    raise TimeoutError("Select button was not clickable after 3 attempts")
            elif action == "remove":
                self.remove_association_button.wait_for(state="visible", timeout=20000)
                with WaitContext(timeout=20.0) as wait:
                    wait.until_visible(self.remove_association_button)
                self.remove_association_button.click()
                logger.info("Click on remove button under account number association")
                self.wait_for_loading_data()
            else:
                self.add_account_association_button.wait_for(state="visible", timeout=20000)
                with WaitContext(timeout=20.0) as wait:
                    wait.until_visible(self.add_account_association_button)
                self.add_account_association_button.click()
                logger.info("Click on add button under account number association")
                self.wait_for_loading_data()

    def click_save_shell_process_button(self) -> None:
        """Click Save Shell Process button — waits until visible then clicks."""
        with logger.step("Click on save shell process button"):
            try:
                # Wait up to 60s total for the Save button to become visible, then click it.
                self.save_shell_process_button.wait_for(state="visible", timeout=60000)
                self.save_shell_process_button.scroll_into_view_if_needed()
                try:
                    self.save_shell_process_button.click(no_wait_after=True)
                except Exception:
                    logger.warning("Save button normal click failed, trying JS click")
                    self.save_shell_process_button.evaluate("el => el.click()")
                logger.info("Save shell process button clicked successfully")
            except Exception as e:
                logger.warning(f"Save button not found or click failed: {e}. Continuing to next step...")


    def click_save_exit_button(self) -> None:
        """Click Save & Exit — closes Shell Process tab."""
        with logger.step("Click on save exit button", page=self.page):
            self.save_exit_button.wait_for(state="visible", timeout=30000)
            self.save_exit_button.scroll_into_view_if_needed()

            # Click Save & Exit button — no_wait_after avoids 30s navigation timeout
            try:
                self.save_exit_button.click(no_wait_after=True)
            except Exception:
                logger.warning("Save & Exit normal click failed, trying JS click")
                self.save_exit_button.evaluate("el => el.click()")
            logger.info("Save & Exit button clicked")

            # Handle alerts (mirrors Java's handleAlert("OK"))
            try:
                self.accept_alert()
                logger.info("First alert handled")
            except Exception as e:
                logger.info(f"First alert handling: {e}")

    def select_internal_status_and_close_work_item(self, status_value: str = "Close-Other") -> None:
        """Select Internal Status value and close Shell Process work item."""
        with logger.step(f"Select Internal Status as '{status_value}' and close work item", page=self.page):
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.wait_for_loading_data(timeout=30000)

            self.internal_status_label.wait_for(state="visible", timeout=30000)
            self.internal_status_label.scroll_into_view_if_needed()

            self.internal_status_dropdown.wait_for(state="visible", timeout=30000)
            with WaitContext(timeout=30.0) as wait:
                wait.until_visible(self.internal_status_dropdown)
                wait.until_enabled(self.internal_status_dropdown)

            self.internal_status_dropdown.scroll_into_view_if_needed()
            self.internal_status_dropdown.click()
            self.internal_status_dropdown.select_option(label=status_value)
            logger.info(f"Internal Status selected: {status_value}")

            self.click_save_exit_button()

    def validate_added_account_in_account_number_association(self) -> Dict[str, str]:
        """Validate and return added account number/name in account number association section."""
        with logger.step("Validate added account number and account name", page=self.page):
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.wait_for_loading_data(timeout=30000)
            self.added_account_number.wait_for(state="visible", timeout=30000)
            self.added_account_name.wait_for(state="visible", timeout=30000)

            account_number = self.get_text(self.added_account_number, timeout=10000).strip()
            account_name = self.get_text(self.added_account_name, timeout=10000).strip()

            assert account_number, "added account number has not been validated"
            assert account_name, "added account name has not been validated"

            logger.info("added account number and account name has been validated on shell page")
            return {
                "accountNumber": account_number,
                "accountName": account_name,
            }

    def spinner_loader(self, appear_timeout: int = 10000, disappear_timeout: int = 60000) -> None:
        """Wait for BAW loading spinner to appear then disappear."""
        try:
            self.baw_loading_spinner.wait_for(state="visible", timeout=appear_timeout)
            logger.info("BAW loading spinner appeared")
        except Exception:
            logger.info("BAW loading spinner did not appear (may have already passed)")
        try:
            self.baw_loading_spinner.wait_for(state="hidden", timeout=disappear_timeout)
            logger.info("BAW loading spinner has disappeared")
        except Exception as e:
            logger.warning(f"BAW loading spinner did not disappear within {disappear_timeout}ms: {e}")

    def enter_custodial_account_value(self, account: str):
        """Enter the custodial account number."""
        self.fill(self.custodial_account, account)
        self.tab_out()
        logger.info(f"Enter the custodial account number: {account}")

    def click_update_transfer_details_button(self) -> "TransferAttributesPage":
        """Click on update transfer details button and switch to TransferAttributes tab.

        Returns:
            TransferAttributesPage for the new tab
        """
        from pages.baw.transfer_attributes_page import TransferAttributesPage

        Assertions.assert_true(self.update_transfer_details_button.is_visible(timeout=10000), "Update Transfer details button is not visible")
        logger.info("Validated Update Transfer Details button is visible")
        with self.page.context.expect_page() as new_page_info:
            self.click(self.update_transfer_details_button)

        transfer_page = new_page_info.value
        transfer_page.wait_for_load_state("domcontentloaded", timeout=30000)
        transfer_page.bring_to_front()
        logger.info(f"Switched to TransferAttributes tab: {transfer_page.url}")
        return TransferAttributesPage(transfer_page)

    def validate_notes_history(self, expected_text: str = "") -> str:
        """Switch to Shell Process page, reload, and validate notes history content."""
        self.page.bring_to_front()
        self.baw_spinner_loader(appear_timeout=15000, disappear_timeout=60000)
        self.page.reload()
        self.baw_spinner_loader(appear_timeout=5000, disappear_timeout=30000)

        if expected_text:
            notes_content = self.get_text(self.notes_table, timeout=10000)
            Assertions.assert_true(expected_text in notes_content, f"Notes history does not contain expected text: '{expected_text}'")
            logger.info(f"Validated notes history contains expected text: '{expected_text}'")

        return self.get_text(self.notes_table, timeout=10000).strip()

    def update_internal_status(self, value: str):
        """Select internal status value from combobox."""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        except Exception:
            pass
        self.wait_for_loading_data()
        self.select_option(self.internal_status, value, timeout=30000)
        logger.info(f"Internal status has been updated to: {value}")

    def fetch_custodian_account(self) -> str:
        """Get the custodian account number text."""
        return self.get_text(self.custodian_acc, timeout=10000).strip()

    def clickAddUpdateButton(self):
        """Click Add/Update OA button and accept the alert."""
        self.accept_alert()
        self.click(self.add_update_button, timeout=20000)
        self.wait_for_timeout(5000)
        logger.info("Clicked on Update OA button and accepted alert")