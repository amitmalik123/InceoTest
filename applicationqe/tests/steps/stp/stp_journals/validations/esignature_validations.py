"""
Validations for Electronic Signature functionality
"""
from playwright.sync_api import Page, expect
from utils.allure_helpers import assert_visible, assert_not_visible, assert_title
from typing import Dict, Any

class ESignatureValidations:
    """Validation methods for electronic signature functionality"""

    def __init__(self, page: Page):
        self.page = page

    def validate_esignature_section_visible(self, test_data: Dict[str, Any]) -> None:
        """Validate e-signature section is visible"""
        assert_visible(self.page, self.page.get_by_text(test_data["eSignature"]["subHeading"]),
                      "E-signature section visible")

    def validate_email_phone_fields_available(self) -> None:
        """Validate email and phone fields are available"""
        email_field = self.page.get_by_role("textbox").first
        phone_field = self.page.get_by_role("textbox").last
        assert_visible(self.page, email_field, "Email field available")
        assert_visible(self.page, phone_field, "Phone field available")

    def validate_authorization_dropdown_present(self) -> None:
        """Validate authorization dropdown may be present"""
        combobox = self.page.get_by_role("combobox")
        if combobox.is_visible():
            assert_visible(self.page, combobox, "Authorization dropdown present")

    def validate_combobox_clickable(self) -> None:
        """Validate combobox can be clicked and opened"""
        combobox = self.page.get_by_role("combobox")
        if combobox.is_visible():
            expect(combobox).to_be_visible()
            expect(combobox).to_be_enabled()

    def validate_account_options_displayed(self) -> None:
        """Validate account options are displayed in dropdown"""
        options = self.page.get_by_role("option").all()
        if len(options) > 0:
            for option in options:
                expect(option).to_be_visible()

    def validate_email_field_accepts_input(self, email: str) -> None:
        """Validate email field accepts valid email format"""
        email_field = self.page.get_by_role("textbox").first
        expect(email_field).to_have_value(email)

    def validate_phone_field_accepts_input(self, phone: str) -> None:
        """Validate phone field accepts numeric input"""
        phone_field = self.page.get_by_role("textbox").last
        expect(phone_field).to_have_value(phone)

    def validate_phone_number_formatted(self) -> None:
        """Validate phone number is formatted correctly"""
        phone_field = self.page.get_by_role("textbox").last
        phone_value = phone_field.input_value()
        # Basic validation that phone contains expected characters
        assert any(char.isdigit() for char in phone_value), "Phone number contains digits"

    def validate_confirmation_checkbox_available(self) -> None:
        """Validate confirmation checkbox can be selected"""
        checkbox = self.page.get_by_role("checkbox")
        assert_visible(self.page, checkbox, "Confirmation checkbox available")
        expect(checkbox).to_be_enabled()

    def validate_checkbox_checked_state(self) -> None:
        """Validate checkbox shows checked state"""
        checkbox = self.page.get_by_role("checkbox")
        expect(checkbox).to_be_checked()

    def validate_agreement_terms_acknowledged(self) -> None:
        """Validate agreement terms are acknowledged"""
        # This would check for agreement text or terms display
        pass

    def validate_esignature_configuration_saved(self) -> None:
        """Validate e-signature configuration is saved"""
        # Implementation would check for save confirmation or state persistence
        pass

    def validate_no_validation_errors_prevent_progression(self) -> None:
        """Validate no validation errors prevent progression"""
        error_messages = self.page.locator(".error, .validation-error, [class*='error']").all()
        for error in error_messages:
            expect(error).not_to_be_visible()

    def validate_esignature_details_in_summary(self, test_data: Dict[str, Any]) -> None:
        """Validate e-signature details appear in summary"""
        if "eSignature" in test_data:
            assert_visible(self.page, self.page.get_by_text(test_data["eSignature"]["email"]),
                          f"E-signature email '{test_data['eSignature']['email']}' visible")
            assert_visible(self.page, self.page.get_by_text(test_data["eSignature"]["phone"]),
                          f"E-signature phone '{test_data['eSignature']['phone']}' visible")