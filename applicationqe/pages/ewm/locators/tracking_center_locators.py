"""
Locators for Tracking Center Page elements
"""

class TrackingCenterLocators:
    """Locators for tracking center page elements"""
    
    # URL patterns
    TRACKING_URL_PATTERN = "**/tracking**"
    
    # Item tracking patterns  
    TRACKING_ITEM_REGEX = r"A\d{9}"
    ITEM_NUMBER_REGEX = r"A\d+"
    
    # Status patterns
    TRACKING_STATUS_REGEX = r"Request Received|In Process|Pending|Completed"
    
    # Page elements
    ITEM_NUMBER_LABEL = "Item Number:"
    STATUS_LABEL = "Status:"
    REQUEST_TYPE = "Journal Request"
    
    # Page elements (STP)
    ROTH_STR_LABEL_TEXT = "Roth Conversion"
    LOGOUT_LINK = "Logout"
    BODY_CONTENT = "div#BodyContent"
    TRACKING_CENTER_LINK = "//ul[@id='mainMenu']//a[contains(text(),'Tracking Center')]"
    LOADING_SPINNER_MODAL = "//*[@id='loadingImageModal' and contains(@style,'block')]"
    SEARCH_INPUT = "#client_search_input"
    SEARCH_BUTTON = "#searchbutton"
    ADDRESS_TEXT_DETAIL = "//table[@id='TrackingCenterItemDetailNotesGrid']/tbody/tr[2]/td[4]"
    VIEW_BUTTON = "//a[text()='View']"
    VIEW_DOCUMENTS_HEADER = "//div[@class='modal-title' and text()='View Documents']"
    PDF_LIST_TABLE = "//div[@class='modal-body']//div[@id='PDFListTable']"
    DOCUMENT_LINKS = "//div[@id='PDFListTable']//a[@name='pdfDetails']"
    ESIGNATURE_BUTTON = "#resendRequest"
    ESIGN_MGMT_DIALOG = "[aria-describedby='resendDialog']"
    ESIGN_MGMT_CONTENT = "#resendDialog"
    ESIGN_MGMT_TITLE_XPATH = 'xpath=preceding-sibling::div[contains(@class,"ui-dialog-titlebar")]//span[contains(@class,"ui-dialog-title")]'
    ESIGN_RESEND_BUTTON = "#btnResendReminder1"
    
    # Upload functionality
    UPLOAD_BUTTON = "Upload"
    UPLOAD_DOCUMENTS_DIALOG = "Upload Documents"
    FILE_INPUT = "files[]"
    FILE_INPUT_ROLE = "link"
    
    # Upload file path (relative to project root)
    UPLOAD_FILE_PATH = "uploadDocuments/myfile.pdf"
    
    # Status values
    REQUEST_RECEIVED = "Request Received"
    IN_PROCESS = "In Process"
    PENDING = "Pending"
    COMPLETED = "Completed"
    PENDING_SETTLEMENT = "In Process - Pending Settlement"
    
    # Retry settings for item appearance
    MAX_RETRY_ATTEMPTS = 20  # 20 attempts * 2000ms = 40s max
    RETRY_DELAY = 2000  # 2 seconds between retries
    
    # Timeouts
    TRACKING_CENTER_TIMEOUT = 30000
    NETWORK_IDLE_TIMEOUT = 10000