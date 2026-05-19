from pathlib import Path
import sys

import pytest
from playwright.sync_api import Page


MODELS_PAGE_DIR = Path(__file__).resolve().parents[4] / "pages" / "model-management" / "wrappermodel"
sys.path.insert(0, str(MODELS_PAGE_DIR))

from models_page import ModelsPage


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
