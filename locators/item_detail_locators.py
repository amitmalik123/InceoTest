"""
Locators for Item Detail Page (Tracking Center Item Detail)

This module contains all locator definitions for the Item Detail page.
Locators are organized by functional area for easy maintenance.
"""

# ========================================================================================
# LOCATORS - All page element locators defined for easy maintenance
# ========================================================================================

# Status field locator
STATUS_LABEL = "span:has-text('Status:') + label"

# Advisor Alert Required field locator
ADVISOR_ALERT_REQUIRED_LABEL = "span:has-text('Advisor Alert Required:') + label"

# Item Number (D-number) field locator
ITEM_NUMBER_LABEL = "span:has-text('Item Number:') + label"

# Agent Name field locator
AGENT_NAME_LABEL = "//span[text()='Agent Name']/following-sibling::label"

# Column flow container (buttons area)
COLUMN_FLOW_CONTAINER = "div#column-flow-container"

# Buttons within the column flow container
BUTTONS_SELECTOR = "button, a.btn, .item-detail-button"

# Upload button (File upload label button)
# Note: Uses get_by_role("button", name="Upload") or get_by_text("Upload") in page object
# HTML: <label class="fileuploadbutton item-detail-button"><span class="">Upload</span></label>
UPLOAD_BUTTON_TEXT = "Upload"

# File input for document upload
FILE_INPUT_SELECTOR = "input[type='file']"

# Close button (Dialog/modal close button)
# Note: Uses get_by_role("button", name="Close") - stable selector
# HTML: <span class="right-padding"><button type="button" class="btn btn-default">Close</button></span>
CLOSE_BUTTON_TEXT = "Close"

# Cancel button (Request cancellation button)
# Note: Uses id selector or get_by_role("link", name="Cancel")
# HTML: <a href="#" class="btn btn-default" id="cancelRequest" onclick="...">Cancel</a>
CANCEL_BUTTON_SELECTOR = "a#cancelRequest"

# Cancel confirmation dialog
# jQuery UI dialog that appears after clicking Cancel button
# HTML: <div tabindex="-1" role="dialog" class="ui-dialog ui-corner-all...">
CANCEL_CONFIRMATION_DIALOG_SELECTOR = ".ui-dialog"
CANCEL_CONFIRMATION_DIALOG_ID = "dialog-confirm"
CANCEL_CONFIRMATION_DIALOG_BY_ID = f"#{CANCEL_CONFIRMATION_DIALOG_ID}"

# Yes button in cancel confirmation dialog
# Note: Uses get_by_text("Yes") with Playwright locators
# HTML: <button type="button" class="formButton" style="width: 65px;">Yes</button>
CANCEL_CONFIRM_YES_BUTTON_TEXT = "Yes"

# Notes grid table
NOTES_GRID_TABLE = "table#TrackingCenterItemDetailNotesGrid"

# Description cells in notes grid
NOTES_DESCRIPTION_CELLS = "td[aria-describedby='TrackingCenterItemDetailNotesGrid_description']"

# Data rows in notes grid (excluding header)
NOTES_GRID_DATA_ROWS = "tbody tr:not(:first-child)"
