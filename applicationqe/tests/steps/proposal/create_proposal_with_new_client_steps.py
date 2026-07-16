"""
Step definitions for creating a proposal with a new client via the New Account Wizard.
Converts TypeScript: createProposalWithNewClient.ts
"""

import logging
from pytest_bdd import when, then, parsers
from playwright.sync_api import Page, expect

from pages.proposal import (
    EwmPage,
    NewAccountWizardPage,
    PortfolioEnginePage,
    TaxManagementServicesPage,
)
from tests.steps.proposal.instance_manager import (
    get_new_account_wizard_instance,
    set_new_account_wizard_instance,
    get_ewm_page_instance,
    set_ewm_page_instance,
    set_portfolio_engine_instance,
    set_tax_mgmt_services_instance,
)
from pages.proposal.helper_functions import navigate_to_home_page, navigate_to_account_wizard
from config.proposal.settings import get_settings

logger = logging.getLogger(__name__)


@when("I click on the Account Wizard link")
def click_account_wizard_link(page: Page):
    settings = get_settings()
    ewm_cfg = settings.config.get("applications", {}).get("ewm", {})
    home_url = ewm_cfg.get("home_url", "")
    login_page_class_name = ewm_cfg.get("login_page_class", "LoginPage")
    is_navbar = login_page_class_name == "NavbarLoginPage"
    
    navigate_to_account_wizard(page, home_url, is_navbar)
    ewm_page = EwmPage(page)
    set_ewm_page_instance(ewm_page)
    
    expect(
        ewm_page.ewm_root.get_by_text("There are two ways to get started"),
    ).to_be_visible(timeout=30000)


@when("I decide to create a new client")
def decide_create_new_client(page: Page):
    ewm_page = get_ewm_page_instance()
    ewm_page.ewm_root.locator("body").wait_for(state="visible", timeout=15000)
    ewm_page.create_new_client.click()
    # The form will load via ASP.NET UpdatePanel postback.
    # complete_client_profile's initial visibility checks will wait for form stability.


@when(parsers.parse('I complete the client profile with first name "{first_name}" and last name "{last_name}"'))
def complete_client_profile(page: Page, first_name: str, last_name: str):
    ewm_page = get_ewm_page_instance()
    new_account_wizard_page = NewAccountWizardPage(ewm_page.page)
    set_new_account_wizard_instance(new_account_wizard_page)
    
    expect(new_account_wizard_page.first_name_input).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.last_name_input).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.fiduciary_non_discretionary).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.fiduciary_discretionary).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.low_risk_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.moderate_risk_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.high_risk_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.very_high_risk_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.two_years_or_less_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.six_to_nine_years_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.twenty_five_to_50_percent_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.growth_risk_return_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.conservative_risk_return_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.moderate_conservative_risk_return_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.moderate_risk_return_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.moderate_growth_risk_return_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.growth_risk_return_radio).to_be_visible(timeout=30000)
    expect(new_account_wizard_page.maximum_growth_risk_return_radio).to_be_visible(timeout=30000)

    logger.debug("\nFilling out new client profile")

    if new_account_wizard_page.agent_dropdown.is_visible():
        settings = get_settings()
        user_id = settings.config.get("test_user", {}).get("user_id", "")
        new_account_wizard_page.agent_dropdown.click()
        new_account_wizard_page.agent_dropdown.select_option(user_id)
        # Agent dropdown selection triggers an UpdatePanel postback — re-wait for name field
        new_account_wizard_page.first_name_input.wait_for(state="visible", timeout=30000)

    new_account_wizard_page.fill_name(first_name, last_name)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render
    new_account_wizard_page.fiduciary_discretionary.click()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render
    new_account_wizard_page.high_risk_radio.click()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render
    new_account_wizard_page.six_to_nine_years_radio.click()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render
    new_account_wizard_page.twenty_five_to_50_percent_radio.click()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render
    new_account_wizard_page.growth_risk_return_radio.click()
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render
    new_account_wizard_page.next_button.click()
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to render


@when("I Complete the Construct Portfolio section")
def complete_construct_portfolio_section(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nFilling out Construct Portfolio section")
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for form to render
    new_account_wizard_page.select_registration_type("Individual")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for UI update
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.select_custodian()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for custodian to be selected
    new_account_wizard_page.fill_investment_amount("500000")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for amount input
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.select_account_type("Multiple Strategy Account")
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for account type to be selected
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)


@when(parsers.parse('I add all strategies to the account "{strategies}"'))
def add_all_strategies_to_account(page: Page, strategies: str):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nAdding all strategies to the account")

    strategy_list = [s.strip() for s in strategies.split(";")]
    for strategy in strategy_list:
        new_account_wizard_page.add_strategy(strategy)
        new_account_wizard_page.page.wait_for_timeout(500)  # Wait for strategy to be added

    # Verify all strategies were added by checking for their respective text in the table
    # Note: Using text-based verification instead of ID-based locators for cross-environment compatibility
    
    expect(new_account_wizard_page.form_root.locator(
        '#assetAllocations .investment-name'
    ).filter(has_text="AssetMark Income Builder")).to_be_visible(timeout=30000)
    
    expect(new_account_wizard_page.form_root.locator(
        '#assetAllocations .investment-name'
    ).filter(has_text="BlackRock Equity Dividend")).to_be_visible(timeout=30000)
    
    expect(new_account_wizard_page.form_root.locator(
        '#assetAllocations .investment-name'
    ).filter(has_text="AIM Decathlon Growth")).to_be_visible(timeout=30000)
    
    expect(new_account_wizard_page.form_root.locator(
        '#assetAllocations .investment-name'
    ).filter(has_text="JPMorgan Absolute Return")).to_be_visible(timeout=30000)
    
    expect(new_account_wizard_page.form_root.locator(
        '#assetAllocations .investment-name'
    ).filter(has_text="Savos US Risk Controlled")).to_be_visible(timeout=30000)


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
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for investment summary to render


