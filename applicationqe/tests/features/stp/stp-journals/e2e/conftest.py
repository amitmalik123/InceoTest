import csv

import pytest
from playwright.sync_api import Page

from pages.ewm.account_detail_page import AccountDetailPage
from pages.ewm.account_list_page import AccountListPage
from pages.ewm.clients_page import ClientsPage
from pages.ewm.login_page import LoginPage
from pages.ewm.roth_conversion_page import RothConversionPage
from pages.ewm.tracking_center_page import TrackingCenterPage
from utils.settings import settings


@pytest.fixture
def test_context():
    """Context to store test data and state across steps."""
    return {}


@pytest.fixture
def test_data():
    """Load test data from CSV file configured in settings."""
    csv_path = settings.test_data_csv
    with open(csv_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return next(reader)


@pytest.fixture
def login_page(page: Page):
    return LoginPage(page)


@pytest.fixture
def clients_page(page: Page):
    return ClientsPage(page)


@pytest.fixture
def account_list_page(page: Page):
    return AccountListPage(page)


@pytest.fixture
def account_detail_page(page: Page):
    return AccountDetailPage(page)


@pytest.fixture
def roth_conversion_page(page: Page):
    return RothConversionPage(page)


@pytest.fixture
def tracking_center_page(page: Page):
    return TrackingCenterPage(page)
