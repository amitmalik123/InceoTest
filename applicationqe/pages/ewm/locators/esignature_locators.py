"""
Locators for Electronic Signature Page elements
"""

class ESignatureLocators:
    """Locators for electronic signature page elements"""
    
    # Page elements
    ESIGNATURE_SECTION_HEADING = "Electronic Signature"
    ESIGNATURE_SUBHEADING = "eSign"
    
    # Form fields
    EMAIL_TEXTBOX_ROLE = "textbox"  # First textbox
    PHONE_TEXTBOX_ROLE = "textbox"  # Last textbox  
    COMBOBOX_ROLE = "combobox"
    OPTION_ROLE = "option" 
    CONFIRMATION_CHECKBOX_ROLE = "checkbox"
    
    # Field labels
    EMAIL_LABEL = "Email"
    PHONE_LABEL = "Phone"
    
    # Navigation
    NEXT_BUTTON = "NEXT"
    
    # Validation
    ERROR_SELECTORS = [".error", ".validation-error", "[class*='error']"]
    
    # Default values for testing
    DEFAULT_EMAIL = "test@example.com"
    DEFAULT_PHONE = "(555) 123-4567"
    
    # Timeouts
    ELEMENT_TIMEOUT = 5000