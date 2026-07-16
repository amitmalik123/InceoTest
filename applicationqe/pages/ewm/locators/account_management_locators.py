"""Locators for Account Management Page elements."""


class AccountManagementLocators:
    """Raw selector strings for the Account Management flow."""

    ACCOUNT_MANAGEMENT_LINK_TEXT = "Account Information change"

    REQUEST_DROPDOWN = "#ctl00_cphContentArea_ddlRequest"
    TYPE_DROPDOWN = "#ctl00_cphContentArea_ddlType"

    COMPLETE_AND_PRINT_BUTTON_TEXT = "Complete and Print"

    DOCUSIGN_CONTINUE_BUTTON_TEXT = "Continue"
    DOCUSIGN_FINISH_BUTTON_TEXT = "Finish"
    DOCUSIGN_CONTINUE_FINISH_BUTTON_TEXT = "Continue & Finish"
    DOCUSIGN_URL_GLOB = "**/docusign**"
    DOCUSIGN_FALLBACK_FINISH_CONTINUE_SELECTOR = (
        "button:has-text('Finish'), button:has-text('Continue'), "
        "a:has-text('Finish'), input[value*='Finish']"
    )

    TRACKING_ID_ELEMENT = "#trackingId, .tracking-id, [data-tracking-id]"
    CLOSE_BUTTON_TEXT = "Close"

    UPLOAD_PDF_INPUT = "input[type='file']"
    UPLOAD_BUTTON_TEXT = "Upload"
