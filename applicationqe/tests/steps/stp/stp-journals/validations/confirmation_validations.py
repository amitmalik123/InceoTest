"""
Validations for Confirmation page
Extracted from test_journal_transfer_refactored_v2.py - Final confirmation assertions
"""
from playwright.sync_api import Page, expect
from utils.allure_helpers import assert_visible
from typing import Dict, Any, Optional
import re


class ConfirmationValidations:
    """Validation methods for final request confirmation page"""

    def __init__(self, page: Page):
        self.page = page

    def _extract_request_number_from_text(self, text: str) -> Optional[str]:
        """Extract a likely request identifier from free-form text."""
        if not text:
            return None

        patterns = [
            r"\b([Aa]\d{6,15})\b",
            r"\b([A-Z]{2,6}-\d{4,20})\b",
            r"(?:Request|Tracking|Reference|Confirmation|Item)\s*(?:number|#|id)?\s*:?\s*([A-Z0-9\-]{6,30})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def validate_confirmation_page_elements(self, test_data: Dict[str, Any]) -> None:
        """
        Validate confirmation page displays all required elements
        Extracted from Step 12 confirmation page validation
        """
        ui_text = test_data.get("uiText", {})

        # Check for main confirmation heading from test data when available.
        confirmation_heading = ui_text.get("confirmation")
        if confirmation_heading:
            assert_visible(
                self.page,
                self.page.get_by_text(confirmation_heading),
                f"confirmation page heading '{confirmation_heading}' visible"
            )

        # Check for confirmation message from test data when available.
        confirmation_message = ui_text.get("confirmationMessage")
        if confirmation_message:
            assert_visible(
                self.page,
                self.page.get_by_text(confirmation_message),
                f"confirmation message '{confirmation_message}' visible"
            )

    def validate_request_number_generated(self, test_data: Dict[str, Any]) -> str:
        """
        Validate request number has been generated and capture it
        Extracted from Step 12 request number validation
        Returns the captured request number
        """
        request_number_text = None

        # Strategy 1: Try configured locator/pattern if provided by test data.
        configured_pattern = test_data.get("patterns", {}).get("requestNumberPattern")
        if configured_pattern:
            try:
                configured_element = self.page.get_by_text(configured_pattern)
                assert_visible(
                    self.page,
                    configured_element,
                    "request number visible on confirmation page"
                )
                raw_text = configured_element.first.inner_text(timeout=3000)
                request_number_text = self._extract_request_number_from_text(raw_text) or (raw_text or "").strip()
            except Exception:
                request_number_text = None

        # Strategy 2: Search common request/tracking labels and nearby values.
        if not request_number_text:
            page_text = self.page.inner_text("body")
            request_number_text = self._extract_request_number_from_text(page_text)

        # Strategy 3: Regex against HTML content as final fallback.
        if not request_number_text:
            page_content = self.page.content()
            request_number_text = self._extract_request_number_from_text(page_content)

        assert request_number_text is not None and len(request_number_text.strip()) > 0, \
            "Request number could not be extracted from confirmation page"

        return request_number_text.strip()

    def validate_successful_submission_indicators(self, test_data: Dict[str, Any]) -> None:
        """
        Validate all indicators of successful request submission
        Comprehensive validation for completion state
        """
        # Check status indicators
        ui_text = test_data.get("uiText", {})
        if "successIndicators" in ui_text:
            for indicator in ui_text["successIndicators"]:
                assert_visible(
                    self.page, 
                    self.page.get_by_text(indicator),
                    f"success indicator '{indicator}' visible"
                )

    def validate_next_steps_information(self, test_data: Dict[str, Any]) -> None:
        """
        Validate next steps information is displayed to user
        Extracted from confirmation page user guidance validation
        """
        ui_text = test_data.get("uiText", {})
        if "nextSteps" in ui_text:
            for step_info in ui_text["nextSteps"]:
                assert_visible(
                    self.page, 
                    self.page.get_by_text(step_info),
                    f"next steps info '{step_info}' visible"
                )

    def validate_tracking_information_available(self, test_data: Dict[str, Any]) -> None:
        """
        Validate tracking/reference information is provided
        For user to track request status later
        """
        ui_text = test_data.get("uiText", {})
        if "trackingInfo" in ui_text:
            assert_visible(
                self.page, 
                self.page.get_by_text(ui_text["trackingInfo"]),
                "tracking information visible"
            )

    def validate_confirmation_complete(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation that entire confirmation process is complete
        Returns summary of confirmation details for reporting
        """
        # Perform all confirmation validations
        self.validate_confirmation_page_elements(test_data)
        request_number = self.validate_request_number_generated(test_data)
        self.validate_successful_submission_indicators(test_data)
        
        return {
            "confirmation_validated": True,
            "request_number": request_number,
            "timestamp": self.page.evaluate("() => new Date().toISOString()")
        }