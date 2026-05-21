"""
Step definitions for creating a proposal with a new client via the New Account Wizard.
Converts TypeScript: createProposalWithNewClient.ts
"""

import logging
import os
from pytest_bdd import when, then, parsers
from playwright.sync_api import Page, expect

from pages.PROPOSAL import (
    EwmPage,
    NewAccountWizardPage,
    PortfolioEnginePage,
    TaxManagementServicesPage,
)
from tests.steps.PROPOSAL.instance_manager import (
    get_new_account_wizard_instance,
    set_new_account_wizard_instance,
    get_ewm_page_instance,
    set_ewm_page_instance,
    set_portfolio_engine_instance,
    set_tax_mgmt_services_instance,
)
from utils.PROPOSAL.helper_functions import navigate_to_home_page

logger = logging.getLogger(__name__)


@when("I click on the Account Wizard link")
def click_account_wizard_link(page: Page):
    navigate_to_home_page(page)
    ewm_page = EwmPage(page)
    set_ewm_page_instance(ewm_page)
    ewm_page.open_account_wizard()
    expect(
        ewm_page.page.get_by_text("There are two ways to get started"),
    ).to_be_visible()


@when("I decide to create a new client")
def decide_create_new_client(page: Page):
    ewm_page = get_ewm_page_instance()
    ewm_page.create_new_client.click()
    ewm_page.page.wait_for_load_state()
    ewm_page.page.wait_for_timeout(1000)  # Wait for UI to fully render new client form


@when(parsers.parse('I complete the client profile with first name "{first_name}" and last name "{last_name}"'))
def complete_client_profile(page: Page, first_name: str, last_name: str):
    ewm_page = get_ewm_page_instance()
    new_account_wizard_page = NewAccountWizardPage(ewm_page.page)
    set_new_account_wizard_instance(new_account_wizard_page)
    
    expect(new_account_wizard_page.first_name_input).to_be_visible()
    expect(new_account_wizard_page.last_name_input).to_be_visible()
    expect(new_account_wizard_page.fiduciary_non_discretionary).to_be_visible()
    expect(new_account_wizard_page.fiduciary_discretionary).to_be_visible()
    expect(new_account_wizard_page.low_risk_radio).to_be_visible()
    expect(new_account_wizard_page.moderate_risk_radio).to_be_visible()
    expect(new_account_wizard_page.high_risk_radio).to_be_visible()
    expect(new_account_wizard_page.very_high_risk_radio).to_be_visible()
    expect(new_account_wizard_page.two_years_or_less_radio).to_be_visible()
    expect(new_account_wizard_page.six_to_nine_years_radio).to_be_visible()
    expect(new_account_wizard_page.twenty_five_to_50_percent_radio).to_be_visible()
    expect(new_account_wizard_page.growth_risk_return_radio).to_be_visible()
    expect(new_account_wizard_page.conservative_risk_return_radio).to_be_visible()
    expect(new_account_wizard_page.moderate_conservative_risk_return_radio).to_be_visible()
    expect(new_account_wizard_page.moderate_risk_return_radio).to_be_visible()
    expect(new_account_wizard_page.moderate_growth_risk_return_radio).to_be_visible()
    expect(new_account_wizard_page.growth_risk_return_radio).to_be_visible()
    expect(new_account_wizard_page.maximum_growth_risk_return_radio).to_be_visible()

    logger.debug("\nFilling out new client profile")

    if new_account_wizard_page.agent_dropdown.is_visible():
        new_account_wizard_page.agent_dropdown.click()
        new_account_wizard_page.agent_dropdown.select_option(os.getenv("userID"))
    
    new_account_wizard_page.fill_name(first_name, last_name)
    new_account_wizard_page.fiduciary_discretionary.click()
    new_account_wizard_page.high_risk_radio.click()
    new_account_wizard_page.six_to_nine_years_radio.click()
    new_account_wizard_page.twenty_five_to_50_percent_radio.click()
    new_account_wizard_page.growth_risk_return_radio.click()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for form to stabilize
    new_account_wizard_page.next_button.click()
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render


