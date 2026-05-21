"""Locators for Change Investments Page elements."""


class ChangeInvestmentsLocators:
    """Raw selector strings for the Change Investments page."""

    ACCOUNT_WIZARD_LINK = "#clientDetailAccountDetailAnchor"
    CHANGE_INVESTMENTS_LINK = "Change Investments"
    NEXT_BUTTON = "Next"
    BACK_BUTTON = "Back"
    INVESTMENT_ACTION_MODAL = "#InvestmentActionModal"
    RADIO_DESTINATION_INVESTMENT = "input[name='action'][value='DestinationInvestment']"
    RADIO_MODIFY_ALLOCATIONS = "input[name='action'][value='ModifyAllocations']"
    MODAL_OK_BUTTON = "OK"
    MODAL_CANCEL_BUTTON = "Cancel"
    STEP_INVESTMENT_SELECTION = "Investment Selection"
    STEP_ACCOUNT_NUMBER = "Account Number"
    COMPLETION_MODAL = "#eSigConfirmModal, .modal:has-text('Investment Change Completed')"
