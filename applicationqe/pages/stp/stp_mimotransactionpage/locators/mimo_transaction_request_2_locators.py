"""Locators for MIMO Transaction Request Page 2 elements."""


class MIMOTransactionRequest2Locators:
    """Raw selector strings for the MIMO Transaction Request page 2."""

    # Section base paths (used to compose child locators)
    CASH_SECTION = "//section[@aria-label='cash-info-section']"
    CONTRIBUTION_AMOUNT_SECTION = "//div[contains(@data-testid,'contribution-amount')]"
    CONTRIBUTION_DATE_SECTION = "//div[contains(@aria-label,'Contribution-input-container')]"

    # Year contribution headings
    CURRENT_YEAR_TITLE = "//h3[normalize-space()='CURRENT YEAR']"
    CONTRIBUTION_LIMIT_CURRENT = "//h3[text()='CURRENT YEAR']//following-sibling::h4[text()='Contribution Limit: ']"
    CONTRIBUTED_CURRENT = "//h3[text()='CURRENT YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Contributed']"
    REMAINING_CURRENT = "//h3[text()='CURRENT YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Remaining']"
    CURRENT_REMAINING_VALUE = "//h3[text()='CURRENT YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//following-sibling::div"
    PRIOR_YEAR_TITLE = "//h3[normalize-space()='PRIOR YEAR']"
    CONTRIBUTION_LIMIT_PRIOR = "//h3[text()='PRIOR YEAR']//following-sibling::h4[text()='Contribution Limit: ']"
    CONTRIBUTED_PRIOR = "//h3[text()='PRIOR YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Contributed']"
    REMAINING_PRIOR = "//h3[text()='PRIOR YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//h4[text()='Remaining']"
    PRIOR_REMAINING_VALUE = "//h3[text()='PRIOR YEAR']//following-sibling::h4/..//following-sibling::div[2]//child::div//following-sibling::div"

    # Cash section locators (full paths)
    MARKET_VALUE_LABEL = "//section[@aria-label='cash-info-section']//div[1]/div[1]/p"
    MARKET_VALUE = "//section[@aria-label='cash-info-section']//p[@aria-label='money-value'][1]"
    CASH_VALUE_LABEL = "//div[2]/div[1]/p"
    CASH_VALUE = "//body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/section[2]/div[2]/div[2]/p[1]"

    # Input fields
    CASH_INPUT = "//input[contains(@name,'AmountInput')]"
    CONTRIBUTION_DATE_INPUT = "//input[@class='MuiInputBase-input MuiInput-input MuiInputBase-inputAdornedEnd']"
    CHECK_MEMO_INPUT = "//input[@name='checkMemoInput']"

    # Federal tax withholding
    FEDERAL_SECTION = "//div[@aria-label='federal-tax-withholding-options']"
    DO_NOT_WITHHOLD_INPUT = "//div[@aria-label='federal-tax-withholding-options']//input[@value='do-not-withhold']"
    DO_NOT_WITHHOLD_RADIO_INPUT = "//div[@aria-label='federal-tax-withholding-options']//input[@value='do-not-withhold']"
    ACKNOWLEDGEMENT_CHECKBOX = "//p[contains(text(), 'I elect not to have federal income tax withheld')]/preceding-sibling::div[@aria-label='checkbox']"
    WITHHOLD_RATE_RADIO_INPUT = "input[value='withhold']"
    FEDERAL_WITHHOLDING_INPUT = "input[@aria-label='federal-withholding' or @name='federalTaxWithholding']"

    # Relative selectors for chained locators
    DO_NOT_WITHHOLD_RELATIVE = "input[value='do-not-withhold']"
    WITHHOLD_RATE_RELATIVE = "input[value='withhold']"
    FEDERAL_WITHHOLDING_RELATIVE = "input[@aria-label='federal-withholding' or @name='federalTaxWithholding']"

    # State tax withholding
    STATE_SECTION = "//div[@aria-label='state-tax-withholding']"
    STATE_TAX_OPTION_RADIO = "input[name='state-tax-withholding-option']"
    STATE_ACKNOWLEDGEMENT_CHECKBOX = "div[aria-label='checkbox']"
    STATE_PERCENTAGE_INPUT = "input[@aria-label='percentage-input']"

    # Distribution reason
    DISTRIBUTION_REASON_DROPDOWN = "//div[contains(@aria-label,'-reason-selector')]//div[@aria-label='form-select-input']"
    DISTRIBUTION_REASON_OPTIONS = "//li[@aria-label='dropdown-menu-item']"
    DISTRIBUTION_REASON_OPTIONS_FIRST = "//li[@aria-label='dropdown-menu-item'][1]"
    DISTRIBUTION_REASON_LABEL = "//label[@aria-label='form-select-item-label']"
    SELECTED_DISTRIBUTION_REASON = "//div[@aria-label='form-select-input']//div[1]"

    # Navigation buttons
    NEXT_BUTTON = "//button[@data-testid='next-button']"
    PROCEED_BUTTON = "//button[@data-testid='proceed-button']"
    CANCEL_BUTTON = "//button[@data-testid='back-button']"
    CALENDAR_BUTTON = "//div[@class='MuiInputAdornment-root MuiInputAdornment-positionEnd']//button"
    CHANGE_CONTRIBUTION_DATE_BUTTON = "//button[@aria-label='change date']"

    # Notes
    IMPORTANT_NOTES_BLOCK = ".MuiCollapse-entered"
    IMPORTANT_NOTES_MESSAGE = "//div[@class='MuiAccordion-region']"

    # Error messages
    CONTRIBUTION_AMOUNT_ERROR = "/div/div/span"  # appended to CONTRIBUTION_AMOUNT_SECTION
    AMOUNT_ERROR_MESSAGE = "//span[contains(text(),'The contribution amount exceeds the allowable limi')]"
    ERROR_MESSAGE = "//p[@aria-label='error-message']"
    MIMO_ERROR_MESSAGE = "//div[@data-testid='transaction-page-submit-error-message']"

    # Date-related
    CONTRIBUTION_DATE_MESSAGE_TEXT = "//p"  # appended to CONTRIBUTION_DATE_SECTION
    CONTRIBUTION_BUSINESS_DATES = "//div[@class='MuiPickersCalendar-week']/div/div/div[not(contains(@style,'color: lightgrey;'))]"
    CONTRIBUTION_DATE_HOLIDAYS = "//div[@style='color: lightgrey; cursor: none;']"

    # Loading
    LOADING_SPINNER = "//div[@data-testid='loading-spinner']"

    # Page ready indicator
    PAGE_READY_INDICATOR = "//div[@id='root']/div/div/div/div/div/div[1]/section[1]/ul/li[1]"
