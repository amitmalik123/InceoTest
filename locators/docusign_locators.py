"""
Locators for DocuSign Page

This module contains all locator definitions for the DocuSign signing page.
"""

# DocuSign URL pattern
DOCUSIGN_URL_PATTERN = "https://apps-d.docusign.com/"

# ========================================================================================
# LOCATORS - All page element locators defined for easy maintenance
# ========================================================================================

# ERSD Consent checkbox and related text
ERSD_CONSENT_TEXT = "I confirm I have read and I consent to the Electronic Record and Signature Disclosure."

# Button locators
# ACTION_BUTTON_WRAPPER is the parent div containing Finish button (scoped search)
ACTION_BUTTON_WRAPPER = '[data-qa="action-button-wrapper"]'
# FINISH_BUTTON uses data-qa attribute (stable for testing)
# Note: Preferably use get_by_role("button", name="Finish") scoped to ACTION_BUTTON_WRAPPER for maximum robustness
FINISH_BUTTON = 'button[data-qa="action-bar-btn-finish"]'
FINISH_BUTTON_TEXT = "Finish"  # For get_by_role() method
SEND_NOW_BUTTON_PATTERN = "Send Now"
CONFIRM_CODE_BUTTON_PATTERN = "Confirm Code"
RESEND_CODE_BUTTON_PATTERN = "Resend Code"
SIGN_HERE_BUTTON_PATTERN = r"Required\s*-\s*Sign Here"
SIGNATURE_APPLIED_BUTTON_PATTERN = r"Required\s*-\s*Signature Applied"

# Dialog locators
REVIEW_CONTINUE_DIALOG = '[aria-label="Review and continue"]'
DIALOG_CONTENT_P_TAG = 'p[data-qa="email-message-content"]'

# Sign button and signature elements
SIGN_BUTTON = '//div[@data-type="SignHere"]/button'
SIGNATURE_TAB_BUTTON = "//button[contains(@data-qa,'signature-tab-required')]"
DATE_SIGNED_INPUT = "//div[@data-type='DateSigned']/descendant::input"

# Session timeout banner
SESSION_TIMEOUT_BANNER = "#ds_hldrBdy_lblHeaderText"

# Stamping element (dynamic text-based locator)
STAMPING_ELEMENT_TEXT_KEY = "As authorized by"  # Used with get_by_text()

# OTP field (dynamic regex pattern)
OTP_FIELD_NAME_PATTERN = "verification code"  # Used with get_by_role()

# Adopt Signature Modal locators
ADOPT_SIGNATURE_MODAL = '[data-qa="adopt-signature-modal"]'
ADOPT_AND_SIGN_BUTTON_TEXT = "Adopt and Sign"  # Used with get_by_role()
ADOPT_AND_SIGN_BUTTON_DATA_QA = "adopt-submit"  # Alternative: data-qa attribute
