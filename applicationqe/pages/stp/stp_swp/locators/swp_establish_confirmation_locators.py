"""Locators for SWP Establish Confirmation Page elements."""


class SWPEstablishConfirmationLocators:
    """Raw selector strings for the SWP Establish Confirmation page."""

    CONFIRMATION_HEADING = "//span[text()='Request Confirmation']"
    CONFIRMATION_HEADER_DETAILS = "//span[text()='Account Information']/parent::div/parent::div/parent::div"
    CONFIRMATION_SCREEN_STATUS = "//div[@aria-label='confirmation-screen-status']"
    STATUS = "//h3[text()='Status:']/parent::div/span"
    DATE = "//h3[text()='Submission date and time:']/parent::div/span"
    SUBMITTED_BY = "//h3[text()='Submitted by:']/parent::div/span"
    ITEM_NUMBER = "//h3[text()='Item number:']/parent::div/a"
    STATUS_TITLE = "//h3[text()='Status:']"
    DATE_TITLE = "//h3[text()='Submission date and time:']"
    SUBMITTED_BY_TITLE = "//h3[text()='Submitted by:']"
    ITEM_NUMBER_TITLE = "//h3[text()='Item number:']"
    CONFIRMATION_REQUEST_DETAILS = "//h3[text()='Request Details']/parent::div"
    ITEM_NUMBER_LINK = "//h3[text()='Item number:']/parent::div/child::a"
    LOADING_SPINNER = "//div[@data-testid='loading-spinner']"
