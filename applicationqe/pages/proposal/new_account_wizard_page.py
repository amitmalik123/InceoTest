"""
New Account Wizard Page Object Model for Proposals application.
Handles the account creation wizard flow with client profiles, risk profiles, and investment selection.
"""

import logging
import random
from typing import Dict, List

from playwright.sync_api import Locator, Page

from ..base_page import BasePage

logger = logging.getLogger(__name__)


class NewAccountWizardPage(BasePage):
    """Page object for the New Account Wizard workflow."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.form_root = self.active_root()

        # Dropdowns
        self.agent_dropdown: Locator = self.form_root.locator("#ctl00_cphContentArea_ddlAgentID")
        self.client_type_dropdown: Locator = self.form_root.locator("#ctl00_cphContentArea_ddlClientType")
        self.registration_type_dropdown: Locator = self.form_root.locator(
            "#registration_container #registration_type_dropdown"
        )
        self.select_custodian_dropdown: Locator = self.form_root.locator("#registration_custodian")
        self.account_type_dropdown: Locator = self.form_root.locator(
            "#account_type_partial_container #account_type_dropdown"
        )

        # Textboxes
        self.first_name_input: Locator = self.form_root.locator("#ctl00_cphContentArea_txtFirstName")
        self.last_name_input: Locator = self.form_root.locator("#ctl00_cphContentArea_txtLastName")
        self.registration_name_input: Locator = self.form_root.locator("#registrationName")
        self.investment_amount_input: Locator = self.form_root.locator("#AccountSectionInvestmentAmount")
        self.adv_flat_fee_input: Locator = self.form_root.locator("#advFlatFee")
        self.percent_labels_inputs: Locator = self.form_root.locator('input[name="percentsLabels"]')

        # Fiduciary radios
        self.fiduciary_radios: Locator = self.form_root.locator('[role="radiogroup"]')
        self.fiduciary_discretionary: Locator = self.form_root.locator("#ctl00_cphContentArea_radlstFuduciaryRole_0")
        self.fiduciary_non_discretionary: Locator = self.form_root.locator("#ctl00_cphContentArea_radlstFuduciaryRole_1")

        # Risk return profile radios
        self.conservative_risk_return_radio: Locator = self.form_root.get_by_label("1-Conservative")
        self.moderate_conservative_risk_return_radio: Locator = self.form_root.get_by_label("2-Moderate Conservative")
        self.moderate_risk_return_radio: Locator = self.form_root.get_by_label("3-Moderate")
        self.moderate_growth_risk_return_radio: Locator = self.form_root.get_by_label("4-Moderate Growth")
        self.growth_risk_return_radio: Locator = self.form_root.get_by_label("5-Growth")
        self.maximum_growth_risk_return_radio: Locator = self.form_root.get_by_label("6-Maximum Growth")

        # Risk Assessment radios
        self.low_risk_radio: Locator = self.form_root.locator('[id="336"]')
        self.moderate_risk_radio: Locator = self.form_root.locator('[id="337"]')
        self.high_risk_radio: Locator = self.form_root.locator('[id="338"]')
        self.very_high_risk_radio: Locator = self.form_root.locator('[id="339"]')
        self.two_years_or_less_radio: Locator = self.form_root.locator('[id="340"]')
        self.three_to_five_years_radio: Locator = self.form_root.locator('[id="341"]')
        self.six_to_nine_years_radio: Locator = self.form_root.locator('[id="342"]')
        self.ten_years_plus_radio: Locator = self.form_root.locator('[id="343"]')
        self.over_75_percent_radio: Locator = self.form_root.locator('[id="344"]')
        self.fifty_to_75_percent_radio: Locator = self.form_root.locator('[id="345"]')
        self.twenty_five_to_50_percent_radio: Locator = self.form_root.locator('[id="346"]')
        self.less_than_25_percent_radio: Locator = self.form_root.locator('[id="347"]')

        # Links & Buttons
        self.risk_tolerance_questionnaire_link: Locator = self.form_root.get_by_role(
            "link", name="Risk Tolerance Questionnaire"
        )
        self.back_button: Locator = self.form_root.get_by_role("button", name="Back")
        self.next_button: Locator = self.form_root.get_by_role("button", name="Next")
        self.confirm_button: Locator = self.form_root.get_by_role("button", name="Confirm")
        self.tms_options_no: Locator = self.form_root.locator("#tmsOptionsNo")
        self.tms_options_yes: Locator = self.form_root.locator("#tmsOptionsYes")
        self.review_button: Locator = self.form_root.get_by_role("button", name="Review")
        self.add_investment_button: Locator = self.form_root.get_by_role("button", name="Add Investment")

        # Strategy rows - use text-based selectors instead of ID-based
        # These match investment rows by their strategy name text
        # Exclude hidden rows by using :not(.hidden) selector
        self.core_strategy_row: Locator = self.form_root.locator(
            'tr:not(.hidden), [class*="strategy-row"]:not(.hidden), [class*="investment-row"]:not(.hidden)'
        ).filter(has_text="AssetMark Income Builder")
        
        self.tactical_enhanced_strategy_row: Locator = self.form_root.locator(
            'tr:not(.hidden), [class*="strategy-row"]:not(.hidden), [class*="investment-row"]:not(.hidden)'
        ).filter(has_text="BlackRock")
        
        self.tactical_limit_strategy_row: Locator = self.form_root.locator(
            'tr:not(.hidden), [class*="strategy-row"]:not(.hidden), [class*="investment-row"]:not(.hidden)'
        ).filter(has_text="Savos US Risk")
        
        self.diversifying_equity_strategy_row: Locator = self.form_root.locator(
            'tr:not(.hidden), [class*="strategy-row"]:not(.hidden), [class*="investment-row"]:not(.hidden)'
        ).filter(has_text="AIM Decathlon")
        
        self.diversifying_bond_strategy_row: Locator = self.form_root.locator(
            'tr:not(.hidden), [class*="strategy-row"]:not(.hidden), [class*="investment-row"]:not(.hidden)'
        ).filter(has_text="JPMorgan")

        # Portfolio summary widget
        self.asset_allocation_summary_widget: Locator = self.form_root.locator("#asset-allocation-summary-widget")
        self.core_markets_section: Locator = self.asset_allocation_summary_widget.locator(
            '.asset-class:has(span:has-text("Core Markets"))'
        )
        self.tac_enhanced_section: Locator = self.asset_allocation_summary_widget.locator(
            '.asset-class:has-text("Enhanced Return Focus")'
        )
        self.tac_limit_section: Locator = self.asset_allocation_summary_widget.locator(
            '.asset-class:has-text("Limit Loss Focus")'
        )
        self.div_equity_section: Locator = self.asset_allocation_summary_widget.locator(
            '.asset-class:has-text("Equity Alternatives")'
        )
        self.div_bonds_section: Locator = self.asset_allocation_summary_widget.locator(
            '.asset-class:has-text("Bonds")'
        )
        self.additional_investments_section: Locator = self.asset_allocation_summary_widget.locator(
            '.asset-class:has-text("Additional Investments")'
        )

        # Portfolio fee summary table
        self.portfolio_fee_summary_table: Locator = self.form_root.locator("#feeSummaryTable .portfolioFeeSummaryTbl")
        self.financial_advisor_fee_row: Locator = self.portfolio_fee_summary_table.locator(
            'tr:has(td:has-text("Financial Advisor"))'
        )
        self.platform_fee_row: Locator = self.portfolio_fee_summary_table.locator('tr:has(td:has-text("Platform"))')
        self.tax_management_services_fee_row: Locator = self.portfolio_fee_summary_table.locator(
            'tr:has(td:has-text("Tax Management Services"))'
        )
        self.portfolio_total_value_row: Locator = self.portfolio_fee_summary_table.locator(
            "tr:has(td.portfolioFeeTotalData)"
        )
        self.total_fee_row: Locator = self.portfolio_fee_summary_table.locator(
            'tr:has(td.portfolioAnnualColumnLabel:has-text("Total"))'
        )

        # Account Wizard - Modify existing client account search elements
        self.account_wizard_search_input: Locator = self.form_root.locator("#ctl00_cphContentArea_txtSearch")
        self.account_wizard_search_go_button: Locator = self.form_root.locator("#ctl00_cphContentArea_btnSearch")
        self.client_table: Locator = self.form_root.locator("#tblTemplate")
        self.client_table_rows: Locator = self.form_root.locator("#tblTemplate tbody tr")
        self.account_wizard_total_client_counter: Locator = self.form_root.locator("#ctl00_cphContentArea_LblTotalClient")
        self.delete_client_link: Locator = self.form_root.locator("#ctl00_cphContentArea_lnkDeleteClient")
        self.delete_confirmation_message: Locator = self.form_root.get_by_text("There are two ways to get started")

    def select_registration_type(self, registration_type: str) -> None:
        """
        Select a registration type from the multilevel dropdown.

        Args:
            registration_type: The specific registration type to select (e.g., 'Individual', 'Traditional IRA')

        Raises:
            Error: If registration type is not found in the category map.
        """
        # Map of registration types to their parent categories
        category_map: Dict[str, str] = {
            "Individual": "Individual",
            "Individual TOD": "Individual",
            "Trust": "Trust",
            "Community Property": "Joint",
            "Community Property with Rights of Survivorship": "Joint",
            "Community Property with Rights of Survivorship TOD": "Joint",
            "Joint Tenant with Rights of Survivorship": "Joint",
            "Joint Tenant with Rights of Survivorship TOD": "Joint",
            "Tenants in Common": "Joint",
            "Tenants by Entirety": "Joint",
            "Tenants by Entirety TOD": "Joint",
            "Traditional IRA": "IRAs",
            "Rollover IRA": "IRAs",
            "Roth IRA": "IRAs",
            "SEP-IRA": "IRAs",
            "Simple IRA": "IRAs",
            "Beneficiary IRA Individual": "IRAs",
            "Beneficiary Roth IRA Individual": "IRAs",
            "Beneficiary IRA Trust": "IRAs",
            "Beneficiary Roth IRA Trust": "IRAs",
            "401(k)": "RetirementPlans",
            "Individual 401(k)": "RetirementPlans",
            "403(b) Plan": "RetirementPlans",
            "Defined Benefit Pension Plan": "RetirementPlans",
            "Money Purchase Pension Plan": "RetirementPlans",
            "Profit Sharing Plan": "RetirementPlans",
            "Self-Directed Brokerage Account": "RetirementPlans",
            "Self-Directed Brokerage Account - 403(b)": "RetirementPlans",
            "Corporation": "BusinessAccounts",
            "Limited Liability Company": "BusinessAccounts",
            "Partnership": "BusinessAccounts",
            "Sole Proprietor": "BusinessAccounts",
            "Sub-Custodian FBO": "BusinessAccounts",
            "501(c)": "Organizations",
            "Endowment (Non-Taxable)": "Organizations",
            "Endowment (Taxable)": "Organizations",
            "Foundation (Non-Taxable)": "Organizations",
            "Foundation (Taxable)": "Organizations",
            "Uniform Gift to Minors": "Other",
            "Uniform Transfer to Minors": "Other",
            "Guardianship": "Other",
            "Estate": "Other",
        }

        category = category_map.get(registration_type)
        if not category:
            raise ValueError(f"Registration type '{registration_type}' not found in category map")

        # Click the main dropdown to open it
        self.registration_type_dropdown.click()

        # Hover the parent category to expand it
        parent_category = self.registration_type_dropdown.locator(
            f'dt.groupedmenu a[data-group-name="{category}"]'
        )
        parent_category.hover()

        # Click the specific nested option
        nested_option = self.registration_type_dropdown.locator(f'ul#{category} li[data-name="{registration_type}"]')
        nested_option.click()

    def select_custodian(self) -> None:
        """Select a random custodian from the dropdown."""
        dropdown_trigger = self.select_custodian_dropdown.locator("dt.firstmenu a")
        option_selector = "#registration_custodian dd dl dd a"
        options = self.select_custodian_dropdown.locator("dd dl dd a")

        # Wait for the dropdown container to exist and be visible
        self.select_custodian_dropdown.wait_for(state="visible")

        # Wait for option elements to be present in the iframe DOM
        self.form_root.locator(option_selector).first.wait_for(state="attached", timeout=30000)

        # Open the dropdown and wait for the options to become visible (retry if handler not ready)
        dropdown_trigger.click()
        try:
            options.first.wait_for(state="visible", timeout=5000)
        except Exception:
            dropdown_trigger.click()
            options.first.wait_for(state="visible", timeout=10000)

        # Get count and select random option
        count = options.count()
        random_index = random.randint(0, count - 1)
        options.nth(random_index).click()

    def select_account_type(self, account_type: str) -> None:
        """
        Select an account type from the multilevel dropdown.

        Args:
            account_type: The account type to select (e.g., 'GPS Fund Strategies')

        Raises:
            Error: If account type option is not found.
        """
        dropdown_trigger = self.account_type_dropdown.locator("dt.firstmenu a")
        option_selector = "#account_type_partial_container #account_type_dropdown dd a"
        options = self.account_type_dropdown.locator("dd a")

        # Wait for the dropdown container to exist
        self.account_type_dropdown.wait_for(state="visible")

        # Wait for option elements to appear in the iframe DOM
        self.form_root.locator(option_selector).first.wait_for(state="attached", timeout=30000)

        # Open the dropdown and wait for options to be visible (retry if handler not ready)
        dropdown_trigger.click()
        try:
            options.first.wait_for(state="visible", timeout=5000)
        except Exception:
            dropdown_trigger.click()
            options.first.wait_for(state="visible", timeout=10000)

        # Find the matching option and click it
        option = self.account_type_dropdown.locator("dd a").filter(has_text=account_type)
        if option.count() == 0:
            raise ValueError(f'Account type option with text "{account_type}" not found')
        option.first.click()

    def fill_registration_name(self, name: str) -> None:
        """
        Fill the registration name field.

        Args:
            name: The registration name to enter.
        """
        self.registration_name_input.fill(name)

    def fill_investment_amount(self, amount: str) -> None:
        """
        Fill the investment amount field.

        Args:
            amount: The investment amount.
        """
        self.investment_amount_input.fill(amount)

    def fill_name(self, first: str, last: str) -> None:
        """
        Fill the client name fields.

        Args:
            first: First name.
            last: Last name.
        """
        self.first_name_input.fill(first)
        self.last_name_input.fill(last)

    def add_strategy(self, strategy_name: str) -> None:
        """
        Add a strategy to the account by searching and selecting it.

        Args:
            strategy_name: The name of the strategy to search for and add.
        """
        # Click the Add Investment button
        self.add_investment_button.wait_for(state="visible", timeout=10000)
        self.add_investment_button.click()

        # Fill in the search field and press Enter
        search_box = (
            self.form_root.get_by_role("textbox", name="Search solution type or")
            .or_(self.form_root.get_by_placeholder("Search solution type or"))
        )
        search_box.wait_for(state="visible", timeout=10000)
        search_box.fill(strategy_name)
        search_box.press("Enter")

        # Click the first matching result cell
        result_cell = self.form_root.get_by_role("cell", name=strategy_name)
        result_cell.click()
        self.form_root.get_by_role("button", name="Ok").click()

        # Move mouse slowly across screen to re-enable the add investments button
        bounding_box = self.add_investment_button.bounding_box()
        if bounding_box:
            target_x = bounding_box["x"] + bounding_box["width"] / 2
            target_y = bounding_box["y"] + bounding_box["height"] / 2

            # Move from top-left to the button gradually
            start_x = 0
            start_y = 0
            steps = 40

            for i in range(steps + 1):
                progress = i / steps
                current_x = start_x + (target_x - start_x) * progress
                current_y = start_y + (target_y - start_y) * progress
                self.page.mouse.move(current_x, current_y)
                self.page.wait_for_timeout(25)

    def search_for_client_in_account_wizard(self, client_name: str) -> None:
        """
        Search for a client in the Account Wizard "Modify an existing client account" section.
        The client_name must be in "LastName, FirstName" format.
        The table updates immediately with matching clients.
        """
        # Clear the field first (triple-click to select all, then delete)
        self.account_wizard_search_input.click()
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Delete")
        
        # Fill with the client name
        self.account_wizard_search_input.fill(client_name)
        
        # Click search button
        self.account_wizard_search_go_button.click()
        
        # On navbar, the Go button triggers an ASP.NET postback inside the iframe.
        # page.wait_for_load_state("networkidle") only watches the outer page and returns
        # immediately — the iframe reload is invisible to it.
        # Instead, bracket the postback by waiting for the counter to disappear (reload
        # started) then reappear (reload complete). Both waits are scoped to form_root
        # so they correctly observe the iframe content.
        try:
            self.account_wizard_total_client_counter.wait_for(state="hidden", timeout=3000)
        except Exception:
            pass  # Postback may have already completed before we get here
        self.account_wizard_total_client_counter.wait_for(state="visible", timeout=15000)
        
        logger.debug(f"Searched for client: {client_name}")

    def get_first_client_row(self) -> Locator:
        """
        Get the first data row (not header) from the search results table.
        Uses :has(a) selector to only match rows with clickable links.
        """
        return self.form_root.locator("#tblTemplate tbody tr:has(a)").first

    def get_total_clients_count(self) -> int:
        """
        Get the total number of clients from the counter ("Total Clients - N" or "Total Clients = N").
        Handles both `-` and `=` delimiters.
        Waits up to 5 seconds for the counter to appear after a search.
        Returns 0 if the counter is not present (no results found).
        """
        import re
        try:
            # Use direct locator to the counter element
            self.account_wizard_total_client_counter.wait_for(state="visible", timeout=5000)
            counter_text = self.account_wizard_total_client_counter.text_content()
            if counter_text:
                # Split on either - or = and take last element
                parts = re.split(r"[-=]", counter_text)
                count_str = parts[-1].strip()
                return int(count_str)
        except Exception as e:
            logger.debug(f"Error reading client counter: {e}")
        return 0

    def delete_client_from_account_wizard(self) -> None:
        """
        Delete the currently selected client from the Account Wizard.
        Accepts the JavaScript confirmation dialog and waits for redirect
        back to the Account Wizard list page.
        On legacy: waits for outer page URL to match AccountWizard.aspx.
        On navbar: outer URL stays at /clients/manage-accounts so wait for
        the iframe content to reload instead.
        """
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.delete_client_link.click()
        # Try the outer-page URL wait (works for legacy direct navigation)
        try:
            self.page.wait_for_url("**/AccountWizard.aspx", timeout=5000)
        except Exception:
            # Navbar: outer URL stays constant — wait for iframe content to settle
            self.page.wait_for_load_state("networkidle", timeout=10000)
        logger.debug("Client deleted and redirected back to Account Wizard")
