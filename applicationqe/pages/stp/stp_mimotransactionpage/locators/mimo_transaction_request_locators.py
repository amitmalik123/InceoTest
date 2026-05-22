"""Locators for MIMO Transaction Request Page elements."""


class MIMOTransactionRequestLocators:
    """Raw selector strings for the MIMO Transaction Request page."""

    HEADER_ITEM = "//h1[.='Transaction request']"
    NEXT_BUTTON = "//button[text()='Next']"
    CANCEL_BUTTON = "//button[contains(text(),'Cancel')]"
    INSTRUCTIONS_ON_FILE_HEADING = "//h3[text()='Instructions on file']"
    INSTRUCTIONS_MESSAGE = "//div[@aria-label='swp-cancel-info-instruction-message']"
