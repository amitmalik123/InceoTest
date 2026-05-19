"""
Locators for Login Page elements
"""

class LoginLocators:
    """Locators for login page elements"""
    
    # Page elements
    COOKIE_CONSENT_BUTTON = "Confirm My Choices"
    ALLOW_ALL_BUTTON = "Allow All"
    USERNAME_FIELD = "input#okta-signin-username"
    PASSWORD_FIELD = "input#okta-signin-password"
    SIGN_IN_BUTTON = "input#okta-signin-submit[type='submit']"
    
    # Alternative selectors
    USERNAME_LABEL = "Username"
    PASSWORD_LABEL = "Password"
    
    # Page identifiers
    LOGIN_FORM = "form#form19.primary-auth-form.o-form.o-form-edit-mode"
    
    # URL patterns
    HOME_URL_PATTERN = "**/en.aspx"
    LOGIN_URL_PATTERN = "**/account/login"
    
    # Cookie consent variations
    COOKIE_CONSENT_BUTTONS = [
        "Confirm My Choices",
        "Accept All Cookies", 
        "Accept All",
        "Accept",
        "Allow All",
        "I Agree",
        "Continue"
    ]
    
    # OneTrust selectors
    ONETRUST_SELECTORS = [
        "#onetrust-accept-btn-handler",
        "#onetrust-banner-sdk button[id*='accept']",
        "[data-testid='ot-pc-btn']", 
        ".ot-sdk-show-settings",
        ".onetrust-close-btn-handler"
    ]
    
    # Timeouts
    COOKIE_CONSENT_TIMEOUT = 3000
    LOGIN_TIMEOUT = 30000
    PAGE_LOAD_TIMEOUT = 10000