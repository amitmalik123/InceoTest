"""
DocuSign Page Object - Digital signature workflow actions
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from typing import Dict, Any, Optional

class DocusignPage(BasePage):
    """Page object for DocuSign digital signature workflow actions"""

    def __init__(self, page: Page):
        super().__init__(page)

    def wait_for_docusign_page_load(self, timeout: int = 30000) -> None:
        """
        Wait for DocuSign page to load completely
        Args:
            timeout: Maximum wait time in milliseconds
        """
        self.logger.info("Waiting for DocuSign page to load")
        
        # Wait for DocuSign URL pattern
        try:
            self.page.wait_for_url("**/docusign**", timeout=timeout)
            self.logger.info("DocuSign URL detected")
        except Exception as e:
            self.logger.warning(f"DocuSign URL not detected: {e}")
        
        # Wait for page load state
        self.wait_for_load_state("networkidle", timeout=timeout)
        
        # Wait for DocuSign-specific elements
        docusign_indicators = [
            'img[title="Signature"]',
            'button:has-text("Sign")',
            'text=DocuSign',
            '[data-qa="signature-field"]'
        ]
        
        for indicator in docusign_indicators:
            try:
                if self.page.locator(indicator).first.is_visible(timeout=5000):
                    self.logger.info(f"DocuSign page loaded with indicator: {indicator}")
                    return
            except:
                continue
                
        self.logger.info("DocuSign page loaded (no specific indicators found)")

    def click_signature_field(self) -> None:
        """Click on the signature field to initiate signing"""
        try:
            signature_selectors = [
                'img[title="Signature"]',
                '[data-qa="signature-field"]',
                '.signature-field',
                'button:has-text("Click to Sign")',
                'span:has-text("Sign Here")'
            ]
            
            for selector in signature_selectors:
                try:
                    field = self.page.locator(selector).first
                    if field.is_visible(timeout=5000):
                        self.logger.info(f"Clicking signature field: {selector}")
                        field.click()
                        return
                except:
                    continue
                    
            self.logger.warning("No signature field found to click")
            
        except Exception as e:
            self.logger.error(f"Failed to click signature field: {e}")

    def select_signature_style(self, style_index: int = 0) -> None:
        """
        Select a signature style from available options
        Args:
            style_index: Index of signature style to select (0-based)
        """
        try:
            # Wait for signature style options to appear
            style_selectors = [
                '.signature-style',
                '[data-qa="signature-style"]',
                'button:has-text("Style")',
                '.signature-option'
            ]
            
            for selector in style_selectors:
                try:
                    styles = self.page.locator(selector)
                    if styles.count() > style_index:
                        self.logger.info(f"Selecting signature style {style_index}")
                        styles.nth(style_index).click()
                        return
                except:
                    continue
                    
            self.logger.warning(f"Signature style {style_index} not found")
            
        except Exception as e:
            self.logger.error(f"Failed to select signature style: {e}")

    def click_adopt_and_sign(self) -> None:
        """Click the 'Adopt and Sign' button to complete signature"""
        try:
            adopt_selectors = [
                'button:has-text("Adopt and Sign")',
                'button:has-text("Adopt & Sign")', 
                'input[value*="Adopt"]',
                'button[data-qa="adopt-sign"]'
            ]
            
            for selector in adopt_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=5000) and button.is_enabled():
                        self.logger.info(f"Clicking adopt and sign: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
            self.logger.warning("Adopt and Sign button not found")
            
        except Exception as e:
            self.logger.error(f"Failed to click adopt and sign: {e}")

    def click_finish_button(self) -> None:
        """Click finish button after signing"""
        try:
            finish_selectors = [
                'button:has-text("Finish")',
                'button:has-text("Complete")',
                'button:has-text("Done")',
                'input[value="Finish"]'
            ]
            
            for selector in finish_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=5000) and button.is_enabled():
                        self.logger.info(f"Clicking finish button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"Finish button not found: {e}")

    def click_continue_button(self) -> None:
        """Click continue button in DocuSign workflow"""
        try:
            continue_selectors = [
                'button:has-text("Continue")',
                'button:has-text("Next")',
                'button:has-text("Proceed")',
                'input[value="Continue"]'
            ]
            
            for selector in continue_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=5000) and button.is_enabled():
                        self.logger.info(f"Clicking continue button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"Continue button not available: {e}")

    def check_agreement_checkbox(self) -> None:
        """Check agreement checkbox if present"""
        try:
            checkbox_selectors = [
                'input[type="checkbox"]',
                '[data-qa="agreement-checkbox"]',
                'input:near(text="agree")',
                'input:near(text="consent")'
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = self.page.locator(selector).first
                    if checkbox.is_visible(timeout=3000):
                        self.logger.info(f"Checking agreement checkbox: {selector}")
                        checkbox.check()
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"No agreement checkbox found: {e}")

    def complete_signature_workflow(self, style_index: int = 0) -> bool:
        """
        Complete the entire DocuSign signature workflow
        Args:
            style_index: Signature style to select
        Returns:
            True if workflow completed successfully, False otherwise
        """
        try:
            self.logger.info("Starting DocuSign signature workflow")
            
            # Step 1: Click signature field
            self.click_signature_field()
            
            # Step 2: Select signature style
            self.select_signature_style(style_index)
            
            # Step 3: Check agreement if present
            self.check_agreement_checkbox()
            
            # Step 4: Adopt and sign
            self.click_adopt_and_sign()
            
            # Step 5: Continue if needed
            self.click_continue_button()
            
            # Step 6: Finish if present
            self.click_finish_button()
            
            self.logger.info("DocuSign signature workflow completed")
            return True
            
        except Exception as e:
            self.logger.error(f"DocuSign workflow failed: {e}")
            return False

    def wait_for_signature_completion(self, timeout: int = 30000) -> bool:
        """
        Wait for signature completion confirmation
        Returns:
            True if completion detected, False if timeout
        """
        try:
            completion_indicators = [
                'text="You have successfully signed"',
                'text="Signing Complete"',
                'text="Document Signed"',
                'text="Thank you"'
            ]
            
            for indicator in completion_indicators:
                try:
                    element = self.page.locator(indicator).first
                    element.wait_for(state="visible", timeout=timeout)
                    self.logger.info(f"Signature completion detected: {indicator}")
                    return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not detect signature completion: {e}")
            return False

    def return_to_application(self) -> None:
        """Return to the main application after signing"""
        try:
            return_selectors = [
                'a:has-text("Return")',
                'button:has-text("Return")',
                'a:has-text("Back to")',
                'button:has-text("Continue to")'
            ]
            
            for selector in return_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=5000):
                        self.logger.info(f"Returning to application: {selector}")
                        element.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"No return link found: {e}")

    def get_docusign_session_details(self) -> Dict[str, Any]:
        """
        Extract DocuSign session details
        Returns:
            Dictionary with session information
        """
        details = {
            "timestamp": self.page.evaluate("() => new Date().toISOString()"),
            "url": self.page.url,
            "domain": None,
            "document_title": None
        }
        
        try:
            # Extract domain
            details["domain"] = self.page.evaluate("() => window.location.hostname")
            
            # Extract document title
            details["document_title"] = self.page.title()
            
        except Exception as e:
            self.logger.warning(f"Could not extract all session details: {e}")
            
        return details
