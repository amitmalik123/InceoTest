"""Locators for Establish AIP Landing Page elements."""


class EstablishAIPLandingLocators:
    """Raw selector strings for the Establish AIP Landing page."""

    HEADER = "//p[text()='Manage Automatic Investment Plans']"
    TITLE_SECTION = "//span[text()='Automatic Investment Plans (AIP)']"
    ADD_BUTTON = "//div[contains(@class,'MuiCardHeader-action')]/button"
    CANCEL_BUTTON = "//button[text()='Cancel']"
    NEXT_BUTTON = "//button[text()='NEXT']"
    ACCOUNT_INFO_LABEL = "//span[text()='Account Information']"
    ACCOUNT_INFO_TEXT = "//span[text()='Account Information']/ancestor::div[contains(@class,'MuiCardHeader-root')]//span[contains(@class,'MuiCardHeader-subheader')]"
    MARKET_VALUE = "//div[contains(text(),'Market Value')]/following-sibling::div"
    CASH_AVAILABLE = "//div[contains(text(),'Cash Available')]/following-sibling::div"
    SELECT_AIP = "//div/li[1]"
    HARD_STOP_MESSAGE = "//p[text()='No automatic investment plans found on file.']"
    ACTIVE_AIP_LIST = "//div[contains(@class,'aip-list')]"
    SPINNER_LOADING = "div[class='App']>div>div>div>span"
    LOADING_OVERLAY = "//div[contains(@class,'loading')]"
