"""Locators for Cancel AIP Page elements."""


class CancelAIPLocators:
    """Raw selector strings for the Cancel AIP page."""

    # Landing Page
    LANDING_PAGE_TITLE = "//span[text()='Automatic Investment Plans (AIP)']"
    SELECT_AIP = "//div[@class='sc-dAbbOL dLmiyp']/descendant::li[1]"
    DELETE_BUTTON = "//button[text()='Delete']"
    NEXT_BUTTON = "//button[text()='NEXT']"
    CANCEL_BUTTON = "//button[text()='Cancel']"

    # Selection Page
    SELECTION_PAGE_TITLE = "//span[text() = 'Delete Automatic Investment Plan (AIP)']"
    END_DATE_SELECTION = "//p[normalize-space()='Immediately (By Next Business Day)']"
    FUTURE_END_SELECTION = "//p[text()='Future End Date: ']"
    CALENDAR_FIELD = "//button[@aria-label='Choose date']"

    # Signature Options
    NOT_OBTAIN_SIGNATURE_RADIO = "//span[starts-with(text(),'Do Not Obtain Client Signature')]"
    SELECT_ESIGN = "//span[normalize-space()='Obtain Electronic Client Signature(s)']"
    SELECT_PRINT = "//span[normalize-space()='Print to Obtain Physical Client Signature(s)']"

    # Summary Page
    SUBMIT_BUTTON = "//button[text()='Submit']"
    SUMMARY_SUBMIT_BUTTON = "//button[normalize-space()='Submit']"
    PRINT_BUTTON = "//button[text()='Complete and Print']"
    ESIGN_BUTTON = "//button[text()='E-Sign and Submit']"
    SUBMIT_REVIEW_BUTTON = "//button[normalize-space()='Submit For Review']"
    SUBMIT_TO_ADVISOR = "//button[text()='SUBMIT TO ADVISOR']"

    # Confirmation Page
    ITEM_NUMBER_LINK = "//h3[@aria-label='a-item-label']/following-sibling::a"
    ITEM_NUMBER_TEXT = "//h3[text()='Item number:']/parent::div/a"

    # Loading
    SPINNER_LOADING = "div[class='App']>div>div>div>span"
