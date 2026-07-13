"""
Locators for DocuSign Integration elements - Merged EWM + STP
"""

class DocuSignLocators:
    """Locators for DocuSign integration elements"""
    
    # URL patterns
    DOCUSIGN_URL_REGEX = r".*docusign.*"
    DOCUSIGN_URL_PATTERN = "**/docusign/**"
    
    # ERSD Modal locators (STP - comprehensive)
    ERSD_MODAL = '[data-qa="ersd-modal"]'
    ERSD_MODAL_ARIA = '[aria-label="Review and continue"]'
    ERSD_CONSENT_CHECKBOX = '[data-qa="ersd-agree-checkbox"]'
    ERSD_CONSENT_CHECKBOX_LABEL = '[data-qa="ersd-agree-checkbox-label"]'
    ERSD_CONTINUE_BUTTON = '[data-qa="ersd-modal-agree"]'
    ERSD_DISCLOSURE_LINK = '[data-qa="show-consumer-disclosure-modal"]'
    DIALOG_CONTENT = 'p[data-qa="email-message-content"]'

    # Action buttons (STP)
    ACTION_BUTTON_WRAPPER = '[data-qa="action-button-wrapper"]'
    FINISH_BUTTON = 'button[data-qa="envelope-finish"]'
    END_OF_DOCUMENT_FINISH_BUTTON = '#end-of-document-btn-finish'
    OTHER_ACTIONS_BUTTON = 'button[aria-label="Other Actions"]'
    FINISH_LATER_OPTION = '//span[@data-qa="exit-text"]'
    ADOPT_SIGNATURE_MODAL = '[data-qa="adopt-signature-modal"]'

    # Signature locators (STP)
    SIGN_BUTTON = '//div[@data-type="SignHere"]/button'
    SIGNATURE_TAB_BUTTON = "//button[contains(@data-qa,'signature-tab-required')]"
    DATE_SIGNED_INPUT = "//div[@data-type='DateSigned']/descendant::input"
    SESSION_TIMEOUT_BANNER = '#ds_hldrBdy_lblHeaderText'
    D_NUMBER_SPAN = '//span[starts-with(text(),"D00")]'

    # Modal dialogs (STP)
    DONE_SIGNING_MODAL = '[data-qa="save-a-copy-done-dialog"]'
    DONE_SIGNING_TITLE = '[data-qa="dialog-title"]'
    DONE_SIGNING_CONTINUE_BUTTON = '[data-qa="dialog-submit"]'

    ESIGN_COMPLETE_MODAL = '#divConfirmation'
    ESIGN_COMPLETE_TITLE = '#divConfirmation .modal-title-transition'
    ESIGN_D_NUMBER_LINK = 'a.eSignConfirmationLink'
    ESIGN_CLOSE_BUTTON = '#divConfirmation button.formButton'

    # OTP/Verification flow (STP)
    SEND_NOW_BUTTON = 'button[data-qa*="send-now"]'
    RESEND_CODE_BUTTON = 'button[data-qa*="resend-code"]'
    SEND_NOW_FALLBACK_BUTTONS_TEXT = r'Send Now|send now'

    VERIFY_SEND_NOW_BUTTON = '[data-qa="verify-choose-method-primary-button"]'
    VERIFY_OTP_TITLE = '[data-qa="verify-confirm-code-title"]'
    VERIFY_OTP_INPUT = '[data-qa="verify-confirm-code-verification-code-input"]'
    VERIFY_CONFIRM_BUTTON = '[data-qa="verify-confirm-code-primary-button"]'
    ACTION_BAR_FINISH_BUTTON = '[data-qa="action-bar-btn-finish"]'
    
    # Page elements (EWM - basic)
    CONFIRMATION_CHECKBOX_ROLE = "checkbox"
    CONTINUE_BUTTON = "Continue"
    
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