import os
os.environ.setdefault('TEST_TEAM', 'stp-ict')

import csv

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, tmp_path_factory):
    """Enable Playwright video recording for all ICT tests."""
    video_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "..", "..",  # up to applicationqe
        "reports", "stp-ict", "videos"
    )
    os.makedirs(video_dir, exist_ok=True)
    return {
        **browser_context_args,
        "record_video_dir": video_dir,
        "record_video_size": {"width": 1280, "height": 720},
    }

import sys
# Add tests/features/stp/stp-ict/ so that 'from validations.xxx' in page objects
# resolves to the validations/ sub-package that lives alongside this conftest.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../../pages/stp/stp-ict')
))

from pages.ewm.account_detail_page import AccountDetailPage
from pages.ewm.account_list_page import AccountListPage
from pages.ewm.clients_page import ClientsPage
from client_suitability_page import ClientSuitabilityPage
from ict_account_number_page import AccountNumberPage
from ict_create_fees_page import CreateFeesPage
from ict_create_forms_page import CreateFormsPage
from ict_docusign_page import DocuSignPage
from ict_login_page import LoginPage
from ict_select_destination_page import SelectDestinationPage
from ict_select_source_account_page import SelectSourceAccountPage
from ict_summary_page import ICTSummaryPage
from ict_tracking_center_page import TrackingCenterPage
from utils.settings import settings


@pytest.fixture
def test_context():
    """Context to store test data and state across steps."""
    return {}


@pytest.fixture
def test_data():
    """Load first row of test data from the stp-ict CSV."""
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
def select_source_account_page(page: Page):
    return SelectSourceAccountPage(page)


@pytest.fixture
def select_destination_page(page: Page):
    return SelectDestinationPage(page)


@pytest.fixture
def account_number_page(page: Page):
    return AccountNumberPage(page)


@pytest.fixture
def client_suitability_page(page: Page):
    return ClientSuitabilityPage(page)


@pytest.fixture
def create_fees_page(page: Page):
    return CreateFeesPage(page)


@pytest.fixture
def ict_summary_page(page: Page):
    return ICTSummaryPage(page)


@pytest.fixture
def create_forms_page(page: Page):
    return CreateFormsPage(page)


@pytest.fixture
def docusign_page(page: Page):
    return DocuSignPage(page)


@pytest.fixture
def tracking_center_page(page: Page):
    return TrackingCenterPage(page)
