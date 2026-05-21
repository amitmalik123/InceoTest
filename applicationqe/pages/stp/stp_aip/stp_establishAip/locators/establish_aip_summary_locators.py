"""Locators for Establish AIP Summary Page elements."""


class EstablishAIPSummaryLocators:
    """Raw selector strings for the Establish AIP Summary page."""

    ACKNOWLEDGEMENTS = "//span[text()='Acknowledgements and Agreements']"
    SUMMARY_SECTION = "//p[text()='Request Summary']"
    REQUEST_TYPE_VALUE = "//p[contains(text(),'Request Type')]/following-sibling::p"
    DELIVERY_METHOD_VALUE = "//p[contains(text(),'Delivery Method')]/following-sibling::p"
    ORIGINATION_VALUE = "//p[contains(text(),'Origination')]/following-sibling::p"
    FREQUENCY_VALUE = "//p[contains(text(),'Frequency')]/following-sibling::p"
    AMOUNT_VALUE = "//p[contains(text(),'Amount')]/following-sibling::p"
    START_DATE_VALUE = "//p[contains(text(),'Start Date')]/following-sibling::p"
    END_DATE_VALUE = "//p[contains(text(),'End Date')]/following-sibling::p"
    ACKNOWLEDGEMENTS_HEADER = "//span[contains(@class,'MuiCardHeader-title') and text()='Acknowledgements and Agreements']"
    ACKNOWLEDGEMENTS_BODY = "//h4[text()='Upon completion of this request, I certify that:']"
    ACKNOWLEDGEMENTS_LIST = "//div[@class='sc-eulNck eRlzjx']//ul/li"
    CANCEL_BUTTON = "//button[contains(@class,'MuiButton-text') and normalize-space()='Cancel']"
    BACK_BUTTON = "//button[contains(@class,'MuiButton-outlined') and normalize-space()='Back']"
    SUBMIT_BUTTON = "//button[contains(@class,'MuiButton-contained') and normalize-space()='Submit']"
    SPINNER_LOADING = "div[class='App']>div>div>div>span"
    LOADING_OVERLAY = "//div[contains(@class,'loading')]"
