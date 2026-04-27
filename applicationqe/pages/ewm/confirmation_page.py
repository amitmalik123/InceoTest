"""  
Confirmation Page Object - Final request confirmation and completion actions
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.ewm.locators.confirmation_locators import ConfirmationLocators
from typing import Dict, Any, Optional

class ConfirmationPage(BasePage):
    """Page object for final confirmation and completion actions"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ConfirmationLocators()

    def wait_for_confirmation_page_load(self, timeout: int = 30000) -> None:
        """Wait for confirmation page to load completely"""
        self.logger.info("Waiting for confirmation page to load")
        self.wait_for_load_state("domcontentloaded", timeout=timeout)
        
        # Wait for key confirmation elements
        try:
            self.page.wait_for_selector("text=confirmation", timeout=10000)
        except Exception as e:
            self.logger.warning(f"Standard confirmation text not found: {e}")

    def extract_request_number(self, pattern: str = None) -> Optional[str]:
        """
        Extract the generated request number from confirmation page
        Args:
            pattern: Regex pattern to match request number format
        Returns:
            Extracted request number or None if not found
        """
        try:
            if pattern:
                # Use provided pattern to extract request number
                request_element = self.page.locator(f"text=/{pattern}/").first
            else:
                # Look for common request number patterns
                selectors_to_try = [
                    "text=/Request\\s*#?:?\\s*([A-Z0-9\\-]+)/",
                    "text=/Number\\s*#?:?\\s*([A-Z0-9\\-]+)/",
                    "text=/ID\\s*#?:?\\s*([A-Z0-9\\-]+)/"
                ]
                
                for selector in selectors_to_try:
                    try:
                        request_element = self.page.locator(selector).first
                        if request_element.is_visible(timeout=2000):
                            break
                    except:
                        continue
                else:
                    return None

            # Extract the request number text
            request_text = request_element.text_content()
            self.logger.info(f"Extracted request number: {request_text}")
            return request_text
            
        except Exception as e:
            self.logger.error(f"Failed to extract request number: {e}")
            return None

    def click_continue_button(self) -> None:
        """Click continue button if present on confirmation page"""
        try:
            continue_button = self.page.get_by_role("button", name="Continue")
            if continue_button.is_visible(timeout=5000):
                self.logger.info("Clicking continue button")
                continue_button.click()
                self.wait_for_load_state("networkidle")
        except Exception as e:
            self.logger.info(f"Continue button not found or not clickable: {e}")

    def click_done_button(self) -> None:
        """Click done/finish button if present"""
        try:
            button_selectors = [
                "button:has-text('Done')",
                "button:has-text('Finish')", 
                "button:has-text('Complete')",
                "text=Done",
                "text=Finish"
            ]
            
            for selector in button_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        self.logger.info(f"Clicking button with selector: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                        
        except Exception as e:
            self.logger.info(f"Done/Finish button not found: {e}")

    def get_confirmation_details(self) -> Dict[str, Any]:
        """
        Extract all confirmation details from the page
        Returns:
            Dictionary with extracted confirmation information
        """
        details = {
            "timestamp": self.page.evaluate("() => new Date().toISOString()"),
            "url": self.page.url,
            "request_number": None,
            "status": "confirmed"
        }
        
        # Try to extract request number
        details["request_number"] = self.extract_request_number()
        
        # Extract any visible success messages
        try:
            success_elements = self.page.locator("text=/success|confirmed|complete/i")
            if success_elements.count() > 0:
                details["success_message"] = success_elements.first.text_content()
        except:
            pass
            
        return details

    def navigate_to_tracking(self) -> None:
        """Navigate to tracking center if link/button available"""
        try:
            tracking_selectors = [
                "a:has-text('Track')",
                "a:has-text('Tracking')",
                "button:has-text('Track')",
                "text=View Status"
            ]
            
            for selector in tracking_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        self.logger.info(f"Clicking tracking link: {selector}")
                        element.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"Tracking navigation not available: {e}")

    def capture_confirmation_screenshot(self, filename: str = None) -> str:
        """
        Capture screenshot of confirmation page
        Args:
            filename: Custom filename for screenshot
        Returns:
            Path to saved screenshot
        """
        if not filename:
            filename = f"confirmation_{self.get_timestamp()}.png"
            
        screenshot_path = f"reports/screenshots/{filename}"
        self.page.screenshot(path=screenshot_path, full_page=True)
        self.logger.info(f"Confirmation screenshot saved: {screenshot_path}")
        return screenshot_path
