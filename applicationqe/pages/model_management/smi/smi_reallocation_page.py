from pages.model_management.smi.smi_home_page import SMIHomePage
from pages.model_management.smi.locators import reallocation_locators


class SMIReallocationPage(SMIHomePage):
    """Locators and tab/submenu name constants for the Reallocations section."""

    TAB_NAME             = "Reallocations"
    SUBMENU_NEW          = "New"
    SUBMENU_IN_PROGRESS  = "In Progress"
    SUBMENU_HISTORY      = "History"
    SUBMENU_TAX_MANAGEMENT = "Tax Management"

    DIALOG_SELECTORS     = reallocation_locators.DIALOG_SELECTORS
    POPUP_DROPDOWN       = reallocation_locators.POPUP_DROPDOWN
    MODEL_SEARCH_BUTTON  = reallocation_locators.MODEL_SEARCH_BUTTON
    MODEL_ID_INPUT       = reallocation_locators.MODEL_ID_INPUT
    POPUP_SUBMIT_BUTTON  = reallocation_locators.POPUP_SUBMIT_BUTTON
