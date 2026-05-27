from pathlib import Path
import sys
import os

import pytest
from playwright.sync_api import Page


WRAPPERMODEL_ROOT_DIR = Path(__file__).resolve().parent
MODELS_PAGE_DIR = Path(__file__).resolve().parents[4] / "pages" / "model-management" / "wrappermodel"
os.environ.setdefault("TEST_ENV", "test01")
sys.path.insert(0, str(WRAPPERMODEL_ROOT_DIR))
sys.path.insert(0, str(MODELS_PAGE_DIR))

from models_page import ModelsPage


def pytest_configure(config):
    config.addinivalue_line("markers", "wrappermodel: wrappermodel BDD scenarios")
    config.addinivalue_line("markers", "models: wrappermodel feature tag")
    config.addinivalue_line("markers", "test_add_model: wrappermodel add-model feature tag")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, request):
    headed = request.config.getoption("--headed", default=False)
    launch_args = list(browser_type_launch_args.get("args", []))

    if headed and "--start-maximized" not in launch_args:
        launch_args.append("--start-maximized")

    return {
        **browser_type_launch_args,
        "args": launch_args,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):
    headed = request.config.getoption("--headed", default=False)
    context_args = {
        **browser_context_args,
        "ignore_https_errors": True,
        "accept_downloads": True,
    }

    if headed:
        context_args["no_viewport"] = True
        context_args.pop("viewport", None)

    return context_args


def pytest_collection_modifyitems(items):
    marker = pytest.mark.wrappermodel
    for item in items:
        item.add_marker(marker)


@pytest.fixture
def test_context() -> dict:
    return {}


@pytest.fixture
def models_page(page: Page) -> ModelsPage:
    return ModelsPage(page)


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    # Backward-compatible alias used by some shared step definitions.
    return page
