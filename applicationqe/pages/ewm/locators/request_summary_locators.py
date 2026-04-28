"""
Locators for Request Summary Page elements
"""

class RequestSummaryLocators:
    """Locators for request summary page elements"""
    
    # Page headings
    REQUEST_SUMMARY_HEADING = "Request Summary"
    REQUEST_TYPE_LABEL = "Request Type:"
    
    # Submission buttons
    SUBMIT_BUTTON = "SUBMIT"
    SUBMIT_TO_REVIEW_BUTTON = "SUBMIT TO REVIEW"
    
    # Submission button selectors
    SUBMIT_BUTTON_SELECTOR = "button:has-text('SUBMIT'):not(:has-text('REVIEW'))"
    SUBMIT_TO_REVIEW_SELECTOR = "button:has-text('SUBMIT TO REVIEW')"
    
    # Page buttons collection
    REVIEW_SUMMARY_PAGE_BUTTONS = [
        "CANCEL",
        "BACK", 
        "SUBMIT TO REVIEW"
    ]
    
    # Status and confirmation
    CONFIRMATION_TEXT = "Request submitted successfully"
    STATUS_PENDING = "In Process - Pending Settlement"
    
    # Item tracking
    ITEM_NUMBER_LABEL = "Item number:"
    ITEM_NUMBER_REGEX = r"A\d+"
    ITEM_NUMBER_FULL_REGEX = r"A\d{9}"
    
    # Date format pattern  
    DATE_TIME_REGEX = r"\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2} (AM|PM) PT"
    
    # Warning and alert selectors
    WARNING_SELECTORS = ["[role='alert']", ".alert", ".warning"]
    
    # Confirmation page elements
    CONFIRMATION_PAGE_BUTTON = "CLOSE"
    REQUEST_SUMMARY_VERBIAGE = "Please click on the item number above to print the completed form for this request."
    
    # Amount display format
    AMOUNT_DISPLAY_PREFIX = "Portion of Account | "
    
    # Timeouts
    CONFIRMATION_TIMEOUT = 10000
    ELEMENT_TIMEOUT = 5000