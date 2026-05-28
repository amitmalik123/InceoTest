"""
Locators for Outlook Page

This module contains all locator definitions for the Outlook OTP retrieval page.
"""

# URLs
OUTLOOK_URL = "https://outlook.office365.com/mail/"

# ========================================================================================
# LOCATORS - All page element locators defined for easy maintenance
# ========================================================================================

# Loading and UI elements
LOADING_LOGO = "#loadingLogo"

# Email time locators
EMAIL_TIME_SPAN = "//span[@class='_rWRU U2XB8 qq2gS cbNn0']"

# Message and email locators
MESSAGE_ROWS = "div[role='option']"
MAIL_BODY_CONTAINER = '[data-test-id="mailMessageBodyContainer"]'

# Sign-in field locators (multiple fallbacks)
USERNAME_FIELD_PRIMARY = "#i0116"
USERNAME_FIELD_FALLBACK1 = "input[name='loginfmt']"
USERNAME_FIELD_FALLBACK2 = "input[type='email']"

# Password field locators (multiple fallbacks)
PASSWORD_FIELD_PRIMARY = "#i0118"
PASSWORD_FIELD_FALLBACK1 = "input[name='passwd']"
PASSWORD_FIELD_FALLBACK2 = "input[type='password']"

# Sign-in button locators (multiple fallbacks)
SIGNIN_BUTTON_PRIMARY = "#idSIButton9"
SIGNIN_BUTTON_FALLBACK1 = "//input[@type='submit' and @value='Next']"
SIGNIN_BUTTON_FALLBACK2 = "//input[@type='submit' and @value='Sign in']"
SIGNIN_BUTTON_FALLBACK3 = "button[type='submit']"

# Stay signed in prompt
STAY_SIGNED_IN_YES = "//input[@type='submit' and @value='Yes']"

# Inbox and search related
INBOX_LINK_LABEL = '[aria-label="Inbox"]'
