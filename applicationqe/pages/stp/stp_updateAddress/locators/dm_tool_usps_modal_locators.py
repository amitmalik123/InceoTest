"""Locators for DM Tool USPS Modal elements (raw string XPath attributes)."""


class DMToolUSPSModalLocators:
    """Raw XPath/CSS selector strings for the DM Tool USPS Address Validation Modal.
    
    NOTE: These are used as raw strings (self.x = loc.X), not as Playwright Locators,
    because methods call self.page.locator(self.x) internally.
    """

    # Modal elements
    MODAL_TITLE = "//h2[contains(text(),'Address Validation')]"
    MODAL_CONTAINER = "//div[@role='dialog' and contains(@aria-label,'usps')]"

    # Address display sections
    ORIGINAL_ADDRESS_SECTION = "//div[@aria-label='original-address-section']"
    SUGGESTED_ADDRESS_SECTION = "//div[@aria-label='suggested-address-section']"

    # Original address elements
    ORIGINAL_ADDRESS_LINE1 = "//div[@aria-label='original-address-section']//p[@aria-label='address-line-1']"
    ORIGINAL_ADDRESS_LINE2 = "//div[@aria-label='original-address-section']//p[@aria-label='address-line-2']"
    ORIGINAL_ADDRESS_CITY_STATE_ZIP = "//div[@aria-label='original-address-section']//p[@aria-label='address-line-city-state-zip']"

    # Suggested address elements
    SUGGESTED_ADDRESS_LINE1 = "//div[@aria-label='suggested-address-section']//p[@aria-label='address-line-1']"
    SUGGESTED_ADDRESS_LINE2 = "//div[@aria-label='suggested-address-section']//p[@aria-label='address-line-2']"
    SUGGESTED_ADDRESS_CITY_STATE_ZIP = "//div[@aria-label='suggested-address-section']//p[@aria-label='address-line-city-state-zip']"

    # Radio buttons for address selection
    USE_ORIGINAL_RADIO = "//input[@type='radio' and @value='original']"
    USE_SUGGESTED_RADIO = "//input[@type='radio' and @value='suggested']"

    # Error message
    ERROR_MESSAGE = "//div[@aria-label='usps-error-message']"

    # Action buttons
    SAVE_BUTTON = "//button[text()='Save']"
    BACK_BUTTON = "//button[text()='Back']"
    CANCEL_BUTTON = "//button[text()='Cancel']"
