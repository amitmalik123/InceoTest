"""Locators for Deceased Bene Page elements."""


class DeceasedBeneLocators:
    """Raw selector strings for the Deceased Bene page."""

    NOT_ELIGIBLE_BANNER = "p.MuiTypography-body1:has-text('Deceased Account(s) Not Eligible')"
    NOT_ELIGIBLE_BANNER_SUBTEXT = "p.MuiTypography-body1:has-text('Please contact your Relationship Manager')"
    DECEASED_ACCOUNT_CARD = ".MuiCard-root:has(span:has-text('Deceased'))"
    DECEASED_LABEL = "span:has-text('(Deceased)')"
    NOT_ELIGIBLE_CHIP = ".MuiChip-root:has(.MuiChip-label:has-text('Not Eligible'))"
