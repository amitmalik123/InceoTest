"""
Authentication State Management - Save and reuse login sessions
"""
import json
import os
from pathlib import Path
from playwright.sync_api import Browser, BrowserContext, Page
from pages.login_page import LoginPage
from utils.settings import Settings

class AuthStateManager:
    """Manages authenticated browser states to skip login"""
    
    def __init__(self, env: str = 'test11'):
        self.settings = Settings(env=env)
        self.auth_state_dir = Path("tests/auth_states")
        self.auth_state_dir.mkdir(exist_ok=True)
        
    def get_auth_state_path(self, username: str) -> Path:
        """Get path for storing auth state"""
        return self.auth_state_dir / f"auth_state_{username}_{self.settings.env}.json"
    
    def save_auth_state(self, browser: Browser, username: str, password: str) -> str:
        """
        Perform login and save authentication state
        Returns the path to the saved state file
        """
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Perform login
            login_page = LoginPage(page)
            login_page.navigate_to_login(self.settings.login_url)
            login_page.dismiss_cookie_consent()
            
            # Enter credentials
            page.fill("input[name='username'], input[id='username']", username)
            page.fill("input[name='password'], input[id='password']", password)
            page.click("input[type='submit'], button[type='submit']")
            
            # Wait for successful login
            page.wait_for_url("**/en.aspx", timeout=30000)
            
            # Save authentication state
            auth_file = self.get_auth_state_path(username)
            context.storage_state(path=str(auth_file))
            
            print(f"✅ Authentication state saved for {username}: {auth_file}")
            return str(auth_file)
            
        finally:
            context.close()
    
    def create_authenticated_context(self, browser: Browser, username: str) -> BrowserContext:
        """
        Create a browser context with saved authentication state
        """
        auth_file = self.get_auth_state_path(username)
        
        if not auth_file.exists():
            raise FileNotFoundError(f"No auth state found for {username}. Run save_auth_state() first.")
        
        # Create context with saved auth state
        context = browser.new_context(storage_state=str(auth_file))
        print(f"✅ Loaded authentication state for {username}")
        return context

# Usage in conftest.py as fixtures
def get_authenticated_page(browser: Browser, username: str = "AlexanderTelidis_T11") -> Page:
    """Get an authenticated page without login"""
    auth_manager = AuthStateManager()
    context = auth_manager.create_authenticated_context(browser, username)
    return context.new_page()