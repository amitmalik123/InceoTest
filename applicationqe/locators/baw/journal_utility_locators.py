"""Locators for BAW Journal Utility page."""


class JournalUtilityLocators:
    COACH_IFRAME = "iframe[title='Coach']"
    DESTINATION_ACCOUNT = '[id="singleselect-JournalCV1\\:DestinationManageAccountNumber"]'
    DESTINATION_MODEL_NAME = '[id="textarea-textarea-JournalCV1\\:DestinationModelName"]'
    UNIT_LABEL = "Unit"
    AMOUNT_LABEL = "Amount"
    ADD_JOURNAL_BUTTON_ROLE = "Add Journal"
    SAVE_AND_CLOSE_BUTTON_ROLE = "Save & Close"
    PENDING_JOURNAL_CELLS = "table:has(th[aria-label='Dest Acct Name']) tbody td"
