from pages.model_management.smi.smi_login_page import SMILoginPage
from pages.model_management.smi.locators import home_locators


class SMIHomePage(SMILoginPage):
    """Locators and CSS selector constants for the SMI home page and navigation bar."""

    MENU_SECTION         = home_locators.MENU_SECTION
    MENU_BAR             = home_locators.MENU_BAR
    MENU_BAR_ITEM_LABELS = home_locators.MENU_BAR_ITEM_LABELS
    MENU_BAR_ITEM_LI     = home_locators.MENU_BAR_ITEM_LI
    SUBMENU_ITEM_LINKS   = home_locators.SUBMENU_ITEM_LINKS
    TABLE_HEADER         = home_locators.TABLE_HEADER
    DIALOG               = home_locators.DIALOG
    DIALOG_ALT           = home_locators.DIALOG_ALT
    POPUP_TITLE          = home_locators.POPUP_TITLE
    POPUP_DROPDOWN       = home_locators.POPUP_DROPDOWN
    SCREENSHOTS_DIR      = home_locators.SCREENSHOTS_DIR
