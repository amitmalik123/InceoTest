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
        "model_management",
        "wrappermodel",
    )
)
if not os.path.exists(os.path.join(MODELS_PAGE_DIR, "models_page.py")):
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
from wrappermodel_credentials import resolve_wrappermodel_credentials


@pytest.fixture
def test_context() -> dict:
    runtime_env = os.getenv("TEST_ENV", "")
    # Keep wrappermodel auth isolated from other suites.
    # Do not consume DEFAULT_USERNAME, which may point to non-wrapper users.
    requested_username = os.getenv("WRAPPERMODEL_TEST_USERNAME")
    selected = resolve_wrappermodel_credentials(runtime_env, requested_username=requested_username)

    # Allow explicit password override for temporary/local runs.
    password_override = os.getenv("WRAPPERMODEL_TEST_PASSWORD")
    if password_override:
        selected["password"] = password_override

    return {
        "test_data": {
            "username": selected["username"],
            "password": selected["password"],
            "aplid": selected["aplid"],
            "environment": selected["environment"],
            # Some shared steps use client_id naming.
            "client_id": selected["aplid"],
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
pytestmark = [pytest.mark.wrappermodel, pytest.mark.app("wrapper")]


# Load scenarios from current WrapperModel BDD feature files.
# Keep explicit per-file registration so TC-to-feature mapping stays readable in code.
scenarios("../../../features/model-management/WrapperModel/Navigate to Model List.feature")
scenarios("../../../features/model-management/WrapperModel/Create Model And Allocate.feature")
scenarios("../../../features/model-management/WrapperModel/Edit Model.feature")
scenarios("../../../features/model-management/WrapperModel/Edit Allocations on Draft Model.feature")
scenarios("../../../features/model-management/WrapperModel/Add aditional Strategies on Draft Model.feature")
scenarios("../../../features/model-management/WrapperModel/Remove and adjust Allocations.feature")
scenarios("../../../features/model-management/WrapperModel/Publish Model.feature")
scenarios("../../../features/model-management/WrapperModel/Edit and add Allocations on Published Model.feature")
