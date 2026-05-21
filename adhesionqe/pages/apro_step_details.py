"""APro Proposal Details step (wizard-0)."""

from typing import Union

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalDetailsPage(BasePage):
    """Page object for APro proposal Details step (wizard-0).

    Handles all client details entry: name, email, address, investment amount,
    account type selection, custodian selection, and advisor selection.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 1 (Details) container
        self.step_details_panel: Locator = page.locator("#proposal-wizard-0")

        # Client detail input fields
        self.name_input: Locator = page.locator("#Name")
        self.email_input: Locator = page.locator("#Email")
        self.address_input: Locator = page.locator("#Address")
        self.city_input: Locator = page.locator("#City")
        self.state_input: Locator = page.locator("#State")
        self.zip_input: Locator = page.locator("#Zip")

        # Account information inputs
        self.account_name_input: Locator = page.locator("#AccountName")
        self.account_number_input: Locator = page.locator("#AccountNumber")
        self.investment_amount_input: Locator = page.locator("#InvestmentAmount")

        # Dropdown selectors (Kendo wrappers)
        self.account_type_dropdown: Locator = page.locator(
            'span.k-dropdownlist[aria-controls="AccountTypeID_listbox"]'
        )
        self.custodian_dropdown: Locator = page.locator(
            'span.k-dropdownlist[aria-controls="CustodianID_listbox"]'
        )
        self.advisor_dropdown: Locator = page.locator(
            'span.k-dropdownlist[aria-controls="AdvisorID_listbox"]'
        )

    def wait_for_details_step(self, timeout: int = 10000) -> None:
        """Wait for the Details step (proposal-wizard-0) to be visible."""
        logger.info("Waiting for Details step to be visible")
        self.wait_for_element(self.step_details_panel, state="visible", timeout=timeout)

    def set_client_name(self, name: str) -> None:
        """Set the client name field."""
        logger.info(f"Setting client name: {name}")
        self.fill(self.name_input, name)

    def set_proposal_email(self, email: str) -> None:
        """Set the proposal email field."""
        logger.info(f"Setting proposal email: {email}")
        self.fill(self.email_input, email)

    def set_name_extended(self, value: str) -> None:
        """Set the extended/full name field."""
        logger.info(f"Setting name extended: {value}")
        self.fill(self.name_extended_input, value)  # type: ignore[attr-defined]

    def set_address(self, value: str) -> None:
        """Set the address field."""
        logger.info(f"Setting address: {value}")
        self.fill(self.address_input, value)

    def set_city(self, value: str) -> None:
        """Set the city field."""
        logger.info(f"Setting city: {value}")
        self.fill(self.city_input, value)

    def set_zip(self, value: str) -> None:
        """Set the ZIP code field."""
        logger.info(f"Setting ZIP: {value}")
        self.fill(self.zip_input, value)

    def set_account_name(self, value: str) -> None:
        """Set the account name field."""
        logger.info(f"Setting account name: {value}")
        self.fill(self.account_name_input, value)

    def set_account_number(self, value: str) -> None:
        """Set the account number field."""
        logger.info(f"Setting account number: {value}")
        self.fill(self.account_number_input, value)

    def set_investment_amount(self, value: Union[str, float, int]) -> None:
        """Set the investment amount field.

        Accepts int, float, or string. Automatically formats floats as
        "1000000.00" before filling.
        """
        if isinstance(value, (int, float)):
            value = f"{value:,.2f}"
        logger.info(f"Setting investment amount: {value}")
        self.empty_field(self.investment_amount_input)
        self.fill(self.investment_amount_input, str(value))

    def set_account_type(self, value: str | None = None) -> None:
        """Set the account type dropdown.

        Args:
            value: Account type value (e.g., "401K"). If None, uses defaults.
        """
        if value is None:
            value = "401K"  # Default
        logger.info(f"Setting account type: {value}")
        self.set_dropdown_value("AccountTypeID", value)

    def set_custodian(self, value: str | None = None) -> None:
        """Set the custodian dropdown.

        Args:
            value: Custodian value (e.g., "Pershing"). If None, uses defaults.
        """
        if value is None:
            value = "Pershing"  # Default
        logger.info(f"Setting custodian: {value}")
        self.set_dropdown_value("CustodianID", value)

    def set_advisor(self, value: str) -> None:
        """Set the advisor dropdown."""
        logger.info(f"Setting advisor: {value}")
        self.set_dropdown_value("AdvisorID", value)

    def set_dropdown_value(self, field_id: str, value: str, timeout: int = 8000) -> None:
        """Generic dropdown value setter using Kendo API.

        Args:
            field_id: The backing input element ID (e.g., "AccountTypeID")
            value: The option text to select
            timeout: Max wait time in ms
        """
        logger.info(f"Setting {field_id} dropdown to: {value}")

        try:
            js_code = f"""
                (function() {{
                    var dd = $('#{field_id}').data('kendoDropDownList');
                    if (!dd) {{ throw new Error('Dropdown not found: {field_id}'); }}

                    // Find the li element by matching text
                    var targetLi = $(dd.ul).find('li').filter(function() {{
                        return $(this).text().trim() === '{value}'.trim();
                    }}).first();

                    if (targetLi.length === 0) {{
                        // Log available options for debugging
                        var available = [];
                        $(dd.ul).find('li').each(function() {{
                            available.push($(this).text().trim());
                        }});
                        throw new Error('Could not find option "' + '{value}' + '". Available: ' + available.join(', '));
                    }}

                    // Select using the li element directly
                    dd.select(targetLi);
                    dd.trigger('change');

                    return {{ success: true, value: dd.value(), text: dd.text() }};
                }})()
            """
            result = self.page.evaluate(js_code)

            if result.get("success"):
                logger.info(f"Successfully set {field_id} to: {result.get('text')}")
            else:
                raise ValueError(f"Failed to set {field_id}")

            # Brief wait to let change handlers process
            self.page.wait_for_timeout(300)
        except Exception as exc:
            logger.error(f"Failed to set {field_id} via Kendo API: {exc}")
            raise

    def get_advisor_dropdown_value(self) -> str:
        """Get the currently selected advisor from the dropdown.

        Returns:
            The selected advisor text
        """
        logger.info("Retrieving advisor dropdown value")

        value = self.page.evaluate(
            """
            (function() {
                var dd = $('#AdvisorID').data('kendoDropDownList');
                if (!dd) { throw new Error('Advisor dropdown not found'); }
                return dd.text();
            })()
            """
        )
        logger.info(f"Retrieved advisor: {value}")
        return value

    def click_next(self) -> None:
        """Click Next button to proceed to Risk Assessment step."""
        logger.info("Clicking Next from Details step")
        next_button = self.step_details_panel.locator("button[data-wizard-next]")

        # Wait for the button to not be disabled
        self.page.locator("#proposal-wizard-0 button[data-wizard-next]:not([disabled])").wait_for(
            state="visible", timeout=10000
        )

        # Give the form validation a moment to settle
        self.page.wait_for_timeout(1000)

        # Force click to bypass any actionability checks
        next_button.click(force=True)

    def click_previous(self) -> None:
        """Click Previous button (if available on Details step)."""
        logger.info("Clicking Previous from Details step")
        prev_button = self.step_details_panel.locator("button[data-wizard-previous]")
        prev_button.click()
