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
