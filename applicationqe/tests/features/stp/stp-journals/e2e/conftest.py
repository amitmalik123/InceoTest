"""
STP-specific pytest configuration

This conftest.py provides EWM page object fixtures for STP tests only.
Scoped to tests/features/stp/ so it doesn't affect OAM or other tests.

Fixtures:
- EWM page objects: login_page, clients_page, account_list_page, account_detail_page,
                    roth_conversion_page, tracking_center_page
"""

import pytest
from playwright.sync_api import Page

from pages.ewm.account_detail_page import AccountDetailPage
from pages.ewm.account_list_page import AccountListPage
from pages.ewm.clients_page import ClientsPage
from pages.ewm.login_page import LoginPage
from pages.ewm.roth_conversion_page import RothConversionPage
from pages.ewm.tracking_center_page import TrackingCenterPage


@pytest.fixture
def login_page(page: Page):
    """Login page object fixture"""
    return LoginPage(page)


@pytest.fixture
def clients_page(page: Page):
    """Clients page object fixture"""
    return ClientsPage(page)


@pytest.fixture
def account_list_page(page: Page):
    """Account list page object fixture"""
    return AccountListPage(page)


@pytest.fixture
def account_detail_page(page: Page):
    """Account detail page object fixture"""
    return AccountDetailPage(page)


@pytest.fixture
def roth_conversion_page(page: Page):
    """Roth conversion page object fixture"""
    return RothConversionPage(page)


@pytest.fixture
def tracking_center_page(page: Page):
    """Tracking center page object fixture"""
    return TrackingCenterPage(page)
