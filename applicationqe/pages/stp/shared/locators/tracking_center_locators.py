"""Locators for Tracking Center Page elements."""


class TrackingCenterLocators:
    """Raw selector strings for the Tracking Center page."""

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
