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
FINISH_BUTTON = '#action-bar-btn-finish'
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
