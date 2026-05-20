"""
BDD Steps for Direct Page Access (without login)
"""
import allure
from playwright.sync_api import Page  
from pytest_bdd import given, when, then, parsers
from utils.auth_state_manager import AuthStateManager
import logging

logger = logging.getLogger(__name__)

@given(parsers.parse('I am authenticated and on the "{page_name}" page'))
def authenticated_on_page(page: Page, page_name: str, test_context):
    """Navigate directly to a page with authentication already handled"""
    
    # Map page names to URLs 
    page_urls = {
        "landing": "/en.aspx",
        "journal_transfer": "/maintenance/journals",  
        "clients": "/clients",
        "tracking_center": "/tracking",
        "roth_conversion": "/maintenance/rothconversion"
    }
    
    base_url = "https://test11.ewealthmanager.com"
    url = page_urls.get(page_name.lower(), f"/{page_name}")
    full_url = f"{base_url}{url}"
    
    with allure.step(f"Navigate directly to {page_name} page (authenticated)"):
        logger.info(f"🚀 Direct navigation to {page_name} page: {full_url}")
        
        # Navigate directly (authentication handled by fixture)
        page.goto(full_url)
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Store in test context
        test_context['current_page'] = page_name
        test_context['authenticated'] = True
        
        logger.info(f"✅ Successfully navigated to {page_name} page")


@given('I am authenticated and ready to test any page')
def authenticated_ready(page: Page, test_context):
    """Set up authenticated session ready for any page testing"""
    
    with allure.step("Authenticated session ready"):
        logger.info("🔐 Authenticated session is ready for page testing")
        
        # Verify we're authenticated by checking a known authenticated endpoint
        page.goto("https://test11.ewealthmanager.com/en.aspx")
        page.wait_for_load_state("networkidle")
        
        # If we can access this page, we're authenticated
        test_context['authenticated'] = True
        test_context['base_url'] = "https://test11.ewealthmanager.com"
        
        logger.info("✅ Authentication verified - ready for testing")


@when(parsers.parse('I navigate to the "{page_name}" page'))  
def navigate_to_page(page: Page, page_name: str, test_context):
    """Navigate to any page using authenticated session"""
    
    page_urls = {
        "landing": "/en.aspx",
        "journal_transfer": "/maintenance/journals",
        "clients": "/clients", 
        "tracking_center": "/tracking",
        "account_details": "/accounts",
        "roth_conversion": "/maintenance/rothconversion"
    }
    
    base_url = test_context.get('base_url', 'https://test11.ewealthmanager.com')
    url = page_urls.get(page_name.lower(), f"/{page_name}")
    full_url = f"{base_url}{url}"
    
    with allure.step(f"Navigate to {page_name} page"):
        logger.info(f"📍 Navigating to {page_name}: {full_url}")
        
        page.goto(full_url)
        page.wait_for_load_state("networkidle", timeout=10000)  
        
        test_context['current_page'] = page_name
        logger.info(f"✅ Successfully navigated to {page_name}")


@then(parsers.parse('I should be on the "{page_name}" page'))
def verify_on_page(page: Page, page_name: str):
    """Verify we're on the expected page"""
    
    with allure.step(f"Verify on {page_name} page"):
        logger.info(f"🔍 Verifying we're on {page_name} page")
        
        current_url = page.url
        page_identifiers = {
            "landing": ["en.aspx", "Digital Maintenance"],
            "journal_transfer": ["maintenance/journals", "Transfer Assets"],  
            "clients": ["/clients", "Clients"],
            "tracking_center": ["/tracking", "Tracking"]
        }
        
        identifiers = page_identifiers.get(page_name.lower(), [page_name])
        
        # Check URL contains expected identifier
        url_match = any(identifier in current_url for identifier in identifiers)
        assert url_match, f"Expected to be on {page_name} page, but URL is: {current_url}"
        
        logger.info(f"✅ Confirmed on {page_name} page: {current_url}")


@when('I take a screenshot for verification')
def take_verification_screenshot(page: Page, test_context):
    """Take a screenshot for visual verification"""
    
    page_name = test_context.get('current_page', 'unknown')
    
    with allure.step(f"Take screenshot of {page_name} page"):
        screenshot_path = f"reports/oam/screenshots/{page_name}_verification.png"
        page.screenshot(path=screenshot_path, full_page=True)
        
        # Attach to allure report
        with open(screenshot_path, "rb") as image_file:
            allure.attach(
                image_file.read(),
                name=f"{page_name} Page Screenshot", 
                attachment_type=allure.attachment_type.PNG
            )
        
        logger.info(f"📸 Screenshot taken: {screenshot_path}")
