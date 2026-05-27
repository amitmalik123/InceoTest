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

        # Dropdowns
        self.agent_dropdown: Locator = page.locator("#ctl00_cphContentArea_ddlAgentID")
        self.client_type_dropdown: Locator = page.locator("#ctl00_cphContentArea_ddlClientType")
        self.registration_type_dropdown: Locator = page.locator(
            "#registration_container #registration_type_dropdown"
        )
        self.select_custodian_dropdown: Locator = page.locator("#registration_custodian")
        self.account_type_dropdown: Locator = page.locator(
            "#account_type_partial_container #account_type_dropdown"
        )

        # Textboxes
        self.first_name_input: Locator = page.locator("#ctl00_cphContentArea_txtFirstName")
        self.last_name_input: Locator = page.locator("#ctl00_cphContentArea_txtLastName")
        self.registration_name_input: Locator = page.locator("#registrationName")
        self.investment_amount_input: Locator = page.locator("#AccountSectionInvestmentAmount")
        self.adv_flat_fee_input: Locator = page.locator("#advFlatFee")
        self.percent_labels_inputs: Locator = page.locator('input[name="percentsLabels"]')

        # Fiduciary radios
        self.fiduciary_radios: Locator = page.locator('[role="radiogroup"]')
        self.fiduciary_discretionary: Locator = page.get_by_role("cell", name="Discretionary", exact=True)
        self.fiduciary_non_discretionary: Locator = page.get_by_role("cell", name="Non-Discretionary", exact=True)

        # Risk return profile radios
        self.conservative_risk_return_radio: Locator = page.get_by_label("1-Conservative")
        self.moderate_conservative_risk_return_radio: Locator = page.get_by_label("2-Moderate Conservative")
        self.moderate_risk_return_radio: Locator = page.get_by_label("3-Moderate")
        self.moderate_growth_risk_return_radio: Locator = page.get_by_label("4-Moderate Growth")
        self.growth_risk_return_radio: Locator = page.get_by_label("5-Growth")
        self.maximum_growth_risk_return_radio: Locator = page.get_by_label("6-Maximum Growth")

        # Risk Assessment radios
        self.low_risk_radio: Locator = page.locator('[id="336"]')
        self.moderate_risk_radio: Locator = page.locator('[id="337"]')
        self.high_risk_radio: Locator = page.locator('[id="338"]')
        self.very_high_risk_radio: Locator = page.locator('[id="339"]')
        self.two_years_or_less_radio: Locator = page.locator('[id="340"]')
        self.three_to_five_years_radio: Locator = page.locator('[id="341"]')
        self.six_to_nine_years_radio: Locator = page.locator('[id="342"]')
        self.ten_years_plus_radio: Locator = page.locator('[id="343"]')
        self.over_75_percent_radio: Locator = page.locator('[id="344"]')
        self.fifty_to_75_percent_radio: Locator = page.locator('[id="345"]')
        self.twenty_five_to_50_percent_radio: Locator = page.locator('[id="346"]')
        self.less_than_25_percent_radio: Locator = page.locator('[id="347"]')

        # Links & Buttons
        self.risk_tolerance_questionnaire_link: Locator = page.get_by_role(
            "link", name="Risk Tolerance Questionnaire"
        )
        self.back_button: Locator = page.get_by_role("button", name="Back")
        self.next_button: Locator = page.get_by_role("button", name="Next")
        self.confirm_button: Locator = page.get_by_role("button", name="Confirm")
        self.tms_options_no: Locator = page.locator("#tmsOptionsNo")
        self.tms_options_yes: Locator = page.locator("#tmsOptionsYes")
        self.review_button: Locator = page.get_by_role("button", name="Review")
        self.add_investment_button: Locator = page.get_by_role("button", name="Add Investment")

        # Strategy rows
        self.core_strategy_row: Locator = page.locator("#Core")
        self.tactical_enhanced_strategy_row: Locator = page.locator("#TacticalEnhanced")
        self.tactical_limit_strategy_row: Locator = page.locator("#TacticalLimit")
        self.diversifying_equity_strategy_row: Locator = page.locator("#DiversifyingEquity")
        self.diversifying_bond_strategy_row: Locator = page.locator("#DiversifyingBond")

        # Portfolio summary widget
        self.asset_allocation_summary_widget: Locator = page.locator("#asset-allocation-summary-widget")
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
        self.portfolio_fee_summary_table: Locator = page.locator("#feeSummaryTable .portfolioFeeSummaryTbl")
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

        # Wait for option elements to be present in the DOM
        self.page.wait_for_function(f'document.querySelectorAll("{option_selector}").length > 0')

        # Open the dropdown and wait for the options to become visible
        dropdown_trigger.click()
        options.first.wait_for(state="visible")

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

        # Wait for option elements to appear in the DOM
        self.page.wait_for_function(f'document.querySelectorAll("{option_selector}").length > 0')

        # Open the dropdown and wait for options to be visible
        dropdown_trigger.click()
        options.first.wait_for(state="visible")

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
        self.add_investment_button.click()
        self.page.wait_for_load_state("networkidle")

        # Fill in the search field and press Enter
        search_box = (
            self.page.get_by_role("textbox", name="Search solution type or")
            .or_(self.page.get_by_placeholder("Search solution type or"))
        )
        search_box.wait_for(state="visible", timeout=10000)
        search_box.fill(strategy_name)
        search_box.press("Enter")

        # Click the first matching result cell
        result_cell = self.page.get_by_role("cell", name=strategy_name)
        result_cell.click()
        self.page.get_by_role("button", name="Ok").click()

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
