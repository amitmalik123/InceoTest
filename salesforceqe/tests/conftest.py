import pytest
from pathlib import Path
import sys

# Ensure the project root is in the path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# pytest-bdd plugin is auto-loaded by pytest
# No need to explicitly register it


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context to ignore HTTPS errors for test environments"""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def vcr_config():
    """VCR configuration for recording HTTP interactions"""
    return {
        "filter_headers": ['authorization'],
    }
