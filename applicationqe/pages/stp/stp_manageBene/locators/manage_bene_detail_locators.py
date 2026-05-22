"""Locators for Manage Bene Detail Page elements."""


class ManageBeneDetailLocators:
    """Raw selector strings for the Manage Bene Detail page."""

    BENEFICIARIES_SECTION = "button:has-text('Manage Beneficiaries')"
    ADD_BENEFICIARY_BUTTON = "button[aria-label='Add']"
    NOTIFICATION_LOCATOR = 'div[role="alert"]'
    ACCOUNT_HOLDER_HEADING = "//div[contains(@class,'MuiBox-root')]//h1[contains(@class,'MuiTypography-h5')]"
    ACCOUNT_CARDS = "div.MuiCard-root"
    CONTINGENT_EMPTY_STATE = "//span[normalize-space(text())='Contingent']/ancestor::div[contains(@class,'MuiBox-root')]/following-sibling::div//span[contains(@class,'MuiTypography-emptyStateText')]"
    ACCOUNT_CARD_TITLE = "span.MuiTypography-h5.MuiCardHeader-title"
    PRIMARY_BENEFICIARY_NAME = "span.MuiTypography-cardTextPrimary"
    CONTINGENT_EMPTY = "//span[contains(text(),'No contingent beneficiaries')]"
    ACCOUNT_TITLE_WITH_CONTINGENT_EMPTY = "//span[contains(text(),'No contingent beneficiaries')]/../../../../..//div/span[contains(text(),'Cleve')]"
    BENEFICIARY_CARDS = "span.MuiTypography-cardTextPrimary"
    SIGNATURE_OPTIONS_SECTION = "span.MuiTypography-h5:has-text('Signature Options')"
    ELECTRONIC_SIGNATURE_RADIO = "input[type='radio'][value='Obtain Electronic Client Signature(s)']"
    PHYSICAL_SIGNATURE_RADIO = "input[type='radio'][value='Print to Obtain Physical Client Signature(s)']"
    CONTINUE_TO_ESIGNATURE_BUTTON = "button:has-text('Continue to e-Signature Details')"
    CONTINUE_TO_REVIEW_BUTTON = "button:has-text('Continue to Review')"
