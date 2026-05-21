"""Locators for Account Wizard Page elements."""


class AccountWizardLocators:
    """Raw selector strings for the Account Wizard page."""

    ACCOUNT_WIZARD_LINK = "Account Wizard"
    ACCOUNT_WIZARD_HEADING = "Account Wizard"
    SELECTED_ACCOUNT_LABEL = "div.radio:has(span.checked) + label"
    COMPLETE_AND_SUBMIT_BTN = "#OnlineSubmitbutton"
    ADDRESS_CHANGE_LINK = "#ctl00_cphContentArea_lnkAddressChange"
    NEXT_BUTTON = "//input[@value='Next']"
    LOADING_MODAL = "#loadingImageModal"
    ADD_ACH_LINK = "Add ACH Instructions and/or Standing Letter of Authorization"
