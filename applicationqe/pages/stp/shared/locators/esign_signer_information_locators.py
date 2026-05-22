"""Locators for eSign Signer Information Page elements."""


class ESignSignerInformationLocators:
    """Raw selector strings for the eSign Signer Information iframe page."""

    IFRAME = "#esig_iframe"
    PAGE_TITLE = "//div[contains(text(),'Signer') and contains(text(),'Information')]"
    FIRST_SIGNER_ROW = "//tr[td[contains(normalize-space(),'Account Owner')]]"
    TEXT_INPUT = "input[type='text']"
    RADIO_INPUT = "input[type='radio']"
    # Use .nth(0), .nth(1), .nth(2) on TEXT_INPUT for name/email/phone respectively.
    # Use .nth(0), .nth(1) on RADIO_INPUT for in-person/by-email respectively.
