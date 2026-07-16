from playwright.sync_api import Locator, Page

from pages.ewm.base_page import BasePage
from pages.stp.stp_mimotransactionpage.locators.mimo_transaction_request_2_locators import MIMOTransactionRequest2Locators
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MIMOTransactionRequestPage2(BasePage):
    PAGE_NAME = "MIMO Transaction Request Page 2"

    def __init__(self, page: Page):
        super().__init__(page)
        ctx = self.active_root()
        loc = MIMOTransactionRequest2Locators

        # Raw string section base paths (used in f-strings in methods)
        self.cash_section = loc.CASH_SECTION
        self.contribution_amount_section = loc.CONTRIBUTION_AMOUNT_SECTION
        self.contribution_date_section = loc.CONTRIBUTION_DATE_SECTION

        self.current_year_title: Locator = ctx.locator(loc.CURRENT_YEAR_TITLE)
        self.contribution_limit_current: Locator = ctx.locator(loc.CONTRIBUTION_LIMIT_CURRENT)
        self.contributed_current: Locator = ctx.locator(loc.CONTRIBUTED_CURRENT)
        self.remaining_current: Locator = ctx.locator(loc.REMAINING_CURRENT)
        self.current_remaining_value: Locator = ctx.locator(loc.CURRENT_REMAINING_VALUE)

        self.prior_year_title: Locator = ctx.locator(loc.PRIOR_YEAR_TITLE)
        self.contribution_limit_prior: Locator = ctx.locator(loc.CONTRIBUTION_LIMIT_PRIOR)
        self.contributed_prior: Locator = ctx.locator(loc.CONTRIBUTED_PRIOR)
        self.remaining_prior: Locator = ctx.locator(loc.REMAINING_PRIOR)
        self.prior_remaining_value: Locator = ctx.locator(loc.PRIOR_REMAINING_VALUE)

        self.market_value_label: Locator = ctx.locator(loc.MARKET_VALUE_LABEL)
        self.market_value: Locator = ctx.locator(loc.MARKET_VALUE)
        self.cash_value_label: Locator = ctx.locator(loc.CASH_VALUE_LABEL)
        self.cash_value: Locator = ctx.locator(loc.CASH_VALUE)

        self.cash_input: Locator = ctx.locator(loc.CASH_INPUT)
        self.contribution_date_input: Locator = ctx.locator(loc.CONTRIBUTION_DATE_INPUT)
        self.check_memo_input: Locator = ctx.locator(loc.CHECK_MEMO_INPUT)

        self.federal_section: Locator = ctx.locator(loc.FEDERAL_SECTION)
        self.do_not_withhold_input: Locator = self.federal_section.locator(loc.DO_NOT_WITHHOLD_RELATIVE)

        # Locator for "Do Not Withhold" radio (Federal Tax)
        self.do_not_withhold_radio_input: Locator = ctx.locator(loc.DO_NOT_WITHHOLD_RADIO_INPUT)

        self.acknowledgement_checkbox: Locator = ctx.locator(loc.ACKNOWLEDGEMENT_CHECKBOX)

        self.withhold_rate_radio: Locator = self.federal_section.locator(loc.WITHHOLD_RATE_RELATIVE)
        self.federal_withholding_input: Locator = self.federal_section.locator(loc.FEDERAL_WITHHOLDING_RELATIVE)

        self.state_section: Locator = ctx.locator(loc.STATE_SECTION)

        # Do Not Withhold radio (first radio)
        self.state_do_not_withhold_radio: Locator = (
            self.state_section.locator(loc.STATE_TAX_OPTION_RADIO).first
        )

        self.state_acknowledgement_checkbox: Locator = (
            self.state_section.locator(loc.STATE_ACKNOWLEDGEMENT_CHECKBOX)
        )

        # State "Withhold at rate" radio (2nd radio)
        self.state_withhold_rate_radio: Locator = (
            self.state_section.locator(loc.STATE_TAX_OPTION_RADIO).nth(1)
        )

        # State withholding percentage input
        self.state_withholding_input: Locator = (
            self.state_section.locator(loc.STATE_PERCENTAGE_INPUT)
        )

        # Locator for distribution reason dropdown
        self.distribution_reason_dropdown: Locator = ctx.locator(loc.DISTRIBUTION_REASON_DROPDOWN)

        # Locator for all dropdown options
        self.distribution_reason_options: Locator = ctx.locator(loc.DISTRIBUTION_REASON_OPTIONS)
        self.distribution_reason_options_first: Locator = ctx.locator(loc.DISTRIBUTION_REASON_OPTIONS_FIRST)

        self.distribution_reason_label: Locator = ctx.locator(loc.DISTRIBUTION_REASON_LABEL)
        self.selected_distribution_reason: Locator = ctx.locator(loc.SELECTED_DISTRIBUTION_REASON)

        self.next_button: Locator = ctx.locator(loc.NEXT_BUTTON)
        self.proceed_button: Locator = ctx.locator(loc.PROCEED_BUTTON)
        self.cancel_button: Locator = ctx.locator(loc.CANCEL_BUTTON)
        self.calendar_button: Locator = ctx.locator(loc.CALENDAR_BUTTON)
        self.change_contribution_date_button: Locator = ctx.locator(loc.CHANGE_CONTRIBUTION_DATE_BUTTON)

        self.important_notes_block: Locator = ctx.locator(loc.IMPORTANT_NOTES_BLOCK)
        self.important_notes_message: Locator = ctx.locator(loc.IMPORTANT_NOTES_MESSAGE)

        self.contribution_amount_error: Locator = ctx.locator(f"{self.contribution_amount_section}{loc.CONTRIBUTION_AMOUNT_ERROR}")
        self.amount_error_message: Locator = ctx.locator(loc.AMOUNT_ERROR_MESSAGE)
        self.error_message: Locator = ctx.locator(loc.ERROR_MESSAGE)
        self.mimo_error_message: Locator = ctx.locator(loc.MIMO_ERROR_MESSAGE)

        self.contribution_date_message_text: Locator = ctx.locator(f"{self.contribution_date_section}{loc.CONTRIBUTION_DATE_MESSAGE_TEXT}")
        self.contribution_business_dates: Locator = ctx.locator(loc.CONTRIBUTION_BUSINESS_DATES)
        self.contribution_date_holidays: Locator = ctx.locator(loc.CONTRIBUTION_DATE_HOLIDAYS)

    def wait_for_page_load(self):
        """Wait for MIMO Transaction Request Page 2 to load"""
        logger.info("Waiting for MIMO Transaction Request Page 2 to load")

        spinner = self.active_root().locator(MIMOTransactionRequest2Locators.LOADING_SPINNER)
        if spinner.count() > 0:
            spinner.wait_for(state='hidden', timeout=30000)

        cash_section_element = self.active_root().locator(self.cash_section)
        cash_section_element.wait_for(state='visible', timeout=35000)
        logger.info("MIMO Transaction Request Page 2 loaded")

    def get_current_year_title(self) -> str:
        """Get current year title text"""
        return self.current_year_title.inner_text()

    def get_current_contribution_limit_title_with_value(self) -> str:
        """Get current contribution limit title without value"""
        text = self.contribution_limit_current.inner_text()
        return text.split(':')[0] if ':' in text else text

    def get_current_contribution_title(self) -> str:
        """Get current contributed title text"""
        return self.contributed_current.inner_text()

    def get_current_remaining_title(self) -> str:
        """Get current remaining title text"""
        return self.remaining_current.inner_text()

    def get_current_remaining_value(self) -> str:
        """Get current remaining value"""
        return self.current_remaining_value.inner_text()

    def get_prior_year_title(self) -> str:
        """Get prior year title text"""
        return self.prior_year_title.inner_text()

    def get_prior_contribution_limit_title_with_value(self) -> str:
        """Get prior contribution limit title without value"""
        text = self.contribution_limit_prior.inner_text()
        return text.split(':')[0] if ':' in text else text

    def get_prior_contribution_title(self) -> str:
        """Get prior contributed title text"""
        return self.contributed_prior.inner_text()

    def get_prior_remaining_title(self) -> str:
        """Get prior remaining title text"""
        return self.remaining_prior.inner_text()

    def get_prior_remaining_value(self) -> str:
        """Get prior remaining value"""
        return self.prior_remaining_value.inner_text()

    def enter_cash(self, cash_amount: str):
        """Enter cash amount"""
        logger.info(f"Entering cash amount: {cash_amount}")
        self.cash_input.wait_for(state='visible', timeout=10000)
        self.cash_input.fill(cash_amount)
        logger.info(f"Cash amount entered: {cash_amount}")

    def get_contribution_amount(self) -> str:
        """Get entered contribution amount"""
        return self.cash_input.input_value()

    def select_distribution(self, reason: str):
        """Select contribution / distribution reason"""
        logger.info(f"Selecting distribution reason: {reason}")

        self.distribution_reason_dropdown.wait_for(state="visible", timeout=10000)
        self.distribution_reason_dropdown.click()

        if reason == "Any":
            option = self.distribution_reason_options.first
        elif reason == "First Value":
            option = self.distribution_reason_options_first
        else:
            option = self.distribution_reason_options.filter(has_text=reason).first

        option.wait_for(state="visible", timeout=5000)
        option.click()

        logger.info(f"Distribution reason selected: {reason}")


    def get_selected_distribution_reason(self) -> str:
        """Return currently selected distribution reason"""
        self.selected_distribution_reason.wait_for(state="visible", timeout=5000)
        text = self.selected_distribution_reason.inner_text()
        return text.strip() if text else ""

    def get_contribution_date(self) -> str:
        """Get contribution date value"""
        return self.contribution_date_input.input_value()

    def get_contribution_date_info_message(self) -> str:
        """Get contribution date info message"""
        return self.contribution_date_message_text.inner_text()

    def click_contribution_change_calendar(self):
        """Click change calendar button"""
        logger.info("Clicking change calendar button")
        self.change_contribution_date_button.click()

    def increase_contribution_date(self):
        """Increase contribution date (placeholder for future implementation)"""
        logger.info("Increase contribution date method called")
        pass

    def get_important_notes(self) -> str:
        """Get important notes text"""
        self.important_notes_message.wait_for(state='visible', timeout=10000)
        return self.important_notes_message.inner_text()

    def click_next(self):
        """Click Next button and navigate to summary page"""
        logger.info("Clicking Next button")

        self.page.wait_for_load_state('domcontentloaded')
        self.active_root().locator(MIMOTransactionRequest2Locators.PAGE_READY_INDICATOR).wait_for(state='visible', timeout=50000)

        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.click()

        spinner = self.active_root().locator(MIMOTransactionRequest2Locators.LOADING_SPINNER)
        if spinner.count() > 0:
            spinner.wait_for(state='hidden', timeout=30000)

        logger.info("Navigated to MIMO Transaction Summary Page")

    def click_proceed_button(self):
        """Click proceed button if visible, otherwise handle errors and retry next"""
        if self.proceed_button.is_visible(timeout=10000):
            logger.info("Clicking Proceed button")
            self.proceed_button.click()
        elif self.mimo_error_message.is_visible(timeout=10000):
            logger.info("Error message visible, retrying Next button")
            for _ in range(3):
                self.next_button.click()
                self.page.wait_for_timeout(2000)
                if not self.mimo_error_message.is_visible(timeout=5000):
                    break

    def press_next(self):
        """Press next and handle proceed button if needed"""
        self.click_next()
        self.click_proceed_button()

    def select_do_not_withhold_federal_tax(self) -> None:
        """Select 'Do Not Withhold' option for federal tax"""
        logger.info("Selecting 'Do Not Withhold' for federal tax")

        self.do_not_withhold_radio_input.click()

        self.acknowledgement_checkbox.wait_for(state="visible", timeout=10000)
        self.acknowledgement_checkbox.click()

        logger.info("Federal tax 'Do Not Withhold' selected with acknowledgement")

    def select_do_not_withhold_state_tax(self) -> None:
        """Select 'Do Not Withhold' option for state tax (Java-equivalent)"""
        logger.info("Selecting 'Do Not Withhold' for state tax")
        self.state_do_not_withhold_radio.wait_for(state="visible", timeout=10000)
        self.state_do_not_withhold_radio.check()
        self.state_acknowledgement_checkbox.wait_for(state="visible", timeout=10000)
        self.state_acknowledgement_checkbox.click()
        logger.info("State tax 'Do Not Withhold' selected")

    def enter_federal_withholding(self, withholding_amount: str) -> None:
        logger.info(f"Entering federal tax withholding: {withholding_amount}")

        self.withhold_rate_radio.wait_for(state="visible", timeout=10000)
        self.withhold_rate_radio.check()

        self.federal_withholding_input.wait_for(state="visible", timeout=10000)
        self.federal_withholding_input.fill("")
        self.federal_withholding_input.type(withholding_amount)


    def enter_tax_withholding(self, withholding_amount: str) -> None:
        """Enter state tax withholding amount"""
        logger.info(f"Entering state tax withholding: {withholding_amount}")
        self.state_withhold_rate_radio.wait_for(state="visible", timeout=10000)
        self.state_withhold_rate_radio.check()
        self.state_withholding_input.wait_for(state="visible", timeout=10000)
        self.state_withholding_input.fill("")
        self.state_withholding_input.type(withholding_amount)
        logger.info(f"State tax withholding amount entered: {withholding_amount}")

    def select_any_distribution_reason(self) -> None:
        """Select the first available distribution reason"""
        logger.info("Selecting first available distribution reason")
        self.distribution_reason_dropdown.wait_for(state="visible", timeout=5000)
        self.distribution_reason_dropdown.click()
        first_option = self.active_root().locator(MIMOTransactionRequest2Locators.DISTRIBUTION_REASON_OPTIONS_FIRST)
        first_option.wait_for(state="visible", timeout=5000)
        first_option.click()
        logger.info("First available distribution reason selected")

    def fill_check_memo_field(self, check_memo: str) -> None:
        """Fill the check memo field if visible"""
        logger.info(f"Attempting to fill check memo field with: {check_memo}")

        try:
            if self.check_memo_input.is_visible(timeout=2000):
                self.check_memo_input.fill(check_memo)
                logger.info(f"Check memo field filled with: {check_memo}")
            else:
                logger.info("Check memo field not visible (likely ACH delivery method)")
        except:
            logger.info("Check memo field not found, skipping (likely ACH delivery method)")