@when("I Complete the Construct Portfolio section")
def complete_construct_portfolio_section(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nFilling out Construct Portfolio section")
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for form to render
    new_account_wizard_page.select_registration_type("Individual")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for UI update
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.select_custodian()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for custodian to be selected
    new_account_wizard_page.fill_investment_amount("500000")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for amount input
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.select_account_type("Multiple Strategy Account")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for account type to be selected
    new_account_wizard_page.page.wait_for_load_state()


@when("I add all strategies to the account")
def add_all_strategies_to_account(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nAdding all strategies to the account")
    
    new_account_wizard_page.add_strategy("assetmark income builder, profile 2, conservative")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for strategy to be added
    new_account_wizard_page.add_strategy("blackrock equity dividend")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for strategy to be added
    new_account_wizard_page.add_strategy("alphasimplex, alternative model portfolio, profile 5, growth")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for strategy to be added
    new_account_wizard_page.add_strategy("jpmorgan absolute return - profile 1")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for strategy to be added
    new_account_wizard_page.add_strategy("savos us risk controlled strategy, profile 6")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for strategy to be added

    # Verify all strategies were added by checking for their respective rows and content
    expect(new_account_wizard_page.core_strategy_row).to_be_visible()
    expect(
        new_account_wizard_page.core_strategy_row.locator(
            "text=AssetMark Income Builder, Profile 2, Conservative, ETF"
        ),
    ).to_be_visible()

    expect(new_account_wizard_page.tactical_enhanced_strategy_row).to_be_visible()
    expect(
        new_account_wizard_page.tactical_enhanced_strategy_row.locator(
            "text=BlackRock Equity Dividend, IMA"
        ),
    ).to_be_visible()

    expect(new_account_wizard_page.diversifying_equity_strategy_row).to_be_visible()
    expect(
        new_account_wizard_page.diversifying_equity_strategy_row.locator(
            "text=AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth, MF"
        ),
    ).to_be_visible()

    expect(new_account_wizard_page.diversifying_bond_strategy_row).to_be_visible()
    expect(
        new_account_wizard_page.diversifying_bond_strategy_row.locator(
            "text=JPMorgan Absolute Return - Profile 1, MF"
        ),
    ).to_be_visible()

    expect(new_account_wizard_page.tactical_limit_strategy_row).to_be_visible()
    expect(
        new_account_wizard_page.tactical_limit_strategy_row.locator(
            "text=Savos US Risk Controlled Strategy, Profile 6, GMS"
        ),
    ).to_be_visible()


@when("I allocate equal percentages to all strategies")
def allocate_equal_percentages(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nAllocating equal percentages to all strategies")
    
    # Use the stable name attribute selector instead of hardcoded investment IDs
    percent_inputs = new_account_wizard_page.percent_labels_inputs
    count = percent_inputs.count()
    
    for i in range(count):
        percent_inputs.nth(i).fill("20")
        percent_inputs.nth(i).press("Enter")
        # Small delay to allow UI to process the input
        new_account_wizard_page.page.wait_for_timeout(500)

    new_account_wizard_page.page.wait_for_timeout(500)  # Wait before proceeding to review
    new_account_wizard_page.review_button.click()
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for investment summary to render


@when("I opt out of tax management services")
def opt_out_tms(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nOpting out of tax management services")
    new_account_wizard_page.tms_options_no.click()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for no selection to register
    new_account_wizard_page.confirm_button.click()
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to load


@when("I opt into tax management services")
def opt_into_tms(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nOpting into tax management services")
    new_account_wizard_page.tms_options_yes.click()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for yes selection to register
    new_account_wizard_page.confirm_button.click()
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for TMS page to fully load
    set_tax_mgmt_services_instance(
        TaxManagementServicesPage(new_account_wizard_page.page)
    )


@then("the investment summary should display correctly with all strategies and allocations")
def verify_investment_summary(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    
    # Verify asset allocation summary widget exists
    expect(new_account_wizard_page.asset_allocation_summary_widget).to_be_visible()

    # Verify Core Markets section with 20% and investment account
    expect(new_account_wizard_page.core_markets_section).to_be_visible()
    expect(
        new_account_wizard_page.core_markets_section.locator("text=20.00%").nth(0)
    ).to_be_visible()
    expect(
        new_account_wizard_page.core_markets_section.locator("text=20.00%").nth(1)
    ).to_be_visible()
    expect(
        new_account_wizard_page.core_markets_section.locator(
            "text=Multiple Strategy Account"
        ),
    ).to_be_visible()

    # Verify Tactical Strategies - Enhanced Return Focus section with 20% and investment account
    expect(new_account_wizard_page.tac_enhanced_section).to_be_visible()
    expect(
        new_account_wizard_page.tac_enhanced_section.locator("text=20.00%").nth(0)
    ).to_be_visible()
    expect(
        new_account_wizard_page.tac_enhanced_section.locator("text=20.00%").nth(1)
    ).to_be_visible()
    expect(
        new_account_wizard_page.tac_enhanced_section.locator(
            "text=Multiple Strategy Account"
        ),
    ).to_be_visible()

    # Verify Tactical Strategies - Limit Loss Focus section with 20% and investment account
    expect(new_account_wizard_page.tac_limit_section).to_be_visible()
    expect(
        new_account_wizard_page.tac_limit_section.locator("text=20.00%").nth(0)
    ).to_be_visible()
    expect(
        new_account_wizard_page.tac_limit_section.locator("text=20.00%").nth(1)
    ).to_be_visible()
    expect(
        new_account_wizard_page.tac_limit_section.locator(
            "text=Multiple Strategy Account"
        ),
    ).to_be_visible()

    # Verify Diversifying Strategies - Equity Alternatives section with 20% and investment account
    expect(new_account_wizard_page.div_equity_section).to_be_visible()
    expect(
        new_account_wizard_page.div_equity_section.locator("text=20.00%").nth(0)
    ).to_be_visible()
    expect(
        new_account_wizard_page.div_equity_section.locator("text=20.00%").nth(1)
    ).to_be_visible()
    expect(
        new_account_wizard_page.div_equity_section.locator(
            "text=Multiple Strategy Account"
        ),
    ).to_be_visible()

    # Verify Diversifying Strategies - Bonds & Bond Alternatives section with 20% and investment account
    expect(new_account_wizard_page.div_bonds_section).to_be_visible()
    expect(
        new_account_wizard_page.div_bonds_section.locator("text=20.00%").nth(0)
    ).to_be_visible()
    expect(
        new_account_wizard_page.div_bonds_section.locator("text=20.00%").nth(1)
    ).to_be_visible()
    expect(
        new_account_wizard_page.div_bonds_section.locator(
            "text=Multiple Strategy Account"
        ),
    ).to_be_visible()

    # Verify Additional Investments section with 0% (no allocation)
    expect(new_account_wizard_page.additional_investments_section).to_be_visible()
    expect(
        new_account_wizard_page.additional_investments_section.locator("text=0.00%"),
    ).to_be_visible()

    # Verify Total Portfolio shows 100%
    expect(
        new_account_wizard_page.asset_allocation_summary_widget.locator(
            '.header-row:has-text("Total Portfolio") >> text=100.00%'
        ),
    ).to_be_visible()

    new_account_wizard_page.page.wait_for_timeout(500)  # Wait before proceeding
    new_account_wizard_page.next_button.click()
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for fee section to render


@then(parsers.parse('I set a flat fee of "{percent}" percent'))
def set_flat_fee(page: Page, percent: str):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug(f"\nSetting flat fee to {percent} percent")
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for fee input field to appear
    new_account_wizard_page.adv_flat_fee_input.wait_for(state="visible", timeout=10000)  # Ensure input is visible
    new_account_wizard_page.page.wait_for_timeout(500)  # Additional buffer before clicking
    new_account_wizard_page.adv_flat_fee_input.click()
    new_account_wizard_page.page.wait_for_timeout(300)  # Wait for focus
    new_account_wizard_page.adv_flat_fee_input.fill(percent)
    new_account_wizard_page.adv_flat_fee_input.press("Enter")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for value to be processed


@then("the portfolio fees should be valid")
def verify_portfolio_fees_valid(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    
    # Verify portfolio fee summary table exists
    expect(new_account_wizard_page.portfolio_fee_summary_table).to_be_visible()

    # Verify Financial Advisor row exists
    expect(new_account_wizard_page.financial_advisor_fee_row).to_be_visible()

    # Get Financial Advisor fee percentage and verify it's not 0
    fa_fee_text = (
        new_account_wizard_page.financial_advisor_fee_row.locator(
            "td.portfolioColumnData label"
        )
        .first.text_content()
    )
    fa_fee_value = float(fa_fee_text.replace("%", "") if fa_fee_text else "0")
    assert fa_fee_value > 0

    # Verify Platform row exists
    expect(new_account_wizard_page.platform_fee_row).to_be_visible()

    # Get Platform fee percentage and verify it's not 0
    platform_fee_text = (
        new_account_wizard_page.platform_fee_row.locator(
            "td.portfolioColumnData label"
        )
        .first.text_content()
    )
    platform_fee_value = float(
        platform_fee_text.replace("%", "") if platform_fee_text else "0"
    )
    assert platform_fee_value > 0

    # Verify portfolio total value row exists and displays $500,000
    expect(new_account_wizard_page.portfolio_total_value_row).to_be_visible()
    expect(
        new_account_wizard_page.portfolio_total_value_row.locator("text=$500,000"),
    ).to_be_visible()

    # Verify fee Total row exists
    expect(new_account_wizard_page.total_fee_row).to_be_visible()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for fee calculation to complete
    expected_total = fa_fee_value + platform_fee_value
    tms_count = new_account_wizard_page.tax_management_services_fee_row.count()
    
    if tms_count > 0:
        tms_fee_text = (
            new_account_wizard_page.tax_management_services_fee_row.locator(
                "td.portfolioColumnData label"
            )
            .first.text_content()
        )
        tms_fee_value = float(tms_fee_text.replace("%", "") if tms_fee_text else "0")
        if tms_fee_value > 0:
            expected_total += tms_fee_value
            logger.debug(f"Including TMS fee: {tms_fee_value}%")

    # Get Total fee percentage and verify it equals the sum of all fees
    total_fee_text = (
        new_account_wizard_page.total_fee_row.locator(
            "td.portfolioAnnualColumnData label"
        )
        .first.text_content()
    )
    total_fee_value = float(total_fee_text.replace("%", "") if total_fee_text else "0")

    # Verify total equals sum of individual fees (with small tolerance for floating point)
    assert abs(total_fee_value - expected_total) < 0.01
    
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait before proceeding
    new_account_wizard_page.next_button.click()
    new_account_wizard_page.page.wait_for_load_state()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for document creation page to render


@when("I create the proposal document")
def create_proposal_document(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nCreating the proposal document")
    portfolio_engine_page = PortfolioEnginePage(new_account_wizard_page.page)
    set_portfolio_engine_instance(portfolio_engine_page)
    
    # Dismiss privacy dialog
    portfolio_engine_page.dismiss_privacy_dialog()
    
    # Wait for preview button to be visible and clickable
    logger.debug("Waiting for Preview Proposal button...")
    portfolio_engine_page.preview_proposal_button.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(500)  # Additional buffer for button stability
    
    # Click preview proposal button
    portfolio_engine_page.preview_proposal_button.click(timeout=10000)
    portfolio_engine_page.page.wait_for_load_state("load", timeout=15000)

