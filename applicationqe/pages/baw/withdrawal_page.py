"""Withdrawal Page - BAW Withdrawal work item actions"""

from pathlib import Path

from playwright.sync_api import Locator, Page

from locators.baw.withdrawal_locators import WithdrawalLocators
from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class WithdrawalPage(BasePage):
    """Page object for BAW Withdrawal workflow (Direct Entry)."""

    PAGE_NAME = "Withdrawal Page"

    def __init__(self, page: Page, home_url: str = ""):
        super().__init__(page, home_url=home_url)

        # ----- OCR Screen locators -----
        self.ocr_checkbox: Locator = page.get_by_role("checkbox").nth(2)
        self.ocr_open_button: Locator = page.get_by_role("button", name=WithdrawalLocators.OCR_OPEN_BUTTON_ROLE)
        self.ocr_complete_button: Locator = page.get_by_role("button", name=WithdrawalLocators.OCR_COMPLETE_BUTTON_ROLE)
        self.custodian_acc_num: Locator = page.locator(WithdrawalLocators.CUSTODIAN_ACC_NUM)
        self.account_name: Locator = page.locator(WithdrawalLocators.ACCOUNT_NAME)

        # ----- IWR Process locators -----
        self.partial_wd_amount: Locator = page.locator(WithdrawalLocators.PARTIAL_WD_AMOUNT)
        self.continue_button: Locator = page.get_by_role("button", name=WithdrawalLocators.CONTINUE_BUTTON_ROLE)

        # ----- Check Delivery Method locators -----
        self.check_payee_name: Locator = page.locator(WithdrawalLocators.CHECK_PAYEE_NAME)
        self.check_payee_name_2: Locator = page.locator(WithdrawalLocators.CHECK_PAYEE_NAME_2)
        self.check_address: Locator = page.locator(WithdrawalLocators.CHECK_ADDRESS)
        self.check_city: Locator = page.locator(WithdrawalLocators.CHECK_CITY)
        self.check_state: Locator = page.locator(WithdrawalLocators.CHECK_STATE)
        self.check_zip: Locator = page.locator(WithdrawalLocators.CHECK_ZIP)
        self.check_po_box: Locator = page.locator(WithdrawalLocators.CHECK_PO_BOX)
        self.check_regular: Locator = page.locator(WithdrawalLocators.CHECK_REGULAR)
        self.check_new_instruction: Locator = page.locator(WithdrawalLocators.CHECK_NEW_INSTRUCTION)
        self.check_type_of_payee: Locator = page.locator(WithdrawalLocators.CHECK_TYPE_OF_PAYEE)
        self.check_sloa_no: Locator = page.locator(WithdrawalLocators.CHECK_SLOA_NO)

        # ----- Initiate OA locators -----
        self.place_withdrawal_oa_button: Locator = page.get_by_role("button", name=WithdrawalLocators.PLACE_WITHDRAWAL_OA_BUTTON_ROLE)
        self.set_followup_date_button: Locator = page.get_by_role("button", name=WithdrawalLocators.SET_FOLLOWUP_DATE_BUTTON_ROLE)

        # ----- Initiate Distribution locators -----
        self.submit_to_beta_button: Locator = page.get_by_role("button", name=WithdrawalLocators.SUBMIT_TO_BETA_BUTTON_ROLE)

    def complete_ocr_screen(self, account_number: str, account_name: str) -> None:
        """Complete OCR screen: click dropdown, check checkbox, click Open, fill account details, click OCR Complete."""
        with logger.step("Complete OCR Screen", page=self.page):
            self.wait_for_loading_data()
            self.page.locator(WithdrawalLocators.OCR_DROPDOWN).click()
            self.page.wait_for_timeout(2000)
            self.ocr_checkbox.check()
            self.ocr_open_button.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=60000)
            self.wait_for_loading_data()

            self.custodian_acc_num.click()
            self.custodian_acc_num.fill(str(account_number))
            self.account_name.click()
            self.account_name.fill(account_name)

            self.ocr_complete_button.click()
            self.page.wait_for_load_state("load", timeout=60000)
            self.wait_for_loading_data()
            logger.info(f"OCR Screen completed for account: {account_number}")

    def complete_iwr_process(self, amount: str, delivery_data: str) -> None:
        """Complete the IWR process with check delivery method.

        Args:
            amount: Withdrawal amount
            delivery_data: Comma-separated delivery info:
                payee_name, address, city, state, zip, delivery_option
        """
        with logger.step("Complete IWR Process", page=self.page):
            self.page.wait_for_load_state("load", timeout=60000)
            self.wait_for_loading_data()
            self.partial_wd_amount.wait_for(state="visible", timeout=60000)
            self.partial_wd_amount.click()
            self.partial_wd_amount.fill(str(amount))
            self.continue_button.click()
            self.wait_for_loading_data()

            # Parse delivery data
            parts = [p.strip() for p in delivery_data.split(",")]
            payee_name = parts[0] if len(parts) > 0 else "Test"
            address = parts[1] if len(parts) > 1 else "123 Test St"
            city = parts[2] if len(parts) > 2 else "TestCity"
            state = parts[3] if len(parts) > 3 else "CA"
            zip_code = parts[4] if len(parts) > 4 else "90000"

            self.check_payee_name.wait_for(state="visible", timeout=30000)
            self.check_payee_name.click()
            self.check_payee_name.fill(payee_name)
            self.check_payee_name_2.wait_for(state="visible", timeout=10000)
            self.check_payee_name_2.click()
            self.check_payee_name_2.fill("name")
            self.check_address.wait_for(state="visible", timeout=10000)
            self.check_address.click()
            self.check_address.fill(address)
            self.check_city.wait_for(state="visible", timeout=10000)
            self.check_city.click()
            self.check_city.fill(city)
            self.check_state.wait_for(state="visible", timeout=10000)
            self.check_state.click()
            self.check_state.fill(state)
            self.check_zip.wait_for(state="visible", timeout=10000)
            self.check_zip.click()
            self.check_zip.fill(zip_code)

            self.check_po_box.check()
            self.check_regular.check()
            self.check_new_instruction.check()
            self.check_type_of_payee.select_option("SameNameAndAddress")
            self.check_sloa_no.check()

            self.continue_button.click()
            self.wait_for_loading_data()
            self.continue_button.click()
            self.wait_for_loading_data()
            logger.info("IWR Process completed with Check delivery method")

    def click_place_withdrawal_oa(self) -> None:
        """Click Place Withdrawal Advisor OA and Set FollowUp Date."""
        with logger.step("Click Place Withdrawal OA", page=self.page):
            self.page.wait_for_load_state("load", timeout=60000)
            self.wait_for_loading_data()
            self.place_withdrawal_oa_button.wait_for(state="visible", timeout=60000)
            # Register dialog handler to click OK on the OA confirmation popup
            self.page.on("dialog", lambda dialog: dialog.accept())
            # Retry clicking Place Withdrawal OA until Set FollowUp Date becomes visible
            for attempt in range(1, 6):
                logger.info(f"Clicking Place Withdrawal OA (attempt {attempt})")
                self.place_withdrawal_oa_button.click(timeout=60000)
                self.page.wait_for_load_state("load", timeout=60000)
                self.wait_for_loading_data()
                if self.set_followup_date_button.is_visible():
                    logger.info(f"Set FollowUp Date visible after {attempt} click(s)")
                    break
                logger.info("Set FollowUp Date not visible yet, retrying...")
                self.wait_for_timeout(2000)
            self.set_followup_date_button.click(timeout=60000)
            try:
                self.page.wait_for_load_state("load", timeout=60000)
            except Exception:
                pass
            self.wait_for_timeout(2000)
            logger.info("Clicked Place Withdrawal Advisor OA and Set FollowUp Date")

    def click_submit_to_beta(self) -> None:
        """Click Submit To BETA button in Initiate Distribution page."""
        with logger.step("Click Submit To BETA", page=self.page):
            # Wait for any in-flight navigation to complete (from Set FollowUp Date click)
            try:
                self.page.wait_for_load_state("networkidle", timeout=120000)
            except Exception:
                pass
            try:
                self.page.wait_for_load_state("load", timeout=90000)
            except Exception:
                pass
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=60000)
            except Exception:
                pass
            try:
                self.wait_for_loading_data()
            except Exception:
                pass
            self.submit_to_beta_button.wait_for(state="visible", timeout=90000)
            self.submit_to_beta_button.click()
            # Page closes after Submit To BETA — this is expected
            try:
                self.wait_for_timeout(3000)
            except Exception:
                pass
            logger.info("Clicked Submit To BETA button")
