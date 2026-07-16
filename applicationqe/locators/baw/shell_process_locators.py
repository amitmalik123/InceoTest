"""Locators for BAW Shell Process page."""


class ShellProcessLocators:
    WORK_ITEM_TYPE_SELECT = "select#InputText3"
    CUSTODIAN_SELECT = "select#InputText0"
    TEAM_NAME = "#ComboBox0"
    INDIVIDUAL_OWNER = "select#ComboBox1"
    RUN_NOW_BUTTON = "#ButtonGroup0_RunNow"

    B_NUMBER = "xpath=//*[normalize-space()='B #']/following-sibling::td[1]"
    HRC_TEXTBOX = "#InputText32"
    HRC_SUBMIT_BUTTON = "#ButtonGroup21_SubmitHRC"

    SAVE_SHELL_PROCESS_BUTTON = "#ButtonGroup0_Save"
    SAVE_EXIT_BUTTON = "button#ButtonGroup0_Button2"
    BAW_LOADING_SPINNER = "img[src*='loading_msg.gif']"

    SELECT_ACCOUNT_BUTTON = "button#ButtonGroup19_SelectAccount"
    REMOVE_ASSOCIATION_BUTTON = "xpath=//button[normalize-space()='Remove']"
    ADD_ACCOUNT_ASSOCIATION_BUTTON = "xpath=//button[normalize-space()='Add']"
    ADDED_ACCOUNT_NUMBER = "#TableCellCustodialAccountNumber0_0"
    ADDED_ACCOUNT_NAME = "#TableCellItemName0_0"

    INTERNAL_STATUS_LABEL = "label#combo_Label"
    INTERNAL_STATUS_DROPDOWN = "select#combo"

    # ------------------------------------------------------------------
    # C95666 - Upload Check Document & Dashboard search locators
    # ------------------------------------------------------------------
    # Document upload flow (Add Document opens a popup with Choose File)
    ADD_DOCUMENT_BUTTON_ROLE = "Add Document"
    CHOOSE_FILE_BUTTON_ROLE = "Choose File"
    COMMIT_DOCUMENTS_BUTTON_ROLE = "Commit Documents"
    SUBMIT_BUTTON_ROLE = "Submit"

    # Top-nav links available on the BAW Process Portal page
    SEARCH_WORK_ITEM_LINK_ROLE = "Search Work Item BAW"
    DASHBOARD_LINK_ROLE = "Dashboard"

    # Iframes hosting the Search Coach and Dashboard views
    COACH_IFRAME_SELECTOR = "iframe[title=\"Coach\"]"
    DASHBOARD_IFRAME_SELECTOR = "iframe[title=\"Dashboard\"]"

    # Dashboard search controls
    DASHBOARD_BNUM_TEXTBOX_ROLE = "B#:"
    DASHBOARD_SEARCH_BUTTON_ROLE = "Search"

    # Default sample document used by C95666 Check Extraction scenario
    DEFAULT_CHECK_DOCUMENT_FILENAME = "frontcheck1_11zon.pdf"

    # CSS-selector variants used by IWR upload flow methods
    # (distinct from the role-based *_ROLE constants used in __init__)
    ADD_DOCUMENT_BUTTON = "button[value='Add Document'], button:has-text('Add Document')"
    UPLOAD_FILE_INPUT = "input[type='file']"
    COMMIT_DOCUMENTS_BUTTON = "button[value='Commit Documents'], button:has-text('Commit Documents')"
    SUBMIT_BUTTON = "button[value='Submit'], button:has-text('Submit')"

    # ------------------------------------------------------------------
    # IWR Extraction locators
    # ------------------------------------------------------------------
    IWR_BROWSE_FILE_INPUT = "#browseFile"
    IWR_VIEW_NOTE_PRE = "div.customHTML pre"
    IWR_CHECK_IMAGE_EXTRACTION_OUTCOME = "Check Image Extraction Outcome"

    # ------------------------------------------------------------------
    # C95666 - Account Funding Validation (AFV) section locators
    # ------------------------------------------------------------------
    AFV_SECTION_TWISTY = (
        "#AccountFundingValidationSection_SectionTitle > .sectionHeaderTwisty > img"
    )
    AFV_CATEGORY_ACCOUNT_NOTES_TEXT = "Account and/or Client Notes"
    AFV_CATEGORY_STATUS_OF_ACCOUNT_TEXT = "Status of Account"
    AFV_RESULTS_CELL_TEXT = (
        "Category Results Account and/or Client Notes There are notes on this "
        "work item that require review Status of Account This account is open"
    )

    # ------------------------------------------------------------------
    # ShellProcessPage.__init__ inline locators (moved to constants)
    # ------------------------------------------------------------------
    SAVE_REFRESH_BUTTON = "button#ButtonGroup0_Button0"
    CUSTODIAL_ACCOUNT_ROLE = "Custodial Account"
    UPDATE_TRANSFER_DETAILS_BUTTON_ROLE = "Update Transfer details"
    NOTES_TABLE = "//table[@id='Table4']"
    CONTRA_FIRM_ACCOUNT_SELECTOR = "#deliveryFirmAccountNo"
    INTERNAL_STATUS_ROLE = "Internal Status"
    CUSTODIAN_ACC_CELL_CSS = "td.LabelFontStyle"
    CUSTODIAN_ACC_LABEL = "Custodian Acc #"
    CUSTODIAN_ACC_FOLLOWING_TD = "xpath=following-sibling::td"
    ADD_UPDATE_OA_BUTTON_PATTERN = r"Add.?Update OA"
    CREATE_NEW_DIGITAL_RECORD_BUTTON_ROLE = "Create New Digital Record"
    ADD_UPDATE_CHECK_DETAILS_BUTTON_ROLE = "Add/Update Check details"
    SELECT_ACCOUNT_BUTTON_ROLE = "Select"

    # Inline locators moved from page methods
    WORK_TYPE_INPUT = ".default"
    SUCCESS_ALERT = "//div[@class='alert alert-success']"
    DUPLICATE_OPTION_RADIO_TPL = "input[type='radio'][value='{duplicate_option}']"
    CHECK_STATUS = "#checkStatus"
    ASSOCIATE_CHECK_BUTTON = "#ButtonGroup27_AssociateCheck"
    CHECK_WI_B_NUMBER = "#checkWIBnumber"
    ASSOCIATE_CHECK_SUBMIT_BUTTON = "#ButtonGroupAssociateCheck_AssociateCheckSubmit"
    CUSTOM_HTML_RESULT_PRE = "#CustomHTML11_0 pre"
