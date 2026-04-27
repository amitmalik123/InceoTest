"""
Locators for Review Summary page elements
"""

class ReviewSummaryLocators:
    """Locators for review summary page elements and approval actions"""

    # Review headings
    REVIEW_HEADING = {
        "selectors": [
            "text=Review",
            "text=Review Summary", 
            "text=Please Review",
            "h1:has-text('Review')",
            "h2:has-text('Review')"
        ],
        "strategy": "text-based with semantic heading fallbacks",
        "description": "Main review page heading"
    }

    SUMMARY_HEADING = {
        "selectors": [
            "text=Summary",
            "text=Request Summary",
            "text=Transaction Summary",
            "[data-testid='summary-heading']"
        ],
        "strategy": "text content preferred for summary sections",
        "description": "Summary section heading"
    }

    # Account information display
    ACCOUNT_DETAILS = {
        "selectors": [
            "text=/\\d{4}-\\d{4}-\\d{4}/",  # Account number pattern
            "[data-testid='account-info']",
            ".account-details",
            ".account-summary"
        ],
        "strategy": "regex for account numbers with semantic fallbacks",
        "description": "Account information display"
    }

    SOURCE_ACCOUNT = {
        "selectors": [
            "text=Source Account",
            "text=From Account",
            "[data-testid='source-account']",
            ".source-account"
        ],
        "strategy": "semantic labels for source account information",
        "description": "Source account section"
    }

    DESTINATION_ACCOUNT = {
        "selectors": [
            "text=Destination Account",
            "text=To Account",
            "[data-testid='destination-account']",
            ".destination-account"
        ],
        "strategy": "semantic labels for destination account information",
        "description": "Destination account section"
    }

    # Transfer amount display
    AMOUNT_DISPLAY = {
        "selectors": [
            "text=/\\$[\\d,]+\\.\\d{2}/",  # Dollar amount pattern
            "text=/\\$[\\d,]+/",
            "[data-testid='transfer-amount']",
            ".amount-display"
        ],
        "strategy": "regex patterns for currency amounts",
        "description": "Transfer amount display"
    }

    # E-signature information
    ESIGNATURE_SECTION = {
        "selectors": [
            "text=Electronic Signature",
            "text=E-Signature",
            "text=Digital Signature",
            "[data-testid='esignature-section']"
        ],
        "strategy": "text content for signature sections",
        "description": "E-signature information display"
    }

    SIGNATURE_EMAIL = {
        "selectors": [
            "text=/[\\w.-]+@[\\w.-]+\\.[\\w]+/",  # Email pattern
            "[data-testid='signature-email']",
            ".signature-email"
        ],
        "strategy": "email pattern recognition",
        "description": "E-signature email address"
    }

    SIGNATURE_PHONE = {
        "selectors": [
            "text=/\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}/",  # Phone pattern
            "[data-testid='signature-phone']",
            ".signature-phone"
        ],
        "strategy": "phone number pattern recognition",
        "description": "E-signature phone number"
    }

    # Review action buttons
    APPROVE_BUTTON = {
        "selectors": [
            "button:has-text('Approve')",
            "button:has-text('Accept')",
            "button:has-text('Confirm')",
            "[data-testid='approve-button']"
        ],
        "strategy": "role-based with approval action text",
        "description": "Approve request button"
    }

    REJECT_BUTTON = {
        "selectors": [
            "button:has-text('Reject')",
            "button:has-text('Decline')",
            "button:has-text('Cancel')",
            "[data-testid='reject-button']"
        ],
        "strategy": "role-based with rejection action text",
        "description": "Reject request button"
    }

    SUBMIT_REVIEW_BUTTON = {
        "selectors": [
            "button:has-text('Submit Review')",
            "button:has-text('Submit')",
            "button:has-text('Complete Review')",
            "[data-testid='submit-review-button']"
        ],
        "strategy": "role-based with submission text",
        "description": "Submit review decision button"
    }

    # Review options
    REVIEW_OPTIONS = {
        "selectors": [
            "input[type='radio']",
            "select",
            "[data-testid='review-option']",
            ".review-option"
        ],
        "strategy": "input elements for review choices",
        "description": "Review decision options"
    }

    # Comment section
    COMMENT_FIELD = {
        "selectors": [
            "textarea[placeholder*='comment']",
            "textarea[name*='comment']",
            "textarea[id*='comment']",
            "[data-testid='comment-field']"
        ],
        "strategy": "textarea with comment-related attributes",
        "description": "Review comment input field"
    }

    # Review summary sections
    REQUEST_TYPE_LABEL = {
        "selectors": [
            "text=Request Type",
            "text=Transaction Type",
            "[data-testid='request-type']",
            ".request-type"
        ],
        "strategy": "semantic labels for request classification",
        "description": "Request type label"
    }

    RESTRICTED_CASH = {
        "selectors": [
            "text=Restricted Cash",
            "text=Cash Restrictions",
            "[data-testid='restricted-cash']",
            ".restricted-cash"
        ],
        "strategy": "text content for cash restriction information",
        "description": "Restricted cash information"
    }

    # Navigation buttons
    EDIT_BUTTON = {
        "selectors": [
            "button:has-text('Edit')",
            "a:has-text('Edit')",
            "[data-testid='edit-button']"
        ],
        "strategy": "role-based edit actions",
        "description": "Edit request button"
    }

    BACK_BUTTON = {
        "selectors": [
            "button:has-text('Back')",
            "button:has-text('Previous')",
            "[data-testid='back-button']"
        ],
        "strategy": "navigation buttons with descriptive text",
        "description": "Back to previous page button"
    }