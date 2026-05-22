"""
Step definitions for verifying proposal document sections.
Converts TypeScript: verifyProposalDocument.ts
"""

import logging
from pytest_bdd import then
from playwright.sync_api import Page, expect

from tests.steps.proposal.instance_manager import get_portfolio_engine_instance

logger = logging.getLogger(__name__)


@then("the proposal document should be generated successfully")
def verify_proposal_document_generated(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    logger.debug("\nVerifying proposal sections were generated")

    # Dismiss privacy dialog if present
    portfolio_engine_page_instance.dismiss_privacy_dialog()

    # Verify the proposal document is loaded
    try:
        portfolio_engine_page_instance.cover_page_header.click()
        expect(portfolio_engine_page_instance.cover_page_header).to_be_visible()
    except Exception as err:
        logger.error(
            "Cover page header not visible in generated proposal document", exc_info=err
        )
        raise err


@then("the document should contain all the relevant information from the proposal")
def verify_document_contains_info(page: Page):
    logger.debug("\nVerifying all proposal document sections")


@then("the cover page section should be verified")
def verify_cover_page_section(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    logger.debug("\nVerifying cover page section...")
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.cover_page_header,
        portfolio_engine_page_instance.preview_layout_content_first,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Cover page validation failed", exc_info=err)
        raise err


@then("the table of contents section should be verified")
def verify_table_of_contents_section(page: Page):
    logger.debug("\nVerifying table of contents section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.table_of_contents_text,
        portfolio_engine_page_instance.table_of_contents_content,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Table of contents validation failed", exc_info=err)
        raise err


@then("the introduction section should be verified")
def verify_introduction_section(page: Page):
    logger.debug("\nVerifying introduction section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.introduction_header,
        portfolio_engine_page_instance.introduction_content,
        portfolio_engine_page_instance.introduction_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Introduction section validation failed", exc_info=err)
        raise err


@then("the investing is personal section should be verified")
def verify_investing_is_personal_section(page: Page):
    logger.debug("\nVerifying investing is personal section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.click_and_wait_for_expansion(
        portfolio_engine_page_instance.pursuing_your_goals_dropdown_icon
    )
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.investing_is_personal_text,
        portfolio_engine_page_instance.investing_content,
        portfolio_engine_page_instance.investing_is_personal_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Investing is Personal section validation failed", exc_info=err)
        raise err


@then("the equities vs bonds section should be verified")
def verify_equities_vs_bonds_section(page: Page):
    logger.debug("\nVerifying equities vs bonds section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.equities_vs_bonds_title,
        portfolio_engine_page_instance.growth_content_first,
        portfolio_engine_page_instance.equities_vs_bonds_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Equities vs Bonds section validation failed", exc_info=err)
        raise err


@then("the cycle of emotions section should be verified")
def verify_cycle_of_emotions_section(page: Page):
    logger.debug("\nVerifying cycle of emotions section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.cycle_of_emotions_header,
        portfolio_engine_page_instance.the_content,
        portfolio_engine_page_instance.cycle_of_emotions_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Cycle of Emotions section validation failed", exc_info=err)
        raise err


@then("the staying invested section should be verified")
def verify_staying_invested_section(page: Page):
    logger.debug("\nVerifying staying invested section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.staying_invested_title,
        portfolio_engine_page_instance.growth_content_second,
        portfolio_engine_page_instance.staying_invested_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Staying Invested section validation failed", exc_info=err)
        raise err


@then("the investment team section should be verified")
def verify_investment_team_section(page: Page):
    logger.debug("\nVerifying investment team section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.your_investment_team_div,
        portfolio_engine_page_instance.your_content_canvas,
        portfolio_engine_page_instance.your_investment_team_checkbox_inside,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Investment Team section validation failed", exc_info=err)
        raise err


@then("the portfolio strategists section should be verified")
def verify_portfolio_strategists_section(page: Page):
    logger.debug("\nVerifying portfolio strategists section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.portfolio_strategists_section,
        portfolio_engine_page_instance.portfolio_content,
        portfolio_engine_page_instance.portfolio_strategists_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Portfolio Strategists section validation failed", exc_info=err)
        raise err


@then("the custodian selection section should be verified")
def verify_custodian_selection_section(page: Page):
    logger.debug("\nVerifying custodian selection section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.custodian_selection_header,
        portfolio_engine_page_instance.custodian_content,
        portfolio_engine_page_instance.custodian_selection_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Custodian Selection section validation failed", exc_info=err)
        raise err


@then("the ongoing review section should be verified")
def verify_ongoing_review_section(page: Page):
    logger.debug("\nVerifying ongoing review section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.ongoing_review_text,
        portfolio_engine_page_instance.ongoing_content,
        portfolio_engine_page_instance.ongoing_review_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Ongoing Review section validation failed", exc_info=err)
        raise err


@then("the financial analysis section should be verified")
def verify_financial_analysis_section(page: Page):
    logger.debug("\nVerifying financial analysis section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.your_financial_analysis_header,
        portfolio_engine_page_instance.your_financial_content,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Financial Analysis section validation failed", exc_info=err)
        raise err


@then("the recommended portfolio section should be verified")
def verify_recommended_portfolio_section(page: Page):
    logger.debug("\nVerifying recommended portfolio section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.click_and_wait_for_expansion(
        portfolio_engine_page_instance.recommended_investment_portfolio_dropdown_icon
    )
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.recommended_portfolio_div,
        portfolio_engine_page_instance.recommended_content,
        portfolio_engine_page_instance.recommended_investment_portfolio_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Recommended portfolio section validation failed", exc_info=err)
        raise err


@then("the allocation by asset class section should be verified")
def verify_allocation_by_asset_class_section(page: Page):
    logger.debug("\nVerifying allocation by asset class section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.allocation_by_asset_class_header,
        portfolio_engine_page_instance.allocation_content,
        portfolio_engine_page_instance.allocation_by_asset_class_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Allocation by asset class validation failed", exc_info=err)
        raise err


@then("the top holdings section should be verified")
def verify_top_holdings_section(page: Page):
    logger.debug("\nVerifying top holdings section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.top_holdings_text,
        portfolio_engine_page_instance.top_holdings_content,
        portfolio_engine_page_instance.top_holdings_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Top holdings section validation failed", exc_info=err)
        raise err


@then("the proposed accounts section should be verified")
def verify_proposed_accounts_section(page: Page):
    logger.debug("\nVerifying proposed accounts section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.proposed_accounts_title,
        portfolio_engine_page_instance.proposed_content_first,
        portfolio_engine_page_instance.proposed_accounts_estimated_yield_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Proposed accounts section validation failed", exc_info=err)
        raise err


@then("the hypothetical performance sections should be verified")
def verify_hypothetical_performance_sections(page: Page):
    logger.debug("\nVerifying hypothetical performance sections...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.click_and_wait_for_expansion(
        portfolio_engine_page_instance.hypothetical_historical_performance_dropdown_icon
    )
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.hypothetical_section_title,
        portfolio_engine_page_instance.hypothetical_content,
        portfolio_engine_page_instance.hypothetical_growth_of_proposed_accounts_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error(
            "Hypothetical performance section checks failed", exc_info=err
        )
        raise err


@then("the rates section should be verified")
def verify_rates_section(page: Page):
    logger.debug("\nVerifying rates section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.rates_header,
        portfolio_engine_page_instance.rates_content,
        portfolio_engine_page_instance.rates_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Rates section validation failed", exc_info=err)
        raise err


@then("the calendar year returns section should be verified")
def verify_calendar_year_returns_section(page: Page):
    logger.debug("\nVerifying calendar year returns section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.calendar_year_returns_text,
        portfolio_engine_page_instance.calendar_content,
        portfolio_engine_page_instance.calendar_year_returns_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Calendar year returns validation failed", exc_info=err)
        raise err


@then("the historical cumulative section should be verified")
def verify_historical_cumulative_section(page: Page):
    logger.debug("\nVerifying historical cumulative section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.historical_cumulative_text,
        portfolio_engine_page_instance.historical_content,
        portfolio_engine_page_instance.historical_cumulative_performance_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Historical cumulative validation failed", exc_info=err)
        raise err


@then("the risk versus return section should be verified")
def verify_risk_versus_return_section(page: Page):
    logger.debug("\nVerifying risk versus return section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.risk_versus_return_section,
        portfolio_engine_page_instance.risk_content,
        portfolio_engine_page_instance.risk_versus_return_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Risk vs Return validation failed", exc_info=err)
        raise err


@then("the fee schedule section should be verified")
def verify_fee_schedule_section(page: Page):
    logger.debug("\nVerifying fee schedule section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.click_and_wait_for_expansion(
        portfolio_engine_page_instance.annual_portfolio_fees_dropdown_icon
    )
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.fee_schedule_div,
        portfolio_engine_page_instance.fee_content_first,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Fee schedule section validation failed", exc_info=err)
        raise err


@then("the tiered fee schedule section should be verified")
def verify_tiered_fee_schedule_section(page: Page):
    logger.debug("\nVerifying tiered fee schedule section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.tiered_fee_schedule_header,
        portfolio_engine_page_instance.tiered_content,
        portfolio_engine_page_instance.tiered_fee_schedule_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Tiered fee schedule validation failed", exc_info=err)
        raise err


@then("the estimated expense section should be verified")
def verify_estimated_expense_section(page: Page):
    logger.debug("\nVerifying estimated expense section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.estimate_expense_title,
        portfolio_engine_page_instance.estimated_expense_canvas,
        portfolio_engine_page_instance.estimate_expense_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Estimated expense section validation failed", exc_info=err)
        raise err


@then("the important information section should be verified")
def verify_important_information_section(page: Page):
    logger.debug("\nVerifying important information section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.important_information_text,
        portfolio_engine_page_instance.important_information_canvas,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Important information section validation failed", exc_info=err)
        raise err


@then("the disclosures section should be verified")
def verify_disclosures_section(page: Page):
    logger.debug("\nVerifying disclosures section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.disclosures_title,
        portfolio_engine_page_instance.disclosures_canvas,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Disclosures section validation failed", exc_info=err)
        raise err


@then("the tax management services section should be verified")
def verify_tax_management_services_section(page: Page):
    logger.debug("\nVerifying tax management services section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.tax_management_services_text,
        portfolio_engine_page_instance.tax_management_services_canvas,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Tax Management Services section validation failed", exc_info=err)
        raise err


@then("the client signature section should be verified")
def verify_client_signature_section(page: Page):
    logger.debug("\nVerifying client signature section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.client_signature_text,
        portfolio_engine_page_instance.client_signature_canvas,
        portfolio_engine_page_instance.client_signature_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error("Client signature section validation failed", exc_info=err)
        raise err


@then("the investment policy statement section should be verified")
def verify_investment_policy_statement_section(page: Page):
    logger.debug("\nVerifying investment policy statement section...")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    result = portfolio_engine_page_instance.verify_proposal_section(
        portfolio_engine_page_instance.investment_policy_statement_text,
        portfolio_engine_page_instance.investment_policy_canvas,
        portfolio_engine_page_instance.investment_policy_statement_checkbox,
    )
    try:
        assert result is True
    except Exception as err:
        logger.error(
            "Investment policy statement validation failed", exc_info=err
        )
        raise err
    
    logger.debug("\nAll proposal document sections verified successfully")
