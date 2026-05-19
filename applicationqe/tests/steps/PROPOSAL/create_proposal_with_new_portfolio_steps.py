"""
Step definitions for creating a proposal with new portfolio and new client.
Converts TypeScript: createProposalWithNewPortfolioAndClient.ts
"""

import logging
import os
from pytest_bdd import when, then, parsers
from playwright.sync_api import Page, expect

from pages.PROPOSAL import PortfolioEnginePage
from tests.steps.PROPOSAL.instance_manager import get_portfolio_engine_instance
from data.PROPOSAL.proposal_variations import select_custodian
from data.PROPOSAL.proposal_pdf_text_manifest import (
    build_proposal_text_validation_manifest,
    build_proposal_text_validation_manifest_excluding_tms,
)
from utils.PROPOSAL.proposal_pdf_utils import download_and_validate_pdf_from_click

logger = logging.getLogger(__name__)


@when("I click the create proposal button")
def click_create_proposal_button(page: Page):
    logger.debug("\nStarting create proposal with new portfolio and new client test")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.create_proposal_button.click()
    portfolio_engine_page_instance.page.wait_for_load_state()


@then("the portfolio strategies should be displayed correctly")
def verify_portfolio_strategies_displayed(page: Page):
    logger.debug("\nVerifying portfolios & percentages are correct")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    expect(portfolio_engine_page_instance.asset_mark_income_builder_text).to_be_visible()
    expect(portfolio_engine_page_instance.black_rock_equity_dividend_text).to_be_visible()
    expect(portfolio_engine_page_instance.savos_us_risk_text).to_be_visible()
    expect(portfolio_engine_page_instance.alpha_simplex_text).to_be_visible()
    expect(portfolio_engine_page_instance.jp_morgan_absolute_return_text).to_be_visible()


@then("the client type options should be visible and editable")
def verify_client_type_options(page: Page):
    logger.debug("\nVerifying client type options")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    expect(portfolio_engine_page_instance.new_client_radio).to_be_editable()
    expect(portfolio_engine_page_instance.new_client_text).to_be_visible()
    expect(portfolio_engine_page_instance.existing_client_radio).to_be_editable()
    expect(portfolio_engine_page_instance.existing_client_text).to_be_visible()
    expect(portfolio_engine_page_instance.discretionary_text).to_be_visible()
    expect(portfolio_engine_page_instance.non_discretionary_text).to_be_visible()


@when(parsers.parse('I fill new client information with first name "{first_name}" and last name "{last_name}"'))
def fill_new_client_information(page: Page, first_name: str, last_name: str):
    logger.debug("\nCreating new client")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.fill_new_client_info(first_name, last_name)
    portfolio_engine_page_instance.next_button.click()
    portfolio_engine_page_instance.page.wait_for_load_state()


@when("I select a risk profile")
def select_risk_profile(page: Page):
    logger.debug("\nSelecting risk profile")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.select_risk_profile()
    portfolio_engine_page_instance.next_button.click()
    portfolio_engine_page_instance.page.wait_for_load_state()


@when("I select a custodian and set up account registration")
def select_custodian_and_registration(page: Page):
    logger.debug("\nSelecting custodian and registration type")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    
    # Click custodian dropdown with wait
    portfolio_engine_page_instance.select_custodian_dropdown.wait_for(state="visible", timeout=10000)
    portfolio_engine_page_instance.select_custodian_dropdown.click()
    portfolio_engine_page_instance.page.wait_for_timeout(500)  # Give dropdown time to open
    
    # Select custodian
    select_custodian(portfolio_engine_page_instance)
    portfolio_engine_page_instance.page.wait_for_load_state()
    portfolio_engine_page_instance.page.wait_for_timeout(1000)  # Wait after selection
    
    # Add registration
    portfolio_engine_page_instance.add_registration_button.wait_for(state="visible", timeout=10000)
    portfolio_engine_page_instance.add_registration_button.click()
    portfolio_engine_page_instance.page.wait_for_timeout(1000)
    portfolio_engine_page_instance.page.wait_for_load_state("domcontentloaded")
    
    # Select registration type
    portfolio_engine_page_instance.registration_type_dropdown.wait_for(state="visible", timeout=10000)
    portfolio_engine_page_instance.page.wait_for_timeout(500)
    portfolio_engine_page_instance.select_registration_type("Individual")
    portfolio_engine_page_instance.page.wait_for_load_state()
    portfolio_engine_page_instance.page.wait_for_timeout(1000)


@when(parsers.parse('I add an account with all strategies and investment amount "{investment_amount}"'))
def add_account_with_all_strategies(page: Page, investment_amount: str):
    logger.debug("\nAdding account with all 5 strategies")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.add_account_button.click()
    portfolio_engine_page_instance.select_all_strategies()
    portfolio_engine_page_instance.model_list_confirm.click()

    logger.debug("\nSetting investment amount")
    portfolio_engine_page_instance.investment_amount_input.fill(investment_amount)
    expect(portfolio_engine_page_instance.enroll_in_tax_radio).to_be_editable()
    portfolio_engine_page_instance.do_not_enroll_in_tax_radio.check()
    portfolio_engine_page_instance.confirm_text.click()
    portfolio_engine_page_instance.next_button.click()
    portfolio_engine_page_instance.page.wait_for_load_state()


