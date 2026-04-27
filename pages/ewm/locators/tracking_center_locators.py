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