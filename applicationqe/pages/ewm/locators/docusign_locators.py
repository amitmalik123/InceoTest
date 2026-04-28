"""
Locators for DocuSign Integration elements
"""

class DocuSignLocators:
    """Locators for DocuSign integration elements"""
    
    # URL patterns
    DOCUSIGN_URL_REGEX = r".*docusign.*"
    DOCUSIGN_URL_PATTERN = "**/docusign/**"
    
    # Page elements
    CONFIRMATION_CHECKBOX_ROLE = "checkbox"
    CONTINUE_BUTTON = "Continue"
    SIGN_BUTTON = "Sign"
    FINISH_BUTTON = "Finish"
    
    # Confirmation elements
    CONFIRM_CHECKBOX_TEXT = "I agree to use electronic records and signatures"
    READY_FOR_SIGNATURE_TEXT = "Ready for Signatures"
    
    # DocuSign specific selectors
    DOCUSIGN_FRAME = "iframe[src*='docusign']"
    SIGNATURE_PAD = ".signature-pad"
    DOCUMENT_CONTAINER = ".document-container"
    
    # Status messages
    SIGNING_COMPLETE = "Signing Complete"
    DOCUMENT_SIGNED = "Document Signed"
    
    # Navigation
    BACK_TO_APPLICATION = "Back to Application"
    
    # Timeouts
    DOCUSIGN_LOAD_TIMEOUT = 20000
    SIGNING_TIMEOUT = 30000
    NETWORK_IDLE_TIMEOUT = 10000