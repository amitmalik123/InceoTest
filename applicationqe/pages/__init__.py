"""Page Objects Package for the supported feature flows."""

from pages.PR.base_page import BasePage
from pages.PR.clients_page import ClientsPage
from pages.PR.document_vault_page import DocumentVaultPage
from pages.PR.login_page import LoginPage
from pages.PR.lookup_page import LookupPage
from pages.PR.navbar_login_page import NavbarLoginPage
from pages.PR.rgl_page import RGLPage
from pages.PR.tracking_center_page import TrackingCenterPage
from pages.PR.tms_page import TMSPage

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
