"""
Validations for Transaction Details Configuration page
Extracted from test_journal_transfer_refactored_v2.py - Transaction phase assertions
"""
from playwright.sync_api import Page, expect
from utils.allure_helpers import assert_visible
from typing import Dict, Any


class TransactionDetailsValidations:
    """Validation methods for transaction details configuration"""

    def __init__(self, page: Page):
        self.page = page

    def validate_transaction_page_loaded(self, test_data: Dict[str, Any]) -> None:
        """
        Validate transaction details page has loaded with all required elements
        Extracted assertions from Step 4 of original test
        """
        # Verify account information is carried over from previous page
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["sourceAccountNumber"]), 
            f"source account number '{test_data['accounts']['sourceAccountNumber']}' on transaction page"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["sourceAccountName"]).first, 
            f"source account name '{test_data['accounts']['sourceAccountName']}' on transaction page"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["destinationAccountNumber"]).last, 
            f"destination account number '{test_data['accounts']['destinationAccountNumber']}' on transaction page"
        )
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["accounts"]["destinationAccountName"]).last, 
            f"destination account name '{test_data['accounts']['destinationAccountName']}' on transaction page"
        )

    def validate_distribution_options_visible(self, test_data: Dict[str, Any]) -> None:
        """
        Validate all distribution type options are visible and accessible
        Extracted from Step 4 distribution options validation
        """
        for option in test_data["uiText"]["distributionsOptions"]:
            assert_visible(
                self.page, 
                self.page.get_by_text(option),
                f"'{option}' option visible on journal transaction page"
            )

    def validate_signature_options_visible(self, test_data: Dict[str, Any]) -> None:
        """
        Validate all signature options are visible and accessible
        Extracted from Step 4 signature options validation
        """
        for option in test_data["uiText"]["signatureOptions"]:
            assert_visible(
                self.page, 
                self.page.get_by_text(option),
                f"'{option}' option visible on journal transaction page"
            )

    def validate_transaction_page_buttons(self, test_data: Dict[str, Any]) -> None:
        """
        Validate transaction page buttons are visible
        Extracted from Step 4 button validations
        """
        for button in test_data["uiText"]["journalTransactionPageButtons"]:
            assert_visible(
                self.page, 
                self.page.get_by_text(button),
                f"'{button}' button visible on journal transaction page"
            )

    def validate_amount_input_visible(self) -> None:
        """
        Validate amount input textbox is visible for portion transfers
        Extracted from Step 6 amount input validation
        """
        assert_visible(
            self.page, 
            self.page.get_by_role("textbox"), 
            "Amount textbox visible"
        )

    def validate_portion_warning_displayed(self, test_data: Dict[str, Any]) -> None:
        """
        Validate journal portion warning is displayed when amount exceeds available cash
        Extracted from Step 6 warning validation
        """
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["uiText"]["journalPortionWarning"]),
            "Journal portion warning displayed"
        )

    def validate_approximate_percentage_calculated(self, test_data: Dict[str, Any]) -> None:
        """
        Validate approximate percentage is calculated and displayed
        Extracted from Step 6 percentage calculation validation
        """
        assert_visible(
            self.page, 
            self.page.get_by_text(test_data["uiText"]["approxText"]),
            "Amount entered and approx percentage calculated"
        )

    def validate_securities_all_button_visible(self) -> None:
        """
        Validate 'All' button is visible for securities selection
        Extracted from Step 6 securities selection validation
        """
        assert_visible(
            self.page, 
            self.page.get_by_role("button", name="All").first,
            "Securities 'All' button visible"
        )