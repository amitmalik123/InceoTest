"""Locators for Establish AIP Add AIP Page elements."""


class EstablishAIPAddAIPLocators:
    """Raw selector strings for the Establish AIP Add AIP page."""

    HEADER = "//p[text()='Manage Automatic Investment Plans']"
    ADD_AIP_TITLE = "//span[text()='Add Automatic Investment Plan (AIP)']"
    CONTRIBUTION_AMOUNT_INPUT = "//div[@class='sc-iA-DsXs khArdT']/descendant::input[@type='text']"
    START_DATE_CALENDAR_BTN = "(//button[.//*[name()='svg' and @data-testid='CalendarIcon']])[1]"
    END_DATE_CALENDAR_BTN = "(//button[.//*[name()='svg' and @data-testid='CalendarIcon']])[2]"
    ENABLED_DAYS = "//button[contains(@class,'MuiPickersDay-root') and not(contains(@class,'Mui-disabled'))]"
    DISABLED_DAYS = "//button[contains(@class,'MuiPickersDay-root') and contains(@class,'Mui-disabled')]"
    NEXT_MONTH_ARROW = "//button[@title='Next month' and not(@disabled)]"
    DATE_PICKER_POPUP = "//div[contains(@class,'MuiDateCalendar-root')]"
    SIGNATURE_HEADER = "//span[@class='sc-etVdmn fElJWm']"
    SIGNATURE_OPTION_LABELS = "//div[@class='sc-cDvQBt EZYBk']/label/span[text()]"
    NEXT_BUTTON = "//button[@type='button' and text()='NEXT']"
    ACCOUNT_INFO_LABEL = "//span[text()='Account Information']"
    ACCOUNT_INFO_TEXT = "//span[text()='Account Information']/ancestor::div[contains(@class,'MuiCardHeader-root')]//span[contains(@class,'MuiCardHeader-subheader')]"
    SPINNER_LOADING = "div[class='App']>div>div>div>span"
    LOADING_OVERLAY = "//div[contains(@class,'loading')]"
