"""Locators for Manage Bene Page elements."""


class ManageBeneLocators:
    """Raw selector strings for the Manage Bene page."""

    ACCOUNT_WIZARD_LINK = "#clientDetailAccountDetailAnchor"
    FUNDED_RADIO_INPUT = "input#ctl00_cphContentArea_rdlAccountList_1[type='radio']"
    MOVE_ASSETS_TEXT = "Move Assets Between Accounts"
    ROTH_IRA_CONVERSION = "#lstSubCategory5"
    NEXT_BUTTON = "Next"
    MANAGE_ACCOUNT_CONTAINER = "div.actionButtons"
    MANAGE_ACCOUNT_BUTTON = "Manage Account"
    MANAGE_BENEFICIARIES_LINK = "#ctl00_cphContentArea_lnkManageBeneficiary"
    BENEFICIARY_CARDS = "div.MuiCard-root:has(p.MuiTypography-body1)"
    FIRST_BENEFICIARY_CARD = "div.MuiCard-root:has(p.MuiTypography-body1)"
    FIRST_BENEFICIARY_NAME = "div.MuiCard-root:has(p.MuiTypography-body1) p.MuiTypography-body1"
    FIRST_BENEFICIARY_SSN = "div.MuiCard-root:has(p.MuiTypography-body1) p.MuiTypography-body1"
    BENEFICIARY_CARD_EXPAND_BUTTON = "div.MuiCard-root svg.MuiSvgIcon-root"
