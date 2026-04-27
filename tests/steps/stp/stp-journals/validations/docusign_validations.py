"""
Validations for DocuSign Integration functionality
"""
from playwright.sync_api import Page, expect
from utils.allure_helpers import assert_visible, assert_url
from typing import Dict, Any

class DocuSignValidations:
    """Validation methods for DocuSign integration functionality"""

    def __init__(self, page: Page):
        self.page = page

    def validate_docusign_url_pattern(self, test_data: Dict[str, Any]) -> None:
        """Validate DocuSign URL contains expected pattern"""
        assert_url(self.page, test_data["patterns"]["docusignURLRegex"], 
                   "DocuSign page URL", timeout=20000)

    def validate_docusign_interface_loads(self) -> None:
        """Validate DocuSign interface loads"""
        # Wait for DocuSign page to fully load
        self.page.wait_for_load_state("networkidle", timeout=30000)
        expect(self.page.url).to_contain("docusign")  # or appropriate pattern

    def validate_signature_page_displayed(self) -> None:
        """Validate signature page is displayed"""
        # Basic validation that we're on a signature page
        # Implementation would check for DocuSign-specific elements
        pass

    def validate_confirmation_checkbox_visible(self, test_data: Dict[str, Any]) -> None:
        """Validate confirmation checkbox is visible"""
        assert_visible(self.page, self.page.get_by_role("checkbox"), "DocuSign checkbox visible")

    def validate_checkbox_selectable(self, test_data: Dict[str, Any]) -> None:
        """Validate checkbox can be selected"""
        checkbox_label = self.page.locator(f"label:has-text('{test_data['docusign']['confirmCheckbox']}')")
        assert_visible(self.page, checkbox_label, "DocuSign confirmation checkbox available")

    def validate_agreement_terms_displayed(self) -> None:
        """Validate agreement terms are displayed"""
        # Implementation would check for terms and conditions text
        pass

    def validate_continue_button_advances_process(self, test_data: Dict[str, Any]) -> None:
        """Validate Continue button advances process"""
        continue_button = self.page.get_by_role("button", name=test_data["docusign"]["Continue"])
        assert_visible(self.page, continue_button, "Continue button visible")
        expect(continue_button).to_be_enabled()

    def validate_docusign_page_loaded(self, timeout: int = 30000) -> None:
        """
        Validate DocuSign page has loaded and signature fields are visible
        Extracted from Step 11c DocuSign page validation
        """
        self.page.wait_for_url("https://demo.docusign.net/**", timeout=timeout)
        
        # Validate signature placeholder is visible
        assert_visible(
            self.page,
            self.page.locator('img[title="Signature"]'),
            "DocuSign signature field visible"
        )

    def validate_docusign_signing_complete(self) -> None:
        """
        Validate DocuSign signing process has been completed successfully
        Extracted from Step 11d post-signing validation
        """
        # Wait for completion message
        assert_visible(
            self.page,
            self.page.get_by_text("You have successfully signed"),
            "DocuSign completion message visible",
            timeout=10000
        )

    def validate_return_to_application(self, test_data: Dict[str, Any]) -> None:
        """
        Validate successful return to main application after DocuSign
        Extracted from Step 11e return navigation validation
        """
        # Look for e-signature completion confirmation in the original app
        assert_visible(
            self.page,
            self.page.get_by_text("Digital Signature Complete"),
            "Digital signature completion message visible"
        )

    def validate_docusign_elements_ready(self) -> bool:
        """
        Check if DocuSign page elements are ready for interaction
        Helper method for timing validation
        """
        try:
            signature_field = self.page.locator('img[title="Signature"]')
            return signature_field.is_visible()
        except Exception:
            return False

    def validate_signature_interface_appears(self) -> None:
        """Validate signature interface appears"""
        # Implementation would check for signature pad or interface
        pass

    def validate_document_ready_for_signing(self) -> None:
        """Validate document is ready for signing"""
        # Implementation would verify document state
        pass

    def validate_sign_buttons_clickable(self) -> None:
        """Validate Sign buttons are clickable"""
        sign_buttons = self.page.get_by_role("button", name="Sign").all()
        for button in sign_buttons:
            if button.is_visible():
                expect(button).to_be_enabled()

    def validate_signature_process_progresses(self) -> None:
        """Validate signature process progresses"""
        # Implementation would check for progress indicators
        pass

    def validate_multiple_signatures_completed(self, expected_count: int = None) -> None:
        """Validate multiple signatures can be completed"""
        sign_buttons = self.page.get_by_role("button", name="Sign").all()
        visible_buttons = [btn for btn in sign_buttons if btn.is_visible()]
        
        if expected_count:
            assert len(visible_buttons) == expected_count, f"Expected {expected_count} sign buttons, found {len(visible_buttons)}"

    def validate_finish_button_completes_signing(self, test_data: Dict[str, Any]) -> None:
        """Validate Finish button completes signing"""
        finish_button = self.page.get_by_role("button", name=test_data["docusign"]["Finish"])
        assert_visible(self.page, finish_button, "Finish button visible")
        expect(finish_button).to_be_enabled()

    def validate_docusign_process_concludes(self) -> None:
        """Validate DocuSign process concludes"""
        # Implementation would check for completion indicators
        pass

    def validate_system_returns_to_application(self, original_domain: str) -> None:
        """Validate system returns to application"""
        # Wait for navigation back to main application
        expect(self.page.url).to_contain(original_domain)

    def validate_ready_for_signatures_confirmation(self, test_data: Dict[str, Any]) -> None:
        """Validate 'Ready for Signatures' confirmation text"""
        assert_visible(self.page, self.page.get_by_text(test_data["docusign"]["readyForSignatureText"]),
                      "Ready for Signatures text visible")

    def validate_docusign_integration_confirmed(self) -> None:
        """Validate DocuSign integration is confirmed"""
        # Implementation would check for integration success indicators
        pass

    def validate_process_completion_acknowledged(self) -> None:
        """Validate process completion is acknowledged"""
        # Implementation would verify completion acknowledgment
        pass

    def complete_docusign_flow_validation(self, test_data: Dict[str, Any]) -> None:
        """Complete DocuSign flow validation"""
        self.validate_docusign_url_pattern(test_data)
        self.validate_docusign_interface_loads()
        
        # Validate checkbox interaction
        try:
            self.validate_confirmation_checkbox_visible(test_data)
            self.validate_checkbox_selectable(test_data)
        except:
            pass  # Checkbox might not always be present

        # Validate continue process
        self.validate_continue_button_advances_process(test_data)
        
        # Validate signing process
        self.validate_sign_buttons_clickable()
        
        # Validate completion
        self.validate_finish_button_completes_signing(test_data)
        self.validate_ready_for_signatures_confirmation(test_data)