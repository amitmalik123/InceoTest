"""
E-Signature Page Object - Electronic signature workflow actions
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from typing import Dict, Any, Optional

class EsignaturePage(BasePage):
    """Page object for electronic signature workflow actions"""

    def __init__(self, page: Page):
        super().__init__(page)

    def wait_for_esignature_page_load(self, timeout: int = 30000) -> None:
        """
        Wait for e-signature page to load completely
        Args:
            timeout: Maximum wait time in milliseconds
        """
        self.logger.info("Waiting for e-signature page to load")
        self.wait_for_load_state("domcontentloaded", timeout=timeout)
        
        # Wait for e-signature specific elements
        esig_indicators = [
            'text="Electronic Signature"',
            'text="E-Signature"',
            'text="Digital Signature"',
            'input[type="email"]',
            'input[type="tel"]',
            'text="Contact Information"'
        ]
        
        for indicator in esig_indicators:
            try:
                if self.page.locator(indicator).first.is_visible(timeout=5000):
                    self.logger.info(f"E-signature page loaded with indicator: {indicator}")
                    return
            except:
                continue
                
        self.logger.info("E-signature page loaded")

    def enter_email(self, email: str) -> None:
        """
        Enter email address for e-signature
        Args:
            email: Email address to enter
        """
        try:
            email_selectors = [
                'input[type="email"]',
                'input[name*="email"]',
                'input[placeholder*="email"]',
                'input[id*="email"]',
                '*:has-text("Email") + input'
            ]
            
            for selector in email_selectors:
                try:
                    email_field = self.page.locator(selector).first
                    if email_field.is_visible(timeout=5000):
                        self.logger.info(f"Entering email: {email}")
                        email_field.clear()
                        email_field.fill(email)
                        return
                except:
                    continue
                    
            self.logger.warning("Email field not found")
            
        except Exception as e:
            self.logger.error(f"Failed to enter email: {e}")

    def enter_phone_number(self, phone: str) -> None:
        """
        Enter phone number for e-signature
        Args:
            phone: Phone number to enter
        """
        try:
            phone_selectors = [
                'input[type="tel"]',
                'input[name*="phone"]',
                'input[placeholder*="phone"]',
                'input[id*="phone"]',
                '*:has-text("Phone") + input'
            ]
            
            for selector in phone_selectors:
                try:
                    phone_field = self.page.locator(selector).first
                    if phone_field.is_visible(timeout=5000):
                        self.logger.info(f"Entering phone: {phone}")
                        phone_field.clear()
                        phone_field.fill(phone)
                        return
                except:
                    continue
                    
            self.logger.warning("Phone field not found")
            
        except Exception as e:
            self.logger.error(f"Failed to enter phone: {e}")

    def select_signature_method(self, method: str) -> None:
        """
        Select signature method (e.g., "Electronic", "DocuSign")
        Args:
            method: Signature method to select
        """
        try:
            # Try radio buttons
            radio_button = self.page.get_by_role("radio", name=method)
            if radio_button.is_visible(timeout=5000):
                self.logger.info(f"Selecting signature method (radio): {method}")
                radio_button.check()
                return
                
            # Try dropdown
            dropdown = self.page.locator("select").first
            if dropdown.is_visible(timeout=5000):
                self.logger.info(f"Selecting signature method (dropdown): {method}")
                dropdown.select_option(label=method)
                return
                
            # Try clickable buttons
            method_button = self.page.get_by_role("button", name=method)
            if method_button.is_visible(timeout=5000):
                self.logger.info(f"Selecting signature method (button): {method}")
                method_button.click()
                return
                
            self.logger.warning(f"Signature method '{method}' not found")
            
        except Exception as e:
            self.logger.error(f"Failed to select signature method '{method}': {e}")

    def click_continue_button(self) -> None:
        """Click continue button to proceed with e-signature"""
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
                    
            self.logger.warning("Continue button not found")
            
        except Exception as e:
            self.logger.error(f"Failed to click continue button: {e}")

    def click_submit_signature_button(self) -> None:
        """Click submit button to finalize e-signature setup"""
        try:
            submit_selectors = [
                'button:has-text("Submit")',
                'button:has-text("Send")',
                'button:has-text("Request Signature")',
                'input[value="Submit"]'
            ]
            
            for selector in submit_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=5000) and button.is_enabled():
                        self.logger.info(f"Clicking submit signature button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to click submit signature button: {e}")

    def check_consent_checkbox(self) -> None:
        """Check consent/agreement checkbox if present"""
        try:
            checkbox_selectors = [
                'input[type="checkbox"]',
                'input:near(text="consent")',
                'input:near(text="agree")',
                'input:near(text="acknowledge")',
                'input:near(text="terms")'
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = self.page.locator(selector).first
                    if checkbox.is_visible(timeout=3000) and not checkbox.is_checked():
                        self.logger.info(f"Checking consent checkbox: {selector}")
                        checkbox.check()
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"No consent checkbox found: {e}")

    def fill_esignature_form(self, email: str, phone: str, method: str = "Electronic") -> None:
        """
        Fill out complete e-signature form
        Args:
            email: Email address
            phone: Phone number  
            method: Signature method
        """
        try:
            self.logger.info("Filling e-signature form")
            
            # Enter contact information
            self.enter_email(email)
            self.enter_phone_number(phone)
            
            # Select signature method
            self.select_signature_method(method)
            
            # Check consent if required
            self.check_consent_checkbox()
            
            self.logger.info("E-signature form completed")
            
        except Exception as e:
            self.logger.error(f"Failed to fill e-signature form: {e}")

    def wait_for_signature_sent_confirmation(self, timeout: int = 30000) -> bool:
        """
        Wait for confirmation that signature request was sent
        Returns:
            True if confirmation detected, False if timeout
        """
        try:
            confirmation_indicators = [
                'text="Signature request sent"',
                'text="Email sent"',
                'text="Request submitted"',
                'text="Successfully sent"'
            ]
            
            for indicator in confirmation_indicators:
                try:
                    element = self.page.locator(indicator).first
                    element.wait_for(state="visible", timeout=timeout)
                    self.logger.info(f"Signature sent confirmation: {indicator}")
                    return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not detect signature sent confirmation: {e}")
            return False

    def get_esignature_setup_details(self) -> Dict[str, Any]:
        """
        Extract e-signature setup details from the page
        Returns:
            Dictionary with setup information
        """
        details = {
            "timestamp": self.page.evaluate("() => new Date().toISOString()"),
            "url": self.page.url,
            "email": None,
            "phone": None,
            "method": None
        }
        
        try:
            # Extract filled email
            email_input = self.page.locator('input[type="email"]').first
            if email_input.is_visible(timeout=1000):
                details["email"] = email_input.input_value()
                
            # Extract filled phone
            phone_input = self.page.locator('input[type="tel"]').first
            if phone_input.is_visible(timeout=1000):
                details["phone"] = phone_input.input_value()
                
            # Extract selected method
            checked_radio = self.page.locator('input[type="radio"]:checked').first
            if checked_radio.is_visible(timeout=1000):
                details["method"] = checked_radio.get_attribute("value")
                
        except Exception as e:
            self.logger.warning(f"Could not extract all setup details: {e}")
            
        return details

    def click_back_button(self) -> None:
        """Click back button to return to previous page"""
        try:
            back_selectors = [
                'button:has-text("Back")',
                'button:has-text("Previous")',
                'a:has-text("Back")'
            ]
            
            for selector in back_selectors:
                try:
                    button = self.page.locator(selector).first
                    if button.is_visible(timeout=3000):
                        self.logger.info(f"Clicking back button: {selector}")
                        button.click()
                        self.wait_for_load_state("networkidle")
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.info(f"Back button not found: {e}")
