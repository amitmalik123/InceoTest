"""Locators for Withdrawal Method Modal Page elements."""


class WithdrawalMethodModalLocators:
    """Raw selector strings for the Withdrawal Method Modal page."""

    IFRAME = "#esig_iframe"
    MODAL_HEADER = "//div[@class='modal-title-transition' and text()='Withdrawal Method']"
    ACH_RADIO = "#rbAch"
    WIRE_RADIO = "#rbWire"
    CHECK_RADIO = "#rbCheck"
    CONTINUE_BUTTON = "#btnContinue"
    SELECTED_INSTRUCTIONS_TABLE = "//span[@class='checked']//parent::div//following-sibling::table"
