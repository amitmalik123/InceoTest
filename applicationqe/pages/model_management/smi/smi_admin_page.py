from pages.model_management.smi.smi_home_page import SMIHomePage


class SMIAdminPage(SMIHomePage):
    """Locators and tab/submenu name constants for the Admin section (Admin agent only)."""

    TAB_NAME = "Admin"
    SUBMENU_MODEL_MAINTENANCE = "Model Maintenance"
    SUBMENU_USER_MAINTENANCE = "User Maintenance"
