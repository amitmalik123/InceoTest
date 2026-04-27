"""
Locators for Transaction Details Page elements - Transaction Configuration Phase
"""

class TransactionDetailsLocators:
    """Locators for transaction details configuration elements"""
    
    # Distribution Types
    JOURNAL_PORTION = "Journal Portion of Account"
    JOURNAL_SECURITIES = "Journal Securities"
    JOURNAL_ENTIRE = "Journal Entire Account"
    
    # Portion Types
    DOLLAR_AMOUNT = "$ Amount"
    PERCENTAGE = "% Percentage"
    
    # Amount Input
    AMOUNT_TEXTBOX_ROLE = "textbox"
    AMOUNT_INPUT = {
        "role": "textbox"
    }
    
    # Securities Selection
    ALL_BUTTON_NAME = "All"
    COMBOBOX_ROLE = "combobox"
    OPTION_ROLE = "option"
    CHECKBOX_ROLE = "checkbox"
    
    # Signature Options
    NO_SIGNATURE = "Do Not Obtain Client Signature(s)"
    ELECTRONIC_SIGNATURE = "Obtain Electronic Client Signature(s)"
    PRINT_SIGNATURE = "Print to Obtain physical Client Signature(s)"
    
    # Navigation buttons for transfer request page
    NEXT_BUTTON = "NEXT"
    BACK_BUTTON = "BACK"
    CANCEL_BUTTON = "CANCEL"
    
    # Cash and calculation elements
    APPROX_TEXT = "Approx:"
    RESTRICTED_CASH = "N/A"
    JOURNAL_PORTION_WARNING_SELECTOR = ".warning-message"
    
    # UI Collections
    DISTRIBUTION_OPTIONS = [
        "Journal Portion of Account",
        "Journal Securities", 
        "Journal Entire Account"
    ]
    
    SIGNATURE_OPTIONS = [
        "Do Not Obtain Client Signature(s)",
        "Obtain Electronic Client Signature(s)",
        "Print to Obtain physical Client Signature(s)"
    ]
    
    TRANSACTION_PAGE_BUTTONS = ["CANCEL", "BACK", "NEXT"]
    
    # Timeouts
    ELEMENT_TIMEOUT = 3000
    NETWORK_IDLE_TIMEOUT = 10000