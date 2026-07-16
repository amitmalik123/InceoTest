"""Shell Process Page Object"""

import os
import re
import time
from typing import Optional
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from playwright.sync_api import FrameLocator, Locator, Page, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Dialog, Locator, Page

from locators.baw.shell_process_locators import ShellProcessLocators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions, SoftAssertions
from utils.wait_utils import WaitContext

if TYPE_CHECKING:
    from pages.baw.transfer_attributes_page import TransferAttributesPage 
    from pages.baw.create_oa_page import CreateOAPage

logger = get_allure_logger(__name__)


class ShellProcessPage(BasePage):
    """Shell Process Page class for work item selections"""

    PAGE_NAME = "Shell Process Page"

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)
        self.work_item_type_select: Locator = page.locator(ShellProcessLocators.WORK_ITEM_TYPE_SELECT)
        self.custodian_select: Locator = page.locator(ShellProcessLocators.CUSTODIAN_SELECT)
        self.team_name: Locator = page.locator(ShellProcessLocators.TEAM_NAME)
        self.individual_owner: Locator = page.locator(ShellProcessLocators.INDIVIDUAL_OWNER)
        self.run_now_button: Locator = page.locator(ShellProcessLocators.RUN_NOW_BUTTON)
        self.b_number: Locator = page.locator(ShellProcessLocators.B_NUMBER)
        self.hrc_textbox: Locator = page.locator(ShellProcessLocators.HRC_TEXTBOX)
        self.hrc_submit_button: Locator = page.locator(ShellProcessLocators.HRC_SUBMIT_BUTTON)
        self.save_shell_process_button: Locator = page.locator(ShellProcessLocators.SAVE_SHELL_PROCESS_BUTTON)
        self.select_account_button: Locator = page.get_by_role("button", name=ShellProcessLocators.SELECT_ACCOUNT_BUTTON_ROLE)
        self.remove_association_button: Locator = page.locator(ShellProcessLocators.REMOVE_ASSOCIATION_BUTTON)
        self.add_account_association_button: Locator = page.locator(ShellProcessLocators.ADD_ACCOUNT_ASSOCIATION_BUTTON)
        self.added_account_number: Locator = page.locator(ShellProcessLocators.ADDED_ACCOUNT_NUMBER)
        self.added_account_name: Locator = page.locator(ShellProcessLocators.ADDED_ACCOUNT_NAME)
        self.save_exit_button: Locator = page.locator(ShellProcessLocators.SAVE_EXIT_BUTTON)
        self.save_refresh_button: Locator = page.locator(ShellProcessLocators.SAVE_REFRESH_BUTTON)
        self.baw_loading_spinner: Locator = page.locator(ShellProcessLocators.BAW_LOADING_SPINNER)
        self.custodial_account: Locator = page.get_by_role("textbox", name=ShellProcessLocators.CUSTODIAL_ACCOUNT_ROLE)
        self.update_transfer_details_button: Locator = page.get_by_role("button", name=ShellProcessLocators.UPDATE_TRANSFER_DETAILS_BUTTON_ROLE)
        self.notes_table: Locator = page.locator(ShellProcessLocators.NOTES_TABLE)
        self.contra_firm_account: Locator = page.locator(ShellProcessLocators.CONTRA_FIRM_ACCOUNT_SELECTOR)
        self.internal_status: Locator = page.get_by_role("combobox", name=ShellProcessLocators.INTERNAL_STATUS_ROLE)
        self.custodian_acc: Locator = page.locator(ShellProcessLocators.CUSTODIAN_ACC_CELL_CSS).filter(has_text=ShellProcessLocators.CUSTODIAN_ACC_LABEL).locator(ShellProcessLocators.CUSTODIAN_ACC_FOLLOWING_TD).first
        self.add_update_button: Locator = page.get_by_role("button", name=re.compile(ShellProcessLocators.ADD_UPDATE_OA_BUTTON_PATTERN))
        # Digital Check work item locators (C95661)
        self.create_new_digital_record_button: Locator = page.get_by_role("button", name=ShellProcessLocators.CREATE_NEW_DIGITAL_RECORD_BUTTON_ROLE)
        self.add_update_check_details_button: Locator = page.get_by_role("button", name=ShellProcessLocators.ADD_UPDATE_CHECK_DETAILS_BUTTON_ROLE)
        # ----- C95666: Check Document Extraction locators (page-level) -----
        self.add_document_button: Locator = page.get_by_role(
            "button", name=ShellProcessLocators.ADD_DOCUMENT_BUTTON_ROLE
        )
        self.submit_button: Locator = page.get_by_role(
            "button", name=ShellProcessLocators.SUBMIT_BUTTON_ROLE
        )
        self.search_work_item_baw_link: Locator = page.get_by_role(
            "link", name=ShellProcessLocators.SEARCH_WORK_ITEM_LINK_ROLE
        )
        self.dashboard_link: Locator = page.get_by_role(
            "link", name=ShellProcessLocators.DASHBOARD_LINK_ROLE
        )
        # ----- C95666: Account Funding Validation (AFV) section locators -----
        self.afv_section_twisty: Locator = page.locator(
            ShellProcessLocators.AFV_SECTION_TWISTY
        )
        self.afv_category_account_notes: Locator = page.get_by_text(
            ShellProcessLocators.AFV_CATEGORY_ACCOUNT_NOTES_TEXT
        )
        self.afv_category_status_of_account: Locator = page.get_by_text(
            ShellProcessLocators.AFV_CATEGORY_STATUS_OF_ACCOUNT_TEXT
        )
        self.afv_results_cell: Locator = page.get_by_role(
            "cell",
            name=ShellProcessLocators.AFV_RESULTS_CELL_TEXT,
            exact=True,
        ).first
        # close_status_combo is the same combobox as internal_status ΓÇö alias used by close_work_item
        # (kept for backwards compat; close methods use self.internal_status directly)

    def select_work_item_type(self, value: str) -> None:
        """
        Select work item type by visible text.

        Args:
            value: Work item type option text
        """
        self.wait_for_loading_data()
        self.select_option(self.work_item_type_select, label=value, timeout=20000)
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
            self.custodian_select.select_option(label=value)
            self.team_name.wait_for(state="visible", timeout=30000)
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

            # Select individual owner by option VALUE (matches Java selectByValue)
            self.individual_owner.wait_for(state="visible", timeout=20000)
            self.individual_owner.select_option(value=value)
            
            # Click run now button ΓÇö use no_wait_after because the form POST
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

    # ------------------------------------------------------------------
    # C95666 - Check Document Extraction helpers
    # ------------------------------------------------------------------
    def select_individual_owner(self, value: str) -> None:
        """
        Select individual owner by option VALUE WITHOUT clicking Run Now.

        Used by the C95666 Check Document Extraction flow where, after
        selecting the owner, the next action is to upload the check
        document (via 'Add Document' / Submit) instead of triggering the
        Run Now navigation.

        Args:
            value: Individual owner option value (matches Java selectByValue).
        """
        with logger.step(f"Select individual owner: {value} (without Run Now)", page=self.page):
            self.wait_for_timeout(5000)
            self.individual_owner.wait_for(state="visible", timeout=20000)
            self.individual_owner.select_option(value=value)
            logger.info(f"Individual owner has been selected as {value}")

    @staticmethod
    def _resolve_check_document_path(file_path: str) -> str:
        """Resolve ``file_path`` to an absolute path under ``applicationqe/upload/BAW/``."""
        candidate = Path(file_path)
        if candidate.is_absolute() and candidate.exists():
            return str(candidate)
        applicationqe_root = Path(__file__).resolve().parent.parent.parent
        default_path = applicationqe_root / "upload" / "BAW" / candidate.name
        if default_path.exists():
            return str(default_path)
        return str(candidate)

    def upload_check_document_and_submit(
        self,
        file_path: str = ShellProcessLocators.DEFAULT_CHECK_DOCUMENT_FILENAME,
    ) -> None:
        """Upload a check document and submit the work item.

        Mirrors the codegen recording for C95666:

        1. Click ``Add Document`` on the current BAW work item page; this
           opens a popup containing the ``Choose File`` button.
        2. In the popup: set the file via the ``Choose File`` input, then
           click ``Commit Documents``. Close the popup.
        3. Back on the parent work item page: auto-dismiss any native
           dialog that appears, then click ``Submit`` and close the
           parent page.

        Args:
            file_path: Absolute path, project-relative path, or bare
                filename of the document to upload. Bare filenames are
                resolved against ``applicationqe/data/baw/``.
        """
        resolved_path = self._resolve_check_document_path(file_path)
        parent_page = self.page

        with logger.step(
            f"Upload check document '{resolved_path}' and Submit", page=parent_page
        ):
            self.wait_for_loading_data()
            self.add_document_button.wait_for(state="visible", timeout=30000)

            # Click Add Document → upload popup opens.
            upload_popup: Optional[Page] = None
            try:
                with parent_page.expect_popup(timeout=30000) as popup_info:
                    self.add_document_button.click()
                upload_popup = popup_info.value
            except Exception as popup_exc:
                logger.warning(
                    f"Add Document popup not captured via expect_popup: {popup_exc}. "
                    "Falling back to context page diff."
                )
                existing = set(parent_page.context.pages)
                try:
                    self.add_document_button.click()
                except Exception:
                    self.add_document_button.evaluate("el => el.click()")
                for _ in range(30):
                    added = [p for p in parent_page.context.pages if p not in existing]
                    if added:
                        upload_popup = added[-1]
                        break
                    parent_page.wait_for_timeout(500)

            if upload_popup is None:
                raise AssertionError(
                    "Upload popup did not open after clicking 'Add Document'"
                )

            try:
                upload_popup.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"Upload popup domcontentloaded wait failed: {e}")
            logger.info("Upload popup opened (Add Document)")

            choose_file = upload_popup.get_by_role(
                "button", name=ShellProcessLocators.CHOOSE_FILE_BUTTON_ROLE
            )
            choose_file.wait_for(state="visible", timeout=20000)

            # set_input_files on the same locator works when 'Choose File'
            # is a button wrapping (or labelled by) the underlying file
            # input element ΓÇö this matches the codegen recording.
            try:
                choose_file.set_input_files(resolved_path)
            except Exception:
                # Fallback: use a file chooser dialog triggered by the click.
                logger.warning(
                    "set_input_files on Choose File button failed; falling back to file chooser"
                )
                with upload_popup.expect_file_chooser(timeout=20000) as fc_info:
                    choose_file.click()
                fc_info.value.set_files(resolved_path)
            logger.info(f"Selected file for upload: {resolved_path}")

            commit_btn = upload_popup.get_by_role(
                "button", name=ShellProcessLocators.COMMIT_DOCUMENTS_BUTTON_ROLE
            )
            commit_btn.wait_for(state="visible", timeout=20000)
            try:
                commit_btn.click()
            except Exception:
                commit_btn.evaluate("el => el.click()")
            logger.info("Clicked Commit Documents")

            # Close the upload popup (codegen explicitly calls page3.close()).
            try:
                upload_popup.wait_for_event("close", timeout=10000)
            except Exception:
                if not upload_popup.is_closed():
                    try:
                        upload_popup.close()
                    except Exception:
                        pass

            # Back on parent page: auto-dismiss any dialog then click Submit.
            try:
                parent_page.bring_to_front()
            except Exception:
                pass

            parent_page.once("dialog", lambda dlg: dlg.dismiss())

            submit_btn = parent_page.get_by_role(
                "button", name=ShellProcessLocators.SUBMIT_BUTTON_ROLE
            )
            submit_btn.wait_for(state="visible", timeout=30000)
            try:
                submit_btn.click(no_wait_after=True)
            except Exception:
                submit_btn.evaluate("el => el.click()")
            logger.info("Clicked Submit on parent work item page")

            # Close the parent work item page so we return to the BAW
            # Process Portal (codegen calls page1.close()).
            try:
                parent_page.wait_for_event("close", timeout=10000)
            except Exception:
                if not parent_page.is_closed():
                    try:
                        parent_page.close()
                    except Exception:
                        pass

            # Re-target this page object at any remaining BAW page in the
            # context (typically the Process Portal) so subsequent steps
            # can find Search Work Item / Dashboard links.
            for candidate in reversed(parent_page.context.pages):
                if candidate is parent_page or candidate.is_closed():
                    continue
                try:
                    candidate.bring_to_front()
                except Exception:
                    pass
                self.page = candidate
                # Rebind ALL locators (not just nav links) so downstream
                # steps don't hit a closed-page locator from the old work item.
                self.__init__(candidate)
                logger.info(f"Switched to BAW portal page: {candidate.url}")
                break

    def _rebind_page_links(self, page: Page) -> None:
        """Rebind the page-level navigation locators after switching to a
        new active page (e.g. after closing a work item popup)."""
        self.search_work_item_baw_link = page.get_by_role(
            "link", name=ShellProcessLocators.SEARCH_WORK_ITEM_LINK_ROLE
        )
        self.dashboard_link = page.get_by_role(
            "link", name=ShellProcessLocators.DASHBOARD_LINK_ROLE
        )

    def search_and_run_check_b_number_in_dashboard(
        self,
        work_item_name: str = "Digital Check",
        work_item_filter: str = "digital",
    ) -> str:
        """Search the Search Work Item BAW page by work item type, capture
        the B# of the first matching result, then navigate to the Dashboard,
        search that B# and open the shell process page popup for it (so
        downstream steps such as ``Fetch b number from shell process page``
        operate on the correct page).

        Mirrors codegen:

            page.locator("iframe[title=\"Coach\"]").content_frame.locator(".default").click()
            ....fill("digital")
            ....get_by_text("Digital Check", exact=True).click()
            ....get_by_role("button", name="Search").click()
            ....get_by_role("cell", name="B100165682").dblclick()
            ....locator("body").press("ControlOrMeta+c")

        Args:
            work_item_name: Exact option text to select in the Work Type
                multiselect (default ``"Digital Check"``).
            work_item_filter: Substring typed into the multiselect's filter
                input to narrow options (default ``"digital"``).

        Returns:
            The B# text captured from the Search Coach iframe.
        """
        page = self.page
        with logger.step(
            f"Search Coach for '{work_item_name}' work items, copy B# and run in Dashboard",
            page=page,
        ):
            try:
                page.bring_to_front()
            except Exception:
                pass

            # 1) Open Search Work Item BAW.
            self.search_work_item_baw_link.wait_for(state="visible", timeout=30000)
            self.search_work_item_baw_link.click()
            logger.info("Clicked 'Search Work Item BAW' link")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

            coach_frame = page.locator(
                ShellProcessLocators.COACH_IFRAME_SELECTOR
            ).content_frame

            # 2) Open the Work Type multiselect, filter by the typed string
            #    and pick the exact work item name option, then click Search.
            work_type_input = coach_frame.locator(ShellProcessLocators.WORK_TYPE_INPUT)
            work_type_input.wait_for(state="visible", timeout=30000)
            work_type_input.click()
            work_type_input.fill(work_item_filter)
            logger.info(
                f"Filtered Work Type multiselect with '{work_item_filter}'"
            )

            work_type_option = (
                coach_frame.locator(
                    "#multiselect_SearchWorkItemCV1_WorkType_Select_chosen"
                ).get_by_text(work_item_name, exact=True)
            )
            work_type_option.wait_for(state="visible", timeout=15000)
            work_type_option.click()
            logger.info(f"Selected Work Type option: {work_item_name}")

            coach_frame.get_by_role(
                "button", name=ShellProcessLocators.DASHBOARD_SEARCH_BUTTON_ROLE
            ).click()
            logger.info("Clicked Coach Search button")
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

            # 3) Find the first cell whose text matches a BAW B# pattern
            #    (e.g. "B100165682"), dblclick + Ctrl+C to mirror codegen,
            #    and read the cell text for downstream use.
            b_number_cell = coach_frame.get_by_role(
                "cell", name=re.compile(r"^B\d{6,}$")
            ).first
            b_number_cell.wait_for(state="visible", timeout=60000)
            b_number_cell.dblclick()
            coach_frame.locator("body").press("ControlOrMeta+c")
            try:
                copied_b_number = (b_number_cell.inner_text() or "").strip()
            except Exception:
                copied_b_number = ""
            match = re.search(r"B\d{6,}", copied_b_number)
            if match:
                copied_b_number = match.group(0)
            logger.info(
                f"Copied Check B# from search results: '{copied_b_number}'"
            )
            if not copied_b_number:
                raise AssertionError(
                    "Could not capture a Check B# (matching pattern B\\d{6,}) "
                    "from the Search Work Item BAW Coach iframe."
                )

            # 4) Navigate to Dashboard.
            self.dashboard_link.wait_for(state="visible", timeout=30000)
            self.dashboard_link.click()
            logger.info("Clicked 'Dashboard' link")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

            # 5) Reuse existing dashboard search + Run-icon flow so the shell
            #    process page popup opens and ``self.page`` is re-targeted at
            #    it for subsequent steps.
            self._navigate_to_shell_via_dashboard(copied_b_number)

            # Rebind ALL locators against the new shell popup page so
            # downstream steps (fetch_b_number, create digital record, ...)
            # don't hit a closed-page locator inherited from __init__.
            try:
                if self.page and not self.page.is_closed():
                    self.__init__(self.page)
            except Exception as rebind_exc:
                logger.warning(f"Failed to rebind locators on shell popup: {rebind_exc}")

            return copied_b_number
            
    def fetch_b_number(self) -> str:
        """Fetch B number from Shell Process page."""
        with logger.step("Fetch B number from Shell Process page", page=self.page):
            # Wait for page navigation to settle before looking for B#
            for state in ("domcontentloaded", "load"):
                try:
                    self.page.wait_for_load_state(state, timeout=90000)
                except Exception as e:
                    logger.warning(f"wait_for_load_state('{state}') timed out: {e}")
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass
            self.wait_for_loading_data()
            self.b_number.wait_for(state="visible", timeout=120000)

            for attempt in range(1, 6):
                b_num = self.get_text(self.b_number, timeout=30000).strip()
                if b_num:
                    logger.info(f"Fetched B number: {b_num}")
                    return b_num
                if attempt < 5:
                    self.wait_for_timeout(2000)

            raise AssertionError("Could not fetch B number after 5 attempts (text was empty)")

    def enter_hrc(self, hrc_number: str) -> None:
        """
        Enter HRC number in the HRC textbox.
        Mirrors Java implementation with additional render-safe checks.

        Args:
            hrc_number: The HRC number to enter (7-digit string)
        """
        self.fill(self.hrc_textbox, hrc_number, timeout=20000)
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
                    logger.warning("BAW page crashed after HRC submit ΓÇö recovering")
                    new_page = self.page.context.new_page()
                    new_page.goto(baw_url, wait_until="load", timeout=30000)
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
                    self.wait_and_click(self.select_account_button, timeout=30000)
                    logger.info("Click on select button under account number association")
                    select_clicked = True
                    break
                except Exception as click_error:
                    logger.warning(f"Select button attempt {attempt} failed: {click_error}")

            if not select_clicked:
                raise TimeoutError("Select button was not clickable after 3 attempts")
        elif action == "remove":
            self.click(self.remove_association_button, timeout=20000)
            logger.info("Click on remove button under account number association")
            self.wait_for_loading_data()
        else:
            self.click(self.add_account_association_button, timeout=20000)
            logger.info("Click on add button under account number association")
            self.wait_for_loading_data()

    def click_save_shell_process_button(self) -> None:
        """Click Save Shell Process button ΓÇö waits until visible then clicks."""
        try:
            self.wait_and_click(self.save_shell_process_button, timeout=60000)
            logger.info("Save shell process button clicked successfully")
        except Exception as e:
            logger.warning(f"Save button not found or click failed: {e}. Continuing to next step...")


    def click_save_exit_button(self) -> Optional[Page]:
        """Click Save & Exit ΓÇö closes Shell Process tab and switches back to NAA Coach."""
        with logger.step("Click on save exit button", page=self.page):
            # Find the NAA Coach page before this tab closes.
            naa_coach_page = None
            for p in self.page.context.pages:
                if p is self.page:
                    continue
                try:
                    title = (p.title() or "").lower()
                except Exception:
                    title = ""
                if "naa coach" in title:
                    naa_coach_page = p 
                    break

            self.save_exit_button.wait_for(state="visible", timeout=30000)
            self.save_exit_button.scroll_into_view_if_needed()
            
            # Click Save & Exit button ΓÇö no_wait_after avoids 30s navigation timeout
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

        # Switch back to NAA Coach.
        if naa_coach_page is None:
            for p in self.page.context.pages:
                try:
                    title = (p.title() or "").lower()
                except Exception:
                    continue
                if "naa coach" in title:
                    naa_coach_page = p
                    break

        if naa_coach_page:
            try:
                naa_coach_page.bring_to_front()
                logger.info("Switched back to NAA Coach page")
                return naa_coach_page
            except Exception as e:
                logger.warning(f"NAA Coach page crashed or closed: {e}")
                naa_coach_page = None

        # Fallback: find any live page (prefer NAA Coach by title)
        for p in self.page.context.pages:
            try:
                title = (p.title() or "").lower()
                if "naa coach" in title:
                    p.bring_to_front()
                    logger.info("Recovered NAA Coach page from context")
                    return p
            except Exception:
                continue

        remaining = self.page.context.pages
        if remaining:
            try:
                remaining[-1].bring_to_front()
            except Exception:
                pass
            return remaining[-1]
        return None

    def validate_added_account_in_account_number_association(self) -> Dict[str, str]:
        """Validate and return added account number/name in account number association section."""
        with logger.step("Validate added account number and account name", page=self.page):
            self.page.wait_for_load_state("load", timeout=30000)
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

    def enter_custodial_account_value(self, account: str):
        """Enter the custodial account number."""
        self.fill(self.custodial_account, account)
        self.tab_out() 
        logger.info(f"Enter the custodial account number: {account}")

    def select_account_row_in_results(self, account: str) -> None:
        """Click the row in account search results that matches the given
        custodial account number, to enable the Individual Owner dropdown.
        """
        with logger.step(f"Select account row in results: {account}", page=self.page):
            # Prefer clicking the row (matches codegen behaviour of selecting
            # an entire result row to enable the Individual Owner dropdown).
            row = self.page.get_by_role("row").filter(has_text=account).first
            try:
                row.wait_for(state="visible", timeout=15000)
                row.click()
            except Exception:
                # Fallback: click cell containing the account number
                cell = self.page.get_by_role("cell", name=account, exact=True).first
                cell.wait_for(state="visible", timeout=10000)
                cell.click()
            # Wait for the Individual Owner dropdown to become enabled
            try:
                self.individual_owner.wait_for(state="visible", timeout=10000)
                self.page.wait_for_function(
                    "() => { const el = document.querySelector('select#ComboBox1');"
                    " return el && !el.disabled; }",
                    timeout=15000,
                )
            except Exception:
                logger.warning("Individual Owner dropdown did not become enabled after row click")
            logger.info(f"Selected account row: {account}")

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
        transfer_page.wait_for_load_state("load", timeout=30000)
        transfer_page.bring_to_front()
        logger.info(f"Switched to TransferAttributes tab: {transfer_page.url}")
        return TransferAttributesPage(transfer_page)

    def validate_notes_history(self, expected_text: str = "") -> str:
        # Switch to Shell Process page and wait for BAW loading spinner
        # (Transfer Attributes Save & Close triggers a refresh on Shell Process page)
        self.page.bring_to_front()
        self.baw_spinner_loader(appear_timeout=15000, disappear_timeout=60000)
        # Wait for any BAW-triggered auto-reload on the shell process page to
        # finish before we explicitly reload; otherwise the page object may be
        # in a transitional ("not attached") state and reload() will throw.
        try:
            self.page.wait_for_load_state("load", timeout=20000)
        except Exception:
            self.wait_for_timeout(3000)
        # Reload to ensure the latest notes are visible after Save & Close
        try:
            self.page.reload(timeout=30000)
        except Exception:
            self.wait_for_timeout(5000)
            self.page.reload(timeout=30000)
        self.baw_spinner_loader(appear_timeout=5000, disappear_timeout=30000)
        # Click Save & Refresh to persist changes and reload notes
        self.save_refresh_button.wait_for(state="visible", timeout=10000)
        self.click(self.save_refresh_button)
        logger.info("Clicked Save & Refresh button")
        self.baw_spinner_loader(appear_timeout=10000, disappear_timeout=60000)
    
        if expected_text:
            notes_content = self.get_text(self.notes_table, timeout=10000)
            logger.info(f"Notes history content: '{notes_content}'")
            Assertions.assert_true(expected_text in notes_content, f"Notes history does not contain expected text: '{expected_text}'")
            logger.info(f"Validated notes history contains expected text: '{expected_text}'")

        return self.get_text(self.notes_table, timeout=10000).strip()
    
    def update_internal_status(self, value: str):
        # Wait for the shell process page to finish loading after Run Now navigation
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=60000)
        except Exception:
            pass
        self.wait_for_loading_data()
        self.select_option(self.internal_status, value, timeout=30000)
        logger.info(f"Internal status has been updated to: {value}")

    def fetch_custodian_account(self) -> str:        
        return self.get_text(self.custodian_acc, timeout=10000).strip()
    
    def clickAddUpdateButton(self):        
        self.accept_alert()
        self.click(self.add_update_button, timeout=20000)
        self.wait_for_timeout(5000)
        logger.info("Clicked on Update OA button and accepted alert")

    # ------------------------------------------------------------------
    # Digital Check work item (C95661)
    # ------------------------------------------------------------------
    def click_create_digital_record_and_add_check_details(self) -> Page:
        """Click 'Create New Digital Record', then 'Add/Update Check details'
        and return the popup page that opens for the Check Details coach."""
        with logger.step("Click Create New Digital Record and Add/Update Check details", page=self.page):
            self.wait_for_loading_data()
            self.create_new_digital_record_button.wait_for(state="visible", timeout=30000)
            try:
                self.create_new_digital_record_button.click()
            except Exception:
                logger.warning("Create New Digital Record normal click failed, trying JS click")
                self.create_new_digital_record_button.evaluate("el => el.click()")
            logger.info("Clicked Create New Digital Record")

            self.wait_for_loading_data()
            self.add_update_check_details_button.wait_for(state="visible", timeout=30000)

            with self.page.expect_popup(timeout=30000) as popup_info:
                try:
                    self.add_update_check_details_button.click()
                except Exception:
                    logger.warning("Add/Update Check details normal click failed, trying JS click")
                    self.add_update_check_details_button.evaluate("el => el.click()")

            popup_page = popup_info.value
            try:
                popup_page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"Popup domcontentloaded wait failed: {e}")
            logger.info("Add/Update Check Details popup opened")
            return popup_page

    def click_create_new_digital_record_only(self) -> None:
        """C95666: Click ONLY the 'Create New Digital Record' button on the
        shell process page. Does NOT click 'Add/Update Check details' so the
        Check Coach popup is not opened (AFV validation runs on the shell
        page next).
        """
        with logger.step("Click Create New Digital Record (only)", page=self.page):
            self.wait_for_loading_data()
            self.create_new_digital_record_button.wait_for(state="visible", timeout=30000)
            try:
                self.create_new_digital_record_button.click()
            except Exception:
                logger.warning("Create New Digital Record normal click failed, trying JS click")
                self.create_new_digital_record_button.evaluate("el => el.click()")
            logger.info("Clicked Create New Digital Record")
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # C95666 - Account Funding Validation (AFV) section validation
    # ------------------------------------------------------------------
    def validate_account_funding_validation_section(self) -> None:
        """Validate the Account Funding Validation section on the shell page.

        Validations performed (C95666):
          1. Click the AFV section twisty to collapse → assert the
             category text 'Account and/or Client Notes' becomes hidden.
          2. Click the twisty again to re-expand → assert the category
             text becomes visible again.
          3. Click each category ('Account and/or Client Notes',
             'Status of Account') and assert the combined Category
             Results cell is visible.

        Raises:
            AssertionError: if any of the soft assertions fail.
        """
        with logger.step(
            "Validate Account Funding Validation section (expand/collapse + categories)",
            page=self.page,
        ):
            self.wait_for_loading_data()
            self.afv_section_twisty.wait_for(state="visible", timeout=30000)

            with SoftAssertions() as soft:
                # 1) Collapse the section and assert content hidden
                self.afv_section_twisty.click()
                logger.info("Clicked AFV twisty (collapse)")
                try:
                    self.afv_category_account_notes.first.wait_for(
                        state="hidden", timeout=10000
                    )
                except Exception as collapse_wait_exc:
                    logger.warning(
                        f"AFV category did not become hidden after collapse: {collapse_wait_exc}"
                    )
                soft.assert_hidden(
                    self.afv_category_account_notes.first,
                    "AFV section did not collapse - 'Account and/or Client Notes' still visible",
                )

                # 2) Expand the section and assert content visible
                self.afv_section_twisty.click()
                logger.info("Clicked AFV twisty (expand)")
                try:
                    self.afv_category_account_notes.first.wait_for(
                        state="visible", timeout=10000
                    )
                except Exception as expand_wait_exc:
                    logger.warning(
                        f"AFV category did not become visible after expand: {expand_wait_exc}"
                    )
                soft.assert_visible(
                    self.afv_category_account_notes.first,
                    "AFV section did not expand - 'Account and/or Client Notes' not visible",
                )

                # 3) Click each category and assert results cell visible
                self.afv_category_account_notes.first.click()
                logger.info("Clicked AFV category: Account and/or Client Notes")
                self.afv_category_status_of_account.first.click()
                logger.info("Clicked AFV category: Status of Account")

                self.afv_results_cell.click()
                soft.assert_visible(
                    self.afv_results_cell,
                    "AFV Category Results cell not visible after clicking categories",
                )
                logger.info("Validated AFV Category Results cell is visible")

    def fill_check_details_and_save_close(
        self,
        popup_page: Page,
        check_type: str = "A_PersonalCheck",
        alpha_amount: str = "123",
        numerical_amount: str = "123",
        check_date_day: str = "20",
        check_number: str = "4535634634",
        aba_routing: str = "011001755",
        duplicate_option: str = "Original",
        bank_account_number: str = "",
    ) -> None:
        """Fill all required Check Detail fields inside the Coach iframe and click Save & Close."""
        with logger.step("Fill check details and click Save & Close", page=popup_page):
            frame = popup_page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR)

            frame.get_by_label("Check Type").select_option(check_type)
            logger.info(f"Selected Check Type: {check_type}")

            frame.get_by_role("textbox", name="Alpha Amount").fill(alpha_amount)
            frame.get_by_role("textbox", name="Numerical Amount").fill(numerical_amount)
            logger.info(f"Entered amounts alpha={alpha_amount} numerical={numerical_amount}")

            # Fill Check Date directly using today's month/year and the given day.
            from datetime import date as _date
            today = _date.today()
            try:
                day_int = int(check_date_day)
            except (TypeError, ValueError):
                day_int = today.day
            check_date_str = f"{today.month:02d}/{day_int:02d}/{today.year}"
            check_date_box = frame.get_by_role("textbox", name="Check Date")
            check_date_box.click(force=True)
            check_date_box.fill(check_date_str)
            popup_page.keyboard.press("Tab")
            logger.info(f"Entered Check Date: {check_date_str}")

            frame.get_by_role("textbox", name="Check Number").fill(check_number)
            frame.get_by_role("textbox", name="ABA Routing Number").fill(aba_routing)
            logger.info(f"Entered check number {check_number} and ABA {aba_routing}")

            # Bank Account Number ΓÇö required for Save & Close to succeed.
            if bank_account_number:
                bank_acct = frame.locator(
                    "#text-input-CheckAttributesCV1\\:BankAccountNumber"
                )
                bank_acct.wait_for(state="visible", timeout=15000)
                bank_acct.fill(bank_account_number)
                logger.info(f"Entered Bank Account Number: {bank_account_number}")
            else:
                logger.warning(
                    "Bank Account Number not provided; skipping fill. "
                    "Save & Close may fail validation."
                )

            # Duplicate / Replacement radio group ΓÇö select by input value if not already checked
            try:
                radio = frame.locator(ShellProcessLocators.DUPLICATE_OPTION_RADIO_TPL.format(duplicate_option=duplicate_option))
                if radio.count() > 0 and not radio.first.is_checked():
                    radio.first.check(force=True)
                    logger.info(f"Selected duplicate option: {duplicate_option}")
                else:
                    logger.info(f"Duplicate option '{duplicate_option}' already selected")
            except Exception as e:
                logger.warning(f"Could not select duplicate option '{duplicate_option}': {e}")

            save_close_btn = frame.locator(
                "#button-button-CheckAttributesCV1\\:SaveAndCloseButton"
            )
            save_close_btn.wait_for(state="visible", timeout=15000)
            try:
                save_close_btn.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            # Small settle so any field blur validation completes before click.
            popup_page.wait_for_timeout(500)

            # Click Save & Close repeatedly until the popup closes (i.e. shell page
            # has taken over). BAW occasionally swallows the first click while a
            # background validation is in flight.
            max_attempts = 10
            for attempt in range(1, max_attempts + 1):
                if popup_page.is_closed():
                    break
                try:
                    save_close_btn.click()
                    logger.info(
                        f"Clicked Save & Close on Check Details popup (attempt {attempt})"
                    )
                except Exception as e:
                    logger.warning(f"Save & Close click attempt {attempt} failed: {e}")
                    try:
                        save_close_btn.click(force=True)
                        logger.info(
                            f"Force-clicked Save & Close (attempt {attempt})"
                        )
                    except Exception as ee:
                        logger.warning(f"Force click attempt {attempt} failed: {ee}")

                try:
                    popup_page.wait_for_event("close", timeout=5000)
                    break
                except Exception:
                    if popup_page.is_closed():
                        break
                    logger.warning(
                        f"Popup still open after attempt {attempt}; retrying Save & Close."
                    )

            if not popup_page.is_closed():
                logger.warning(
                    "Popup still open after Save & Close retries; "
                    "downstream validation will likely fail."
                )

            # After Save & Close, the shell page's Check Details section should
            # display the newly created record with Status = 'Received'.
            self._validate_check_status_on_shell(expected_status="Received")

    def _validate_check_status_on_shell(self, expected_status: str = "Received") -> None:
        """Read the 'Check Status' field in the Check Details section on the
        shell page and assert it equals ``expected_status``."""
        try:
            self.page.bring_to_front()
        except Exception:
            pass

        # After Save & Close the shell page navigates to the next coach view.
        # Wait for that navigation/load to settle before searching. The popup
        # close can briefly detach frames, so we also wait for the shell page
        # body to be stable and call wait_for_loading_data before probing.
        for state in ("domcontentloaded", "load", "networkidle"):
            try:
                self.page.wait_for_load_state(state, timeout=30000)
            except Exception:
                pass
        try:
            self.wait_for_loading_data()
        except Exception:
            pass
        try:
            self.page.wait_for_selector("body", state="visible", timeout=15000)
        except Exception:
            pass
        # Small settle delay so the new coach view finishes attaching #checkStatus.
        self.page.wait_for_timeout(2000)

        # The Check Status field (#checkStatus, label id=checkStatus_Label) lives
        # on the shell process page after Save & Close. The shell page itself IS
        # the coach view (URL is coach.lsw / fauxRedirect.lsw), so the field is
        # typically at page level ΓÇö but in some BAW configurations it may be
        # nested inside an iframe. Try page-level first, then known iframes.
        status_locator = None
        last_error: Exception | None = None
        # Retry the whole probe a few times ΓÇö right after Save & Close the
        # frame tree can be transiently detached while the new coach renders.
        for probe_attempt in range(1, 6):
            candidates = [
                ("page", self.page.locator(ShellProcessLocators.CHECK_STATUS)),
                (
                    ShellProcessLocators.COACH_IFRAME_SELECTOR,
                    self.page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR).locator(
                        ShellProcessLocators.CHECK_STATUS
                    ),
                ),
            ]
            try:
                for fr in self.page.frames:
                    if fr is self.page.main_frame:
                        continue
                    candidates.append(
                        (f"frame:{fr.name or fr.url[:40]}", fr.locator(ShellProcessLocators.CHECK_STATUS))
                    )
            except Exception:
                pass

            for label, loc in candidates:
                try:
                    loc.wait_for(state="visible", timeout=15000)
                    logger.info(
                        f"Located #checkStatus via {label} (attempt {probe_attempt})"
                    )
                    status_locator = loc
                    break
                except Exception as exc:
                    last_error = exc
                    logger.info(
                        f"#checkStatus not found via {label} "
                        f"(attempt {probe_attempt}); trying next."
                    )

            if status_locator is not None:
                break

            # Wait for the page to settle again before retrying.
            logger.info(
                f"#checkStatus probe attempt {probe_attempt} did not find the "
                "field; waiting for page to settle before retry."
            )
            for state in ("domcontentloaded", "load", "networkidle"):
                try:
                    self.page.wait_for_load_state(state, timeout=15000)
                except Exception:
                    pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            self.page.wait_for_timeout(2000)

        if status_locator is None:
            raise AssertionError(
                "Check Details 'Check Status' field (#checkStatus) not found "
                f"on shell page after Save & Close: {last_error}"
            )

        # Read the value ΓÇö input_value() for inputs, text content for span/div.
        actual_status = ""
        try:
            actual_status = (status_locator.input_value() or "").strip()
        except Exception:
            pass
        if not actual_status:
            try:
                actual_status = (status_locator.text_content() or "").strip()
            except Exception:
                pass

        logger.info(
            f"Check Details Status on shell page: '{actual_status}' "
            f"(expected: '{expected_status}')"
        )
        assert actual_status == expected_status, (
            f"Check Status mismatch on shell page. "
            f"Expected '{expected_status}', got '{actual_status}'"
        )
        logger.info(
            f"Validated Check Status = '{expected_status}' on shell page",
            attach_to_allure=True,
        )

    def associate_check_with_transfer(self, check_b_number: str) -> None:
        """In the Transfer section on the shell page (Coach iframe), click the
        'Associate Check' button, enter the previously fetched Check work item
        B#, select the 'All funds expected were received' radio, and click
        Submit. Asserts visibility of each control before interacting.

        Args:
            check_b_number: The B# of the Digital Check work item created
                earlier in the scenario (must be non-empty).
        """
        if not check_b_number or not str(check_b_number).strip():
            raise ValueError("check_b_number is required and cannot be empty")
        check_b_number = str(check_b_number).strip()

        with logger.step(
            f"Associate Check {check_b_number} with transfer", page=self.page
        ):
            try:
                self.page.bring_to_front()
            except Exception:
                pass

            # The transfer coach's Save & Close triggers a navigation/reload of
            # the shell page. We MUST wait until the shell page is fully
            # loaded before clicking Associate Check ΓÇö clicking too early
            # leaves the popup's inputs unbound and any subsequent fill is
            # silently discarded. Do NOT reload manually (it races with the
            # in-flight post-save navigation).
            #
            # Strong full-load gate (sequential):
            #   1. Wait for navigation states: domcontentloaded -> load ->
            #      networkidle (90s each).
            #   2. Wait for BAW loading-data spinner to disappear.
            #   3. URL-stability poll ΓÇö URL must remain unchanged for 3
            #      consecutive 1-second checks (i.e. all post-save redirects
            #      have completed).
            #   4. Wait for the Associate Check button to be VISIBLE (120s).
            #   5. Wait for the Associate Check button to be ENABLED.
            #   6. Re-run spinner check + 3s extra settle for Coach JS.
            for state in ("domcontentloaded", "load", "networkidle"):
                try:
                    self.page.wait_for_load_state(state, timeout=90000)
                except Exception as exc:
                    logger.info(f"wait_for_load_state('{state}') skipped: {exc}")
            try:
                self.wait_for_loading_data()
            except Exception as exc:
                logger.info(f"wait_for_loading_data skipped: {exc}")

            # URL-stability poll: keep sampling the URL until it has been
            # unchanged for 3 consecutive samples (1s gap), or 30 samples max.
            stable_url = ""
            stable_streak = 0
            for sample in range(1, 31):
                try:
                    current_url = self.page.url
                except Exception:
                    current_url = ""
                if current_url and current_url == stable_url:
                    stable_streak += 1
                    if stable_streak >= 3:
                        logger.info(
                            f"Shell URL stable after {sample} sample(s): {current_url}"
                        )
                        break
                else:
                    stable_url = current_url
                    stable_streak = 1
                self.page.wait_for_timeout(1000)
            else:
                logger.warning(
                    f"Shell URL not stable after 30s; last url={stable_url}"
                )

            # Re-run load-state + spinner waits after the URL settled (the
            # final redirect may have triggered fresh XHRs).
            for state in ("domcontentloaded", "load", "networkidle"):
                try:
                    self.page.wait_for_load_state(state, timeout=60000)
                except Exception:
                    pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            logger.info("Shell page load states settled; waiting for Associate Check button")

            coach = self.page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR)

            # Locate Associate Check button (page level first, then Coach iframe).
            associate_check_locators = [
                ("page", self.page.locator(ShellProcessLocators.ASSOCIATE_CHECK_BUTTON)),
                (ShellProcessLocators.COACH_IFRAME_SELECTOR, coach.locator(ShellProcessLocators.ASSOCIATE_CHECK_BUTTON)),
            ]
            associate_check_btn = None
            for label, loc in associate_check_locators:
                try:
                    loc.wait_for(state="visible", timeout=120000)
                    logger.info(f"Located 'Associate Check' button via {label}")
                    associate_check_btn = loc
                    break
                except Exception:
                    continue
            if associate_check_btn is None:
                raise AssertionError(
                    "'Associate Check' button (#ButtonGroup27_AssociateCheck) "
                    "is not visible at page level or in iframe[title='Coach']"
                )

            # Final readiness gate: button must be ENABLED (Coach JS bound).
            for poll in range(1, 61):
                try:
                    if associate_check_btn.is_enabled():
                        logger.info(
                            f"Associate Check button enabled after {poll} poll(s); shell fully loaded"
                        )
                        break
                except Exception:
                    pass
                self.page.wait_for_timeout(500)
            else:
                logger.warning(
                    "Associate Check button never reported enabled within 30s; proceeding anyway"
                )

            # Final spinner re-check and a longer settle so Coach JS finishes
            # binding popup handlers before we click.
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            self.page.wait_for_timeout(3000)

            Assertions.assert_true(
                associate_check_btn.is_visible(),
                "'Associate Check' button is not visible in transfer section",
            )
            associate_check_btn.click()
            logger.info("Clicked 'Associate Check' button in transfer section")

            # Wait for the Associate Check popup form to render before
            # locating its inputs.
            self.page.wait_for_timeout(1000)

            # 2) Fill the Work Item Number (B#) textbox with the check B#.
            b_number_locators = [
                ("page #checkWIBnumber", self.page.locator(ShellProcessLocators.CHECK_WI_B_NUMBER)),
                ("iframe #checkWIBnumber", coach.locator(ShellProcessLocators.CHECK_WI_B_NUMBER)),
                ("page get_by_role", self.page.get_by_role("textbox", name="Work Item Number (B#)")),
                ("iframe get_by_role", coach.get_by_role("textbox", name="Work Item Number (B#)")),
            ]
            b_number_input = None
            for label, loc in b_number_locators:
                try:
                    loc.wait_for(state="visible", timeout=20000)
                    logger.info(f"Located B# input via {label}")
                    b_number_input = loc
                    break
                except Exception:
                    continue
            if b_number_input is None:
                raise AssertionError(
                    "'Work Item Number (B#)' textbox is not visible (page or Coach iframe)"
                )
            Assertions.assert_true(
                b_number_input.is_visible(),
                "'Work Item Number (B#)' textbox is not visible",
            )
            # BAW Coach inputs sometimes drop a single `fill()` if they are
            # bound to a JS controller that re-renders on focus. Use a
            # focus+clear+type pattern with retries, and tab out so BAW
            # commits the value.
            final_val = ""
            for attempt in range(1, 4):
                try:
                    b_number_input.click()
                except Exception:
                    pass
                try:
                    b_number_input.fill("")
                except Exception:
                    pass
                try:
                    b_number_input.fill(check_b_number)
                except Exception:
                    # Fallback: type keystrokes.
                    try:
                        b_number_input.press_sequentially(check_b_number, delay=30)
                    except Exception:
                        pass
                try:
                    self.page.keyboard.press("Tab")
                except Exception:
                    pass
                final_val = (b_number_input.input_value() or "").strip()
                if final_val == check_b_number:
                    break
                logger.warning(
                    f"B# fill attempt {attempt}: got '{final_val}', "
                    f"expected '{check_b_number}'; retrying"
                )
            Assertions.assert_equal(
                final_val,
                check_b_number,
                "'Work Item Number (B#)' value did not match after fill",
            )
            logger.info(f"Entered Check work item B#: {check_b_number}")

            # 3) Select the "All funds expected were received" radio.
            all_funds_locators = [
                ("page get_by_role", self.page.get_by_role("radio", name="All funds expected were")),
                ("iframe get_by_role", coach.get_by_role("radio", name="All funds expected were")),
            ]
            all_funds_radio = None
            for label, loc in all_funds_locators:
                try:
                    loc.wait_for(state="visible", timeout=15000)
                    logger.info(f"Located 'All funds expected' radio via {label}")
                    all_funds_radio = loc
                    break
                except Exception:
                    continue
            if all_funds_radio is None:
                raise AssertionError(
                    "'All funds expected were received' radio is not visible (page or Coach iframe)"
                )
            Assertions.assert_true(
                all_funds_radio.is_visible(),
                "'All funds expected were received' radio is not visible",
            )
            all_funds_radio.check()
            Assertions.assert_true(
                all_funds_radio.is_checked(),
                "'All funds expected were received' radio is not checked after click",
            )
            logger.info("Selected 'All funds expected were received' radio option")

            # 4) Click the Submit button.
            submit_locators = [
                ("page", self.page.locator(ShellProcessLocators.ASSOCIATE_CHECK_SUBMIT_BUTTON)),
                (ShellProcessLocators.COACH_IFRAME_SELECTOR, coach.locator(ShellProcessLocators.ASSOCIATE_CHECK_SUBMIT_BUTTON)),
            ]
            submit_btn = None
            for label, loc in submit_locators:
                try:
                    loc.wait_for(state="visible", timeout=15000)
                    logger.info(f"Located Associate Check Submit via {label}")
                    submit_btn = loc
                    break
                except Exception:
                    continue
            if submit_btn is None:
                raise AssertionError(
                    "'Associate Check Submit' button is not visible (page or Coach iframe)"
                )
            Assertions.assert_true(
                submit_btn.is_visible(),
                "'Associate Check Submit' button is not visible",
            )

            # Behaviour requested:
            #   * Click Submit rapidly until the Associate Check box closes
            #     (Submit button no longer visible) or max attempts reached.
            #   * If a confirm() dialog appears, auto-accept (OK); if no
            #     dialog appears, just proceed.
            dialog_accepted = {"count": 0}

            def _accept_dialog(dlg) -> None:
                dialog_accepted["count"] += 1
                logger.info(
                    f"Associate Check Submit dialog #{dialog_accepted['count']} "
                    f"appeared: '{dlg.message}' ΓÇö accepting"
                )
                try:
                    dlg.accept()
                except Exception as dlg_exc:
                    logger.warning(
                        f"Dialog accept failed: {str(dlg_exc).splitlines()[0]}"
                    )

            self.page.on("dialog", _accept_dialog)
            try:
                try:
                    submit_btn.scroll_into_view_if_needed()
                except Exception:
                    pass
                try:
                    submit_btn.focus()
                except Exception:
                    pass

                max_attempts = 5
                click_gap_ms = 30000  # wait 30s after each click; loop will exit early if box closes
                box_closed = False
                for attempt in range(1, max_attempts + 1):
                    # Stop as soon as the Associate Check box is gone
                    # (Submit button no longer visible means BAW accepted
                    # the submission and tore the form down).
                    try:
                        if not submit_btn.is_visible():
                            box_closed = True
                            logger.info(
                                f"Associate Check box closed after {attempt - 1} click(s)"
                            )
                            break
                    except Exception:
                        # If the locator is detached entirely, treat as closed.
                        box_closed = True
                        logger.info(
                            f"Associate Check box detached after {attempt - 1} click(s)"
                        )
                        break

                    # Click rapidly. Prefer real click; JS click as fallback.
                    try:
                        submit_btn.click(
                            force=True, timeout=2000, no_wait_after=True
                        )
                    except Exception as click_exc:
                        logger.info(
                            f"Submit click {attempt} (real) skipped: "
                            f"{str(click_exc).splitlines()[0]}"
                        )
                        try:
                            submit_btn.evaluate("el => el.click()")
                        except Exception as js_exc:
                            logger.info(
                                f"Submit click {attempt} (JS) skipped: "
                                f"{str(js_exc).splitlines()[0]}"
                            )

                    self.page.wait_for_timeout(click_gap_ms)

                if not box_closed:
                    logger.warning(
                        f"Associate Check box still visible after "
                        f"{max_attempts} Submit click(s); continuing anyway"
                    )
                logger.info(
                    f"Associate Check Submit: dialogs accepted="
                    f"{dialog_accepted['count']}, box_closed={box_closed}"
                )
            finally:
                try:
                    self.page.remove_listener("dialog", _accept_dialog)
                except Exception:
                    pass

            # After the box closes, BAW POSTs and reloads the shell. Wait for
            # that navigation to settle so the notes section is rendered for
            # the next verify step.
            for state in ("domcontentloaded", "load", "networkidle"):
                try:
                    self.page.wait_for_load_state(state, timeout=60000)
                except Exception:
                    pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            logger.info(
                f"Associated Check work item {check_b_number} with transfer",
                attach_to_allure=True,
            )

    def verify_associate_check_note(self, expected_text: str = "Associate Check") -> str:
        """Read the latest note from the notes section
        (//*[@id='CustomHTML11_0']/pre) and assert it contains `expected_text`.

        Note: this method does NOT click 'Save & Refresh'. The Associate Check
        Submit click already saves & refreshes the shell, so the latest note
        is rendered on return. We just wait for the note element and poll its
        text until the expected substring appears.

        Args:
            expected_text: Substring expected in the rendered note. Defaults
                to 'Associate Check'.

        Returns:
            The trimmed note text read from the notes element.
        """
        with logger.step("Verify added note for Associate Check", page=self.page):
            try:
                self.page.bring_to_front()
            except Exception:
                pass

            # Give the shell a moment to settle after the Associate Check Submit
            # navigation/reload before reading the notes section.
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            for state in ("domcontentloaded", "load", "networkidle"):
                try:
                    self.page.wait_for_load_state(state, timeout=30000)
                except Exception:
                    pass

            coach = self.page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR)

            # Locate the latest note element (//*[@id='CustomHTML11_0']/pre).
            note_locators = [
                ("page #CustomHTML11_0 pre", self.page.locator(ShellProcessLocators.CUSTOM_HTML_RESULT_PRE)),
                ("iframe #CustomHTML11_0 pre", coach.locator(ShellProcessLocators.CUSTOM_HTML_RESULT_PRE)),
            ]
            note_loc = None
            for label, loc in note_locators:
                try:
                    loc.first.wait_for(state="visible", timeout=30000)
                    logger.info(f"Located Associate Check note via {label}")
                    note_loc = loc.first
                    break
                except Exception:
                    continue
            if note_loc is None:
                raise AssertionError(
                    "Associate Check note element (//*[@id='CustomHTML11_0']/pre) "
                    "is not visible at page level or in iframe[title='Coach']"
                )

            # Poll the note text until the expected substring appears.
            note_text = ""
            poll_attempts = 30  # ~60s total at 2s interval
            for poll_idx in range(1, poll_attempts + 1):
                try:
                    note_text = (note_loc.inner_text() or "").strip()
                except Exception:
                    note_text = ""
                if note_text and expected_text.lower() in note_text.lower():
                    logger.info(
                        f"Associate Check note matched expected text on poll {poll_idx}: '{note_text}'",
                        attach_to_allure=True,
                    )
                    break
                logger.info(
                    f"Poll {poll_idx}/{poll_attempts}: note text='{note_text}' "
                    f"(expected to contain '{expected_text}') ΓÇö waiting"
                )
                self.page.wait_for_timeout(2000)
                try:
                    note_loc.wait_for(state="visible", timeout=5000)
                except Exception:
                    pass

            logger.info(
                f"Final Associate Check note text: '{note_text}'",
                attach_to_allure=True,
            )
            Assertions.assert_true(
                bool(note_text),
                "Associate Check note (//*[@id='CustomHTML11_0']/pre) is empty",
            )
            Assertions.assert_true(
                expected_text.lower() in note_text.lower(),
                f"Expected text '{expected_text}' not found in Associate Check note. "
                f"Actual note text: '{note_text}'",
            )
            return note_text

    def click_save_refresh(self) -> None:
        """Click the 'Save & Refresh' button on the shell process page.
        Used after Save & Close on the Transfer Attributes coach so the shell
        re-renders with the latest transfer state.
        """
        with logger.step("Click Save & Refresh on shell page", page=self.page):
            try:
                self.page.bring_to_front()
            except Exception:
                pass
            for state in ("domcontentloaded", "load", "networkidle"):
                try:
                    self.page.wait_for_load_state(state, timeout=30000)
                except Exception as exc:
                    logger.info(f"wait_for_load_state('{state}') skipped: {exc}")
            try:
                self.wait_for_loading_data()
            except Exception as exc:
                logger.info(f"wait_for_loading_data skipped: {exc}")

            candidates = [
                ("page get_by_role", self.page.get_by_role("button", name="Save & Refresh")),
                (
                    "iframe[title='Coach'] get_by_role",
                    self.page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR).get_by_role(
                        "button", name="Save & Refresh"
                    ),
                ),
            ]
            btn = None
            for label, loc in candidates:
                try:
                    loc.wait_for(state="visible", timeout=15000)
                    logger.info(f"Located 'Save & Refresh' via {label}")
                    btn = loc
                    break
                except Exception:
                    continue
            if btn is None:
                raise AssertionError("'Save & Refresh' button is not visible on shell page")
            Assertions.assert_true(btn.is_visible(), "'Save & Refresh' button is not visible")
            btn.click()
            logger.info("Clicked 'Save & Refresh' on shell page", attach_to_allure=True)
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Advisor Notification verification
    # ------------------------------------------------------------------
    #: (label, element-id) pairs for the Advisor Notification items.
    #: IDs come from the shell page (e.g. //*[@id='pnlHdr-lbl-21']).
    ADVISOR_NOTIFICATION_ITEMS: tuple[tuple[str, str], ...] = (
        ("Receipt and Completion - New Accounts", "pnlHdr-lbl-21"),
        ("Receipt and Completion - Money In", "pnlHdr-lbl-31"),
        ("Receipt and Completion - Standing Instructions", "pnlHdr-lbl-41"),
        ("Receipt and Completion - Investment Changes and Journals", "pnlHdr-lbl-51"),
        ("Receipt and Completion - Withdrawals and Bank Maintenance", "pnlHdr-lbl-61"),
        ("Receipt and Completion - Terminations and Transfer Out", "pnlHdr-lbl-81"),
    )

    def verify_advisor_notification_items(
        self,
        expected_items: tuple[tuple[str, str], ...] | None = None,
    ) -> list[str]:
        """Click the 'View Notification Preferences' link on the current shell
        page and assert each Advisor Notification item is visible on the
        Advisor Preferences view.

        Each item is located by its element ``id`` (e.g. ``pnlHdr-lbl-21`` ΓåÆ
        XPath ``//*[@id='pnlHdr-lbl-21']``). The element is searched on the
        top-level page first and then in every child frame, so it works
        regardless of iframe nesting.

        Args:
            expected_items: Tuple of ``(label, element_id)`` pairs to assert.
                Defaults to :attr:`ADVISOR_NOTIFICATION_ITEMS`.

        Returns:
            The list of expected item labels that were located and asserted.
        """
        items = tuple(expected_items) if expected_items else self.ADVISOR_NOTIFICATION_ITEMS

        with logger.step(
            "Verify newly added Item Notification in Advisor Notification page",
            page=self.page,
        ):
            try:
                self.page.bring_to_front()
            except Exception:
                pass

            link_candidates = [
                ("page get_by_text", self.page.get_by_text("View Notification Preferences")),
                (
                    "iframe[title='Coach'] get_by_text",
                    self.page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR).get_by_text(
                        "View Notification Preferences"
                    ),
                ),
            ]
            link_loc = None
            for label, loc in link_candidates:
                try:
                    loc.first.wait_for(state="visible", timeout=15000)
                    logger.info(f"Located 'View Notification Preferences' via {label}")
                    link_loc = loc.first
                    break
                except Exception:
                    continue
            if link_loc is None:
                raise AssertionError(
                    "'View Notification Preferences' link is not visible on shell page"
                )

            link_loc.click()
            logger.info("Clicked 'View Notification Preferences'", attach_to_allure=True)

            # Allow the Advisor Preferences view to render.
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
            try:
                self.page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            def _wait_visible_anywhere(element_id: str, timeout_ms: int = 20000) -> bool:
                """Return True if an element with the given id becomes visible
                on the top-level page or in any child frame within ``timeout_ms``."""
                selector = f"#{element_id}"
                # First try the top-level page (fast path).
                try:
                    self.page.locator(selector).first.wait_for(
                        state="visible", timeout=5000
                    )
                    logger.info(f"Found '{selector}' on top-level page")
                    return True
                except Exception:
                    pass

                # Poll across all frames until timeout.
                import time as _time
                deadline = _time.monotonic() + (timeout_ms / 1000.0)
                while _time.monotonic() < deadline:
                    for f in self.page.frames:
                        try:
                            handle = f.query_selector(selector)
                            if handle is not None and handle.is_visible():
                                logger.info(
                                    f"Found '{selector}' in frame name={f.name!r}"
                                )
                                return True
                        except Exception:
                            continue
                    self.page.wait_for_timeout(500)
                return False

            missing: list[str] = []
            for label, element_id in items:
                if _wait_visible_anywhere(element_id, timeout_ms=20000):
                    logger.info(
                        f"Advisor Notification item visible: '{label}' "
                        f"(id={element_id})",
                        attach_to_allure=True,
                    )
                else:
                    missing.append(f"{label} (id={element_id})")
                    logger.warning(
                        f"Advisor Notification item NOT visible: '{label}' "
                        f"(id={element_id})"
                    )

            if missing:
                frame_summary = " | ".join(
                    f"name={f.name!r} url={f.url!r}" for f in self.page.frames
                )
                logger.info(f"Page frames after search: {frame_summary}")

            Assertions.assert_true(
                not missing,
                "Advisor Notification items not visible on Advisor Preferences "
                f"Coach: {missing}",
            )
            logger.info(
                f"Verified {len(items)} Advisor Notification item(s) on Advisor "
                "Preferences Coach",
                attach_to_allure=True,
            )
            return [label for label, _ in items]

    def select_b_number_and_save_exit(self, b_number: str) -> None:
        """Double-click the B# cell on the shell page, dismiss any dialog,
        then click Save & Exit on the shell coach."""
        with logger.step(f"Select B# {b_number} and click Save & Exit", page=self.page):
            try:
                self.page.bring_to_front()
            except Exception:
                pass
            self.wait_for_loading_data()

            b_cell = self.page.get_by_role("cell", name=b_number, exact=True)
            b_cell.wait_for(state="visible", timeout=30000)
            b_cell.scroll_into_view_if_needed()
            b_cell.dblclick()
            logger.info(f"Double-clicked B# cell: {b_number}")

            # Register dialog handler before triggering Save & Exit.
            # BAW may raise one or more native confirms ("Do you wish to
            # proceed?" / "Are you sure..."). We must click OK on each so the
            # work item is actually saved.
            dialog_count = {"n": 0}

            def _accept_dialog(dialog: Dialog) -> None:
                dialog_count["n"] += 1
                logger.info(
                    f"Dialog #{dialog_count['n']} accepted: {dialog.message}"
                )
                dialog.accept()

            self.page.on("dialog", _accept_dialog)

            try:
                # Wait for shell page to settle after the dblclick before
                # locating Save & Exit (it can be slow to render in BAW).
                for state in ("domcontentloaded", "load", "networkidle"):
                    try:
                        self.page.wait_for_load_state(state, timeout=30000)
                    except Exception as exc:
                        logger.info(
                            f"wait_for_load_state('{state}') skipped: {exc}"
                        )
                try:
                    self.wait_for_loading_data()
                except Exception as exc:
                    logger.info(f"wait_for_loading_data skipped: {exc}")

                self.save_exit_button.wait_for(state="visible", timeout=120000)
                self.save_exit_button.scroll_into_view_if_needed()
                try:
                    self.save_exit_button.click(no_wait_after=True)
                except Exception:
                    logger.warning("Save & Exit normal click failed, trying JS click")
                    self.save_exit_button.evaluate("el => el.click()")
                logger.info("Save & Exit clicked")

                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                except Exception:
                    pass

                # Give any follow-up confirmation dialog time to surface and
                # be auto-accepted by the persistent handler.
                try:
                    self.page.wait_for_timeout(2000)
                except Exception:
                    pass

                if dialog_count["n"] == 0:
                    logger.warning(
                        "No native dialog appeared after Save & Exit "
                        "\u2014 work item may not have been persisted"
                    )
                else:
                    logger.info(
                        f"Save & Exit confirmed via {dialog_count['n']} dialog(s)"
                    )
            finally:
                try:
                    self.page.remove_listener("dialog", _accept_dialog)
                except Exception:
                    pass

    def _close_current_work_item(self) -> None:
        """Internal: select Close-other and click Save & Exit on the current shell page."""
        self.internal_status.wait_for(state="visible", timeout=20000)
        # Option 38 (1-based) = index 37 (0-based) per user-confirmed XPath
        # //*[@id="combo"]/option[38] ΓÇö Close-other
        self.internal_status.select_option(index=37)
        logger.info("Selected 'Close-other' (option index 37) from Internal Status combo")

        dialog_count = {"n": 0}

        def _accept_dialog(dialog: Dialog) -> None:
            dialog_count["n"] += 1
            logger.info(
                f"Dialog #{dialog_count['n']} accepted: {dialog.message}"
            )
            dialog.accept()

        # Persistent handler ΓÇö accepts every confirm/alert popup that appears
        # after Save & Exit (BAW raises a confirm, then a follow-up OK alert).
        self.page.on("dialog", _accept_dialog)

        try:
            # Save & Exit is in the main frame (toolbar outside the Coach iframe)
            self.save_exit_button.wait_for(state="visible", timeout=20000)
            self.save_exit_button.scroll_into_view_if_needed()
            try:
                self.save_exit_button.click(no_wait_after=True)
            except Exception:
                logger.warning("Save & Exit normal click failed, trying JS click")
                self.save_exit_button.evaluate("el => el.click()")
            logger.info("Save & Exit button clicked")

            try:
                self.wait_for_loading_data()
            except Exception:
                pass

            # Wait briefly so the second dialog (final OK confirmation) has time
            # to surface and be auto-accepted by the handler above before we
            # move on to the next work item.
            try:
                self.page.wait_for_timeout(2000)
            except Exception:
                pass

            if dialog_count["n"] < 1:
                logger.warning(
                    "No native dialogs were captured after Save & Exit ΓÇö "
                    "work item may not be fully closed"
                )
            else:
                logger.info(
                    f"Work item close confirmed via {dialog_count['n']} dialog(s)"
                )
        finally:
            try:
                self.page.remove_listener("dialog", _accept_dialog)
            except Exception:
                pass

    def _navigate_to_shell_via_dashboard(self, b_number: str) -> None:
        """Search for b_number in the Dashboard iframe and click the Run icon
        to open the shell process page for that work item."""
        with logger.step(f"Search {b_number} in Dashboard and open shell page", page=self.page):
            dashboard_frame = self.page.locator(ShellProcessLocators.DASHBOARD_IFRAME_SELECTOR).content_frame

            b_search = dashboard_frame.get_by_role("textbox", name="B#:")
            b_search.wait_for(state="visible", timeout=20000)
            b_search.click()
            try:
                b_search.fill("")
            except Exception:
                pass
            b_search.fill(b_number)
            logger.info(f"Entered B# {b_number} in dashboard search")

            dashboard_frame.get_by_role("button", name="Search").click()
            logger.info("Clicked Search button in dashboard")
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

            # Run icon = first empty cell in the row that matches our B#.
            # Scoping to the matching row prevents accidentally opening the
            # wrong work item when multiple rows are listed.
            matching_row = dashboard_frame.get_by_role("row").filter(
                has_text=b_number
            ).first
            try:
                matching_row.wait_for(state="visible", timeout=20000)
                run_icon = matching_row.get_by_role("cell").filter(
                    has_text=re.compile(r"^$")
                ).first
                run_icon.wait_for(state="visible", timeout=10000)
            except Exception:
                logger.warning(
                    f"Could not locate row for B# {b_number}; falling back to first empty cell"
                )
                run_icon = dashboard_frame.get_by_role("cell").filter(
                    has_text=re.compile(r"^$")
                ).first
                run_icon.wait_for(state="visible", timeout=20000)

            context = self.page.context
            existing_pages = set(context.pages)
            new_page = None
            try:
                with self.page.expect_popup(timeout=20000) as popup_info:
                    run_icon.click()
                new_page = popup_info.value
            except Exception:
                # Some BAW flows open the popup without triggering Playwright's
                # popup event ΓÇö fall back to diffing the context pages.
                try:
                    run_icon.click()
                except Exception:
                    pass
                for _ in range(30):
                    added = [p for p in context.pages if p not in existing_pages]
                    if added:
                        new_page = added[-1]
                        break
                    self.page.wait_for_timeout(500)
            logger.info(f"Clicked Run icon for {b_number}")

            if new_page is not None and new_page is not self.page:
                try:
                    new_page.wait_for_load_state("domcontentloaded", timeout=30000)
                except Exception:
                    pass
                try:
                    new_page.bring_to_front()
                except Exception:
                    pass
                # Re-target this page object at the popup so the combo locator
                # resolves against the shell process page.
                self.page = new_page
                # Rebuild key locators on the new page.
                self.internal_status = new_page.get_by_role(
                    "combobox", name="Internal Status"
                )
                self.save_exit_button = new_page.locator(ShellProcessLocators.SAVE_EXIT_BUTTON)
                logger.info(f"Switched to shell popup: {new_page.url}")

            # ----- NAA Coach branch -----
            # If the popup we just landed on is an NAA Coach page (it has an
            # 'Open' button rather than the Internal Status combo), click
            # 'Open' to spawn yet another popup and click 'Remove Association'
            # there.  That second popup carries the Internal Status combo so
            # the existing close logic continues to work.
            naa_open_button = self.page.get_by_role("button", name="Open", exact=True)
            try:
                naa_open_button.wait_for(state="visible", timeout=5000)
                is_naa = True
            except Exception:
                is_naa = False
            if is_naa:
                logger.info("NAA Coach page detected ΓÇö clicking 'Open' button")
                naa_context = self.page.context
                naa_existing_pages = set(naa_context.pages)
                inner_popup = None
                try:
                    with self.page.expect_popup(timeout=20000) as inner_popup_info:
                        naa_open_button.click()
                    inner_popup = inner_popup_info.value
                except Exception:
                    try:
                        naa_open_button.click()
                    except Exception:
                        pass
                    for _ in range(30):
                        added = [p for p in naa_context.pages if p not in naa_existing_pages]
                        if added:
                            inner_popup = added[-1]
                            break
                        self.page.wait_for_timeout(500)

                if inner_popup is not None and inner_popup is not self.page:
                    try:
                        inner_popup.wait_for_load_state("domcontentloaded", timeout=30000)
                    except Exception:
                        pass
                    try:
                        inner_popup.bring_to_front()
                    except Exception:
                        pass
                    self.page = inner_popup
                    self.internal_status = inner_popup.get_by_role(
                        "combobox", name="Internal Status"
                    )
                    self.save_exit_button = inner_popup.locator(ShellProcessLocators.SAVE_EXIT_BUTTON)
                    logger.info(f"Switched to NAA inner popup: {inner_popup.url}")

                remove_association = self.page.get_by_role(
                    "button", name="Remove Association"
                )
                try:
                    remove_association.wait_for(state="visible", timeout=30000)
                    remove_association.scroll_into_view_if_needed()
                    remove_association.click()
                    logger.info("Clicked 'Remove Association' on NAA inner popup")
                except Exception:
                    logger.info(
                        "'Remove Association' not present ΓÇö skipping and "
                        "continuing with Internal Status close flow"
                    )

            # Wait for shell process page to render
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            self.internal_status.wait_for(state="visible", timeout=30000)
            logger.info("Shell process page loaded after dashboard navigation")

    def _is_on_dashboard(self) -> bool:
        """Return True if the browser is currently on the BAW Dashboard page."""
        try:
            url = self.page.url or ""
            return "dashboards" in url or (
                "ProcessPortal/portal" in url and "process.lsw" not in url
            )
        except Exception:
            return False

    def close_work_item(self, b_numbers: list[str] | None = None) -> None:
        """Close one or more work items.

        For each B number:
        - If the browser URL indicates the BAW Dashboard, search for the B#
          there, click the Run icon to open the shell page, then close it.
        - Otherwise (already on a shell/process page) wait for ``#combo`` to
          render and close directly ΓÇö no dashboard navigation needed.

        Args:
            b_numbers: Optional list of B numbers to close.  If None or empty
                       the currently open shell page work item is closed.
        """
        targets = [b.strip() for b in (b_numbers or []) if b and b.strip()]

        if not targets:
            # No specific B numbers supplied ΓÇö close whatever is open right now.
            with logger.step("Close current work item", page=self.page):
                # Wait for the page to settle after any previous navigation.
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                except Exception:
                    pass
                self._close_current_work_item()
            return

        for b_number in targets:
            with logger.step(f"Close work item {b_number}", page=self.page):
                if self._is_on_dashboard():
                    # Browser is on the dashboard ΓÇö search and navigate to shell.
                    logger.info(f"On dashboard ΓÇö searching for {b_number}")
                    self._navigate_to_shell_via_dashboard(b_number)
                else:
                    # Browser is on a shell/process page ΓÇö wait for Internal Status combo.
                    logger.info(f"On shell page ΓÇö waiting for Internal Status combo")
                    try:
                        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                    except Exception:
                        pass
                    self.internal_status.wait_for(state="visible", timeout=30000)
                self._close_current_work_item()
                logger.info(f"Work item {b_number} closed successfully")

    # ==========================================================================
    # IWR Extraction methods
    # ==========================================================================

    def upload_check_document(
        self,
        file_path: str = ShellProcessLocators.DEFAULT_CHECK_DOCUMENT_FILENAME,
    ) -> None:
        """Click Add Document on the IWR shell page, upload the file in the popup,
        click Commit Documents, then close the popup. Does NOT click Submit.

        Args:
            file_path: Bare filename resolved against ``applicationqe/PDF to Upload/``
                       or an absolute path. Defaults to ``fnbnationwide.pdf``.
        """
        resolved_path = self._resolve_check_document_path(file_path)
        with logger.step(f"Upload check document '{resolved_path}'", page=self.page):
            self.wait_for_loading_data()
            self.add_document_button.wait_for(state="visible", timeout=30000)

            upload_popup = None
            try:
                with self.page.expect_popup(timeout=30000) as popup_info:
                    self.add_document_button.click()
                upload_popup = popup_info.value
            except Exception as popup_exc:
                logger.warning(
                    f"expect_popup did not fire for Add Document: {popup_exc}. "
                    "Falling back to context page diff."
                )
                existing = set(self.page.context.pages)
                try:
                    self.add_document_button.click()
                except Exception:
                    self.add_document_button.evaluate("el => el.click()")
                for _ in range(30):
                    added = [p for p in self.page.context.pages if p not in existing]
                    if added:
                        upload_popup = added[-1]
                        break
                    self.page.wait_for_timeout(500)

            if upload_popup is None:
                raise AssertionError(
                    "Upload Document popup did not open after clicking 'Add Document'"
                )
            try:
                upload_popup.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass
            logger.info("Upload Document popup opened")

            browse_input = upload_popup.locator(ShellProcessLocators.IWR_BROWSE_FILE_INPUT)
            browse_input.wait_for(state="attached", timeout=20000)
            browse_input.set_input_files(resolved_path)
            logger.info(f"Set file on #browseFile: {resolved_path}")

            commit_btn = upload_popup.get_by_role(
                "button", name=ShellProcessLocators.COMMIT_DOCUMENTS_BUTTON_ROLE
            )
            commit_btn.wait_for(state="visible", timeout=20000)
            try:
                commit_btn.click()
            except Exception:
                commit_btn.evaluate("el => el.click()")
            logger.info("Clicked Commit Documents")

            try:
                upload_popup.wait_for_event("close", timeout=15000)
            except Exception:
                if not upload_popup.is_closed():
                    try:
                        upload_popup.close()
                    except Exception:
                        pass
            logger.info("Check document committed, upload popup closed")

    def submit_iwr_work_item(self) -> str:
        """Click Submit on the IWR shell page, capture the work item number from
        the 'Work item created successfully:XXXXXXXX' alert, accept it, then
        re-target self.page to the remaining Process Portal page.

        Returns:
            Work item number string (e.g. ``"10017594"``).
        """
        with logger.step("Submit IWR work item and capture work item number", page=self.page):
            captured: dict = {"number": ""}

            iwr_submit_btn = self.submit_button
            iwr_submit_btn.wait_for(state="visible", timeout=30000)

            def _handle_dialog(dialog: Dialog) -> None:
                msg = dialog.message or ""
                logger.info(f"Submit alert: {msg}")
                match = re.search(r":(\d+)", msg)
                if match:
                    captured["number"] = match.group(1)
                    logger.info(f"Captured work item number: {captured['number']}")
                try:
                    dialog.accept()
                    logger.info("Dialog accepted")
                except Exception:
                    pass

            self.page.on("dialog", _handle_dialog)
            try:
                iwr_submit_btn.click(no_wait_after=True)
            except Exception:
                logger.warning("IWR Submit normal click failed, trying JS click")
                iwr_submit_btn.evaluate("el => el.click()")
            logger.info("Clicked IWR Submit button")

            # Wait up to 30s for the dialog handler to fire and capture the number
            for _ in range(60):
                try:
                    self.page.wait_for_timeout(500)
                except Exception:
                    break
                if captured["number"]:
                    break
            self.page.remove_listener("dialog", _handle_dialog)

            try:
                self.page.wait_for_timeout(2000)
            except Exception:
                pass  # page may have closed after the Submit dialog was accepted

            parent_page = self.page
            for candidate in reversed(parent_page.context.pages):
                if candidate is parent_page or candidate.is_closed():
                    continue
                try:
                    candidate.bring_to_front()
                except Exception:
                    pass
                self.page = candidate
                self.__init__(candidate)
                logger.info(f"Re-targeted self.page to Process Portal: {candidate.url}")
                break

            work_item_number = captured["number"]
            logger.info(f"IWR work item number: {work_item_number}", attach_to_allure=True)
            return work_item_number

    def navigate_to_search_baw_and_enter_work_item_id(self, work_item_id: str) -> None:
        """Click 'Search Work Item BAW' in the left nav and enter work_item_id
        in the Work Item ID field.

        Args:
            work_item_id: Work item number captured from the Submit alert.
        """
        with logger.step(
            f"Navigate to Search Work Item BAW and enter work item ID: {work_item_id}",
            page=self.page,
        ):
            self.search_work_item_baw_link.wait_for(state="visible", timeout=30000)
            self.search_work_item_baw_link.click()
            logger.info("Clicked 'Search Work Item BAW' link")
            self.wait_for_loading_data()

            coach_frame = self.page.locator(ShellProcessLocators.COACH_IFRAME_SELECTOR).content_frame
            work_item_id_field = coach_frame.get_by_role("textbox", name="Work Item ID")

            if not work_item_id_field.is_visible():
                for attempt in range(1, 6):
                    logger.info(f"Work Item ID field not visible (attempt {attempt}/5), reloading page...")
                    self.page.reload()
                    self.wait_for_loading_data()
                    self.page.get_by_role("link", name=ShellProcessLocators.SEARCH_WORK_ITEM_LINK_ROLE).first.click()
                    self.wait_for_loading_data()
                    coach_frame = self.page.locator(ShellProcessLocators.COACH_IFRAME_SELECTOR).content_frame
                    work_item_id_field = coach_frame.get_by_role("textbox", name="Work Item ID")
                    if work_item_id_field.is_visible():
                        logger.info("Re-clicked 'Search Work Item BAW' link")
                        break
                else:
                    raise AssertionError("Work Item ID field not visible after 5 reload attempts")

            work_item_id_field.fill(work_item_id)
            logger.info(f"Entered work item ID: {work_item_id}")

    def validate_iwr_extraction_note(self, expected_text: str) -> None:
        """Assert the IWR Check Image Extraction Outcome note contains expected_text.

        Searches across all frames (main page, Dashboard iframe, Coach iframe,
        and Dashboard>Coach nested iframe) for ``div[id^='CustomHTML'] pre``.
        Clicks Save & Refresh before each scan so BAW fetches the latest notes.

        Args:
            expected_text: Substring that must appear in the rendered note.
        """
        with logger.step(
            f"Validate IWR extraction note contains: '{expected_text}'", page=self.page
        ):
            # ── 1. Bring the shell page to front and wait for DOM to settle ──
            try:
                self.page.bring_to_front()
            except Exception:
                pass

            for state in ("domcontentloaded", "load"):
                try:
                    self.page.wait_for_load_state(state, timeout=30000)
                except Exception:
                    pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass

            # Normalize Unicode apostrophes so BAW's right-single-quote (\u2019)
            # matches a straight apostrophe (') in expected_text.
            def _norm(text: str) -> str:
                return text.replace("\u2019", "'").replace("\u2018", "'")

            expected_norm = _norm(expected_text)
            css = "div[id^='CustomHTML'] pre"
            notes_td_css = "table[id='Table4'] td"

            def _check_frame(frame_locator, label: str) -> bool:
                """Return True if expected text found in <pre> or notes table cell."""
                try:
                    # 1. CustomHTML pre (original path)
                    elems = frame_locator.locator(css).all()
                    for pre in elems:
                        raw = pre.inner_text(timeout=5000) or ""
                        note_text = _norm(raw)
                        snippet = note_text[:200].replace("\n", " ")
                        logger.info(f"  [{label}] pre: '{snippet}'")
                        if expected_norm in note_text:
                            return True
                    # 2. Notes history table cells (note is in Table4 td when popup or inline)
                    cells = frame_locator.locator(notes_td_css).all()
                    for cell in cells:
                        raw = cell.inner_text(timeout=3000) or ""
                        note_text = _norm(raw)
                        if expected_norm in note_text:
                            snippet = note_text[:200].replace("\n", " ")
                            logger.info(f"  [{label}] notes td: '{snippet}'")
                            return True
                    if not elems and not cells:
                        logger.info(f"  [{label}] no <pre> elements found")
                except Exception as exc:
                    logger.info(f"  [{label}] error: {exc}")
                return False

            # ── 2. Log diagnostics on startup ──
            try:
                logger.info(f"DIAG page URL: {self.page.url}")
                frames = self.page.frames
                logger.info(f"DIAG frame count: {len(frames)}")
                for i, f in enumerate(frames):
                    logger.info(f"DIAG frame[{i}]: {f.url}")
            except Exception as de:
                logger.info(f"DIAG failed: {de}")

            # ── 3. Poll across all frames ──
            max_attempts = 40
            poll_ms = 15000

            for attempt in range(1, max_attempts + 1):
                # Every 5 attempts do a hard reload to rebuild the frame tree
                # (headless pipeline: Save & Refresh alone may not re-render notes).
                if attempt > 1 and attempt % 5 == 1:
                    try:
                        self.page.reload(timeout=60000)
                        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
                        logger.info(f"Hard page reload on attempt {attempt}")
                    except Exception as re:
                        logger.info(f"Hard reload failed (attempt {attempt}): {re}")

                # Click Save & Refresh so BAW fetches the latest IWR notes.
                try:
                    if self.save_refresh_button.is_visible(timeout=3000):
                        self.save_refresh_button.click()
                        logger.info(f"Clicked Save & Refresh (attempt {attempt})")
                        try:
                            self.wait_for_loading_data()
                        except Exception:
                            pass
                        try:
                            self.page.wait_for_load_state("networkidle", timeout=20000)
                        except Exception:
                            pass
                    else:
                        logger.info(f"Save & Refresh not visible (attempt {attempt})")
                except Exception as e:
                    logger.info(f"Save & Refresh check failed (attempt {attempt}): {e}")

                # Main frame
                if _check_frame(self.page, "main"):
                    logger.info(f"IWR note found in main frame (attempt {attempt})", attach_to_allure=True)
                    return

                # Top-level Coach iframe
                try:
                    if _check_frame(self.page.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR), "Coach"):
                        logger.info(f"IWR note found in Coach iframe (attempt {attempt})", attach_to_allure=True)
                        return
                except Exception as e:
                    logger.info(f"Coach iframe check error (attempt {attempt}): {e}")

                # Dashboard iframe
                try:
                    dash_fl = self.page.frame_locator(ShellProcessLocators.DASHBOARD_IFRAME_SELECTOR)
                    if _check_frame(dash_fl, "Dashboard"):
                        logger.info(f"IWR note found in Dashboard iframe (attempt {attempt})", attach_to_allure=True)
                        return
                    # Coach nested inside Dashboard
                    if _check_frame(dash_fl.frame_locator(ShellProcessLocators.COACH_IFRAME_SELECTOR), "Dashboard>Coach"):
                        logger.info(f"IWR note found in Dashboard>Coach iframe (attempt {attempt})", attach_to_allure=True)
                        return
                except Exception as e:
                    logger.info(f"Dashboard iframe check error (attempt {attempt}): {e}")

                # Scan all frames via Playwright's frame list (catches any nesting)
                try:
                    for i, f in enumerate(self.page.frames):
                        try:
                            # CustomHTML pre
                            elems = f.locator(css).all()
                            for pre in elems:
                                raw = pre.inner_text(timeout=3000) or ""
                                note_text = _norm(raw)
                                snippet = note_text[:200].replace("\n", " ")
                                logger.info(f"  [frame[{i}] {f.url[:60]}] pre: '{snippet}'")
                                if expected_norm in note_text:
                                    logger.info(f"IWR note found in frame[{i}] (attempt {attempt})", attach_to_allure=True)
                                    return
                            # Notes table cells
                            cells = f.locator(notes_td_css).all()
                            for cell in cells:
                                raw = cell.inner_text(timeout=3000) or ""
                                note_text = _norm(raw)
                                if expected_norm in note_text:
                                    snippet = note_text[:200].replace("\n", " ")
                                    logger.info(f"  [frame[{i}] {f.url[:60]}] notes td: '{snippet}'")
                                    logger.info(f"IWR note found in notes table frame[{i}] (attempt {attempt})", attach_to_allure=True)
                                    return
                        except Exception:
                            pass
                except Exception as e:
                    logger.info(f"All-frames scan error (attempt {attempt}): {e}")

                logger.info(f"IWR extraction note not yet visible (attempt {attempt}/{max_attempts})")
                if attempt < max_attempts:
                    try:
                        self.page.wait_for_timeout(poll_ms)
                    except Exception:
                        pass

            raise AssertionError(
                f"IWR extraction note '{expected_text}' was not found across all "
                f"frames after {max_attempts} polling attempts "
                f"(~{max_attempts * poll_ms // 1000}s total)."
            )

    def select_work_item_type(self, work_item_type: str) -> None:
        """Select work item type from dropdown.

        The Open New Work Item action opens the Shell Process form in a new
        browser tab whose title contains "Shell Process". Switch to that tab
        first and resolve the dropdown at top level of the popup page
        (not inside an iframe).
        """
        self.pause_in_shell_coach("Paused after opening Shell coach popup")

        try:
            self.page.wait_for_load_state("load", timeout=60000)
        except Exception:
            pass
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        self.baw_spinner_loader()

        dropdown = self.page.locator(ShellProcessLocators.WORK_ITEM_TYPE_SELECT)
        dropdown.wait_for(state="visible", timeout=60000)

        try:
            dropdown.select_option(label=work_item_type)
        except Exception:
            dropdown.select_option(value=work_item_type)
        self.baw_spinner_loader()

    def enter_custodial_account_value(self, account_number: str) -> None:
        """Enter custodial account value into the 'Custodial Account #' field.

        IMPORTANT: The Shell form has several similarly-named fields
        (Custodial Account #, Account Apl Id, Bundle Id, Doc ID ...).
        Match by the *exact* label "Custodial Account" to avoid binding
        to "Account Apl Id" (which sits adjacent in the layout).
        """
        logger.info(f"Entering custodial account value: {account_number}")
        # Order matters: prefer label-anchored locators over generic input ids.
        candidates = [
            # Exact label "Custodial Account #" → first input that follows it
            "xpath=//label[normalize-space(.)='Custodial Account #']"
            "/following::input[not(@type='hidden') and not(@disabled)][1]",
            "xpath=//label[starts-with(normalize-space(.),'Custodial Account')]"
            "/following::input[not(@type='hidden') and not(@disabled)][1]",
            "xpath=//td[starts-with(normalize-space(.),'Custodial Account')]"
            "/following-sibling::td//input[not(@type='hidden') and not(@disabled)][1]",
            "input[id*='CustodialAccount' i]",
            "input[name*='custodialAccount' i]",
        ]
        input_field = self._first_visible_locator(candidates, timeout=8000)
        if not input_field:
            raise ValueError("Could not locate Custodial Account input field on Shell Process page")

        input_field.fill(str(account_number))
        # BAW form uses JS onchange/onblur handlers to enable downstream
        # controls (e.g. the Individual Owner dropdown). Playwright's fill()
        # alone does not always fire these in headless mode, so trigger
        # them explicitly and then commit focus by tabbing out.
        try:
            input_field.dispatch_event("change")
            input_field.dispatch_event("blur")
        except Exception:
            pass
        try:
            input_field.press("Tab")
        except Exception:
            pass



    def _wait_and_switch_to_coach_page(self, timeout_s: int = 120) -> None:
        """Poll all browser-context pages until the BAW work-item coach is found.

        After Run Now the Shell Process popup closes and the coach opens on
        a different tab (process.lsw?zTaskId=...). This method updates
        ``self.page`` to point at that tab.
        """
        import time as _time
        context = self.page.context
        deadline = _time.time() + timeout_s
        while _time.time() < deadline:
            for p in context.pages:
                try:
                    url = p.url or ""
                    if "process.lsw" in url and ("zTaskId" in url or "zWorkflowState" in url):
                        self.page = p
                        logger.info(f"Switched to work-item coach: {url}")
                        return
                except Exception:
                    pass
            _time.sleep(1)
        logger.warning(f"Work-item coach (process.lsw) not found within {timeout_s}s; staying on current page")


    def switch_to_shell_process_page(self, source_page: Page) -> None:
        """Switch to Shell Process page from source page"""
        logger.info("Switching to Shell Process page")
        # TODO: Implement window/page switching logic

    def fetch_custodian_account(self) -> str:
        """Fetch custodian account"""
        logger.info("Fetching custodian account")
        # TODO: Implement locators and functionality
        return ""

    def select_internal_status_and_close_work_item(self, status: str) -> None:
        """Select internal status and close work item"""
        logger.info(f"Selecting internal status '{status}' and closing work item")
        # TODO: Implement locators and functionality

    def click_add_document_and_switch_to_upload_tab(self, timeout: int = 30000) -> Page:
        """Click 'Add Document' button on Direct Entry for Shell page. A new
        browser tab ('Upload Document - Work') opens. Switch this page object
        to the popup and return it."""
        logger.info("Clicking Add Document button")
        add_doc_btn = self.page.locator(ShellProcessLocators.ADD_DOCUMENT_BUTTON).first
        add_doc_btn.wait_for(state="visible", timeout=timeout)
        try:
            add_doc_btn.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass

        with self.page.context.expect_page(timeout=timeout) as page_info:
            add_doc_btn.click()
        popup_page = page_info.value
        try:
            popup_page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            logger.warning("Upload Document popup domcontentloaded wait timed out; continuing")
        popup_page.bring_to_front()
        # Keep a reference to the parent shell page so we can switch back later.
        self._parent_shell_page = self.page
        self.page = popup_page
        logger.info("Switched to Upload Document popup tab")
        return popup_page

    def upload_document(self, file_path: str, timeout: int = 30000) -> None:
        """Set file on the hidden file input inside the Upload Document popup."""
        logger.info(f"Uploading document: {file_path}")
        file_input = self.page.locator(ShellProcessLocators.UPLOAD_FILE_INPUT).first
        file_input.wait_for(state="attached", timeout=timeout)
        file_input.set_input_files(file_path)
        logger.info("Document file set on upload input")

    def click_commit_documents(self, timeout: int = 30000) -> None:
        """Click the 'Commit Documents' button. The button may live either
        in the Upload Document popup or back on the main Shell page; try the
        popup first and fall back to the parent page."""
        logger.info("Clicking Commit Documents button")
        commit_btn = self.page.locator(ShellProcessLocators.COMMIT_DOCUMENTS_BUTTON).first
        try:
            commit_btn.wait_for(state="visible", timeout=timeout)
            commit_btn.click()
        except Exception:
            parent = getattr(self, "_parent_shell_page", None)
            if not parent:
                raise

            logger.info("Commit Documents not found on popup; switching back to parent shell page")
            try:
                if not self.page.is_closed():
                    pass
            except Exception:
                pass
            self.page = parent
            self.page.bring_to_front()
            commit_btn = self.page.locator(ShellProcessLocators.COMMIT_DOCUMENTS_BUTTON).first
            commit_btn.wait_for(state="visible", timeout=timeout)
            commit_btn.click()

        # After commit the popup usually closes; ensure we are back on the
        # parent shell page for subsequent steps.
        parent = getattr(self, "_parent_shell_page", None)
        if parent and self.page is not parent:
            self.page = parent
            self.page.bring_to_front()
        try:
            self.baw_spinner_loader()
        except Exception:
            pass

    def fetch_pending_upload_details_and_submit(self, timeout: int = 30000) -> str:
        """Fetch the red 'Pending Upload - <filename>' text from the Direct
        Entry for Shell page, attach a screenshot, then click Submit."""
        # Make sure we are on the parent shell page (popup should be closed by now).
        parent = getattr(self, "_parent_shell_page", None)
        if parent and self.page is not parent:
            self.page = parent
        try:
            self.page.bring_to_front()
        except Exception:
            pass
        # Give the shell coach a moment to finish reloading after Commit.
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            pass

        # Priority: click Submit as soon as it is visible. Pending-upload
        # text capture is best-effort and must not delay Submit.
        logger.info("Waiting for Submit button on Direct Entry for Shell")
        submit_btn = self.page.locator(ShellProcessLocators.SUBMIT_BUTTON).first
        submit_btn.wait_for(state="visible", timeout=timeout)

        pending_text = ""
        pending_candidates = [
            "xpath=//*[contains(normalize-space(.),'Pending Upload') and not(.//*[contains(normalize-space(.),'Pending Upload')])]",
            "div#getDocuments span",
            "div#getDocuments",
        ]
        try:
            pending_locator = self._first_visible_locator(pending_candidates, timeout=2000)
            if pending_locator:
                pending_text = (pending_locator.inner_text(timeout=2000) or "").strip()
                logger.info(f"Pending upload details: {pending_text}")
        except Exception as exc:
            logger.info(f"Skipping pending upload capture (best-effort): {exc}")

        logger.info("Clicking Submit button on Direct Entry for Shell")
        try:
            submit_btn.scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass
        submit_btn.click()
        return pending_text

    def handle_work_item_created_popup(self, timeout: int = 30000) -> str:
        """Wait for the browser 'Work item created successfully:<id>' confirm
        dialog, extract the numeric work item id, accept the dialog, and
        return the id."""
        import re

        captured: dict[str, str] = {}

        def _on_dialog(dialog):
            try:
                msg = dialog.message or ""
                logger.info(f"Browser dialog appeared: {msg}")
                match = re.search(r":\s*(\d+)", msg)
                if match:
                    captured["work_item_id"] = match.group(1)
                try:
                    logger.attach_screenshot(self.page, "Work Item Created Popup")
                except Exception:
                    pass
            finally:
                try:
                    dialog.accept()
                except Exception:
                    pass

        self.page.on("dialog", _on_dialog)

        # Poll until the dialog handler captured the id (BAW sometimes takes
        # a few seconds after Submit to raise the alert).
        import time as _time

        end = _time.time() + (timeout / 1000)
        while _time.time() < end and "work_item_id" not in captured:
            self.page.wait_for_timeout(500)

        # Detach the listener regardless of outcome.
        try:
            self.page.remove_listener("dialog", _on_dialog)
        except Exception:
            pass

        if "work_item_id" not in captured:
            raise RuntimeError("Work item created confirm dialog was not observed within timeout")

        work_item_id = captured["work_item_id"]
        logger.info(f"Captured Work Item ID: {work_item_id}")
        return work_item_id

    def select_document_and_commit(self, file_path: str) -> str:
        """End-to-end check document submission flow:
          1. Click Add Document -> switch to Upload Document popup
          2. Choose file
          3. Click Commit Documents
          4. Back on Direct Entry for Shell, attach screenshot of pending upload text
          5. Click Submit
          6. Handle the 'Work item created successfully:<id>' browser dialog
        Returns the captured work item id.
        """
        # The dialog can fire from the parent shell page. Register listener
        # BEFORE Submit so we don't miss it.
        import re

        captured: dict[str, str] = {}

        def _on_dialog(dialog):
            try:
                msg = dialog.message or ""
                logger.info(f"Browser dialog: {msg}")
                match = re.search(r":\s*(\d+)", msg)
                if match:
                    captured["work_item_id"] = match.group(1)
            finally:
                try:
                    dialog.accept()
                except Exception:
                    pass

        parent_page = self.page
        parent_page.on("dialog", _on_dialog)
        try:
            self.click_add_document_and_switch_to_upload_tab()
            self.upload_document(file_path)
            self.click_commit_documents()
            self.fetch_pending_upload_details_and_submit()

            import time as _time
            end = _time.time() + 30
            while _time.time() < end and "work_item_id" not in captured:
                try:
                    parent_page.wait_for_timeout(500)
                except Exception:
                    # Page/popup may close right after the dialog is accepted.
                    break
        finally:
            try:
                parent_page.remove_listener("dialog", _on_dialog)
            except Exception:
                pass

        if "work_item_id" not in captured:
            raise RuntimeError("Work item created confirm dialog was not observed within timeout")

        work_item_id = captured["work_item_id"]
        logger.info(f"Captured Work Item ID: {work_item_id}")
        return work_item_id

    def _coach_frame(self):
        """Return the root locator scope for Shell Process elements.

        The "Direct Entry for Shell" / Shell Process form renders at the top
        level of the popup page (not inside an iframe). Returning ``self.page``
        keeps the locator API identical to the previous ``FrameLocator``
        usage while binding to the correct scope.
        """
        return self.page

    def spinner_loader(self) -> None:
        """Wait for spinner loader to disappear."""
        logger.info("Waiting for spinner loader to disappear")
        self.baw_spinner_loader()

    def baw_spinner_loader(self, appear_timeout: int = 10000, disappear_timeout: int = 60000) -> None:
        """Wait for BAW loading spinner to complete if present."""
        spinner = self._coach_frame().locator(ShellProcessLocators.BAW_LOADING_SPINNER).first
        try:
            spinner.wait_for(state="visible", timeout=appear_timeout)
            spinner.wait_for(state="hidden", timeout=disappear_timeout)
        except PlaywrightTimeoutError:
            # Spinner may not appear for every action; treat as non-fatal.
            logger.info("BAW spinner not observed for this action")

    def pause_in_shell_coach(self, reason: str = "Shell coach debug pause") -> None:
        """Pause execution in Shell coach when debugging with Playwright Inspector.

        Controlled by env var ``SHELL_COACH_PAGE_PAUSE``:
        * ``1``/``true``/``yes`` => call ``page.pause()``
        * anything else => no-op
        """
        flag = str(os.getenv("SHELL_COACH_PAGE_PAUSE", "")).strip().lower()
        if flag not in {"1", "true", "yes"}:
            return

        logger.info(f"{reason} (SHELL_COACH_PAGE_PAUSE={flag})")
        self.page.pause()

    def _first_visible_locator(self, candidates: list[str], timeout: int = 5000) -> Optional[Locator]:
        """Resolve the first visible locator from a candidate list within the coach frame."""
        frame = self._coach_frame()
        for selector in candidates:
            locator = frame.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=timeout)
                return locator
            except Exception:
                continue
        return None

    def fetch_b_number(self) -> str:
        """Fetch B number from shell process page"""
        logger.info("Fetching B number from shell process page")
        # After Run Now the page navigates to process.lsw (the work-item coach).
        # The click(timeout=120000) in select_individual_owner_and_click_run_now
        # already waited for that navigation to commit, so self.page is valid.
        # Give the coach ample time to render the B# cell.
        b_number_cell = self._coach_frame().locator(ShellProcessLocators.B_NUMBER).first
        b_number_cell.wait_for(state="visible", timeout=90000)
        b_number = (b_number_cell.inner_text() or "").strip()
        logger.info(f"Fetched B number: {b_number}")
        return b_number

    def get_phone_call_required_for_nigo(self) -> str:
        """Get phone call required for NIGO value"""
        logger.info("Getting phone call required for NIGO")
        candidates = [
            "xpath=//*[contains(normalize-space(),'Phone call required for NIGO')]/following::td[1]",
            "xpath=//*[contains(normalize-space(),'Phone call required for NIGO')]/following::*[self::span or self::div][1]",
            "xpath=//*[contains(normalize-space(),'NIGO')]/following::td[1]",
        ]

        value_locator = self._first_visible_locator(candidates, timeout=8000)
        if not value_locator:
            logger.warning("Could not locate NIGO value field; defaulting to empty")
            return ""

        value = (value_locator.inner_text() or "").strip()
        logger.info(f"Phone call required for NIGO: {value}")
        return value

    def click_view_notification_preferences(self):
        """Click on View Notification Preferences button"""
        logger.info("Clicking View Notification Preferences button")
        candidates = [
            "a:has-text('View Notification Preferences')",
            "text=View Notification Preferences",
            "xpath=//a[contains(normalize-space(),'View Notification Preferences')]",
            "xpath=//*[contains(normalize-space(),'View Notification Preferences')]",
        ]
        link = self._first_visible_locator(candidates, timeout=10000)
        if not link:
            logger.warning("View Notification Preferences control not found")
            return None

        try:
            with self.page.context.expect_page(timeout=15000) as page_info:
                link.click()
            popup_page = page_info.value
            popup_page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info("Notification Preferences popup opened")
            return popup_page
        except Exception:
            logger.warning("No popup detected after clicking notification preferences link")
            return None

    def create_new_digital_record_and_open_check_details(
        self,
        wait_after_create_ms: int = 60000,
        click_timeout: int = 30000,
    ) -> None:
        """Click 'Create New Digital Record', wait for shell coach to reload,
        then click 'Add/Update Check Details'. Stays on the same shell page (no popup).
        """
        frame = self._coach_frame()
        section_candidates = [
            'xpath=//td[@id="CheckDetailsSection_SectionTitle"]',
            "xpath=//td[contains(@id,'CheckDetailsSection') and contains(@id,'SectionTitle')]",
            "xpath=//*[normalize-space(.)='Check Details']",
        ]
        create_candidates = [
            'xpath=//button[@id="ButtonGroup33_CreateNewDigitalRecord"]',
            "xpath=//button[contains(@id,'CreateNewDigitalRecord')]",
            "button:has-text('Create New Digital Record')",
        ]
        add_check_candidates = [
            'xpath=//button[@id="ButtonGroup32_AddCheck"]',
            "xpath=//button[contains(@id,'AddCheck')]",
            "button:has-text('Add/Update Check Details')",
            "button:has-text('Add Check')",
        ]

        # 1. Scroll to Check Details section
        logger.info("Scrolling to Check Details section")
        section = self._first_visible_locator(section_candidates, timeout=15000)
        if section:
            try:
                section.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass

        # 2. Click Create New Digital Record
        logger.info("Clicking Create New Digital Record button")
        # Wait for any in-flight BAW spinner to disappear so the click isn't intercepted.
        try:
            self.baw_spinner_loader(appear_timeout=2000, disappear_timeout=30000)
        except Exception:
            pass
        create_btn = self._first_visible_locator(create_candidates, timeout=click_timeout)
        if not create_btn:
            raise RuntimeError("Create New Digital Record button not found")
        try:
            create_btn.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        try:
            create_btn.click(timeout=15000)
        except Exception as click_err:
            logger.warning(
                f"Normal click on Create New Digital Record failed ({click_err}); "
                f"retrying with force=True"
            )
            create_btn.click(force=True, timeout=15000)

        # 3. Wait for shell coach to reload (spinner + Add/Update Check Details visible)
        self.baw_spinner_loader(appear_timeout=10000, disappear_timeout=wait_after_create_ms)
        logger.info("Waiting for shell coach to display Add/Update Check Details button")
        add_btn = self._first_visible_locator(add_check_candidates, timeout=wait_after_create_ms)
        if not add_btn:
            raise RuntimeError("Add/Update Check Details button not found after reload")
        logger.info("Shell coach with digital record displayed")

        # 4. Scroll back to Check Details section
        logger.info("Scrolling back to Check Details section")
        section = self._first_visible_locator(section_candidates, timeout=10000)
        if section:
            try:
                section.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass

        # 5. Click Add/Update Check Details
        logger.info("Clicking Add/Update Check Details button")
        add_btn = self._first_visible_locator(add_check_candidates, timeout=click_timeout)
        if not add_btn:
            raise RuntimeError("Add/Update Check Details button not found")
        try:
            add_btn.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        add_btn.click()
        self.baw_spinner_loader()

    def wait_for_shell_page_and_open_check_details(
        self,
        wait_timeout_ms: int = 60000,
        click_timeout: int = 30000,
    ) -> None:
        """After returning from Check Coach, wait for Shell page and reopen Add/Update Check Details."""
        section_candidates = [
            'xpath=//td[@id="CheckDetailsSection_SectionTitle"]',
            "xpath=//td[contains(@id,'CheckDetailsSection') and contains(@id,'SectionTitle')]",
            "xpath=//*[normalize-space(.)='Check Details']",
        ]
        add_check_candidates = [
            'xpath=//button[@id="ButtonGroup32_AddCheck"]',
            "xpath=//button[contains(@id,'AddCheck')]",
            "button:has-text('Add/Update Check Details')",
            "button:has-text('Add Check')",
        ]

        logger.info("Waiting for Shell Process page to be displayed")
        self.switch_to_page_by_title("Shell Process", timeout=max(30, wait_timeout_ms // 1000))
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=wait_timeout_ms)
        except Exception:
            pass

        self.pause_in_shell_coach("Paused after returning to Shell coach")

        logger.info("Scrolling to Check Details section")
        section = self._first_visible_locator(section_candidates, timeout=15000)
        if section:
            try:
                section.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass

        logger.info("Clicking Add/Update Check Details button")
        add_btn = self._first_visible_locator(add_check_candidates, timeout=click_timeout)
        if not add_btn:
            raise RuntimeError("Add/Update Check Details button not found on Shell Process page")
        try:
            add_btn.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        add_btn.click()
        self.baw_spinner_loader()

    def wait_for_shell_page_displayed(self, wait_timeout_ms: int = 60000) -> None:
        """Wait until Shell Process coach is displayed and interactive."""
        logger.info("Waiting for Shell Process page to be displayed")
        self.switch_to_page_by_title("Shell Process", timeout=max(30, wait_timeout_ms // 1000))
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=wait_timeout_ms)
        except Exception:
            pass
        try:
            self.baw_spinner_loader(appear_timeout=2000, disappear_timeout=min(wait_timeout_ms, 60000))
        except Exception:
            pass

    def fetch_check_image_extraction_details(self, wait_timeout_ms: int = 60000) -> dict:
        """Open/check the Check Image Extraction section, capture details, and take a screenshot."""
        with logger.step("Fetch Shell Check Image Extraction details", page=self.page):
            self.wait_for_shell_page_displayed(wait_timeout_ms=wait_timeout_ms)

            header_candidates = [
                "xpath=//*[normalize-space(.)='Check Image Extraction']",
                "text=Check Image Extraction",
            ]
            details_candidates = [
                "xpath=//td[contains(normalize-space(.),'Account Funding Validation') and contains(normalize-space(.),'Status of Account')]",
                "xpath=//td[contains(normalize-space(.),'Account Funding Validation')]",
                "xpath=//*[self::td or self::div or self::span][contains(normalize-space(.),'Account Funding Validation')]",
            ]

            header = self._first_visible_locator(header_candidates, timeout=15000)
            if header:
                try:
                    header.scroll_into_view_if_needed(timeout=5000)
                except Exception:
                    pass
                try:
                    header.click(timeout=5000)
                except Exception:
                    pass

            details_loc = self._first_visible_locator(details_candidates, timeout=20000)
            if not details_loc:
                raise RuntimeError("Check Image Extraction details cell not found on Shell Process page")

            try:
                details_loc.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            try:
                details_loc.click(timeout=5000)
            except Exception:
                pass

            details_text = (details_loc.inner_text(timeout=5000) or "").strip()
            details_items = [
                line.strip(" -\t") for line in re.split(r"\r?\n+", details_text) if line.strip()
            ]

            try:
                logger.attach_screenshot(self.page, "Shell - Check Image Extraction")
            except Exception as e:
                logger.warning(f"Screenshot attach failed for Shell Check Image Extraction: {e}")

            return {
                "details_text": details_text,
                "details_items": details_items,
            }

    def switch_to_page_by_title(self, title: str, timeout: int = 30000) -> None:
        """Switch to a page by its title"""
        logger.info(f"Switching to page with title: {title}")
        timeout_seconds = timeout if timeout <= 300 else timeout / 1000
        end_time = time.time() + timeout_seconds

        while time.time() < end_time:
            for context_page in self.page.context.pages:
                try:
                    page_title = context_page.title()
                    if title.lower() in page_title.lower():
                        context_page.bring_to_front()
                        self.page = context_page
                        logger.info(f"Switched to page title: {page_title}")
                        return
                except Exception:
                    continue
            self.page.wait_for_timeout(500)

        raise ValueError(f"Could not find page with title containing '{title}'")
