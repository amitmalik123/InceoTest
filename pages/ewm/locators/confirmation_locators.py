"""
Locators for Confirmation page elements
"""

class ConfirmationLocators:
    """Locators for confirmation page elements and success indicators"""

    # Confirmation headings
    CONFIRMATION_HEADING = {
        "selectors": [
            "text=Confirmation",
            "text=Request Confirmed", 
            "text=Successfully Submitted",
            "h1:has-text('Confirmation')",
            "h2:has-text('Confirmation')"
        ],
        "strategy": "text-based with fallback to heading tags",
        "description": "Main confirmation page heading"
    }

    # Success messages
    SUCCESS_MESSAGE = {
        "selectors": [
            "text=Your request has been submitted",
            "text=Request submitted successfully",
            "text=Thank you for your submission",
            "[data-testid='success-message']",
            ".success-message"
        ],
        "strategy": "text content preferred, fallback to test identifiers",
        "description": "Success confirmation message"
    }

    # Request number patterns
    REQUEST_NUMBER = {
        "selectors": [
            "text=/Request\\s*#?:?\\s*([A-Z0-9\\-]+)/",
            "text=/Number\\s*#?:?\\s*([A-Z0-9\\-]+)/",
            "text=/ID\\s*#?:?\\s*([A-Z0-9\\-]+)/",
            "[data-testid='request-number']",
            ".request-number"
        ],
        "strategy": "regex patterns for flexible matching",
        "description": "Generated request number or ID"
    }

    # Action buttons
    CONTINUE_BUTTON = {
        "selectors": [
            "button:has-text('Continue')",
            "button:has-text('Next')",
            "button:has-text('Proceed')",
            "[data-testid='continue-button']"
        ],
        "strategy": "role-based with text content",
        "description": "Continue to next step button"
    }

    DONE_BUTTON = {
        "selectors": [
            "button:has-text('Done')",
            "button:has-text('Finish')",
            "button:has-text('Complete')",
            "[data-testid='done-button']"
        ],
        "strategy": "role-based with text variations",
        "description": "Final completion button"
    }

    # Tracking navigation
    TRACKING_LINK = {
        "selectors": [
            "a:has-text('Track')",
            "a:has-text('Tracking')",
            "button:has-text('Track')",
            "a:has-text('View Status')",
            "[data-testid='tracking-link']"
        ],
        "strategy": "link and button roles with descriptive text",
        "description": "Navigate to tracking center link"
    }

    # Status indicators
    STATUS_INDICATOR = {
        "selectors": [
            "text=/status|confirmed|complete/i",
            "[data-testid='status']",
            ".status-indicator",
            ".completion-status"
        ],
        "strategy": "text pattern matching with class fallbacks",
        "description": "Request status indicator"
    }

    # Next steps information
    NEXT_STEPS_SECTION = {
        "selectors": [
            "text=Next Steps",
            "text=What happens next",
            "[data-testid='next-steps']",
            ".next-steps"
        ],
        "strategy": "section headings and semantic classes",
        "description": "Next steps information section"
    }

    # Download/print options
    DOWNLOAD_BUTTON = {
        "selectors": [
            "button:has-text('Download')",
            "a:has-text('Download')",
            "button:has-text('Print')",
            "[data-testid='download-button']"
        ],
        "strategy": "action buttons for document retrieval",
        "description": "Download confirmation or receipt"
    }