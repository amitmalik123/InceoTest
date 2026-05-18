"""Page Objects Package for the supported feature flows."""

from pages.base_page import BasePage
from pages.clients_page import ClientsPage
from pages.login_page import LoginPage
from pages.lookup_page import LookupPage
from pages.navbar_login_page import NavbarLoginPage
from pages.PR.document_vault_page import DocumentVaultPage
from pages.PR.rgl_page import RGLPage
from pages.PR.tms_page import TMSPage
from pages.tracking_center_page import TrackingCenterPage

__all__ = [
    "BasePage",
    "ClientsPage",
    "DocumentVaultPage",
    "LoginPage",
    "LookupPage",
    "NavbarLoginPage",
    "RGLPage",
    "TrackingCenterPage",
    "TMSPage",
]
