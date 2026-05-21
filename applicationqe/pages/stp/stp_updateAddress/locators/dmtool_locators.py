"""Locators for DM Tool Page elements (raw string XPath attributes)."""


class DMToolLocators:
    """Raw XPath/CSS selector strings for the DM Tool Page.
    
    NOTE: These are used as raw strings (self.x = loc.X), not as Playwright Locators,
    because methods call self.page.locator(self.x) internally.
    """

    # Section XPath patterns
    FOOTER_SECTION = "//footer"
    HEADER_SECTION = "//header[@data-testid='header']"
    NOTES_SECTION = "//li[@aria-label='list-item']"
    BOTTOM_BUTTONS_SECTION = "//div[@data-testid='action-buttons']"
    ACCOUNT_INFO_SECTION = "//section[@aria-label='account-info-section']"
    ADDRESSES_SECTION = "//section[@aria-label='address-change-section']"

    # Table row
    TABLE_ROW = "//section[@aria-label='account-info-section']//tr[@aria-label='table-row']"

    # Notes
    IMPORTANT_NOTES_BULLETINS_FIRST = "//li[@aria-label='list-item'][1]"
    IMPORTANT_NOTES_BULLETINS_SECOND = "//li[@aria-label='list-item'][2]"
    IMPORTANT_NOTES_BULLETINS_THIRD = "//li[@aria-label='list-item'][3]"
    IMPORTANT_NOTES_BULLETINS_FOURTH = "//li[@aria-label='list-item'][4]"

    # Header elements
    UPDATE_ADDRESSES_TEXT = "//header[@data-testid='header']//h1[@data-testid='header-tool-name']"
    ADVISOR_ID = "//header[@data-testid='header']//span[@data-testid='header-advisor-id']"

    # Legal Address elements
    LEGAL_ADDRESS_SECTION = "//section[@aria-label='address-change-section']//div[@data-testid='legal-address-card']"
    LEGAL_ADDRESS_LABEL = "//section[@aria-label='address-change-section']//div[@data-testid='legal-address-card']//h3[@data-testid='address-card-name']"
    LEGAL_ADDRESS_CONTENTS = "//section[@aria-label='address-change-section']//div[@data-testid='legal-address-card']//ul/li"
    LEGAL_EDIT_BUTTON = "//section[@aria-label='address-change-section']//div[@data-testid='legal-address-card']//button[@aria-label='icon-button']//*[local-name() = 'svg']"

    # Mailing Address elements
    MAILING_ADDRESS_SECTION = "//section[@aria-label='address-change-section']//div[@data-testid='mailing-address-card']"
    MAILING_ADDRESS_LABEL = "//section[@aria-label='address-change-section']//div[@data-testid='mailing-address-card']//h3[@data-testid='address-card-name']"
    MAILING_ADDRESS_CONTENTS = "//section[@aria-label='address-change-section']//div[@data-testid='mailing-address-card']//ul/li"
    MAILING_EDIT_BUTTON = "//section[@aria-label='address-change-section']//div[@data-testid='mailing-address-card']//button[@aria-label='icon-button']//*[local-name() = 'svg']"

    # Action buttons
    SUBMIT_BUTTON = "//div[@data-testid='action-buttons']//button[@data-testid='submit-button']"
    CANCEL_BUTTON = "//div[@data-testid='action-buttons']//button[@data-testid='cancel-button']"

    # Footer elements
    ASSETMARK_TEXT = "//footer//p[@aria-label='company-name']"
    PRIVACY_LINK = "//footer//button[.='Privacy and Security Policy']"
    TERMS_LINK = "//footer//button[.='Terms of Use']"
    SUPPORTED_BROWSERS_LINK = "//footer//button[.='Supported Browsers']"
    COPYRIGHT_TEXT = "//footer//p[@aria-label='copyright']"

    # Account Information elements
    HOUSEHOLD_NAME = "//section[@aria-label='account-info-section']//h3[@aria-label='household-name']"
    ACCOUNT_INFORMATION_LABEL = "//section[@aria-label='account-info-section']//h3[@class='section-title']"
    ACCOUNT_NAME_COLUMN_LABEL = "//section[@aria-label='account-info-section']//th[contains(text(),'Account Name')]"
    ACCOUNT_NUMBER_COLUMN_LABEL = "//section[@aria-label='account-info-section']//th[contains(text(),'Account Number')]"
    STRATEGY_COLUMN_LABEL = "//section[@aria-label='account-info-section']//th[contains(text(),'Strategy')]"
    STATUS_COLUMN_LABEL = "//section[@aria-label='account-info-section']//th[contains(text(),'Status')]"

    # Address section title
    ADDRESS_SECTION_TITLE = "//section[@aria-label='address-change-section']//h3[@aria-label='address-change-section-title']"

    # Error messages
    NO_CHANGES_ERROR = "//div[@data-testid='no-changes-note']"
    FRAUD_MESSAGE = "//div[@aria-label='no-changes-note']"

    # Loading indicators
    LOADING_SPINNER = "//div[@class='spinner-border']"
