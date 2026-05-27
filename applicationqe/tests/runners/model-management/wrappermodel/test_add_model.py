"""
Test module for Advisor Model Management BDD scenarios.

Scenarios covered:
  - Navigate to Advisor model list page (Published tab, Create Model button, table columns)
  - Create Model (strategy modal, allocation, widgets, Save Draft -> Publish)
"""

import os
import sys

os.environ.setdefault("TEST_ENV", "test01")

# Ensure the application root is in PYTHONPATH.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

# Load step modules from the wrappermodel step folder directly. This avoids
# package import issues caused by hyphenated directory names.
STEP_DEFS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "steps",
        "model-management",
        "wrappermodel",
    )
)
sys.path.insert(0, STEP_DEFS_DIR)

MODELS_PAGE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "pages",
        "model-management",
        "wrappermodel",
    )
)
WRAPPERMODEL_ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "features",
        "model-management",
        "WrapperModel",
    )
)
sys.path.insert(0, WRAPPERMODEL_ROOT_DIR)
sys.path.insert(0, MODELS_PAGE_DIR)

import pytest
from pytest_bdd import scenarios
from playwright.sync_api import Page
from models_page import ModelsPage


@pytest.fixture
def test_context() -> dict:
    return {
        "test_data": {
            "username": os.getenv("DEFAULT_USERNAME", "T11_AG8959_Perf"),
            "password": os.getenv("DEFAULT_PASSWORD", "QAAdminUser_33a"),
            "role": "internal_admin",
        }
    }


@pytest.fixture
def models_page(page: Page) -> ModelsPage:
    return ModelsPage(page)


# Import step definitions - order matters for pytest-bdd step registration
from common_steps import *  # noqa: F401, F403
from login_steps import *  # noqa: F401, F403
from add_model_steps import *  # noqa: F401, F403


# Load scenarios from all individual TC feature files
scenarios("../../../features/model-management/WrapperModel/add_model_tc1.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc2.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc3.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc4.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc5.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc6.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc7.feature")
scenarios("../../../features/model-management/WrapperModel/add_model_tc9.feature")
