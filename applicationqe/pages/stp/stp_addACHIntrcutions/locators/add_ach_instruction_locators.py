"""Locators for Add ACH Instruction Page elements."""


class AddACHInstructionLocators:
    """Raw selector strings for the Add ACH Instruction page."""

    ROUTING_NUMBER = 'input[maxlength="9"][inputmode="numeric"]'
    BANK_ACCOUNT_NUMBER = '[aria-label="Bank-AccountNumber"] input'
    CONFIRM_BANK_ACCOUNT_NUMBER = '[aria-label="Confirm-BankAccount-Number"] input'
    VERIFY_BUTTON = "span:text('Verify')"
    BANK_NAME_DISPLAY = "span:text('Bank Name') + span"
    NAME_ON_BANK_ACCOUNT = '[aria-label="Bank-Account-OwnerName"] textarea[aria-invalid]'
    ADDITIONAL_BANK_ACCOUNT_OWNER_NAME_PLACEHOLDER = "Additional Bank Account Owner Name"
    NEXT_BUTTON = "Next"
    ACCOUNT_NAME_LIST_TESTID = "account-details"
    ACCOUNT_NAME_SPAN = "span"
    CHECKING_RADIO = "Checking"
    SAVINGS_RADIO = "Savings"
    FIRST_PARTY_RADIO = "1st Party"
    THIRD_PARTY_RADIO = "3rd Party"
    CERTIFY_CHECKBOX = "input[name='certifyCheckbox']"
    INVESTMENT_ACCOUNT_CHECKBOX_TESTID = "checkbox"
    INVESTMENT_ACCOUNT_CHECKBOX_INPUT = "input[type='checkbox']"
