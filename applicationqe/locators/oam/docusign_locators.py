"""
Locators for DocuSign Page

This module contains all locator definitions for the DocuSign signing page.
"""

# DocuSign URL pattern - simple substring check
# Matches any DocuSign domain: production, demo, staging, etc.
# Examples: www.docusign.net, demo.docusign.net, apps-d.docusign.com, verify-d.docusign.net
DOCUSIGN_URL_KEYWORD = "docusign"
# ========================================================================================
# LOCATORS - All page element locators defined for easy maintenance
# ========================================================================================

# ERSD Modal and Consent Checkbox Locators
# ================================================
# PRIMARY: Use data-qa selectors (most stable)
# FALLBACK: Use ARIA/text locators (for other environments/versions)

# ERSD Modal Dialog
ERSD_MODAL_PRIMARY = '[data-qa="ersd-modal"]'  # Primary: data-qa selector for ERSD modal container
ERSD_MODAL_ARIA = '[aria-label="Review and continue"]'  # Fallback: ARIA label

# ERSD Consent Checkbox
ERSD_CONSENT_CHECKBOX_PRIMARY = '[data-qa="ersd-agree-checkbox"]'  # Primary: stable data-qa selector
ERSD_CONSENT_CHECKBOX_LABEL = '[data-qa="ersd-agree-checkbox-label"]'  # Label element (associated with checkbox)
ERSD_CONSENT_TEXT = "I confirm I have read and I consent to the Electronic Record and Signature Disclosure."  # Fallback: text-based locator

# ERSD Continue Button
ERSD_CONTINUE_BUTTON_PRIMARY = '[data-qa="ersd-modal-agree"]'  # Primary: stable data-qa selector
ERSD_CONTINUE_BUTTON_TEXT = "Continue"  # Fallback: button text (for get_by_role)

# Button locators
# ACTION_BUTTON_WRAPPER is the parent div containing Finish button (scoped search)
ACTION_BUTTON_WRAPPER = '[data-qa="action-button-wrapper"]'
# FINISH_BUTTON uses data-qa attribute (stable for testing)
# Note: Preferably use get_by_role("button", name="Finish") scoped to ACTION_BUTTON_WRAPPER for maximum robustness
FINISH_BUTTON = 'button[data-qa="envelope-finish"]'
FINISH_BUTTON_TEXT = "Finish"  # For get_by_role() method
SEND_NOW_BUTTON_PATTERN = "Send Now"
CONFIRM_CODE_BUTTON_PATTERN = "Confirm Code"
RESEND_CODE_BUTTON_PATTERN = "Resend Code"
SIGN_HERE_BUTTON_PATTERN = r"Required\s*-\s*Sign Here"
SIGNATURE_APPLIED_BUTTON_PATTERN = r"Required\s*-\s*Signature Applied"

# Dialog content verification
REVIEW_CONTINUE_DIALOG = '[aria-label="Review and continue"]'  # Backward compatibility alias for ERSD_MODAL_ARIA (used in fetch_docusign_review_and_continue_dialog_text)
DIALOG_CONTENT_P_TAG = 'p[data-qa="email-message-content"]'  # Message text verification
ERSD_DISCLOSURE_LINK = '[data-qa="show-consumer-disclosure-modal"]'  # Disclosure link in modal

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

# D-Number Locators
# Document tracking number displayed in envelope completion messages
D_NUMBER_SPAN = '//span[starts-with(text(),"D0")]'  # XPath to match D-number spans (e.g., D003525811, D003518970)

# Finish Later Locators
# ================================================
# Used for deferred completion of signing process
OTHER_ACTIONS_BUTTON = 'button[aria-label="Other Actions"]'  # Main dropdown menu button
FINISH_LATER_OPTION = '//span[@data-qa="exit-text"]'  # Option text in the menu
FINISH_LATER_BUTTON_TEXT = "Finish Later"  # Alternative text-based locator for get_by_role()
