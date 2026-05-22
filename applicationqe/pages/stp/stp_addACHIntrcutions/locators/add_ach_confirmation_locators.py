"""Locators for Add ACH Confirmation Page elements."""


class AddACHConfirmationLocators:
    """Raw selector strings for the Add ACH Confirmation page."""

    CONFIRMATION_HEADER = "//span[text()='Request Confirmation']"
    CONFIRMATION_DETAILS_LIST = "//h3[@aria-label]/following-sibling::span"
    SINGLE_INVESTMENT_ACCOUNT = "//li[@class]"
    INVESTMENT_ACCOUNTS_LIST = "//ol"
    CLOSE_BUTTON = "//button[text()='Close']"
    SUBHEADER_HOUSEHOLD = "//span[text()='Client Household']/following-sibling::div"
    SUBHEADER_ADVISOR_ID = "//span[text()='Advisor ID']/following-sibling::div"
    REQUEST_BANNER = "//div[@aria-label='confirmation-screen-status']"
    INFORMATION_BANNER = "//button[@aria-label='info']/parent::p/parent::div"
    ITEM_NUMBER = "//h3[text()='Item number:']/following-sibling::a"
