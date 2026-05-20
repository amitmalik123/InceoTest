# XPath/CSS string constants for RGLPage.
# Locator objects are built in the page class using active_root() for iframe awareness.

# form_root-scoped selectors
CLIENTS_TAB = "a:has-text('Clients')"
GAIN_LOSS_LINK = "a:has-text('Gain/Loss')"
ACCOUNT_INFORMATION_LINK = "a:has-text('Account Information')"
ACCOUNT_LIST_LINK = "a:has-text('Account List')"
SEARCH_BUTTON = "button:has-text('Search'), [class*='search'][class*='button']"
CLIENT_LIST_SEARCH_INPUT = "input[name='search_input']"
CASH_ADVANTAGE_ACCOUNT = "//td[contains(normalize-space(), 'Cash Advantage')]"
MOUSE_OVER_DATE = "//input[@name='GetSessionstickyValue']//parent::div"
ALL_OPTION = "//div[@class='ui-genworthdropdownpanel-dropdownContent']//div[text()='All']"
SOLUTION_TYPES_DROPDOWN = "//span[text()='Solution Types']"
LIST_OF_HEADERS = (
    "//*[@role='tab' and not(ancestor-or-self::*[contains(@style, 'display: none')])]/a"
)
HEADER_EXPANDER = (
    "//div[@aria-disabled='false']//h3[@aria-expanded='false']"
    "//span[@class='ui-accordion-header-icon ui-icon ui-icon-triangle-1-e'"
    " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
)
PROCEEDS_LIST = (
    "//h3[@aria-expanded='true']//parent::div[@role='tablist']"
    "//div//div//table//tr//td[contains(@aria-describedby,'proceeds')]"
)
COST_BASIS_LIST = (
    "//h3[@aria-expanded='true']//parent::div[@role='tablist']"
    "//div//div//table//tr//td[contains(@aria-describedby,'costBasis')]"
)
GAIN_LOSS_LIST = (
    "//h3[@aria-expanded='true']//parent::div[@role='tablist']"
    "//div//div//table//tr//td[contains(@aria-describedby,'gainLoss')]"
)
INCOME_LIST = (
    "//h3[@aria-expanded='true']//parent::div[@role='tablist']"
    "//div//div//table//tr//td[contains(@aria-describedby,'income')]"
)
EXPANDED_HEADER = (
    "//h3[@aria-expanded='true']//span[contains(@class,'ui-accordion-header-icon')"
    " and not(ancestor-or-self::*[contains(@style, 'display: none')])]"
)
PRINT_BUTTON = "//div[text()='Print']"
DOWNLOAD_BUTTON = "//div[text()='Download']"
CSV_LINK = "//a[@href='#CSV']"
XLS_LINK = "//a[@href='#XLS']"
INDIVIDUAL_DROPDOWN = "//span[@class='selectBox-arrow']"
INDIVIDUAL_ACCOUNT = "(//div[text()='eSig Test 4 Individual'])[1]"
NET_INVESTMENT = (
    "//div[@class='ui-jqgrid-bdiv']//div//table//tbody//tr//following-sibling::tr"
    "//td[@class='null ui-td-notsort ui-td-netInvestment']"
)
CLIENT_NAMES = (
    "//div[@class='ui-jqgrid-bdiv']//div//table//tbody//tr//following-sibling::tr"
    "//td[@class='null ui-td-notsort ui-td-clientName']"
)
LOADING_SPINNER = "//div[contains(@class,'loading-indicator-component__spinner')]"
LOADING_INDICATOR = (
    "//*[contains(@class, 'loading-indication-component')"
    " and contains(@class, 'isVisible')]"
)
LOADING_MODAL = "#loadingImageModal"

# page-level selectors (not frame-scoped)
CASH_ADVANTAGE_CHECKBOX = (
    "//*[@id='filter-3']//label[normalize-space(.)='Cash Advantage']"
    "/preceding-sibling::a[contains(@class,'ui-genworthcheckbox')]"
)
CASH_ADVANTAGE_LABEL = "//*[@id='filter-3']//label[normalize-space(.)='Cash Advantage']"
APPLY_BUTTON = (
    "//*[@id='filter-3']//div[@class='button save' and normalize-space(.)='Apply']"
)
FIRST_ACCOUNT_ROW = (
    "(//*[@id='AccountListGrid']"
    "//td[@aria-describedby='AccountListGrid_accountAccordianArrow'])[1]"
)
FIRST_NON_CASH_ADVANTAGE_ACCOUNT_ROW = (
    "(//*[@id='AccountListGrid']"
    "//tr[not(.//td[contains(normalize-space(),'Cash Advantage')])]"
    "//td[@aria-describedby='AccountListGrid_accountAccordianArrow'])[1]"
)
LEARN_MORE_ABOUT_LINK = "//a[text()='Learn more about additional account information']"
NET_COLUMN = "//th[@id='ClientListGrid_netInvestment']"
