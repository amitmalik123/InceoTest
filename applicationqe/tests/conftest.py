import pytest
from pathlib import Path
import sys
import getpass
import os

# Ensure the project root is in the path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# pytest-bdd plugin is auto-loaded by pytest
# No need to explicitly register it

def pytest_addoption(parser):
    """Add a custom --env option to specify the test environment."""
    parser.addoption(
        "--env",
        action="store",
        default="test11",
        help="Specify the test environment (e.g., test01, test11, prod). Default is test11."
    )

@pytest.fixture(scope="session")
def test_environment(request):
    """Provide the test environment as a fixture."""
    return request.config.getoption("--env")

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


@pytest.fixture(scope="session")
def maximize_window_and_login(browser):
    """Maximize the browser window and perform login with default credentials."""
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})  # Maximize window

    # Use default credentials
    username = os.getenv("DEFAULT_USERNAME", "sampleadvisorlogin")
    password = os.getenv("DEFAULT_PASSWORD", "amkF1n@nc23S")

    # Navigate to login page and perform login
    login_page = LoginPage(page)
    login_page.navigate_to_login(Settings().login_url)
    login_page.dismiss_cookie_consent()
    page.fill("input[name='username'], input[id='username']", username)
    page.fill("input[name='password'], input[id='password']", password)
    page.click("input[type='submit'], button[type='submit']")

    # Wait for successful login
    page.wait_for_url("**/en.aspx", timeout=30000)
    return page
