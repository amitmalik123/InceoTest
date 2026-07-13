import os
import re
import time
from typing import Optional
from urllib.parse import urljoin

import allure
from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from pages.ewm.locators.docusign_locators import DocuSignLocators
from utils.allure_logger import get_allure_logger
from utils.assertions import Assertions
from utils.outlook_utils import OutlookOTPPage, outlook_perform_sign_in

logger = get_allure_logger(__name__)


class DocuSignPage(BasePage):

    nNumber = ""

    # Text constants used for get_by_role / get_by_text calls and logic checks
    ERSD_CONSENT_TEXT = "I confirm I have read and I consent to the Electronic Record and Signature Disclosure."
    ERSD_CONTINUE_BUTTON_TEXT = "Continue"
    FINISH_BUTTON_TEXT = "Finish"
    SEND_NOW_BUTTON_PATTERN = "Send Now"
    CONFIRM_CODE_BUTTON_PATTERN = "Confirm Code"
    RESEND_CODE_BUTTON_PATTERN = "Resend Code"
    SIGN_HERE_BUTTON_PATTERN = r"Required\s*-\s*Sign Here"
    SIGNATURE_APPLIED_BUTTON_PATTERN = r"Required\s*-\s*Signature Applied"
    STAMPING_ELEMENT_TEXT_KEY = "As authorized by"
    OTP_FIELD_NAME_PATTERN = "verification code"
    ADOPT_AND_SIGN_BUTTON_TEXT = "Adopt and Sign"
    ADOPT_AND_SIGN_BUTTON_DATA_QA = "adopt-submit"
    FINISH_LATER_BUTTON_TEXT = "Finish Later"

    def otp_verification(self) -> None:
        """Run common Outlook pre-login + Send Now + OTP submission flow."""
        logger.info("[common_otp] Start")

        outlook_page = None
        try:
            outlook_page = self.page.context.new_page()
            outlook_otp = OutlookOTPPage(outlook_page)

            outlook_otp.navigate_to_outlook()
            if not outlook_perform_sign_in(outlook_page):
                raise RuntimeError("Outlook login failed before Send Now")

            self.click_send_now()

            otp_submitted = self.fetch_and_submit_otp(
                outlook_otp,
                timeout=180.0,
                refresh_interval=5.0,
                preferred_sender=getattr(self, "_preferred_otp_sender", None),
                max_attempts=2,
            )

            if not otp_submitted:
                raise RuntimeError("OTP retrieval failed during e-signature flow")

            logger.info("[common_otp] Completed")
        finally:
            if outlook_page:
                logger.info("[common_otp] Closing Outlook OTP tab")
                outlook_page.close()

    """Page object for DocuSign signing flow"""

    PAGE_NAME = "DOCUSIGN PAGE"

    def __init__(self, page: Page):
        super().__init__(page)
        self._outlook_page_for_by_mail = None
        self._review_documents_page = None
        self._by_mail_tracking_center_href = None
        self._by_mail_client_flow_active = False
        self._init_locators(page)

    def _init_locators(self, page: Page):
        loc = DocuSignLocators

        # Disclosure checkbox strategies
        self.disclosure_checkbox_exact: Locator = page.locator(
            "span[data-qa*='ersd-agree-checkbox-label-text']:has-text('I confirm I have read and I consent to the Electronic Record and Signature Disclosure.')"
        )
        self.checkbox: Locator = self.disclosure_checkbox_exact
        self.disclosure_checkbox_primary_text: Locator = page.locator("span").filter(has_text="I confirm I have read and I").first
        self.disclosure_checkbox_data_qa: Locator = page.locator("span[data-qa*='ersd-agree-checkbox-label-text']").first
        self.disclosure_checkbox_contains_text: Locator = page.get_by_text("I confirm I have read and I").first
        self.disclosure_checkbox_error: Locator = page.locator("p[data-qa='ersd-agree-checkbox-error']")
        self.continue_button_by_role: Locator = page.get_by_role("button", name=loc.CONTINUE_BUTTON)

        # Pre-OTP sign controls
        self.clientSignButton: Locator = page.locator("#signButton").first
        self.clientSignButtonBackup: Locator = page.get_by_role("button", name="Sign", exact=True)

        # OTP verification locators
        self.send_now_button: Locator = page.locator(loc.VERIFY_SEND_NOW_BUTTON).first
        self.send_now_button_by_role: Locator = page.get_by_role("button", name=re.compile(r"^\s*send\s*now\s*$", re.IGNORECASE)).first
        self.send_now_button_text: Locator = page.locator("button:has-text('Send Now')").first
        self.otp_code_input: Locator = page.locator(loc.VERIFY_OTP_INPUT)
        self.otp_verify_button: Locator = page.locator(
            "button[data-qa*='verify'], button:has-text('Verify'), button:has-text('Confirm')"
        )
        self.otp_confirm_code_button: Locator = page.get_by_role("button", name="Confirm Code")
        self.otp_error_label: Locator = page.locator(
            "//*[contains(text(),'Code is incorrect') or contains(text(),'Code must be 6 numbers')]"
        )
        self.resend_code_button: Locator = page.locator("button[data-qa='verify-resend-modal-link']")
        self.resend_code_primary_button: Locator = page.locator("button[data-qa='verify-resend-modal-primary-button']")
        self.navigate_next_button: Locator = page.locator("#navigate-btn")
        self.in_person_signing_modal: Locator = page.locator(
            "#prompt_to_leave_modalLabel.modal-title.modal-title-transition"
        )
        self.by_mail_sent_modal: Locator = page.locator(
            "#prompt_to_leave_modalLabel:has-text('Email Sent to Client(s)'), #prompt_to_leave_modalLabel:has-text('Email Sent to Financial Advisor')"
        ).first
        self.by_mail_tracking_center_link: Locator = page.locator(
            "#prompt_to_leave_modal a[href*='TrackingCenterItemDetail'], #prompt_to_leave_modal a[onclick*='TrackingCenterItemDetail']"
        ).first
        self.close_button: Locator = page.get_by_role("button", name="Close")
        self.close_button_fallback: Locator = page.locator("#close-button")

        # Disclosure/signature/finalization locators
        self.primary_sign_button: Locator = page.locator("#signButton, button[id*='Next']")
        self.sign_tab_first: Locator = page.locator(
            "xpath=(//div[contains(@class,'signature-tab-content')][.//div[contains(@class,'tab-text') and normalize-space()='Sign']])[1]"
        )
        self.sign_tab_all: Locator = page.locator(
            "xpath=//div[contains(@class,'signature-tab-content') and .//div[contains(@class,'tab-text') and normalize-space()='Sign']]"
        )
        self.loading_spinner: Locator = page.locator(".loading-spinner")
        self.diy_disclosure_iframe: Locator = page.locator('iframe[title="DIY Electronic Disclosure"]')
        self.required_sign_here_button: Locator = page.get_by_role("button", name="Required - Sign Here - Sign")
        self.required_initial_here_button: Locator = page.get_by_role("button", name="Required - Initial Here -").first
        self.adopt_and_sign_button: Locator = page.locator('button[data-qa="adopt-submit"], button:has-text("Adopt and Sign"), button:has-text("Adopt and Initial")')
        self.required_signature_tab_buttons: Locator = page.locator(loc.SIGNATURE_TAB_BUTTON)
        self.required_view_button: Locator = page.get_by_role("button", name="Required - View,")
        self.go_back_close_button: Locator = page.get_by_role("button", name="GO BACK Close")
        self.required_accept_button: Locator = page.get_by_role("button", name="Required - Accept,")
        self.finish_button_by_label: Locator = page.get_by_label("Finish")
        self.finish_button_action_bar: Locator = page.locator(loc.ACTION_BAR_FINISH_BUTTON)
        self.finish_button_slide_up_id: Locator = page.locator("#slide-up-bar-finish-button")
        self.finish_button_slide_up_data_qa: Locator = page.locator("button[data-qa='slide-up-bar-finish-button']")
        self.finish_button_mobile_id: Locator = page.locator(loc.END_OF_DOCUMENT_FINISH_BUTTON + "-mobile")
        self.finish_button_envelope_data_qa: Locator = page.locator(loc.FINISH_BUTTON)
        self.finish_button_by_role: Locator = page.get_by_role("button", name="Finish")
        self.send_now_fallback_buttons: Locator = page.locator("button", has_text=re.compile(r"send\s*now", re.IGNORECASE))
        self.eSingature_btn_disabled: Locator = page.locator("button#eSignatureButton[disabled='disabled']").first
        self.other_actions_button: Locator = page.get_by_role("button", name="Other Actions")
        self.finish_later_menu_item: Locator = page.get_by_role("menuitem", name="Finish Later")
        self.tracking_center_link: Locator = page.get_by_role("link", name="Tracking Center.")
        self.finish_later_dialog: Locator = page.get_by_role("dialog", name="Finish Later")
        self.finish_later_close_button: Locator = page.get_by_role("button", name="Close")

        # ERSD modal locators
        self.ersd_modal: Locator = page.locator(loc.ERSD_MODAL)
        self.ersd_modal_aria: Locator = page.locator(loc.ERSD_MODAL_ARIA)
        self.ersd_consent_checkbox: Locator = page.locator(loc.ERSD_CONSENT_CHECKBOX)
        self.ersd_consent_checkbox_label: Locator = page.locator(loc.ERSD_CONSENT_CHECKBOX_LABEL)
        self.ersd_continue_button: Locator = page.locator(loc.ERSD_CONTINUE_BUTTON)
        self.dialog_content: Locator = page.locator(loc.DIALOG_CONTENT)

        # Signature / adopt-modal / sign-button locators
        self.signature_tab_button: Locator = page.locator(loc.SIGNATURE_TAB_BUTTON)
        self.signature_applied_tab: Locator = page.get_by_role("button", name=re.compile(r"Required\s*-\s*Signature Applied"))
        self.adopt_signature_modal: Locator = page.locator(loc.ADOPT_SIGNATURE_MODAL)
        self.sign_button: Locator = page.locator(loc.SIGN_BUTTON)
        self.date_signed_input: Locator = page.locator(loc.DATE_SIGNED_INPUT)

        # D-number and eSignature process complete modal
        self.d_number_span: Locator = page.locator(loc.D_NUMBER_SPAN)
        self.esign_complete_modal: Locator = page.locator(loc.ESIGN_COMPLETE_MODAL)
        self.esign_complete_title: Locator = page.locator(loc.ESIGN_COMPLETE_TITLE)
        self.esign_d_number_link: Locator = page.locator(loc.ESIGN_D_NUMBER_LINK)
        self.request_submitted_link: Locator = page.locator('.printConfirmationLink')

    def e_signature_sign(
        self,
        first_name: str,
        second_name: str,
        reg_type: str,
        custodian: str,
        client_type: str,
        role: str,
        option: str,
        is_sub_advisory: str,
    ) -> None:
        logger.info("[esign] Starting e-signature signing flow")
        logger.info(
            f"[esign] Inputs | role={role}, option={option}, custodian={custodian}, reg_type={reg_type}, "
            f"client_type={client_type}, is_sub_advisory={is_sub_advisory}"
        )
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.wait_for_timeout(5000)
        self.capture_additional_screenshot(name=f"esign_start_{role.replace(' ', '_')}")
        if "Client" in role and "in person" in (option or "").lower():
            logger.info("[esign] Branch selected: Client + in person")
            self.otp_verification()
        elif "Client" in role and "by mail" in (option or "").lower():
            logger.info("[esign] Branch selected: Client + by mail")
            self.client_by_mail_eSignature()
        elif "Agent" in role and (custodian or "").strip().lower() == "fidelity":
            logger.info("[esign] Branch selected: Agent + Fidelity OTP verification")
            self.otp_verification()
        else:
            logger.info("[esign] No OTP pre-sign branch matched for current role/option/custodian")

        self.wait_for_timeout(5000)

        # Handle checkbox and continue flow
        try:
            self._handle_checkbox_and_continue(custodian, role)
        except Exception as e:
            logger.error(f"Failed to handle checkbox and continue: {str(e).splitlines()[0]}")
            raise RuntimeError(f"Failed to handle checkbox and continue: {e}")
        
        self.wait_for_timeout(5000)
        # Wait for signing interface to be ready before attempting to sign
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            self.wait_for_timeout(3000)

        if "Agent" in role:
            logger.info("[esign] Starting indexed signing for Agent")
            self._sign_indexed_elements("agent", reg_type, client_type, custodian)
            self.wait_for_timeout(5000)

        if "Client" in role:
            logger.info("[esign] Starting indexed signing for Client")
            self._sign_indexed_elements("client", reg_type, client_type, custodian)
            self.wait_for_timeout(5000)

        logger.info("[esign] Finalizing signature")
        self.capture_additional_screenshot(name="esign_before_finalize")
        self._finalize_signature()
        self.wait_for_timeout(5000)

        if self._by_mail_client_flow_active:
            self._close_by_mail_tabs()

    def e_signature_sign_tracking_center(
        self,
        first_name: str,
        second_name: str,
        reg_type: str,
        custodian: str,
        client_type: str,
        role: str,
        option: str,
        is_sub_advisory: str,
        action: str = "Finish Later",
    ) -> None:
        """eSignature flow with Finish Later option."""
        logger.info(f"[esign-fl] Starting e-signature signing flow with action: {action}")
        logger.info(
            f"[esign-fl] Inputs | role={role}, option={option}, custodian={custodian}, reg_type={reg_type}, "
            f"client_type={client_type}, is_sub_advisory={is_sub_advisory}, action={action}"
        )
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.wait_for_timeout(5000)
        self.capture_additional_screenshot(name=f"esign_tracking_center_start_{role.replace(' ', '_')}")

        # Handle checkbox and continue flow
        try:
            self._handle_checkbox_and_continue(custodian, role)
        except Exception as e:
            logger.error(f"Failed to handle checkbox and continue: {str(e).splitlines()[0]}")
            raise RuntimeError(f"Failed to handle checkbox and continue: {e}")
    
        self.wait_for_timeout(5000)
        # Wait for signing interface to be ready before attempting to sign
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            self.wait_for_timeout(3000)

        if "Agent" in role:
            logger.info("[esign-fl] Starting Agent Finish Later flow")
            self.selectDocuSignActions(action)

            from pages.ewm.view_documents_page import ViewDocumentsPage
            view_documents_page = ViewDocumentsPage(self.page, page_verification=False)
            view_documents_page.clickTrackingCenterLink()

            from pages.ewm.tracking_center_page import TrackingCenterPage
            tracking_center_page = TrackingCenterPage(self.page)

            # Track pages before clicking Sign — DocuSign may open in a new tab
            existing_pages = list(self.page.context.pages)
            tracking_center_page.clickESignatureLink(role="Agent")

            # Switch to new DocuSign tab if one was opened
            current_pages = list(self.page.context.pages)
            if len(current_pages) > len(existing_pages):
                self.page = current_pages[-1]
                logger.info("[esign-fl] Switched to new DocuSign tab for Agent")

            # Re-init locators and handle checkbox/continue on re-entered DocuSign page
            self._init_locators(self.page)
            try:
                self._handle_checkbox_and_continue(custodian, role)
            except Exception as e:
                logger.error(f"[esign-fl] Agent checkbox/continue failed after tracking center: {str(e).splitlines()[0]}")
                raise RuntimeError(f"Agent checkbox/continue failed: {e}")

            self.wait_for_timeout(5000)
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                self.wait_for_timeout(3000)

            self._sign_indexed_elements("agent", reg_type, client_type, custodian)
            self.wait_for_timeout(5000)

        if "Client" in role:
            logger.info("[esign-fl] Starting Client signing from Tracking Center")

            from pages.ewm.tracking_center_page import TrackingCenterPage
            tracking_center_page = TrackingCenterPage(self.page)
            tracking_center_page.clickESignatureLink(role="Client")
            self.otp_verification()

            # Re-init locators on the DocuSign page and handle checkbox/continue
            self._init_locators(self.page)
            try:
                self._handle_checkbox_and_continue(custodian, role)
            except Exception as e:
                logger.error(f"[esign-fl] Client checkbox/continue failed: {str(e).splitlines()[0]}")
                raise RuntimeError(f"Client checkbox/continue failed: {e}")

            self.wait_for_timeout(5000)
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                self.wait_for_timeout(3000)

            self._sign_indexed_elements("client", reg_type, client_type, custodian)
            self.wait_for_timeout(5000)

        logger.info("[esign-fl] Finalizing signature")
        self.capture_additional_screenshot(name="esign_tracking_center_before_finalize")
        self._finalize_signature()
        self.wait_for_timeout(5000)

        logger.info(f"[esign-fl] e-signature flow with {action} completed")

    def selectDocuSignActions(self, action: str = "Finish Later") -> None:
        """Click Other Actions > Finish Later on the DocuSign signing page."""
        logger.info("[esign-fl] Clicking 'Other Actions' button")
        try:
            self._heal_and_retry(self.other_actions_button, lambda loc: loc.click())
        except Exception:
            logger.warning("[esign-fl] Other Actions click failed, falling back to JS click")
            self.other_actions_button.evaluate("el => el.click()")
        self.wait_for_timeout(2000)

        if action == "Finish Later":
            logger.info("[esign-fl] Clicking 'Finish Later' menu item")
            try:
                self._heal_and_retry(self.finish_later_menu_item, lambda loc: loc.click())
            except Exception:
                logger.warning("[esign-fl] Finish Later click failed, falling back to JS click")
                self.finish_later_menu_item.evaluate("el => el.click()")
            self.wait_for_timeout(5000)
            logger.info("[esign-fl] 'Finish Later' selected successfully")

    def _handle_checkbox_and_continue(self, custodian: str = "", role: str = "") -> None:
        """Handle checkbox click and continue button."""

        logger.info("Handling checkbox and continue button click")

        custodian_value = (custodian or "").strip().lower()
        role_value = (role or "").strip().lower()

        diy_handled = False
        if custodian_value == "fidelity" and role_value in ["agent", "client"]:
            diy_handled = self.handle_diy_electronic_disclosure()
        else:
            logger.info("[handle_checkbox_and_continue] Skipping DIY disclosure; applicable only for Fidelity Agent/Client")

        if diy_handled:
            logger.info("DIY Electronic Disclosure handled, proceeding to continue button logic as well.")
        try:
            self.continue_button()
        except Exception as e:
            logger.error(f"[handle_checkbox_and_continue] Continue button logic failed: {str(e).splitlines()[0]}")
            raise RuntimeError(f"Continue button logic failed: {e}")

    def continue_button(self) -> None:
        # Try multiple locator strategies for the checkbox
        checkbox_strategies = [
            ("primary", self.disclosure_checkbox_primary_text),
            ("data-qa", self.disclosure_checkbox_data_qa),
            ("contains text", self.disclosure_checkbox_contains_text),
        ]
        
        checkbox_locator = None
        for strategy_name, locator in checkbox_strategies:
            try:
                locator.wait_for(state="visible", timeout=5000)
                checkbox_locator = locator
                break
            except Exception as e:
                logger.warning(f"[continue_button] Checkbox not found with {strategy_name} strategy: {str(e)[:80]}")
                continue
        
        if checkbox_locator is None:
            continue_locator_fallback = self.continue_button_by_role
            try:
                if continue_locator_fallback.is_visible(timeout=2000):
                    continue_locator_fallback.click()
                    logger.info("[continue_button] Checkbox not found; clicked Continue directly")
                    self.wait_for_timeout(5000)
                    return
            except Exception as e:
                logger.info(f"[continue_button] Continue direct-click fallback unavailable: {str(e)[:120]}")

            logger.info("[continue_button] Disclosure checkbox not found; likely not required for this signer state. Skipping continue flow.")
            return
        
        self.capture_additional_screenshot(name="continue_button_before_checkbox")
        try:
            checkbox_locator.scroll_into_view_if_needed()
            checkbox_locator.click()
            logger.info("[continue_button] Clicked disclosure checkbox")
            self.wait_for_timeout(5000)
        except Exception as e:
            logger.error(f"[continue_button] Failed to click disclosure checkbox: {str(e).splitlines()[0]}")
            raise RuntimeError("Continue button flow failed - disclosure checkbox was not clicked")

        continue_locator = self.continue_button_by_role
        try:
            continue_locator.wait_for(state="visible", timeout=10000)
            continue_locator.click()
            logger.info("[continue_button] Clicked Continue")
            try:
                continue_locator.wait_for(state="hidden", timeout=30000)
                logger.info("[continue_button] Consent dialog dismissed")
            except Exception:
                self.wait_for_timeout(5000)
        except Exception as e:
            logger.error(f"[continue_button] Failed to click Continue button: {str(e).splitlines()[0]}")
            raise RuntimeError("Continue button flow failed - Continue button was not clicked")

        # If checkbox reappears after Continue, click checkbox + Continue again
        try:
            if checkbox_locator.is_visible(timeout=5000):
                logger.info("[continue_button] Checkbox reappeared, retrying checkbox + Continue")
                checkbox_locator.click()
                self.wait_for_timeout(2000)
                continue_locator.click()
                try:
                    continue_locator.wait_for(state="hidden", timeout=30000)
                except Exception:
                    self.wait_for_timeout(5000)
                logger.info("[continue_button] Retry checkbox + Continue completed")
        except Exception:
            logger.info("[continue_button] Checkbox not reappearing, proceeding")

    def handle_diy_electronic_disclosure(self) -> bool:
        """Handle DIY Electronic Disclosure only when visible."""
        last_error = None
        for _ in range(3):
            try:
                self.diy_disclosure_iframe.wait_for(state="attached", timeout=5000)
                frame = self.diy_disclosure_iframe.content_frame

                if frame is None:
                    self.wait_for_timeout(1000)
                    continue

                disclosure_text = frame.get_by_text("By clicking the button below")
                if disclosure_text.first.is_visible(timeout=3000):
                    logger.info("[handle_diy_electronic_disclosure] Found DIY disclosure, clicking text button")
                    try:
                        disclosure_text.first.click()
                    except Exception:
                        logger.warning("[handle_diy_electronic_disclosure] Normal click failed, trying JS click")
                        disclosure_text.first.evaluate("el => el.click()")
                    self.wait_for_timeout(5000)

                    agree_button = frame.get_by_role("button", name="Agree")
                    if agree_button.first.is_visible(timeout=5000):
                        logger.info("[handle_diy_electronic_disclosure] Clicking Agree button")
                        try:
                            agree_button.first.click()
                        except Exception:
                            logger.warning("[handle_diy_electronic_disclosure] Agree normal click failed, trying JS click")
                            agree_button.first.evaluate("el => el.click()")
                        self.wait_for_timeout(5000)
                        logger.info("[handle_diy_electronic_disclosure] DIY disclosure handled successfully")
                        return True
                self.wait_for_timeout(1000)
            except Exception as e:
                last_error = e
                self.wait_for_timeout(1000)

        if last_error:
            logger.info(
                f"[handle_diy_electronic_disclosure] DIY iframe not found or not visible (expected): {str(last_error)[:100]}"
            )
        logger.info("[handle_diy_electronic_disclosure] DIY disclosure not visible, returning False")
        return False


    def _sign_indexed_elements(self, signer_type: str, registration_type: str, client_type: str, custodian: str = "") -> None:
        """Playwright-only signing flow for Agent/Client + Trust + Fidelity."""
        from tests.steps.naw.construct_portfolio_step import ConstructPortfolioStep

        signer = (signer_type or "").strip().lower()
        registration = (registration_type or "").strip().lower()
        custodian_name = (custodian or "").strip().lower()

        # Wait for DocuSign signing interface to be fully ready before any signing action
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            self.wait_for_timeout(5000)

        if (
            (signer == "agent" and registration == "trust" and custodian_name == "fidelity")
            or (signer == "agent" and "roth ira trust" in registration and "pershing" in custodian_name)
        ):
        
            try:
                self.required_sign_here_button.wait_for(state="visible", timeout=20000)
                self.required_sign_here_button.click()
                logger.info("[esign] Clicked Required - Sign Here")
            except Exception:
                logger.warning("[esign] Sign Here not found, clicking Initial Here instead")
                self.required_initial_here_button.wait_for(state="visible", timeout=10000)
                self.required_initial_here_button.click()
                logger.info("[esign] Clicked Required - Initial Here")
            self.wait_for_timeout(5000)
            self.click_adopt_and_sign_button()

        elif signer == "client" and registration == "trust" and custodian_name == "fidelity":
            # Dynamic loop: find all Sign/Initial tabs (divs or buttons), click actionable ones
            sign_or_initial_xpath = (
                "//div[(contains(@class,'signature-tab-content') and .//text()[contains(., 'Sign')]) "
                "or (contains(@class,'initials-tab-content') and contains(@class,'tab-button-cobalt') and contains(@class,'v2'))] "
                "| //button[contains(@id, 'tab-form-element') and contains(@class, 'tab-button')]//div[@class='tab-text' and text()='Sign']/.. "
                "| //button[.//div[contains(text(), 'Initial')]]"
            )
            max_empty_retries = 3
            empty_retry_count = 0

            while True:
                all_tabs = self.page.locator(f"xpath={sign_or_initial_xpath}")
                tab_count = all_tabs.count()
                actionable_found = False

                for i in range(tab_count):
                    tab = all_tabs.nth(i)
                    try:
                        if not tab.is_visible(timeout=1000):
                            continue
                    except Exception:
                        continue

                    aria_invalid = tab.get_attribute("aria-invalid") or ""
                    aria_hidden = tab.get_attribute("aria-hidden") or ""

                    if aria_invalid.lower() == "true" or aria_hidden.lower() == "true":
                        actionable_found = True
                        try:
                            tab.scroll_into_view_if_needed()
                            self.wait_for_timeout(500)
                            tab.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")
                        except Exception:
                            tab.click(force=True)
                        logger.info(f"[esign] Clicked Sign/Initial tab index={i}")
                        self.wait_for_timeout(1000)

                        # Adopt & Sign modal appears after clicking a signature tab
                        self.click_adopt_and_sign_button(post_click_wait_ms=3000)
                        self.click_finish_button_action_bar(post_click_wait_ms=3000)
                        break

                if not actionable_found:
                    empty_retry_count += 1
                    if empty_retry_count >= max_empty_retries:
                        break
                    self.wait_for_timeout(500)
                else:
                    empty_retry_count = 0

            logger.info("[esign] Client+Trust+Fidelity dynamic signing loop completed")

        elif signer == "client" and "401" in registration and custodian_name == "assetmark trust":
            self.click_finish_button_action_bar(post_click_wait_ms=3000)
            adopted = False
            # Initial Here tabs — adopt-and-initial dialog appears only on the first click
            for _ in range(10):
                initial_tab = self.page.locator("[data-qa^='initials-tab-required'][aria-invalid='true']").first
                try:
                    self.wait_for_element(initial_tab, state="visible", timeout=5000)
                    self.click(initial_tab)
                    if not adopted:
                        self.click_adopt_and_sign_button()
                        adopted = True
                    logger.info("[esign] Clicked required Initial Here tab")
                    self.click_finish_button_action_bar(post_click_wait_ms=3000)
                except Exception:
                    break
            # Sign Here tabs — no adopt dialog after first adoption
            for _ in range(10):
                sign_tab = self.page.locator("[data-qa^='signature-tab-required'][aria-invalid='true']").first
                try:
                    self.wait_for_element(sign_tab, state="visible", timeout=8000)
                    self.click(sign_tab)
                    logger.info("[esign] Clicked required Sign Here tab")
                    self.click_finish_button_action_bar(post_click_wait_ms=3000)
                except Exception:
                    break
            logger.info(f"[esign] Client 401k signing flow completed: signer={signer}, reg={registration}, custodian={custodian_name}")

        elif signer == "client" and "roth ira trust" in registration and "pershing" in custodian_name:
            self.click_sign_tab_element()

            self.click_adopt_and_sign_button()

            sign_here_button = self.page.get_by_role("button", name="Required\u00a0-\u00a0Sign Here - Sign")
            sign_here_first_button = self.page.get_by_role("button", name="Required\u00a0-\u00a0Sign Here - Sign").first

            self.click_finish_button_action_bar()

            self.click_sign_here_button(sign_here_button)

            self.click_finish_button_action_bar()

            self.click_sign_here_button(sign_here_first_button)

            self.click_finish_button_action_bar()

            self.click_sign_here_button(sign_here_button)

        elif signer == "agent" and registration == "self-directed brokerage account - 403(b)" and custodian_name == "schwab":
            self.click_required_sign_here_button(post_click_wait_ms=0)
            self.click_adopt_and_sign_button(post_click_wait_ms=0)
            self.required_initial_here_button.wait_for(state="visible", timeout=20000)
            self.required_initial_here_button.click()
            self.wait_for_timeout(3000)

        elif signer == "client" and registration == "self-directed brokerage account - 403(b)" and custodian_name == "schwab" and ConstructPortfolioStep.is_sub_advisory == "SubAdvisory":
            for required_index in range(1, 4):
                required_sign_btn = self.required_signature_tab_buttons.nth(required_index - 1)
                required_sign_btn.wait_for(state="visible", timeout=20000)
                required_sign_btn.click()

                if required_index == 1:
                    self.click_adopt_and_sign_button(post_click_wait_ms=0)

                self.wait_for_timeout(5000)

        elif signer == "client" and registration == "self-directed brokerage account - 403(b)" and custodian_name == "schwab" and ConstructPortfolioStep.is_sub_advisory == "Non SubAdvisory":
            self.click_sign_tab_element(post_click_wait_ms=3000)

            self.click_adopt_and_sign_button(post_click_wait_ms=3000)

            for _ in range(2):
                self.required_initial_here_button.wait_for(state="visible", timeout=20000)
                self.required_initial_here_button.click()
                self.wait_for_timeout(3000)

            sign_here_button = self.page.get_by_role("button", name="Required\u00a0-\u00a0Sign Here - Sign").first
            for _ in range(2):
                self.click_sign_here_button(sign_here_button, post_click_wait_ms=3000)
            logger.info("[esign] NonSubAdvisory Sign Here clicked")

            self.wait_for_timeout(5000)

        elif (signer == "agent" or signer == "client") and (
            (registration == "limited liability company" and custodian_name == "assetmark trust")
            or (registration == "beneficiary roth ira individual" and custodian_name == "schwab direct")
            or (signer == "agent" and registration == "traditional ira" and custodian_name == "fidelity direct")
        ):
            
            self.click_sign_tab_element(post_click_wait_ms=0)
            self.click_adopt_and_sign_button()

        elif (signer == "agent" or signer == "client") and (
            (registration == "individual" and custodian_name == "assetmark trust")
            or (signer == "agent" and "401" in registration and custodian_name == "assetmark trust")
        ):
             
            self.click_finish_button_action_bar(post_click_wait_ms=3000)
            self.click_required_sign_here_button(post_click_wait_ms=0)
            self.click_adopt_and_sign_button()
            logger.info(f"[esign] 401k signing flow for signer={signer}, registration={registration}, custodian={custodian_name}")


    def _finalize_signature(self) -> None:
        logger.info("Finalizing signature...")
        self.capture_additional_screenshot(name="finalize_signature_start")

        # Disclosure steps (View → GO BACK Close → Accept) - optional, not all flows have them
        required_view = self.required_view_button.first
        if required_view.is_visible(timeout=10000):
            try:
                required_view.click(timeout=8000)
                logger.info("[finalize_signature] Clicked Required - View")
            except Exception:
                try:
                    required_view.scroll_into_view_if_needed()
                    required_view.evaluate("el => el.click()")
                    logger.info("[finalize_signature] Clicked Required - View (JS fallback)")
                except Exception as e:
                    logger.error(f"[finalize_signature] Failed to click Required - View: {str(e).splitlines()[0]}")
                    raise RuntimeError("Finalize signature failed at Required - View")
            self.wait_for_timeout(5000)

            # GO BACK Close - only after View
            if self.go_back_close_button.is_visible(timeout=10000):
                try:
                    self.go_back_close_button.click()
                    logger.info("[finalize_signature] Clicked GO BACK Close")
                except Exception:
                    try:
                        self.go_back_close_button.evaluate("el => el.click()")
                        logger.info("[finalize_signature] Clicked GO BACK Close (JS fallback)")
                    except Exception as e:
                        logger.error(f"[finalize_signature] Failed to click GO BACK Close: {str(e).splitlines()[0]}")
                        raise RuntimeError("Finalize signature failed at GO BACK Close")
                self.wait_for_timeout(5000)
            else:
                logger.info("[finalize_signature] GO BACK Close not visible, skipping")

            # Required - Accept - only after View
            if self.required_accept_button.is_visible(timeout=10000):
                try:
                    self.required_accept_button.click()
                    logger.info("[finalize_signature] Clicked Required - Accept")
                except Exception:
                    try:
                        self.required_accept_button.evaluate("el => el.click()")
                        logger.info("[finalize_signature] Clicked Required - Accept (JS fallback)")
                    except Exception as e:
                        logger.error(f"[finalize_signature] Failed to click Required - Accept: {str(e).splitlines()[0]}")
                        raise RuntimeError("Finalize signature failed at Required - Accept")
                self.wait_for_timeout(5000)
            else:
                logger.info("[finalize_signature] Required - Accept not visible, skipping")
        else:
            logger.info("[finalize_signature] Required - View not visible, skipping disclosure steps")

        try:
            finish_locators = [
                (self.finish_button_action_bar, "#action-bar-btn-finish"),
                (self.finish_button_by_label, "label=Finish"),
                (self.finish_button_slide_up_id, "#slide-up-bar-finish-button"),
                (self.finish_button_slide_up_data_qa, "data-qa=slide-up-bar-finish-button"),
                (self.finish_button_mobile_id, "#end-of-document-btn-finish-mobile"),
                (self.finish_button_envelope_data_qa, "data-qa=envelope-finish"),
                (self.finish_button_by_role, "role=button[name='Finish']"),
            ]

            last_error = None
            finish_clicked = False

            def _try_click_finish(locator: Locator, locator_name: str) -> bool:
                nonlocal last_error
                try:
                    locator.wait_for(state="visible", timeout=5000)
                    locator.click(timeout=5000)
                    logger.info(f"Clicked Finish Button via {locator_name}")
                    return True
                except Exception as visible_error:
                    last_error = visible_error
                try:
                    locator.wait_for(state="attached", timeout=3000)
                    locator.scroll_into_view_if_needed()
                    locator.click(timeout=3000, force=True)
                    logger.info(f"Clicked Finish Button via {locator_name} (force)")
                    return True
                except Exception as force_error:
                    last_error = force_error
                # JS fallback
                try:
                    locator.wait_for(state="attached", timeout=3000)
                    locator.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")
                    logger.info(f"Clicked Finish Button via {locator_name} (JS fallback)")
                    return True
                except Exception as js_error:
                    last_error = js_error
                    return False

            for finish_locator, locator_name in finish_locators:
                if _try_click_finish(finish_locator, locator_name):
                    finish_clicked = True
                    break

            if not finish_clicked:
                self.wait_for_timeout(3000)
                for finish_locator, locator_name in finish_locators:
                    if _try_click_finish(finish_locator, locator_name):
                        finish_clicked = True
                        break

            if not finish_clicked:
                self.capture_additional_screenshot(name=f"finalize_finish_not_found_{int(time.time())}")
                Assertions.fail(
                    f"[finalize_signature] HARD FAIL: Finish button not found or not clickable after trying all "
                    f"7 locator strategies. Last error: {last_error}"
                )

            self.wait_for_timeout(5000)
        except AssertionError:
            raise
        except Exception as e:
            self.capture_additional_screenshot(name=f"finalize_finish_exception_{int(time.time())}")
            Assertions.fail(f"[finalize_signature] HARD FAIL: Finish button click failed unexpectedly: {str(e).splitlines()[0]}")

    def fetch_n_number(self) -> None:
        logger.info("[by-mail] Fetching N number from page URL")

        # Wait for redirect back to eWealthManager with externalId in URL
        try:
            self.page.wait_for_url(
                lambda url: "externalId=N" in url,
                timeout=90000,
            )
        except Exception:
            logger.warning(f"[by-mail] URL redirect wait timed out, current URL: {self.page.url}")

        url_match = re.search(r"externalId=(N\d+)", self.page.url)
        assert url_match, f"[by-mail] Failed to fetch N number. Page URL: {self.page.url}"

        DocuSignPage.nNumber = url_match.group(1)
        logger.info(f"[by-mail] Captured tracking number: {DocuSignPage.nNumber}")
        self.capture_additional_screenshot(name=f"fetch_n_number_{DocuSignPage.nNumber}")

        self.click_close_button()
        
    def click_review_document_link(self) -> Page | None:
        """Open Tracking Center item detail link captured from by-mail modal and click REVIEW DOCUMENTS."""
        href_value = (self._by_mail_tracking_center_href or "").strip()
        if not href_value:
            logger.info("[by-mail] No Tracking Center href captured from modal")
            return None

        try:
            tracking_center_url = urljoin(self.page.url, href_value)
            logger.info(f"[by-mail] Fallback: opening Tracking Center URL directly: {tracking_center_url}")

            tracking_page = self.page.context.new_page()
            tracking_page.goto(tracking_center_url, wait_until="domcontentloaded", timeout=30000)
            tracking_page.wait_for_load_state("domcontentloaded", timeout=30000)

            review_documents_link = tracking_page.get_by_role("link", name="REVIEW DOCUMENTS", exact=True).first
            review_documents_link.wait_for(state="visible", timeout=20000)

            with tracking_page.context.expect_page(timeout=30000) as new_page_info:
                review_documents_link.click()

            review_page = new_page_info.value
            review_page.wait_for_load_state("domcontentloaded", timeout=30000)
            logger.info(f"[by-mail] Fallback succeeded: REVIEW DOCUMENTS opened at {review_page.url}")

            try:
                if not tracking_page.is_closed():
                    tracking_page.close()
            except Exception:
                pass

            return review_page
        except Exception as e:
            logger.warning(f"[by-mail] Fallback via Tracking Center link failed: {str(e).splitlines()[0]}")
            return None

    def client_by_mail_eSignature(self) -> None:
        """For by-mail client flow: use Outlook tracking search to open REVIEW DOCUMENTS, then Send Now + OTP using tab2/tab3."""
        self._by_mail_client_flow_active = True
        if not DocuSignPage.nNumber:
            logger.warning("[by-mail] Tracking number not available; skipping Outlook tracking flow")
            return

        outlook_page = None
        try:
            outlook_page = self.page.context.new_page()
            self._outlook_page_for_by_mail = outlook_page

            outlook_otp = OutlookOTPPage(outlook_page)
            review_page = outlook_otp.open_client_review_documents_page(DocuSignPage.nNumber)

            if not review_page:
                logger.warning("[by-mail] First attempt failed; retrying with a fresh Outlook tab")
                try:
                    if outlook_page and not outlook_page.is_closed():
                        outlook_page.close()
                except Exception:
                    pass
                outlook_page = self.page.context.new_page()
                self._outlook_page_for_by_mail = outlook_page
                outlook_otp = OutlookOTPPage(outlook_page)
                review_page = outlook_otp.open_client_review_documents_page(DocuSignPage.nNumber)

            if not review_page:
                Assertions.fail(
                    f"Tracking number result not found / REVIEW DOCUMENTS page not opened for tracking '{DocuSignPage.nNumber}'"
                )

            self._review_documents_page = review_page
            self.page = review_page
            self._init_locators(self.page)
            self.capture_additional_screenshot(name="by_mail_review_tab_opened")

            self.click_send_now()
            otp_submitted = self.fetch_and_submit_otp(
                outlook_otp,
                timeout=120.0,
                refresh_interval=5.0,
                preferred_sender=getattr(outlook_otp, "_preferred_otp_sender", None),
                max_attempts=2,
            )
            if not otp_submitted:
                Assertions.fail("OTP not found/submitted from existing Outlook tab")
            logger.info("[by-mail] OTP submitted on REVIEW DOCUMENTS tab")
        except Exception as e:
            logger.warning(f"[by-mail] Failed during Outlook tracking/OTP workflow: {str(e).splitlines()[0]}")
            raise

    def agentSignature_internal_admin_flow(self, reg_type: str, client_type: str, custodian: str) -> None:
        """Agent signs via Outlook using N number captured from Internal Admin eSign."""
        n_number = DocuSignPage.nNumber
        assert n_number, "[agent-outlook] N number not available from Internal Admin eSign"

        outlook_page = self.page.context.new_page()
        review_page = None
        try:
            outlook_otp = OutlookOTPPage(outlook_page)
            review_page = outlook_otp.open_client_review_documents_page(n_number)
            assert review_page, f"[agent-outlook] REVIEW DOCUMENTS not opened for '{n_number}'"

            docusign_page = DocuSignPage(review_page)
            docusign_page.page.wait_for_load_state("domcontentloaded", timeout=30000)
            docusign_page.wait_for_timeout(5000)
            docusign_page.capture_additional_screenshot(name="agent_internal_admin_review_tab")

            # OTP verification before signing
            docusign_page.click_send_now()
            otp_submitted = docusign_page.fetch_and_submit_otp(
                outlook_otp, timeout=180.0, refresh_interval=5.0, max_attempts=2,
            )
            if not otp_submitted:
                raise RuntimeError("[agent-outlook] OTP verification failed")
            logger.info("[agent-outlook] OTP verification completed")
            docusign_page._handle_checkbox_and_continue(custodian, "Agent")
            docusign_page.wait_for_timeout(5000)

            try:
                docusign_page.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                docusign_page.wait_for_timeout(3000)

            docusign_page._sign_indexed_elements("agent", reg_type, client_type, custodian)
            docusign_page.wait_for_timeout(5000)
            docusign_page.capture_additional_screenshot(name="agent_internal_admin_before_finalize")

            docusign_page._finalize_signature()
            docusign_page.wait_for_timeout(5000)
            logger.info("[agent-outlook] Agent eSignature completed")
        finally:
            for tab in (review_page, outlook_page):
                if tab and not tab.is_closed():
                    try:
                        tab.close()
                    except Exception:
                        pass

    def _close_by_mail_tabs(self) -> None:
        """Close tab2 (Outlook) and tab3 (Review Documents) after by-mail completion."""
        for tab in (self._review_documents_page, self._outlook_page_for_by_mail):
            if tab is None:
                continue
            try:
                if not tab.is_closed():
                    tab.close()
            except Exception as e:
                logger.warning(f"[by-mail] Failed to close tab: {str(e).splitlines()[0]}")

        self._review_documents_page = None
        self._outlook_page_for_by_mail = None
        self._by_mail_client_flow_active = False

    def _fetch_and_submit_otp_from_outlook(self) -> None:
        """Fetch OTP from Outlook and submit it in DocuSign."""
        outlook_page = None
        try:
            logger.info("Starting OTP flow")
            # Open Outlook in a new tab within the same context
            outlook_page = self.page.context.new_page()

            # Initialize Outlook page
            outlook_otp = OutlookOTPPage(outlook_page)

            otp_submitted = self.fetch_and_submit_otp(
                outlook_otp,
                timeout=180.0,
                refresh_interval=5.0,
                preferred_sender=getattr(self, "_preferred_otp_sender", None),
                max_attempts=2,
            )

            if not otp_submitted:
                logger.error("Failed to fetch OTP from Outlook")
                raise RuntimeError("OTP retrieval failed during e-signature flow")

            logger.info("OTP flow completed")

        except Exception as e:
            logger.warning(f"Outlook OTP flow failed: {str(e).splitlines()[0]}")
            raise  # Re-raise the exception to stop execution
        finally:
            if outlook_page:
                logger.info("Closing Outlook OTP tab")
                outlook_page.close()

    def fetch_and_submit_otp(
        self,
        outlook_otp: OutlookOTPPage,
        timeout: float = 120.0,
        refresh_interval: float = 5.0,
        preferred_sender: str = None,
        max_attempts: int = 2,
    ) -> bool:
        """Fetch and submit OTP with retry attempts."""
        max_missing_otp_resends = 2
        max_incorrect_otp_resends = 3
        max_total_attempts = max(max_attempts, 1 + max_missing_otp_resends + max_incorrect_otp_resends)

        missing_otp_resends = 0
        incorrect_otp_resends = 0
        attempt = 0

        while attempt < max_total_attempts:
            attempt += 1
            otp_code = outlook_otp.get_otp_with_retry(
                timeout=timeout,
                refresh_interval=refresh_interval,
                sent_after_epoch=getattr(self, "_last_send_now_epoch", None),
                preferred_sender=preferred_sender,
            )

            if not otp_code:
                if missing_otp_resends < max_missing_otp_resends:
                    missing_otp_resends += 1
                    logger.warning(
                        f"OTP not fetched on attempt {attempt}; triggering resend "
                        f"({missing_otp_resends}/{max_missing_otp_resends})"
                    )
                    self._click_resend_code_button()
                    continue
                continue

            try:
                # Ensure submit happens on current DocuSign/review page
                self.page.bring_to_front()
                self._init_locators(self.page)
                self.submit_otp(otp_code)
                logger.info("OTP submitted successfully")
                return True
            except RuntimeError as otp_error:
                message = str(otp_error)
                if "Code is incorrect" in message:
                    if incorrect_otp_resends < max_incorrect_otp_resends:
                        incorrect_otp_resends += 1
                        logger.warning(
                            f"Incorrect OTP on attempt {attempt}; triggering resend "
                            f"({incorrect_otp_resends}/{max_incorrect_otp_resends})"
                        )
                        self._click_resend_code_button()
                        continue
                    Assertions.assert_true(False, "OTP verification failed after max incorrect-OTP retries")
                raise

        logger.error(
            f"OTP attempts exhausted without success | attempts={attempt}, "
            f"missing_otp_resends={missing_otp_resends}/{max_missing_otp_resends}, "
            f"incorrect_otp_resends={incorrect_otp_resends}/{max_incorrect_otp_resends}"
        )
        return False

    def _click_resend_code_button(self) -> None:
        """Click Resend Code when OTP is incorrect."""
        self.page.bring_to_front()

        # Check if DocuSign has locked out due to too many attempts
        auth_limit_text = self.page.locator("text=You've reached the authentication limit")
        if auth_limit_text.is_visible(timeout=2000):
            raise RuntimeError(
                "DocuSign authentication limit reached — too many OTP attempts. "
                "Cannot resend code. The envelope must be re-sent."
            )

        resend_button = self.resend_code_button
        resend_button.wait_for(state="visible", timeout=10000)
        resend_button.click(timeout=5000)
        self.page.wait_for_timeout(3000)

        resend_primary_button = self.resend_code_primary_button
        resend_primary_button.wait_for(state="visible", timeout=10000)
        resend_primary_button.click(timeout=5000)

        self._last_send_now_epoch = time.time()
        self.page.wait_for_timeout(3000)
        logger.info("Clicked Resend Code")

    def click_send_now(self) -> None:
        """Click the Send Now button to trigger OTP email in DocuSign"""
        try:
            self.page.bring_to_front()
            self._init_locators(self.page)
            self.capture_additional_screenshot(name="send_now_before_click")

            for locator, label in (
                (self.send_now_button, "data-qa locator"),
                (self.send_now_button_by_role, "role locator"),
                (self.send_now_button_text, "text locator"),
            ):
                try:
                    locator.wait_for(state="visible", timeout=10000)
                    if not locator.is_enabled():
                        continue
                    locator.scroll_into_view_if_needed()
                    locator.click(timeout=5000)
                    self._last_send_now_epoch = time.time()
                    logger.info("Send Now Button Clicked")
                    self.capture_additional_screenshot(name="send_now_after_click")
                    self.wait_for_timeout(15000)
                    return
                except Exception:
                    continue

            # Final fallback: pick any visible+enabled Send Now-like button and click first match
            fallback_buttons = self.send_now_fallback_buttons
            fallback_count = fallback_buttons.count()
            for index in range(fallback_count):
                candidate = fallback_buttons.nth(index)
                try:
                    if candidate.is_visible(timeout=1000) and candidate.is_enabled(timeout=1000):
                        candidate.scroll_into_view_if_needed()
                        candidate.click(timeout=5000)
                        self._last_send_now_epoch = time.time()
                        logger.info("Send Now Button Clicked")
                        self.wait_for_timeout(15000)
                        return
                except Exception:
                    continue

            raise RuntimeError("Send Now button not found or not visible")
        except Exception as e:
            try:
                os.makedirs("reports/screenshots", exist_ok=True)
                screenshot_path = f"reports/screenshots/send_now_missing_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.error(f"Send Now button FAILED - screenshot saved: {screenshot_path}")
                logger.error(f"Current URL: {self.page.url}")
            except Exception as screenshot_error:
                logger.warning(f"Failed to capture Send Now screenshot: {screenshot_error}")
            logger.error(f"ERROR: {str(e).splitlines()[0]}")
            raise

    def verify_e_signature_status(self, role: str, option: str, agent_text: str) -> None:
        logger.info(f"Verifying eSignature status for {role} with option: {option}")

        role_value = (role or "").lower()
        option_value = (option or "").lower()
        advisory_value = (agent_text or "").lower()
        is_agent_or_client = ("agent" in role_value) or ("client" in role_value)

        if "agent" in role_value and advisory_value == "subadvisory":
            Assertions.assert_true(
                self.eSingature_btn_disabled.is_visible(timeout=15000),
                "Expected disabled eSignature button for Agent SubAdvisory flow",
            )
            logger.info("Verified disabled eSignature button for Agent SubAdvisory flow")
            return

        # Wait for page to navigate back from DocuSign to eWealthManager
        try:
            self.page.wait_for_url(
                lambda url: "docusign" not in url.lower() and "ewealthmanager" in url.lower(),
                timeout=90000,
            )
            logger.info(f"[verify_esig] Navigated back to eWealthManager: {self.page.url}")
        except Exception as nav_error:
            logger.warning(f"[verify_esig] Navigation wait timed out, current URL: {self.page.url} | {nav_error}")

        # Extract N number from URL externalId parameter
        current_url = self.page.url
        n_match = re.search(r"externalId=(N\d+)", current_url)
        if n_match:
            DocuSignPage.nNumber = n_match.group(1)
            logger.info(f"[verify_esig] Extracted N number from URL: {DocuSignPage.nNumber}")
        else:
            logger.warning(f"[verify_esig] externalId N number not found in URL: {current_url}")

        # Re-initialize locators on the current (returned) page
        self._init_locators(self.page)

        if is_agent_or_client and "in person" in option_value:
            try:
                self.in_person_signing_modal.wait_for(state="visible", timeout=15000)
                in_person_modal_visible = True
            except Exception:
                in_person_modal_visible = False

            Assertions.assert_true(
                in_person_modal_visible,
                f"eSignature status verification failed for role '{role}': "
                f"expected in-person signing modal was not visible within 15s",
            )
            logger.info(f"[verify_esig] N number: {DocuSignPage.nNumber}")
            # Click Sign button on the in-person modal
            try:
                if self.clientSignButton.is_visible(timeout=5000):
                    self.clientSignButton.click()
                    logger.info("[verify_esig] Clicked Sign button on in-person modal")
                elif self.clientSignButtonBackup.is_visible(timeout=3000):
                    self.clientSignButtonBackup.click()
                    logger.info("[verify_esig] Clicked Sign button (backup) on in-person modal")
                else:
                    logger.warning("[verify_esig] Sign button not visible on in-person modal")
            except Exception as sign_err:
                logger.warning(f"[verify_esig] Failed to click Sign on in-person modal: {sign_err}")
            logger.info(f"{role} signature completed")

        elif is_agent_or_client and "by mail" in option_value:
            try:
                self.by_mail_sent_modal.wait_for(state="visible", timeout=15000)
                by_mail_modal_visible = True
            except Exception:
                by_mail_modal_visible = False

            Assertions.assert_true(
                by_mail_modal_visible,
                f"eSignature status verification failed for role '{role}': "
                f"expected by-mail confirmation modal was not visible within 15s",
            )
            logger.info(f"[verify_esig] N number: {DocuSignPage.nNumber}")
            self.click_close_button()
            logger.info(f"{role} signature completed")

        logger.info(f"eSignature process for {role} with {option} option completed")

    def e_signature_sign_by_mail(
        self,
        first_name: str,
        second_name: str,
        reg_type: str,
        custodian: str,
        client_type: str,
        role: str,
        option: str,
        is_sub_advisory: str,
        outlook_email: str,
        outlook_password: str,
    ) -> None:
      
        logger.info(f"Starting eSignature signing for 'by mail' option")
        
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        
        self.wait_for_timeout(1000)
        
        # Handle checkbox
        self._handle_checkbox_and_continue(custodian, role)
        
        # Get OTP from email
        logger.info("Retrieving OTP for 'by mail' eSignature")
        otp_code = self._get_otp_from_outlook(outlook_email, outlook_password)
        
        if not otp_code:
            logger.error("Failed to retrieve OTP from Outlook")
            raise RuntimeError("OTP retrieval failed")
        
        # Handle OTP verification
        self.submit_otp(otp_code)
        
        # Sign document
        if "Agent" in role:
            self._sign_indexed_elements("agent", reg_type, client_type, custodian)
        
        if "Client" in role:
            self._sign_indexed_elements("client", reg_type, client_type, custodian)
        
        # Finalize signature
        self._finalize_signature()
        
        logger.info("eSignature 'by mail' signing completed")

    def _get_otp_from_outlook(self, outlook_email: str = None, outlook_password: str = None, max_retries: int = 3) -> str:
        """Retrieve OTP from Outlook using a new tab in the same browser context."""
        logger.info("Opening Outlook in a new tab for OTP retrieval")
        
        try:
            # Open Outlook in a new tab within the same context
            outlook_page = self.page.context.new_page()
            
            # Create OutlookOTPPage instance
            outlook_otp = OutlookOTPPage(outlook_page)
            
            # Retrieve OTP with retries (will load from config if credentials are None)
            otp = outlook_otp.get_otp_with_retry(
                timeout=120.0,
                refresh_interval=5.0,
            )
            
            # Close Outlook tab
            outlook_page.close()
            
            if not otp:
                logger.error("Failed to retrieve OTP from Outlook")
                raise RuntimeError("OTP not found in email")
            
            return otp
            
        except Exception as e:
            logger.error(f"Error retrieving OTP from Outlook: {str(e).splitlines()[0]}")
            raise

    def submit_otp(self, otp_code: str) -> bool:
        logger.info("Submitting OTP verification")

        try:
            self.page.bring_to_front()

            # Fail fast if DocuSign locked out
            auth_limit_text = self.page.locator("text=You've reached the authentication limit")
            if auth_limit_text.is_visible(timeout=2000):
                raise RuntimeError(
                    "DocuSign authentication limit reached — too many OTP attempts."
                )

            otp_input = self.otp_code_input

            otp_input.wait_for(state="visible", timeout=30000)
            otp_input.scroll_into_view_if_needed()
            self.capture_additional_screenshot(name="otp_before_fill")

            # Fill and verify the input value actually took effect
            otp_input.fill(otp_code)
            self.page.wait_for_timeout(300)

            try:
                current_val = otp_input.input_value(timeout=2000)
            except Exception:
                current_val = None

            if current_val != otp_code:
                logger.warning(f"[otp_submit] OTP input value mismatch (got={current_val}), refilling once")
                otp_input.fill(otp_code)
                self.page.wait_for_timeout(300)

            # Click Confirm/Verify
            if self.otp_confirm_code_button.is_visible(timeout=3000):
                self.otp_confirm_code_button.click(timeout=8000)
            elif self.otp_verify_button.first.is_visible(timeout=3000):
                self.otp_verify_button.first.click(timeout=8000)
            else:
                self.capture_additional_screenshot(name=f"otp_submit_no_confirm_button_{int(time.time())}")
                raise RuntimeError("OTP submit button not found (Confirm Code/Verify not visible)")

            # Wait for either success (OTP input disappears) or failure (error label appears)
            end_time = time.time() + 30
            while time.time() < end_time:
                # Error?
                try:
                    if self.otp_error_label.is_visible(timeout=500):
                        error_text = self.otp_error_label.text_content() or "OTP error"
                        if "Code is incorrect" in error_text:
                            self.capture_additional_screenshot(name=f"otp_incorrect_{int(time.time())}")
                        raise RuntimeError(f"OTP verification failed: {error_text}")
                except RuntimeError:
                    raise
                except Exception:
                    pass

                # Success?
                try:
                    if not otp_input.is_visible(timeout=500):
                        return True
                except Exception:
                    # DOM changed; treat as likely success
                    logger.info("OTP verification likely completed (input visibility check failed due to DOM change)")
                    return True

                self.page.wait_for_timeout(500)

            self.capture_additional_screenshot(name=f"otp_submit_timeout_{int(time.time())}")
            raise RuntimeError("OTP verification did not complete (timeout waiting for success/error)")

        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Error during OTP verification: {str(e).splitlines()[0]}")
            raise

    def click_adopt_and_sign_button(self, post_click_wait_ms: int = 5000) -> None:
        # Try multiple locator strategies — DocuSign may show "Adopt and Sign" or "Adopt and Initial"
        adopt_locators = [
            (self.adopt_and_sign_button.first, "data-qa/has-text"),
            (self.page.get_by_role("button", name=re.compile(r"adopt\s*and\s*(sign|initial)", re.IGNORECASE)).first, "role regex"),
            (self.page.locator("button").filter(has_text=re.compile(r"adopt\s*and\s*(sign|initial)", re.IGNORECASE)).first, "filter regex"),
            (self.page.locator("button[data-qa*='adopt']").first, "data-qa contains adopt"),
        ]
        btn = None
        for locator, label in adopt_locators:
            try:
                locator.wait_for(state="visible", timeout=5000)
                btn = locator
                logger.info(f"[esign] Adopt and Sign found via {label}")
                break
            except Exception:
                continue

        if btn is None:
            self.capture_additional_screenshot(name=f"adopt_sign_not_found_{int(time.time())}")
            logger.warning("[esign] Adopt and Sign button not visible with any locator, skipping click")
            return

        self.capture_additional_screenshot(name="adopt_and_sign_before_click")
        self.click(btn)
        logger.info("[esign] Adopt and Sign clicked")
        self.wait_for_timeout(post_click_wait_ms)

    def click_required_sign_here_button(self, post_click_wait_ms: int = 5000) -> None:
        try:
            self.required_sign_here_button.wait_for(state="visible", timeout=20000)
        except Exception:
            logger.warning("[esign] Required Sign Here button not visible after 20s wait, skipping click")
            return
        self._click_element_with_strategies(self.required_sign_here_button, "Required Sign Here")
        self.wait_for_timeout(post_click_wait_ms)

    def click_sign_here_div_tab(self, post_click_wait_ms: int = 5000) -> None:
        """Click Sign div tab (div#tab-form-element-<guid> with aria-hidden). Uses JS click."""
        sign_el = self.page.locator(
            "xpath=(//div[starts-with(@id,'tab-form-element-')][.//div[contains(@class,'tab-text') and normalize-space()='Sign']])[1]"
        )
        try:
            sign_el.wait_for(state="attached", timeout=15000)
        except Exception:
            sign_el = self.page.locator("div.signature-tab-content:has(svg[data-qa='signature-icon'])").first
            try:
                sign_el.wait_for(state="attached", timeout=10000)
            except Exception:
                logger.warning("[esign] Sign div tab not found, skipping")
                return
        try:
            sign_el.evaluate("el => { el.scrollIntoView({block:'center'}); el.click(); }")
        except Exception:
            sign_el.click(force=True)
        logger.info("[esign] Clicked Sign Here div tab")
        self.wait_for_timeout(post_click_wait_ms)

    def click_sign_tab_element(self, post_click_wait_ms: int = 5000) -> None:
        tab_element = self.sign_tab_first
        try:
            tab_element.wait_for(state="visible", timeout=20000)
        except Exception:
            logger.warning("[esign] Sign tab element not visible after 20s wait, skipping click")
            return
        self._click_element_with_strategies(tab_element, "Sign tab")
        self.wait_for_timeout(post_click_wait_ms)

    def click_finish_button_action_bar(self, post_click_wait_ms: int = 5000) -> None:
        try:
            self.finish_button_action_bar.wait_for(state="visible", timeout=20000)
        except Exception:
            logger.warning("[esign] Finish button not visible after 20s, scrolling to bottom and retrying")
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.wait_for_timeout(2000)
            self.finish_button_action_bar.wait_for(state="visible", timeout=15000)
        self._click_element_with_strategies(self.finish_button_action_bar, "Finish button")
        self.wait_for_timeout(post_click_wait_ms)

    def click_sign_here_button(self, sign_here_locator: Locator, post_click_wait_ms: int = 5000) -> None:
        sign_here_locator.wait_for(state="visible", timeout=20000)
        sign_here_locator.click()
        self.wait_for_timeout(post_click_wait_ms)

    def click_close_button(self) -> None:
        contexts = [self.page]
        try:
            iframe_element = self.page.query_selector("#iframeWrapper")
            iframe = iframe_element.content_frame() if iframe_element else None
            if iframe:
                contexts.append(iframe)
        except Exception:
            pass

        selectors = ["role", "#prompt_to_leave_modal button:has-text('Close')", "#close-button"]
        for ctx in contexts:
            for sel in selectors:
                locator = ctx.get_by_role("button", name="Close", exact=True).first if sel == "role" else ctx.locator(sel).first
                try:
                    locator.wait_for(state="visible", timeout=1500)
                    try:
                        locator.click(timeout=2000)
                    except Exception:
                        locator.click(force=True, timeout=2000)
                    logger.info("[by-mail] Close button clicked")
                    return
                except Exception:
                    continue

        logger.error("[by-mail] Unable to click Close button in page or iframe context")

    def get_d_number(self, timeout: int = 60000) -> str:
        logger.info(f"[get_d_number] Waiting for D-number span (timeout={timeout}ms)")
        try:
            locator = self.d_number_span.first
            locator.wait_for(state="visible", timeout=timeout)
            text = (locator.text_content() or "").strip()
            if not text:
                raise AssertionError("D-number span found but text is empty")
            logger.info(f"[get_d_number] D-number: {text}")
            return text
        except Exception as e:
            raise AssertionError(f"Failed to fetch D-number from DocuSign page: {e}") from e

    def check_ersd_consent_checkbox(self, timeout: int = 120000) -> None:
        logger.info("[ersd] Clicking ERSD consent checkbox")
        for strategy in (
            self.disclosure_checkbox_primary_text,
            self.disclosure_checkbox_data_qa,
            self.disclosure_checkbox_contains_text,
        ):
            try:
                strategy.wait_for(state="visible", timeout=5000)
                strategy.scroll_into_view_if_needed()
                strategy.click()
                logger.info("[ersd] ERSD consent checkbox clicked")
                return
            except Exception:
                continue
        try:
            self.ersd_consent_checkbox_label.wait_for(state="visible", timeout=timeout)
            self.ersd_consent_checkbox_label.click()
            logger.info("[ersd] ERSD consent checkbox clicked via label fallback")
        except Exception as e:
            logger.warning(f"[ersd] Could not click ERSD checkbox: {str(e)[:120]}")

    def click_ersd_continue_button(self, timeout: int = 120000) -> None:
        logger.info("[ersd] Clicking ERSD Continue button")
        try:
            self.continue_button_by_role.wait_for(state="visible", timeout=timeout)
            self.continue_button_by_role.click()
            try:
                self.continue_button_by_role.wait_for(state="hidden", timeout=30000)
            except Exception:
                self.wait_for_timeout(3000)
            logger.info("[ersd] ERSD Continue button clicked")
        except Exception as e:
            logger.error(f"[ersd] Failed to click ERSD Continue button: {str(e)[:120]}")
            raise RuntimeError(f"ERSD Continue button not clickable: {e}")

    def verify_docusign_url(self, timeout: int = 60000) -> str:
        logger.info("[verify_docusign_url] Waiting for DocuSign URL...")
        try:
            self.page.wait_for_url(
                lambda url: "docusign.com/sign" in url,
                timeout=timeout,
            )
        except Exception as e:
            raise AssertionError(
                f"[FAIL] DocuSign URL not detected within {timeout / 1000}s. "
                f"Current URL: {self.page.url}. Error: {str(e).splitlines()[0]}"
            ) from e

        current_url = self.page.url
        assert "docusign.com" in current_url, (
            f"[FAIL] Expected URL to contain 'docusign.com', got: {current_url}"
        )
        logger.info(f"[PASS] DocuSign URL verified: {current_url}")
        try:
            allure.attach(
                self.page.screenshot(),
                name="DocuSign - URL Verified",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        return current_url

    def scroll_to_last_page_and_sign(self, timeout: int = 60000) -> None:
        logger.info("[scroll_and_sign] Scrolling to Sign button...")
        try:
            self.signature_tab_button.first.wait_for(state="visible", timeout=timeout)
            self.signature_tab_button.first.scroll_into_view_if_needed()
        except Exception as e:
            raise AssertionError(
                f"[FAIL] Sign button not visible within {timeout / 1000}s: {str(e).splitlines()[0]}"
            ) from e

        try:
            allure.attach(
                self.page.screenshot(),
                name="DocuSign - Before Sign Click",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass

        try:
            self.signature_tab_button.first.click()
            logger.info("[scroll_and_sign] Sign button clicked")
        except Exception as e:
            raise AssertionError(
                f"[FAIL] Could not click Sign button: {str(e).splitlines()[0]}"
            ) from e

        try:
            self.adopt_signature_modal.wait_for(state="visible", timeout=5000)
            logger.info("[scroll_and_sign] Adopt-and-Sign modal appeared, clicking adopt button")
            self.click_adopt_and_sign_button()
        except Exception:
            logger.info("[scroll_and_sign] Adopt-and-Sign modal not shown (pre-adopted signature)")

        try:
            self.signature_applied_tab.wait_for(state="visible", timeout=timeout)
            logger.info("[PASS] Signature applied - 'Signature Applied' button visible")
        except Exception:
            try:
                is_invalid = self.signature_tab_button.first.get_attribute("aria-invalid")
                assert is_invalid != "true", "Sign tab still aria-invalid=true after signing"
                logger.info("[PASS] Signature applied - aria-invalid cleared")
            except Exception as fallback_err:
                raise AssertionError(
                    "[FAIL] Signature not confirmed after Adopt and Sign"
                ) from fallback_err

        try:
            allure.attach(
                self.page.screenshot(),
                name="DocuSign - Signature Applied",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        logger.info("[PASS] scroll_to_last_page_and_sign completed")

    def verify_esign_complete_modal(self, timeout: int = 60000) -> None:
        logger.info("[verify_esign_modal] Waiting for eSignature Process Complete modal...")
        try:
            self.esign_complete_modal.wait_for(state="visible", timeout=timeout)
            title_text = self.esign_complete_title.text_content() or ""
            assert "eSignature Process Complete" in title_text, (
                f"[FAIL] Modal title mismatch. Got: '{title_text.strip()}'"
            )
            logger.info(f"[PASS] eSignature Process Complete modal verified: '{title_text.strip()}'")
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(
                f"[FAIL] eSignature Process Complete modal not visible within "
                f"{timeout / 1000}s: {str(e).splitlines()[0]}"
            ) from e
        try:
            allure.attach(
                self.page.screenshot(),
                name="eSignature Process Complete Modal",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass

    def click_d_number_in_esign_modal(self, timeout: int = 30000) -> str:
        logger.info("[click_d_number] Clicking D-number link in eSignature modal...")
        try:
            self.esign_d_number_link.wait_for(state="visible", timeout=timeout)
            d_number = (self.esign_d_number_link.text_content() or "").strip()
            logger.info(f"[click_d_number] D-number: {d_number}")
        except Exception as e:
            raise AssertionError(
                f"[FAIL] D-number link (a.eSignConfirmationLink) not visible within "
                f"{timeout / 1000}s: {str(e).splitlines()[0]}"
            ) from e
        try:
            allure.attach(
                self.page.screenshot(),
                name=f"eSignature Modal - D Number: {d_number}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        with self.page.expect_navigation(
            url=lambda u: "TrackingCenter" in u or "trackingcenter" in u.lower(),
            timeout=timeout,
        ):
            self.esign_d_number_link.click()
        logger.info(f"[PASS] Navigated to Tracking Center via D-number: {d_number}")
        try:
            allure.attach(
                self.page.screenshot(),
                name=f"Tracking Center - After D Number ({d_number})",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        return d_number

    def verify_docusign_page_loaded(self, timeout: int = 120000) -> None:
        logger.info(f"[verify_docusign_page_loaded] Waiting for DocuSign page (timeout={timeout}ms)")
        current_url = self.page.url
        if "docusign" in current_url.lower():
            logger.info(f"[verify_docusign_page_loaded] Already on DocuSign page: {current_url}")
        else:
            logger.info(f"[verify_docusign_page_loaded] Current URL: {current_url} — waiting for DocuSign navigation")
            self.page.wait_for_url(lambda url: "docusign" in url.lower(), timeout=timeout)
            logger.info("[verify_docusign_page_loaded] DocuSign URL detected")
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.info("[verify_docusign_page_loaded] Page reached networkidle")
        except Exception as e:
            logger.warning(f"[verify_docusign_page_loaded] networkidle not reached: {str(e)[:100]}")
        time.sleep(1.0)
        try:
            allure.attach(
                self.page.screenshot(),
                name="DocuSign Page Loaded",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            logger.warning(f"[verify_docusign_page_loaded] Screenshot failed: {str(e)[:100]}")

    def click_finish_button(self, timeout: int = 30000) -> None:
        logger.info("[click_finish_button] Attempting to click Finish button")
        try:
            self.page.wait_for_load_state("networkidle", timeout=min(timeout, 10000))
        except Exception:
            pass

        candidates = [
            ("end-of-document-btn-finish", self.page.locator("#end-of-document-btn-finish")),
            ("action-bar-btn-finish", self.finish_button_action_bar),
            ("finish-button-by-role", self.finish_button_by_role.first),
        ]
        for name, locator in candidates:
            try:
                locator.wait_for(state="visible", timeout=5000)
                locator.scroll_into_view_if_needed()
                locator.click(timeout=5000)
                logger.info(f"[click_finish_button] Clicked via strategy: {name}")
                try:
                    allure.attach(
                        self.page.screenshot(),
                        name="DocuSign - After Finish Button Click",
                        attachment_type=allure.attachment_type.PNG,
                    )
                except Exception:
                    pass
                return
            except Exception as e:
                logger.debug(f"[click_finish_button] Strategy '{name}' failed: {str(e)[:80]}")

        raise AssertionError(
            f"[FAIL] click_finish_button: No Finish button found within {timeout}ms. "
            "Tried: end-of-document-btn-finish, action-bar-btn-finish, button[role] Finish."
        )

    def get_stamping_element(self, stamping_text: str) -> "Locator":
        logger.info(f"[get_stamping_element] Locating element with text: '{stamping_text}'")
        return self.page.get_by_text(stamping_text, exact=False)

    def fetch_docusign_review_and_continue_dialog_text(self, timeout: int = 120000) -> str:
        logger.info(f"[fetch_docusign_review_and_continue_dialog_text] Waiting for ERSD dialog (timeout={timeout}ms)")
        dialog_locator = None
        for name, locator in [
            ("ersd-modal[data-qa]", self.ersd_modal),
            ("ersd-modal[aria-label]", self.ersd_modal_aria),
            ("dialog[role]", self.page.get_by_role("dialog").first),
        ]:
            try:
                locator.wait_for(state="visible", timeout=timeout)
                dialog_locator = locator
                logger.info(f"[fetch_docusign_review_and_continue_dialog_text] Dialog found via: {name}")
                break
            except Exception:
                logger.debug(f"[fetch_docusign_review_and_continue_dialog_text] Strategy '{name}' failed")

        if dialog_locator is None:
            try:
                allure.attach(
                    self.page.screenshot(),
                    name="ERSD Dialog Not Found",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
            raise AssertionError(
                f"[FAIL] fetch_docusign_review_and_continue_dialog_text: "
                f"ERSD dialog not visible after {timeout / 1000}s"
            )

        try:
            self.dialog_content.wait_for(state="visible", timeout=5000)
            text = (self.dialog_content.text_content() or "").strip()
        except Exception:
            text = (dialog_locator.text_content() or "").strip()

        logger.info(f"[fetch_docusign_review_and_continue_dialog_text] Dialog text length: {len(text)}")
        return text

    def verify_request_submitted_popup(self, timeout: int = 15000) -> None:
        logger.info(f"[verify_request_submitted_popup] Waiting for Request Submitted link (timeout={timeout}ms)")
        logger.info(f"[verify_request_submitted_popup] Current URL: {self.page.url}")
        try:
            link = self.request_submitted_link.first
            link.wait_for(state="visible", timeout=timeout)
            logger.info("[PASS] Request Submitted popup confirmed — D# link is visible")
            try:
                allure.attach(
                    self.page.screenshot(),
                    name="Request Submitted Popup",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
        except Exception as e:
            raise AssertionError(
                f"[FAIL] verify_request_submitted_popup: .printConfirmationLink not visible "
                f"within {timeout / 1000}s. URL: {self.page.url}. Error: {str(e).splitlines()[0]}"
            ) from e

    def get_d_number_and_click(self, test_context: dict) -> str:
        logger.info("[get_d_number_and_click] Locating D-number link (.printConfirmationLink)")
        try:
            link = self.request_submitted_link.first
            link.wait_for(state="visible", timeout=15000)
            d_number = (link.inner_text() or "").strip()
            logger.info(f"[get_d_number_and_click] D-number: {d_number}")
            test_context['d_number'] = d_number
            link.click()
            logger.info(f"[get_d_number_and_click] D# link clicked — navigating to Tracking Center")
            return d_number
        except Exception as e:
            raise AssertionError(
                f"[FAIL] get_d_number_and_click: .printConfirmationLink not visible within 15s. "
                f"Error: {str(e).splitlines()[0]}"
            ) from e