@when("I opt out of tax management services")
def opt_out_tms(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nOpting out of tax management services")
    new_account_wizard_page.tms_options_no.click()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for no selection to register
    new_account_wizard_page.confirm_button.click()
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for next section to load


@when("I opt into tax management services")
def opt_into_tms(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug("\nOpting into tax management services")
    new_account_wizard_page.tms_options_yes.click()
    new_account_wizard_page.page.wait_for_timeout(500)  # Wait for yes selection to register
    new_account_wizard_page.confirm_button.click()
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for TMS page to fully load
    set_tax_mgmt_services_instance(
        TaxManagementServicesPage(new_account_wizard_page.page)
    )


@then("The investment summary should display correctly with all strategies and allocations")
def verify_investment_summary(page: Page):
    new_account_wizard_page = get_new_account_wizard_instance()
    
    widget = new_account_wizard_page.asset_allocation_summary_widget
    
    # Verify widget exists
    expect(widget).to_be_visible(timeout=30000)

    # Verify Core Markets section (20%)
    core_section = widget.locator('.asset-class').filter(has=new_account_wizard_page.form_root.locator('span:has-text("Core Markets")'))
    expect(core_section.locator('.header-row').locator('text=20.00%')).to_be_visible(timeout=30000)
    expect(core_section.locator('text=Multiple Strategy Account')).to_be_visible(timeout=30000)

    # Verify Tactical Strategies - Enhanced Return Focus (40%)
    enhanced_section = widget.locator('.asset-class').filter(has=new_account_wizard_page.form_root.locator('text=Enhanced Return Focus'))
    expect(enhanced_section.locator('.header-row').locator('text=40.00%')).to_be_visible(timeout=30000)
    expect(enhanced_section.locator('text=Multiple Strategy Account')).to_be_visible(timeout=30000)

    # Verify Tactical Strategies - Limit Loss Focus (20%)
    limit_section = widget.locator('.asset-class').filter(has=new_account_wizard_page.form_root.locator('text=Limit Loss Focus'))
    expect(limit_section.locator('.header-row').locator('text=20.00%')).to_be_visible(timeout=30000)
    expect(limit_section.locator('text=Multiple Strategy Account')).to_be_visible(timeout=30000)

    # Verify Diversifying Strategies - Equity Alternatives (0%)
    equity_section = widget.locator('.asset-class').filter(has=new_account_wizard_page.form_root.locator('text=Equity Alternatives'))
    expect(equity_section.locator('.header-row').locator('text=0.00%')).to_be_visible(timeout=30000)

    # Verify Diversifying Strategies - Bonds & Bond Alternatives (20%)
    bonds_section = widget.locator('.asset-class').filter(has=new_account_wizard_page.form_root.locator('text=Bonds & Bond Alternatives'))
    expect(bonds_section.locator('.header-row').locator('text=20.00%')).to_be_visible(timeout=30000)
    expect(bonds_section.locator('text=Multiple Strategy Account')).to_be_visible(timeout=30000)

    # Verify Additional Investments (0%)
    additional_section = widget.locator('.asset-class').filter(has=new_account_wizard_page.form_root.locator('span:has-text("Additional Investments")'))
    expect(additional_section.locator('.header-row').locator('text=0.00%')).to_be_visible(timeout=30000)

    # Verify Total Portfolio (100%)
    expect(widget.locator('.header-row').filter(has=new_account_wizard_page.form_root.locator('text=Total Portfolio')).locator('text=100.00%')).to_be_visible(timeout=30000)

    new_account_wizard_page.page.wait_for_timeout(500)  # Wait before proceeding
    
    """Move mouse slowly across screen to re-enable the next button."""
    bounding_box = new_account_wizard_page.next_button.bounding_box()
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
            new_account_wizard_page.page.mouse.move(current_x, current_y)
            new_account_wizard_page.page.wait_for_timeout(25)

    new_account_wizard_page.next_button.click()
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for fee section to render


@then(parsers.parse('I set a flat fee of "{percent}" percent'))
def set_flat_fee(page: Page, percent: str):
    new_account_wizard_page = get_new_account_wizard_instance()
    logger.debug(f"\nSetting flat fee to {percent} percent")
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
    new_account_wizard_page.page.wait_for_timeout(1000)  # Wait for fee input field to appear
    new_account_wizard_page.adv_flat_fee_input.wait_for(state="visible", timeout=30000)  # Ensure input is visible
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
    expect(new_account_wizard_page.portfolio_fee_summary_table).to_be_visible(timeout=30000)

    # Verify Financial Advisor row exists
    expect(new_account_wizard_page.financial_advisor_fee_row).to_be_visible(timeout=30000)

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
    expect(new_account_wizard_page.platform_fee_row).to_be_visible(timeout=30000)

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
    expect(new_account_wizard_page.portfolio_total_value_row).to_be_visible(timeout=30000)
    expect(
        new_account_wizard_page.portfolio_total_value_row.locator("text=$500,000"),
    ).to_be_visible(timeout=30000)

    # Verify fee Total row exists
    expect(new_account_wizard_page.total_fee_row).to_be_visible(timeout=30000)
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
    new_account_wizard_page.form_root.locator("body").wait_for(state="visible", timeout=15000)
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
    portfolio_engine_page.preview_proposal_button.wait_for(state="visible", timeout=30000)
    page.wait_for_timeout(500)  # Additional buffer for button stability
    
    # Click preview proposal button
    portfolio_engine_page.preview_proposal_button.click(timeout=30000)
    portfolio_engine_page.form_root.locator("body").wait_for(state="visible", timeout=30000)

