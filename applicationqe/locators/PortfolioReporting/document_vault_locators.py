# XPath/CSS string constants for DocumentVaultPage.
# Locator objects are built in the page class using active_root() for iframe awareness.

CLIENT_REPORTS_VAULT_HEADING = '//span[normalize-space()="Client Document and Reports Vault"]'
DOCUMENT_TYPE_DROPDOWN = '//span[text()="Select a document type"]'
DOCUMENT_TYPE_SELECT = '//select[@name="ddDocType"]'
YEAR_DROPDOWN = '//select[@name="ddYear"]'
QUARTER_DROPDOWN = '//select[@name="ddQtrMonth"]'
ALL_CHECKBOXES = '//input[@type="checkbox"]'
QUARTER_LABEL = "//td[contains(text(),'Quarter')]"
DOCUMENT_LABEL = "//td[contains(normalize-space(),'Document')]"
PERIOD_LABEL = "//td[contains(text(),'Period')]"
MONTH_LABEL = "//td[contains(text(),'Month')]"
YEAR_DISPLAY = '//div[@id="uniform-ddYear"]//span'
QUARTER_DISPLAY = '//div[@id="uniform-ddQtrMonth"]//span'
DOCUMENT_DROPDOWN = '//select[@name="ddDocument"]'
FIND_BUTTON = "//input[@name='btSearch']"
NO_DOCUMENTS_MESSAGE = "//td[contains(text(),'There are no documents')]"
SELECT_ALL_EXACT = "//a[normalize-space()='Select All']"
SELECT_ALL_CONTAINS = "//a[contains(normalize-space(), 'Select All')]"
CLEAR_ALL_EXACT = "//a[normalize-space()='Clear All']"
CLEAR_ALL_CONTAINS = "//a[contains(normalize-space(), 'Clear All')]"
TOTAL_FILTER_CHECKERS = "//div[contains(@class,'checker')]/span"
CHECKED_FILTER_CHECKERS = "//div[contains(@class,'checker')]/span[contains(@class,'checked')]"
VIEW_SELECTED_BUTTON = '//input[@id="btSelectOneUp"]'
SAVE_SELECTED_BUTTON = '//input[@id="btDownloadUp"]'
TAX_SAVINGS_REPORT_OPTION = '//span[text()="Tax Savings Report"]'

# Nav links (page-level, not frame-scoped)
STATEMENTS_REPORTS_LINK = '//a[text()="Statements & Reports"]'
SERVICE_CENTER_LINK = '//a[text()="Service Center"]'
TAX_AND_REPORTING_LINK = '//a[text()="Tax and Reporting"]'
DOCUMENT_VAULT_NAV_LINK = '//a[text()="Document Vault"]'

# Frame-scoped options
QPR_DOCUMENT_TYPE_OPTION = '//span[text()="Quarterly Performance Reports (QPR)"]'
MARKET_VALUE_REPORT_OPTION = '//span[text()="Market Value Reports"]'

# Client search (frame-scoped)
CLIENTS_TAB = "//a[text()='Clients']"
CLIENT_LIST_SEARCH_INPUT = "//input[@name='search_input']"
SEARCH_BUTTON = "//button[@class='searchbutton']"
DOCUMENT_VAULT_LINK = "//li//a[text()='Document Vault']"
DOCUMENT_VAULT_DROPDOWN = "//div[@class='ui-genworthdropdownpanel-buttonContent']"
DATE_FILTER_ALL_OPTION = (
    "//div[@class='ui-genworthdropdownpanel-dropdownContent']//div[text()='All']"
)
LIST_OF_HEADERS = (
    "//*[@role='tab' and not(ancestor-or-self::*[contains(@style, 'display: none')])]/a"
)
HEADER_EXPANDER = (
    "//div[@aria-disabled='false']//h3[@aria-expanded='false']"
    "//span[@class='ui-accordion-header-icon ui-icon ui-icon-triangle-1-e'"
    " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
)
EXPANDED_HEADER = (
    "//h3[@aria-expanded='true']//span[contains(@class,'ui-accordion-header-icon')"
    " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
)
