"""Locators for Item Details Page elements."""


class ItemDetailsLocators:
    """Raw selector strings for the Item Details page."""

    PAGE_LABEL = "//div[@id='genworth-breadcrumb']//a[contains(text(),'Item Detail')]"
    DESCRIPTION = "//div[@class='description']/span"
    ITEM_NUMBER = "//div[@class='item-number']//span[@class='value']"
    NAME = "//div[@class='name']//span[@class='value']"
    STATUS = "//span[contains(text(),'AGA1TO')]/parent::div//child::span[3]"
    CLOSED_ON_DATE = "//span[contains(text(), 'Closed On:')]/following-sibling::label"
    STATUS_LABEL = "//span[contains(text(), 'Status: ')]/following-sibling::label"
    DESCRIPTION_LABEL = "//span[contains(text(), 'Description: ')]/following-sibling::label"
    DESCRIPTION_INFO = "//table[@id='TrackingCenterItemDetailNotesGrid']//tr//td[contains(@class, 'description')]"
    DESCRIPTION_NOTES = "//table[@id='TrackingCenterItemDetailNotesGrid']"
    TIME_STAMPS = "//table[@id='TrackingCenterItemDetailNotesGrid']//tr//td[contains(@class, 'createdOn')]"
    ITEM_DETAILS_T11 = "//article//label"
    TRACKING_CENTER_TAB = "//div[@class]/a[text()='Tracking Center']"
    VIEW_BUTTON = "//a[text()='View']"
    VIEW_DOCUMENTS_HEADER = "//div[@class='modal-title' and text()='View Documents']"
    VIEW_DOCUMENTS_PDF_LIST = "//div[@class='modal-body']//div[@id='PDFListTable']"
    VIEW_DOCUMENTS_FILE_LINKS = "//div[@id='PDFListTable']//a[@name='pdfDetails']"
    CLOSE_BUTTON = "//div[@class='modal-footer']//button[contains(text(),'Close') and @aria-hidden='true']"
