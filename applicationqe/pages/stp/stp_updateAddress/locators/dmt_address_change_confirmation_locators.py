"""Locators for DMT Address Change Confirmation Page elements (raw string XPath attributes)."""


class DMTAddressChangeConfirmationLocators:
    """Raw XPath/CSS selector strings for the DMT Address Change Confirmation Page.
    
    NOTE: These are used as raw strings (self.x = loc.X), not as Playwright Locators,
    because methods call self.page.locator(self.x) internally.
    """

    # Section base paths (inlined into full paths below)
    HEADER_TEXT = "//div[@aria-label='confirmation-screen-header']//h2"
    CLOSE_BUTTON = "//div[@aria-label='confirmation-screen-buttons']//button"
    PRINT_BUTTON = "//div[@aria-label='confirmation-screen-header']//button"
    UPDATED_SUCCESSFULLY_TEXT = "//div[3]//h3[.='Address updated successfully']"

    # Household section
    HOUSEHOLD_LABEL = "(//div[@aria-label='confirmation-screen-account-information']//h3)[1]"
    HOUSEHOLD_DATA = "(//div[@aria-label='confirmation-screen-account-information']//p)[1]"
    HOUSEHOLD_ADVISOR_LABEL = "(//div[@aria-label='confirmation-screen-account-information']//h3)[2]"
    HOUSEHOLD_ADVISOR_DATA = "(//div[@aria-label='confirmation-screen-account-information']//p)[2]"
    CUSTODIAN_LABEL = "(//div[@aria-label='confirmation-screen-account-information']//h3)[3]"
    CUSTODIAN_DATA = "(//div[@aria-label='confirmation-screen-account-information']//p)[3]"

    # Important notes section
    IMPORTANT_NOTES_LABEL = "//div[@role='presentation']/div[3]/div/div[2]/div[3]//h3"
    IMPORTANT_NOTES_DATA = "//div[@role='presentation']/div[3]/div/div[2]/div[3]//p"

    # Summary section
    STATUS_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-status-completed']//h3[.='Status']"
    STATUS_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-status-completed']//p"
    SUBMITTED_BY_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-submitted-by']//h3[.='Submitted by']"
    SUBMITTED_BY_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-submitted-by']//p"
    SUBMISSION_DATE_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-submitted-date']//h3[.='Submission date and time']"
    SUBMISSION_DATE_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-submitted-date']//p"
    ITEM_NUMBER_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-item-number']//h3[.='Item number']"
    ITEM_NUMBER_LINK = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-item-number']//a"

    # Updated/Previous information
    UPDATED_INFORMATION_LABEL = "//div[@aria-label='confirmation-screen-summary']//h3[.='Updated Information']"
    PREVIOUS_INFORMATION_LABEL = "//div[@aria-label='confirmation-screen-summary']//h3[.='Previous Information']"
    LEGAL_ADDRESS_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-updated-legal']//h3[.='Legal Address']"
    LEGAL_ADDRESS_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-updated-legal']//p"
    MAILING_ADDRESS_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-updated-mailing']//h3[.='Mailing Address']"
    MAILING_ADDRESS_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-updated-mailing']//p"
    PREVIOUS_LEGAL_ADDRESS_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-previous-legal']//h3[.='Legal Address']"
    PREVIOUS_LEGAL_ADDRESS_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-previous-legal']//p"
    PREVIOUS_MAILING_ADDRESS_LABEL = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-previous-mailing']//h3[.='Mailing Address']"
    PREVIOUS_MAILING_ADDRESS_DATA = "//div[@aria-label='confirmation-screen-summary']//div[@aria-label='confirmation-screen-previous-mailing']//p"
