from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MIMOTransactionRequestPage2(BasePage):
    PAGE_NAME = "MIMO Transaction Request Page 2"

    def __init__(self, page: Page):
        super().__init__(page)

        self.cash_section = "//section[@aria-label='cash-info-section']"
        self.contribution_amount_section = "//div[contains(@data-testid,'contribution-amount')]"
        self.contribution_date_section = "//div[contains(@aria-label,'Contribution-input-container')]"

        self.current_year_title: Locator = page.locator("//h3[normalize-space()='CURRENT YEAR']")
        self.contribution_limit_current: Locator = page.locator("//h3[text()='CURRENT YEAR']//following-sibling::h4[text()='Contribution Limit: ']")
        self.contributed_current: Locator = page.locator("//h3[text()='CURRENT YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Contributed']")
        self.remaining_current: Locator = page.locator("//h3[text()='CURRENT YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Remaining']")
        self.current_remaining_value: Locator = page.locator("//h3[text()='CURRENT YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//following-sibling::div")

        self.prior_year_title: Locator = page.locator("//h3[normalize-space()='PRIOR YEAR']")
        self.contribution_limit_prior: Locator = page.locator("//h3[text()='PRIOR YEAR']//following-sibling::h4[text()='Contribution Limit: ']")
        self.contributed_prior: Locator = page.locator("//h3[text()='PRIOR YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Contributed']")
        self.remaining_prior: Locator = page.locator("//h3[text()='PRIOR YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Remaining']")
        self.prior_remaining_value: Locator = page.locator("//h3[text()='PRIOR YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//following-sibling::div")

        self.market_value_label: Locator = page.locator(f"{self.cash_section}//div[1]/div[1]/p")
        self.market_value: Locator = page.locator(f"{self.cash_section}//p[@aria-label='money-value'][1]")
        self.cash_value_label: Locator = page.locator("//div[2]/div[1]/p")
        self.cash_value: Locator = page.locator("//body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/section[2]/div[2]/div[2]/p[1]")

        self.cash_input: Locator = page.locator("//input[contains(@name,'AmountInput')]")
        self.contribution_date_input: Locator = page.locator("//input[@class='MuiInputBase-input MuiInput-input MuiInputBase-inputAdornedEnd']")
        self.check_memo_input: Locator = page.locator("//input[@name='checkMemoInput']")

        # self.do_not_withhold_span: Locator = page.get_by_text("Do not withhold")
        self.federal_section: Locator = page.locator("//div[@aria-label='federal-tax-withholding-options']")
        self.do_not_withhold_input: Locator = self.federal_section.locator("input[value='do-not-withhold']")

        # Locator for "Do Not Withhold" radio (Federal Tax)
        self.do_not_withhold_radio_input: Locator = page.locator(
            "//div[@aria-label='federal-tax-withholding-options']//input[@value='do-not-withhold']"
        )

        self.acknowledgement_checkbox: Locator = page.locator(
            "//p[contains(text(), 'I elect not to have federal income tax withheld')]/preceding-sibling::div[@aria-label='checkbox']" 
        )

        self.withhold_rate_radio: Locator = (self.federal_section.locator("input[value='withhold']"))
        self.federal_withholding_input: Locator = (self.federal_section.locator("input[@aria-label='federal-withholding' or @name='federalTaxWithholding']"))


        self.state_section: Locator = page.locator(
            "//div[@aria-label='state-tax-withholding']"
        )

        # Do Not Withhold radio (first radio)
        self.state_do_not_withhold_radio: Locator = (
            self.state_section.locator("input[name='state-tax-withholding-option']").first
        )

        self.state_acknowledgement_checkbox: Locator = (
            self.state_section.locator("div[aria-label='checkbox']")
        )

        # State "Withhold at rate" radio (2nd radio)
        self.state_withhold_rate_radio: Locator = (
            self.state_section.locator("input[name='state-tax-withholding-option']").nth(1)
        )

        # State withholding percentage input
        self.state_withholding_input: Locator = (
            self.state_section.locator("input[@aria-label='percentage-input']")
        )

        # Locator for distribution reason dropdown
        self.distribution_reason_dropdown: Locator = page.locator(
            "//div[contains(@aria-label,'-reason-selector')]//div[@aria-label='form-select-input']"
        )

        # Locator for all dropdown options
        self.distribution_reason_options: Locator = page.locator("//li[@aria-label='dropdown-menu-item']")
        self.distribution_reason_options_first: Locator = page.locator("//li[@aria-label='dropdown-menu-item'][1]")

        self.distribution_reason_label: Locator = page.locator("//label[@aria-label='form-select-item-label']")
        self.selected_distribution_reason: Locator = page.locator("//div[@aria-label='form-select-input']//div[1]")


        self.next_button: Locator = page.locator("//button[@data-testid='next-button']")
        self.proceed_button: Locator = page.locator("//button[@data-testid='proceed-button']")
        self.cancel_button: Locator = page.locator("//button[@data-testid='back-button']")
        self.calendar_button: Locator = page.locator("//div[@class='MuiInputAdornment-root MuiInputAdornment-positionEnd']//button")
        self.change_contribution_date_button: Locator = page.locator("//button[@aria-label='change date']")

        self.important_notes_block: Locator = page.locator(".MuiCollapse-entered")
        self.important_notes_message: Locator = page.locator("//div[@class='MuiAccordion-region']")

        self.contribution_amount_error: Locator = page.locator(f"{self.contribution_amount_section}/div/div/span")
        self.amount_error_message: Locator = page.locator("//span[contains(text(),'The contribution amount exceeds the allowable limi')]")
        self.error_message: Locator = page.locator("//p[@aria-label='error-message']")
        self.mimo_error_message: Locator = page.locator("//div[@data-testid='transaction-page-submit-error-message']")

        self.contribution_date_message_text: Locator = page.locator(f"{self.contribution_date_section}//p")
        self.contribution_business_dates: Locator = page.locator("//div[@class='MuiPickersCalendar-week']/div/div/div[not(contains(@style,'color: lightgrey;'))]")
        self.contribution_date_holidays: Locator = page.locator("//div[@style='color: lightgrey; cursor: none;']")

    def wait_for_page_load(self):
        """Wait for MIMO Transaction Request Page 2 to load"""
        logger.info("Waiting for MIMO Transaction Request Page 2 to load")

        spinner = self.page.locator("//div[@data-testid='loading-spinner']")
        if spinner.count() > 0:
            spinner.wait_for(state='hidden', timeout=30000)

        cash_section_element = self.page.locator(self.cash_section)
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
        self.page.locator("//div[@id='root']/div/div/div/div/div/div[1]/section[1]/ul/li[1]").wait_for(state='visible', timeout=50000)

        self.next_button.wait_for(state='visible', timeout=10000)
        self.next_button.click()

        spinner = self.page.locator("//div[@data-testid='loading-spinner']")
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
        first_option = self.page.locator("//li[@aria-label='dropdown-menu-item'][1]")
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
