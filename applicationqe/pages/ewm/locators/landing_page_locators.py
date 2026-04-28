"""
Locators for Landing Page elements - Account Selection Phase
"""

class LandingPageLocators:
    """Locators for landing page account selection elements"""
    
    # Page identification
    PAGE_TITLE = "AssetMark - Digital Maintenance"
    TRANSFER_HEADING = "Transfer Assets Between Accounts"
    JOURNAL_TEXT = "Journal"
    
    # Live Chat
    LIVE_CHAT_CLOSE = "button[aria-label='Close']"
    LIVE_CHAT_TIMEOUT = 3000
    
    # Account Selection
    DESTINATION_ACCOUNT_BUTTON_ROLE = "button"
    DESTINATION_ACCOUNT_LISTITEM_ROLE = "listitem"
    
    # Other Account Configuration
    OTHER_ACCOUNT_NAME_INPUT = "AccountNameInput"
    OTHER_ACCOUNT_NUMBER_INPUT = "AccountNumberInput"
    OTHER_ACCOUNT_CONFIRM_INPUT = "ConfirmAccountNumberInput"
    QUALIFIED_CHECKBOX = "Qualifiedcheckbox"
    ACCOUNT_STATUS_RADIO = "radio"
    
    # Navigation buttons for landing page
    NEXT_BUTTON = "NEXT"
    CANCEL_BUTTON = "CANCEL"
    
    # Landing page button collection
    LANDING_PAGE_BUTTONS = ["CANCEL", "NEXT"]
    
    # Timeouts
    NETWORK_IDLE_TIMEOUT = 30000
    ELEMENT_TIMEOUT = 3000