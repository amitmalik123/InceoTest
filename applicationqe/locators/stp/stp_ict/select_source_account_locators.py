class SelectSourceAccountLocators:
    # Label template: find by account number text, then traverse to sibling checker div
    ACCOUNT_LABEL_TEMPLATE = "label[for='mInfo_AccountData']:has-text('Account #: {account_number}')"
    NEXT = {"role": "button", "name": "Next"}
