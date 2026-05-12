import csv
from pathlib import Path

import pytest
from playwright.sync_api import Page

from pages.ewm.account_detail_page import AccountDetailPage
from pages.ewm.account_list_page import AccountListPage
from pages.ewm.clients_page import ClientsPage
from pages.ewm.login_page import LoginPage
from pages.ewm.roth_conversion_page import RothConversionPage
from pages.ewm.tracking_center_page import TrackingCenterPage
from config.oam.settings import get_settings


@pytest.fixture
def test_context():
    """Context to store test data and state across steps"""
    return {}


@pytest.fixture
def test_data():
    """Load test data from CSV file"""
    csv_path = get_settings().test_data_csv
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        return next(reader)


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

