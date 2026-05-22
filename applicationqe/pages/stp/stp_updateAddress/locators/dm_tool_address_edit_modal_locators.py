"""Locators for DM Tool Address Edit Modal elements (raw string XPath attributes)."""


class DMToolAddressEditModalLocators:
    """Raw XPath/CSS selector strings for the DM Tool Address Edit Modal.
    
    NOTE: These are used as raw strings (self.x = loc.X), not as Playwright Locators,
    because methods call self.page.locator(self.x) internally.
    """

    # Modal elements
    MODAL_TITLE = "//h2[contains(text(),'Edit Address')]"
    MODAL_CONTAINER = "//div[@role='dialog']"
    MODAL_TITLE_TEXT = "//div[@data-testid='form-name']//h2"
    PLACE_TO_CLICK_OUTSIDE = "//div[@data-testid='form-name']//h2"
    NO_PO_TEXT = ".form-warning h3"

    # Div sections
    ADDRESS_LINE_DIV = "//div[@data-testid='addressLine1Div']"
    ADDRESS_LINE_OPTIONAL_DIV = "//div[@data-testid='addressLine2Div']"
    CITY_DIV = "//div[@data-testid='cityDiv']"
    STATE_DIV = "//div[@aria-label='form-select-item']"
    ZIP_DIV = "//div[@data-testid='zipCodeDiv']"
    EXTENSION_DIV = "//div[@data-testid='extensionDiv']"

    # Form input fields
    STREET_INPUT = "//div[@aria-label='form-input-item']//input[@name='addressLine1']"
    STREET2_INPUT = "//div[@aria-label='form-input-item']//input[@name='addressLine2']"
    CITY_INPUT = "//div[@aria-label='form-input-item']//input[@name='city']"
    STATE_DROPDOWN = "//div[@aria-label='form-select-item']//select"
    ZIP_INPUT = "//div[@aria-label='form-input-item']//input[@name='zipCode']"
    ZIP_EXTENSION_INPUT = "//div[@aria-label='form-input-item']//input[@name='extension']"

    # Label texts
    ADDRESS_LINE_TEXT = "//div[@aria-label='form-input-item']//label[@for='addressLine1']"
    ADDRESS_LINE_OPTIONAL_TEXT = "//div[@aria-label='form-input-item']//label[@for='addressLine2']"
    CITY_TEXT = "//div[@aria-label='form-input-item']//label[@for='city']"
    STATE_TEXT = "//div[@aria-label='form-select-item']//label[@for='state']"
    ZIP_TEXT = "//div[@aria-label='form-input-item']//label[@for='zipCode']"
    EXTENSION_TEXT = "[for='extension']"

    # PO Box checkbox
    PO_BOX_CHECKBOX = "//span[@aria-label='checkbox']"
    PO_BOX_CHECKBOX_IOS = "[type='checkbox']"

    # Error message elements
    UPDATE_ERROR_TEXT = "//span[@aria-label='error-message']"

    # Action buttons
    NEXT_BUTTON = "//div[@role='presentation']/div[3]//form//button[2]"
    CANCEL_BUTTON = "//div[@role='presentation']/div[3]//form//button[1]"
    BACK_BUTTON = "//button[text()='Back']"