@then(parsers.parse('the proposed accounts should display correctly with amount "{expected_amount}", first name "{first_name}", and last name "{last_name}"'))
def verify_proposed_accounts_display(
    page: Page, expected_amount: str, first_name: str, last_name: str
):
    logger.debug("\nVerifying proposed accounts information")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    expect(portfolio_engine_page_instance.proposed_accounts_header).to_contain_text(
        "Proposed Accounts (1)"
    )
    expect(portfolio_engine_page_instance.proposed_accounts_amount).to_contain_text(
        expected_amount
    )
    expect(portfolio_engine_page_instance.account_holder_name).to_contain_text(
        f"{first_name} {last_name}, Individual"
    )
    expect(portfolio_engine_page_instance.multiple_strategy_account_name).to_contain_text(
        "Multiple Strategy Account, Profile"
    )
    expect(portfolio_engine_page_instance.multiple_strategy_account_amount).to_contain_text(
        expected_amount
    )


@when(parsers.parse('I enter fee percentage "{fee_percentage}"'))
def enter_fee_percentage(page: Page, fee_percentage: str):
    logger.debug("\nEntering fee values")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.enter_fee_percentage_textbox.fill(fee_percentage)
    portfolio_engine_page_instance.page.wait_for_load_state()
    portfolio_engine_page_instance.next_button.click()


@then(parsers.parse('the fee summary should display correctly with portfolio value "{portfolio_value}" and financial advisor fee "{advisor_fee}"'))
def verify_fee_summary_display(
    page: Page, portfolio_value: str, advisor_fee: str
):
    logger.debug("\nVerifying fee summary values")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    expect(portfolio_engine_page_instance.portfolio_value_amount).to_contain_text(
        portfolio_value
    )
    expect(portfolio_engine_page_instance.financial_advisor_fee).to_contain_text(
        advisor_fee
    )
    expect(portfolio_engine_page_instance.platform_fee).not_to_contain_text(
        "0.00%"
    )  # Ensure fee service is returning something


@then("the total fee calculation should be correct")
def verify_total_fee_calculation(page: Page):
    logger.debug("\nValidating total fee calculation")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    financial_advisor_fee_text = (
        portfolio_engine_page_instance.financial_advisor_fee.text_content()
    )
    platform_fee_text = portfolio_engine_page_instance.platform_fee.text_content()
    total_fee_text = portfolio_engine_page_instance.total_fee.text_content()

    financial_advisor_value = float(financial_advisor_fee_text.replace("%", ""))
    platform_value = float(platform_fee_text.replace("%", ""))
    total_value = float(total_fee_text.replace("%", ""))
    expected_total = financial_advisor_value + platform_value

    if abs(total_value - expected_total) > 0.01:
        raise AssertionError(
            f"Total fee {total_value}% does not match sum of Financial Advisor {financial_advisor_value}% and Platform {platform_value}% fees (expected {expected_total}%)"
        )
    
    portfolio_engine_page_instance.page.wait_for_load_state()


@when("I generate the proposal document with all sections")
def generate_proposal_document_all_sections(page: Page):
    logger.debug("\nGenerating proposal document with all sections")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.next_button.click()
    portfolio_engine_page_instance.continue_button.click()
    portfolio_engine_page_instance.preview_proposal_button.click()
    portfolio_engine_page_instance.page.wait_for_load_state()

    # Dismiss privacy dialog if present when preview proposal opens
    portfolio_engine_page_instance.dismiss_privacy_dialog()


@then("I save the proposal")
def save_proposal(page: Page):
    logger.debug("\nSaving proposal")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.save_proposal_button.click()
    # Wait for proposal generation (can take several minutes)
    portfolio_engine_page_instance.view_documents_button.click(timeout=180000)
    portfolio_engine_page_instance.page.wait_for_load_state()


@then(parsers.parse('the proposal should be saved successfully with {expected_proposal_page_count:d} pages including Tax Management Services'))
def verify_proposal_saved_with_tms(page: Page, expected_proposal_page_count: int):
    logger.debug("\nVerifying proposal was saved with Tax Management Services")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    expect(portfolio_engine_page_instance.one_combined_document_text).to_be_visible()

    # Adjust for prod environment
    environment = (os.getenv("ENVIRONMENT") or os.getenv("Environment") or "").lower()
    if environment == "prod":
        expected_proposal_page_count += 3

    proposal_text_validation = build_proposal_text_validation_manifest(
        include_table_of_contents=True
    )

    download_and_validate_pdf_from_click(
        portfolio_engine_page_instance.page,
        lambda: portfolio_engine_page_instance.one_combined_document_text.click(),
        {
            "expectedPageCount": expected_proposal_page_count,
            "filenamePrefix": "proposal",
            "expectedBrowserFilename": "DownloadCombinedDocuments.pdf",
            "proposalTextValidation": proposal_text_validation,
        },
    )


@then(parsers.parse('the proposal should be saved successfully with {expected_proposal_page_count:d} pages'))
def verify_proposal_saved(page: Page, expected_proposal_page_count: int):
    logger.debug("\nVerifying proposal was saved")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    expect(portfolio_engine_page_instance.one_combined_document_text).to_be_visible()

    # Adjust for prod environment
    environment = (os.getenv("ENVIRONMENT") or os.getenv("Environment") or "").lower()
    if environment == "prod":
        expected_proposal_page_count += 3

    proposal_text_validation = build_proposal_text_validation_manifest_excluding_tms(
        include_table_of_contents=True
    )

    download_and_validate_pdf_from_click(
        portfolio_engine_page_instance.page,
        lambda: portfolio_engine_page_instance.one_combined_document_text.click(),
        {
            "expectedPageCount": expected_proposal_page_count,
            "filenamePrefix": "proposal",
            "expectedBrowserFilename": "DownloadCombinedDocuments.pdf",
            "proposalTextValidation": proposal_text_validation,
        },
    )
