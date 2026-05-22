"""
Validations for Review Summary page
Extracted from test_journal_transfer_refactored_v2.py - Review phase assertions
"""
from playwright.sync_api import Page, expect
from utils.allure_helpers import assert_visible
from typing import Dict, Any


class ReviewSummaryValidations:
    """Validation methods for request review and summary page"""

    def __init__(self, page: Page):
        self.page = page

    def _build_amount_display_candidates(self, test_data: Dict[str, Any], calculated_amount: str = None) -> list[str]:
        candidates: list[str] = []

        expected_display = test_data.get("expectedResults", {}).get("amountDisplay")
        transaction = test_data.get("transactionDetails", {})
        raw_amount = transaction.get("amount")
        formatted_amount = transaction.get("amountFormatted")
        distribution_type = transaction.get("distributionType", "")

        if expected_display:
            candidates.append(str(expected_display).strip())

        if formatted_amount:
            normalized_formatted = str(formatted_amount).strip()
            candidates.append(normalized_formatted)
            if distribution_type == "Journal Portion of Account":
                candidates.append(f"Portion of Account | {normalized_formatted}")

        if raw_amount not in (None, ""):
            raw_amount_text = str(raw_amount).strip()
            candidates.append(raw_amount_text)
            if distribution_type == "Journal Portion of Account":
                candidates.append(f"Portion of Account | {raw_amount_text}")

            try:
                normalized_numeric = f"{float(raw_amount_text):,.2f}"
                candidates.append(normalized_numeric)
                candidates.append(f"${normalized_numeric}")
                if distribution_type == "Journal Portion of Account":
                    candidates.append(f"Portion of Account | {normalized_numeric}")
                    candidates.append(f"Portion of Account | ${normalized_numeric}")
            except ValueError:
                pass

        if calculated_amount:
            normalized_calculated = f"${float(calculated_amount):,.2f}"
            candidates.append(normalized_calculated)
            if distribution_type == "Journal Portion of Account":
                candidates.append(f"Portion of Account | {normalized_calculated}")

        deduped_candidates = []
        for candidate in candidates:
            if candidate and candidate not in deduped_candidates:
                deduped_candidates.append(candidate)

        return deduped_candidates

    def validate_request_summary_page_loaded(self, test_data: Dict[str, Any]) -> None:
        """
        Validate request summary page has loaded correctly with all headers
        Extracted assertions from Step 9 of original test
        """
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["uiText"]["requestSummary"]),
            "Request summary heading visible"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["uiText"]["requestTypeLabel"]),
            "Request type label visible"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["uiText"]["journalText"], exact=True).first,
            "Journal text visible"
        )

    def validate_account_summary_details(self, test_data: Dict[str, Any]) -> None:
        """
        Validate account information is correctly displayed in summary
        Extracted from Step 9 account validation
        """
        # Source account validation
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["sourceAccountNumber"]), 
            f"source account number '{test_data['accounts']['sourceAccountNumber']}' on request summary page"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["sourceAccountName"]).first, 
            f"source account name '{test_data['accounts']['sourceAccountName']}' on request summary page"
        )
        
        # Destination account validation
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["destinationAccountNumber"]).last, 
            f"destination account number '{test_data['accounts']['destinationAccountNumber']}' on request summary page"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["destinationAccountName"]).last, 
            f"destination account name '{test_data['accounts']['destinationAccountName']}' on request summary page"
        )

    def validate_transfer_amount_display(self, test_data: Dict[str, Any], calculated_amount: str = None) -> None:
        """
        Validate transfer amount is displayed correctly based on type
        Extracted from Step 9 amount validation with branching logic
        """
        candidates = self._build_amount_display_candidates(test_data, calculated_amount)

        for candidate in candidates:
            locator = self.page.get_by_text(candidate, exact=True).first
            try:
                expect(locator).to_be_visible(timeout=1500)
                return
            except Exception:
                continue

        if candidates:
            assert_visible(
                self.page,
                self.page.get_by_text(candidates[0], exact=True).first,
                f"Amount display visible (checked: {', '.join(candidates)})"
            )

    def validate_restricted_cash_display(self, test_data: Dict[str, Any]) -> None:
        """
        Validate restricted cash information is displayed
        Extracted from Step 10 restricted cash validation
        """
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["uiText"]["restrictedCash"]), 
            f"restricted cash '{test_data['uiText']['restrictedCash']}' on summary page"
        )

    def validate_esignature_details(self, test_data: Dict[str, Any]) -> None:
        """
        Validate e-signature details when electronic signature is selected
        Extracted from Step 8b and Step 9 e-signature validation
        """
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["eSignature"]["subHeading"]),
            f"'{test_data['eSignature']['subHeading']}' sub-heading on summary"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["eSignature"]["email"]),
            f"e-Signature email '{test_data['eSignature']['email']}' on summary"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["eSignature"]["phone"]),
            f"e-Signature phone '{test_data['eSignature']['phone']}' on summary"
        )

    def validate_review_summary_buttons(self, test_data: Dict[str, Any]) -> None:
        """
        Validate all expected buttons are visible on review summary page
        Extracted from Step 10 button validations
        """
        for button in test_data["uiText"]["journalReviewSummaryPageButtons"]:
            assert_visible(
                self.page, 
                self.page.get_by_text(button),
                f"'{button}' button visible on journal review summary page"
            )