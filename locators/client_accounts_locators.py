"""
Locators for Client Accounts Page

This module contains all locator definitions for the Client Accounts page.
"""

# ========================================================================================
# LOCATORS - All page element locators defined for easy maintenance
# ========================================================================================

# IFrame and container locators
ESIG_IFRAME = "iframe#esig_iframe"
DROPDOWN_DIV = "div#dropdownDiv"
NOTE_TC_DIV = "div#noteTc"

# Form input locators
AUTHORIZED_SIGNERS_DROPDOWN = "select[name='authorizedSignersDropdown']"
AUTHORIZED_SIGNERS_SELECTED_OPTION = "select[name='authorizedSignersDropdown'] option[selected]"
AUTHORIZED_SIGNERS_DROPDOWN_DISABLED = "select[name='authorizedSignersDropdown'][disabled]"
EMAIL_INPUT = "input[name='emailText']"
PHONE_INPUT = "input[name='PhoneText']"
CONTINUE_BUTTON = "input[type='submit'][value='Continue']"

# Radio button and approval option locators
RADIO_YES = "input[value='radiobtnYes']"
RADIO_NO = "input[value='radiobtnNo']"
RADIO_SMS = "input#radiobtnSMS"
RADIO_TC = "input#radiobtnTC"

# Label locators
AUTHORIZED_SIGNERS_LABEL = "span:has-text('Authorized Signers')"
EMAIL_ADDRESS_LABEL = "span:has-text('Email Address')"
PHONE_LABEL = "span:has-text('Phone')"

# Dialog and form elements
DIALOG_ROLE = '[role="dialog"]'
CONFIRMATION_LINK = 'a.printConfirmationLink'
DOWNLOAD_LINK = 'a[onclick*="btnDownload"]'
CLOSE_BUTTON_CONTAINER = '.close-button-container button.formButton'

# Request/Type table locators
TABLE_CONTAINER = "#divlstContainer"
REQUEST_LIST = "#HTMLlslCategory"
REQUEST_LIST_ITEM = "#lstcategoryli0"
SUBCATEGORY_CONTAINER = "#divSubCategory"
SUBCATEGORY_LIST = "#HTMLSubCategory"

# Submit buttons
COMPLETE_SUBMIT_BUTTON = "OnlineSubmitbutton"
COMPLETE_PRINT_BUTTON = "HTMLPrintButton"
COMPLETE_ESIGN_BUTTON = "eSignatureButton"

# Form elements
FORM_HEADING_SPAN = "span#ctl00_cphContentArea_AccountActionsBox1_lblTaskName"
FORM_HEADING_BOLD = "b"
MODAL_TITLE = "div.modal-title-transition"

# Radio buttons for signature options
RADIO_SUBMIT = "input#rbSubmit"
RADIO_PRINT = "input#rbPrint"
RADIO_ESIGN = "input#rbEsign"

# Dialog action buttons
CANCEL_BUTTON = "input#btnCancel"
CONTINUE_BUTTON_DIALOG = "input#btnContinue"

# Client In Person Signing Dialog locators
CLIENT_IN_PERSON_SIGNING_DIALOG = '[role="dialog"][aria-describedby="divConfirmation"]'
CLIENT_IN_PERSON_SIGNING_HEADING = "div.modal-title-transition"
CLIENT_IN_PERSON_SIGNING_BODY = "div#divConfirmation"
CLIENT_IN_PERSON_SIGNING_PARAGRAPH = "div#divConfirmation p"
CLIENT_IN_PERSON_SIGNING_LIST = "ul.inPersoneSigList"
CLIENT_IN_PERSON_SIGNING_LIST_ITEMS = "ul.inPersoneSigList li.inPersoneSigMain"
CLIENT_IN_PERSON_SIGNING_BUTTON_RETURN = "button.formButton:has-text('Return to eWealthManager')"
CLIENT_IN_PERSON_SIGNING_BUTTON_START = "button.formButton:has-text('Start Client Signing')"
CLIENT_IN_PERSON_SIGNING_BUTTONS = "button.formButton"

# Finish Later Dialog locators
FINISH_LATER_DIALOG = '[role="dialog"]'
FINISH_LATER_DIALOG_TITLE = "div.modal-title-transition"
FINISH_LATER_DIALOG_BODY = "div#divConfirmation"
FINISH_LATER_DIALOG_TEXT = "div#divConfirmation p"
FINISH_LATER_BUTTON_SAVE = "button.formButton:has-text('Save')"
FINISH_LATER_BUTTON_SAVE_XPATH = "//button[text()='Save']"
FINISH_LATER_BUTTON_DELETE = "button.formButton:has-text('Delete')"

# Generic form button locator - use with button text parameter
# Example: page.locator('button.formButton:has-text("Return to eWealthManager")')
FORM_BUTTON_SELECTOR = "button.formButton"
