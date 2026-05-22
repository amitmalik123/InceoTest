"""Locators for Manage Instruction Step 1 Page elements."""


class ManageInstruction1Locators:
    """Raw selector strings for the Manage Instruction step 1 page."""

    NEXT_BUTTON = "NEXT"
    CLOSED_ON_DATE = "//span[contains(text(), 'Closed On:')]/following-sibling::label"
    STATUS = "//span[contains(text(), 'Status: ')]/following-sibling::label"
    DESCRIPTION = "//span[contains(text(), 'Description: ')]/following-sibling::label"
