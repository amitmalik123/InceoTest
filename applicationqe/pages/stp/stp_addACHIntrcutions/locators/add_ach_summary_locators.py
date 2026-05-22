"""Locators for Add ACH Summary Page elements."""


class AddACHSummaryLocators:
    """Raw selector strings for the Add ACH Summary page."""

    REQUEST_SUMMARY_HEADER = "//p[contains(text(),'Request Summary')]"
    REQUEST_SUMMARY_SUBHEADER = "//p[contains(text(),'Please review the details')]"
    SUMMARY_BLOCK_LIST = "xpath=//p[text()=':']/following-sibling::p"
    SUMMARY_LABELS = "//div[@class='MuiGrid-root']//p[1]"
    SUMMARY_VALUES = "//div[@class='MuiGrid-root']//p[2]"
    INVESTMENT_ACCOUNTS_SINGLE = "//p[text()=':']/following-sibling::div/child::p"
    INVESTMENT_ACCOUNTS_MULTI = "//p[text()=':']/following-sibling::div/child::ol"
    ADVISOR_ALERT = "//div[contains(@class,'MuiAlert')]//div[contains(@class,'message')]"
    SLOA_TEXT_TESTID = "SLOA-value"
    AGREEMENTS_TITLE = "//span[text()='Acknowledgements and Agreements']"
    AGREEMENTS_SUBHEADER = "//h4[text()='Upon completion of this request, I certify that:']"
    AGREEMENTS_BULLETS = "//*[contains(text(),'Upon completion of this ')]/parent::div/child::ul"
    SUBMIT_BUTTON = "Submit"
    SUBMIT_BUTTON_ALT = "button:has-text('Submit')"
    SPINNER = "div[class*='css-8jl1ua'], div[role='progressbar'], svg[class*='MuiCircularProgress']"
    NUMBERED_PATTERN = "p:has-text('1.')"
