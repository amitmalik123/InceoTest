"""Page object fixtures for the supported feature flows."""

import pytest
from playwright.sync_api import Page

from config.settings import get_settings
from pages.PortfolioReporting.clients_page import ClientsPage
from pages.PortfolioReporting.document_vault_page import DocumentVaultPage
from pages.PortfolioReporting.login_page import LoginPage
from pages.PortfolioReporting.navbar_login_page import NavbarLoginPage
from pages.PortfolioReporting.tracking_center_page import TrackingCenterPage

# Resolve base_url once from the active environment config
_base_url = get_settings().base_url


@pytest.fixture
def login_page(authenticated_page: Page) -> LoginPage:
    """Login page object fixture"""
    return LoginPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def navbar_login_page(authenticated_page: Page) -> NavbarLoginPage:
    """Navbar login page object fixture"""
    return NavbarLoginPage(authenticated_page)


@pytest.fixture
def clients_page(authenticated_page: Page) -> ClientsPage:
    """Clients page object fixture"""
    return ClientsPage(authenticated_page, base_url=_base_url)


@pytest.fixture
def document_vault_page(authenticated_page: Page) -> DocumentVaultPage:
    """Document Vault page object fixture"""
    return DocumentVaultPage(authenticated_page)


@pytest.fixture
def tracking_center_page(authenticated_page: Page) -> TrackingCenterPage:
    """Tracking Center page object fixture"""
    return TrackingCenterPage(authenticated_page, base_url=_base_url)
