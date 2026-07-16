"""Locators for BAW Transfer Attributes page."""


class TransferAttributesLocators:
    COACH_IFRAME = "iframe[title='Coach']"

    # Transfer request - role names
    FULL_RADIO_ROLE = "Full"
    PARTIAL_RADIO_ROLE = "Partial"
    NON_ACAT_CHECKBOX_ROLE = "non-ACAT"
    CONTRIBUTION_CODE = '[id="singleselect-TransferAttributesCV\\:ContributionCode"]'
    CONTRA_FIRM_ACCOUNT_ROLE = "Contra Firm Account"
    CONTRA_FIRM_NAME_LINE1_ROLE = "Contra Firm Name Line 1"
    CONTRA_FIRM_NAME_LINE2_ROLE = "Contra Firm Name Line 2"
    AMOUNT_ROLE = "Amount"
    ESTIMATED_RADIO_ROLE = "Estimated"
    SPECIAL_INSTRUCTIONS_ROLE = "Special Instructions"

    # Chosen.js widgets
    CLEARING_FIRM_CHOSEN = "#singleselect_TransferAttributesCV_ClearingFirm_chosen"
    CLEARING_FIRM_CHOSEN_LINK = "//div[@id='singleselect_TransferAttributesCV_ClearingFirm_chosen']/a"
    CONTRA_FIRM_CHOSEN = "//div[@id='singleselect_TransferAttributesCV_ContraFirm_chosen']/a/div"
    CONTRA_FIRM_REGISTRATION_CHOSEN = "//div[@id='singleselect_TransferAttributesCV_ContraFirmRegistration_chosen']/a/div"
    CONTRA_FIRM_RESULTS = "#singleselect_TransferAttributesCV_ContraFirm_chosen .chosen-results li"
    CLEARING_FIRM_RESULTS = "#singleselect_TransferAttributesCV_ClearingFirm_chosen .chosen-results li"
    CONTRA_FIRM_REGISTRATION_RESULTS = "#singleselect_TransferAttributesCV_ContraFirmRegistration_chosen .chosen-results li"

    # Destination account
    HEADER_ACCOUNT_TEXT = "Account #"
    DESTINATION_ACCOUNT = '[id="singleselect-TransferAttributesCV\\:AccountNumberSelect"]'
    DESTINATION_AMOUNT_ROLE = "Destination Amount"
    ADD_BUTTON_ROLE = "Add"
    CREATE_FUNDING_ACCOUNT_ROLE = "Create Funding Account"
    CREATE_FUNDING_ACCOUNT_INPUT_ROLE = "Funding Account #"
    CREATE_TOAR_BUTTON_ROLE = "Create TOAR Record"
    EDS_CONFIRMATION_NUMBER_ROLE = "EDS Confirmation Number"
    SUBMITTED_TO_FIDELITY_ROLE = "Submitted to Fidelity"
    SAVE_CLOSE_BUTTON_ROLE = "Save & Close"
    WARNING_CHECKBOXES = "input[id*='WarningCheckboxes']"
    WARNING_PROCEED_BUTTON = "[id*='WarningPopupProceedButton']"
    DESTINATION_ACCOUNTS_TABLE = '[data-viewid="DestinationAccountsTable"]'
    ERROR_MSG = ".error-message"
    ALERT_INDICATOR = "[role='alert']"
    IWR_COMPLETE_ROLE = "IWR Complete"
    CREATE_TOAD_BUTTON_ROLE = "Create TOAD Record"
    CREATE_CHECKLIST_BUTTON_ROLE = "Create Checklist"
    CHECKLIST_TABLE = "[data-viewid='CreateChecklistTable']"
    TOAD_SUCCESS_ALERT = ".alert-success"
    TRANSFER_RECORDS_PANELS = "[data-viewid='TransferRecordsPanel']"
    QUESTION_CHECK = "//table[@class='table table-striped']//tr//div[contains(@class,'_style CPP CoachView_show')]//textarea[not(@disabled)]"
    COST_BASIS = "select[id*='CostBasis']"
    COST_BASIS_DISABLED = "select[id*='CostBasis'][disabled]"

    # Delivery method & allocation (dynamic — use .format(...))
    ALLOCATION_UNIT_RADIO_TPL = "input[value='{allocation_unit}']"
    DELIVERY_METHOD_RADIO_TPL = "input[value='{delivery_method_value}']"

    # Full/Partial Transfer Out In Kind radios
    CUSTODIAN_CHANGE_NO = "input[id*='CustodianChange'][value='No']"
    WHAT_TRANSFERRED_BOTH = "input[id*='WhatIsBeingTransferred'][value='Both']"
    PTD_ELIGIBILITY_NO = "input[id*='PTDEligibility'][value='No']"
    BONDS_IN_ACCOUNT_NO = "input[id*='BondsInAccount'][value='No']"

    # Non-Transferable Securities radios
    OPTIONS_NO_OPTIONS = "input[id*='Options'][value='NoOptions']"
    SECURITIES_TO_EXCLUDE_NO = "input[id*='SecuritiesToExclude'][value='No']"
    SECURITIES_TO_SELL_NO = "input[id*='SecuritiesToSell'][value='No']"

    # TOAD Securities table
    ADD_SECURITIES_BUTTON = '[id="button-button-TransferAttributesCV:AddSecuritiesToTransferButton"]'
    SECURITY_DROPDOWN = "#singleselect_TransferAttributesCV_SecuritiesToTransferTable_TransferSecurityCell_0__TransferSecurity_chosen"
    CHOSEN_ACTIVE_RESULTS = ".chosen-results li.active-result"

    # Create TOAD Record radios/checkboxes
    PENDING_TRADES_NO = "input[id*='PendingTrades'][value='No']"
    IMPLICATION_ACK_CHECKBOX = "input[id*='Implication_Ack_Checkbox']"
    PANEL_TITLE = ".panel-title"
    PANEL_BODY = ".panel-body"
