"""
Portfolio Engine Page Object Model - Complete Implementation
"""
import logging
from typing import List
from playwright.sync_api import Locator, Page

from ..base_page import BasePage
from utils.PROPOSAL.helper_functions import select_if_visible

logger = logging.getLogger(__name__)


class PortfolioEnginePage(BasePage):
    """Portfolio Engine page for proposal creation and document verification."""

    def __init__(self, page: Page):
        super().__init__(page)

        # NAVIGATION
        self.investments_link: Locator = page.get_by_role("link", name="Investments")
        self.portfolio_engine_link: Locator = page.get_by_role("link", name="PortfolioEngine", exact=True)
        self.launch_portfolio_engine_img: Locator = page.get_by_role("img", name="Launch Portfolio Engine").first
        self.clients_link: Locator = page.locator('a[href="/AccountsAnalysis/Clients/ClientList"]')

        # WIDGET HEADERS
        self.upside_downside_capture_header: Locator = page.get_by_role("heading", name="Upside/Downside Capture")
        self.investment_approach_header: Locator = page.get_by_role("heading", name="Investment Approach")
        self.return_by_strategy_header: Locator = page.get_by_role("heading", name="Return by Strategy")
        self.stress_test_header: Locator = page.get_by_role("heading", name="Stress Test")
        self.asset_allocation_holdings_header: Locator = page.get_by_role("heading", name="Asset Allocation & Holdings")
        self.risk_vs_return_header: Locator = page.get_by_role("heading", name="Risk vs Return")
        self.summary_statistics_header: Locator = page.get_by_role("heading", name="Summary Statistics")
        self.drawdown_header: Locator = page.get_by_role("heading", name="Drawdown")
        self.performance_header: Locator = page.get_by_role("heading", name="Performance")

        # PORTFOLIO MANAGEMENT BUTTONS
        self.get_started_button: Locator = page.get_by_role("button", name="Get Started...")
        self.manage_portfolios_button: Locator = page.get_by_role("button", name="Manage Portfolios")
        self.create_new_model_portfolio_button: Locator = page.get_by_role("button", name="Create New Model Portfolio")
        self.create_proposal_button: Locator = page.get_by_role("button", name="Create Proposal")
        self.next_button: Locator = page.get_by_role("button", name="NEXT")
        self.strategy_save_button: Locator = page.locator('[class*="popup-component__footer"]').get_by_role("button", name="Save")
        self.portfolio_close_button: Locator = page.locator('[class*="popup-component__footer"]').get_by_role("button", name="Close")
        self.preview_proposal_button: Locator = page.get_by_role("button", name="Preview Proposal")
        self.save_proposal_button: Locator = page.get_by_role("button", name="save proposal")
        self.view_documents_button: Locator = page.get_by_role("button", name="View Documents")
        self.one_combined_document_text: Locator = page.get_by_text("One Combined Document")
        self.quit_proposal_button: Locator = page.locator('img[src*="x-icon"]')

        # PORTFOLIO CREATION
        self.asset_mark_platform_strategies_text: Locator = page.get_by_text("AssetMark Platform Strategies", exact=True)
        self.strategy_search_box: Locator = page.get_by_role("textbox", name="Search")
        self.add_to_portfolio_text: Locator = page.get_by_text("Add to Portfolio")
        self.model_portfolio_name_textbox: Locator = page.get_by_role("textbox", name="Model Portfolio Name")
        self.investment_allocation_text: Locator = page.locator('[class*="sidebar-portfolio-component"]').locator('[class*="sectionTwo"]')

        # STRATEGY CHECKBOXES
        self.asset_mark_income_builder_checkbox: Locator = page.get_by_role("checkbox", name="AssetMark Income Builder")
        self.black_rock_equity_dividend_checkbox: Locator = page.get_by_role("checkbox", name="BlackRock Equity Dividend")
        self.savos_us_risk_checkbox: Locator = page.get_by_role("checkbox", name="Savos US Risk Controlled Strategy")
        self.alpha_simplex_checkbox: Locator = page.get_by_role("checkbox", name="AlphaSimplex")
        self.jp_morgan_absolute_return_checkbox: Locator = page.get_by_role("checkbox", name="JPMorgan Absolute Return")

        # PROPOSAL CREATION - CLIENT
        self.new_client_radio: Locator = page.get_by_role("radio", name="New Client")
        self.new_client_text: Locator = page.get_by_text("New Client")
        self.existing_client_radio: Locator = page.get_by_role("radio", name="Existing Client")
        self.existing_client_text: Locator = page.get_by_text("Existing Client")
        self.discretionary_radio: Locator = page.get_by_role("radio", name="Discretionary", exact=True)
        self.discretionary_text: Locator = page.get_by_text("Discretionary", exact=True)
        self.non_discretionary_radio: Locator = page.get_by_role("radio", name="Non-Discretionary")
        self.non_discretionary_text: Locator = page.get_by_text("Non-Discretionary")
        self.first_name_textbox: Locator = page.get_by_role("textbox", name="First")
        self.last_name_textbox: Locator = page.get_by_role("textbox", name="Last")


        # PROPOSAL CREATION - RISK PROFILE
        self.moderate_risk_radio: Locator = page.get_by_role("radio", name="Moderate", exact=True)
        self.time_horizon_nine_years_radio: Locator = page.get_by_role("radio", name="6 - 9 years")
        self.decline_fifty_percent_radio: Locator = page.get_by_role("radio", name="25 - 50%")
        self.risk_tolerance_moderate_radio: Locator = page.get_by_role("radio", name="3 - Moderate")

        # PROPOSAL CREATION - ACCOUNT SETUP
        self.select_custodian_dropdown: Locator = page.locator('[class*="custodian"], [class*="dropdown"]').get_by_role("img", name="ArrowDown").first
        self.fidelity_text: Locator = page.get_by_role("listitem").filter(has_text="Fidelity")
        self.assetmark_text: Locator = page.get_by_role("listitem").filter(has_text="AssetMark Trust")
        self.asset_mark_text: Locator = page.get_by_role("listitem").filter(has_text="AssetMark Trust")
        self.schwab_text: Locator = page.get_by_role("listitem").filter(has_text="Schwab")
        self.pershing_advisor_solutions_text: Locator = page.get_by_role("listitem").filter(has_text="Pershing Advisor Solutions")
        self.add_registration_button: Locator = page.locator('img[class*="accounts_icon"]').first
        self.registration_name_textbox: Locator = page.get_by_role("textbox")
        self.registration_type_dropdown: Locator = page.locator('[class*="accounts-select-dropdown_secondSelectCss"]').filter(has_text="Select")
        self.individual_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="Individual").locator("p").first
        self.trust_category: Locator = page.locator('[class*="accounts-select-dropdown_parentList"]').filter(has_text="Trust").locator("p")
        self.joint_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="Joint").locator("p").first
        self.iras_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="IRA's").locator("p").first
        self.retirement_plans_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="Retirement Plans").locator("p").first
        self.business_accounts_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="Business Accounts").locator("p").first
        self.organizations_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="Organizations").locator("p").first
        self.other_category: Locator = page.locator('[class*="accounts-select-dropdown_group"]').filter(has_text="Other").locator("p").first
        self.add_account_button: Locator = page.locator('img[class*="addAccIcon"]')
        self.model_list_confirm: Locator = page.locator('[class*="accounts-popUp"]').get_by_role("button", name="CONFIRM", exact=True)
        self.investment_amount_input: Locator = page.locator('input[name="investmentAmount"]')
        self.enroll_in_tax_radio: Locator = page.get_by_role("radio", name="Enroll in Tax Management Services", exact=True)
        self.do_not_enroll_in_tax_radio: Locator = page.get_by_role("radio", name="Do not enroll in Tax")
        self.confirm_text: Locator = page.get_by_text("CONFIRM", exact=True)

        # PROPOSED ACCOUNTS DISPLAY
        self.proposed_accounts_container: Locator = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleCta"]')
        self.proposed_accounts_header: Locator = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleHeader"]')
        self.proposed_accounts_amount: Locator = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleAmount"]')
        self.account_holder_name: Locator = page.locator('[class*="proposedAccounts-sidebar-toggle_regName"]')
        self.multiple_strategy_account_name: Locator = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleDataName"]')
        self.multiple_strategy_account_amount: Locator = page.locator('[class*="proposedAccounts-sidebar-toggle_toggleDataValue"]')

        # FEE DETAILS
        self.fee_details_container: Locator = page.locator('[class*="fees_feeDetails"]')
        self.portfolio_value_label: Locator = self.fee_details_container.locator('[class*="fees_feeValue"]').filter(has_text="Portfolio Value").locator("div").first
        self.portfolio_value_amount: Locator = self.fee_details_container.locator('[class*="fees_feeValue"]').filter(has_text="Portfolio Value").locator("div").last
        self.financial_advisor_fee_label: Locator = self.fee_details_container.locator('[class*="fees_feeValue"]').filter(has_text="Financial Advisor").locator("div").first
        self.financial_advisor_fee: Locator = self.fee_details_container.locator('[class*="fees_feeValue"]').filter(has_text="Financial Advisor").locator("div").last
        self.platform_fee_label: Locator = self.fee_details_container.locator('[class*="fees_feeValue"]').filter(has_text="Platform").locator("div").first
        self.platform_fee: Locator = self.fee_details_container.locator('[class*="fees_feeValue"]').filter(has_text="Platform").locator("div").last
        self.total_fee_label: Locator = self.fee_details_container.locator('[class*="fees_totalFee"]').locator("div").first
        self.total_fee: Locator = self.fee_details_container.locator('[class*="fees_totalFee"]').locator("div").last
        self.enter_fee_percentage_textbox: Locator = page.get_by_role("textbox", name="Enter %")
        self.continue_button: Locator = page.get_by_role("button", name="Continue")
        self.funded_accounts_div: Locator = page.locator("div").filter(has_text="Funded Accounts(0) $0").first

        # PROPOSAL DOCUMENT CHECKBOXES (24 sections)
        self.introduction_checkbox: Locator = page.locator(".th-Introduction-wrap .checkbox-container .clsA")
        self.pursuing_your_goals_checkbox: Locator = page.locator(".th-wrap.th-Investing .checkbox-container .clsA").first
        self.investing_is_personal_checkbox: Locator = page.locator(".th-wrap.th-Investing .checkbox-container .clsA").nth(1)
        self.equities_vs_bonds_checkbox: Locator = page.locator(".th-wrap.th-Growth .checkbox-container .clsA").first
        self.cycle_of_emotions_checkbox: Locator = page.locator(".th-wrap.th-The.Cycle .checkbox-container .clsA")
        self.staying_invested_checkbox: Locator = page.locator(".th-wrap.th-Growth .checkbox-container .clsA").nth(1)
        self.your_investment_team_checkbox_top: Locator = page.locator(".th-wrap.th-Your .checkbox-container .clsA").first
        self.your_investment_team_checkbox_inside: Locator = page.locator(".th-wrap.th-Your .checkbox-container .clsA").nth(1)
        self.portfolio_strategists_checkbox: Locator = page.locator(".th-wrap.th-Portfolio .checkbox-container .clsA")
        self.custodian_selection_checkbox: Locator = page.locator(".th-wrap.th-Custodian .checkbox-container .clsA")
        self.ongoing_review_checkbox: Locator = page.locator(".th-wrap.th-Ongoing .checkbox-container .clsA")
        self.recommended_investment_portfolio_checkbox: Locator = page.locator(".th-wrap.th-Recommended .checkbox-container .clsA").first
        self.allocation_by_asset_class_checkbox: Locator = page.locator(".th-wrap.th-Allocation .checkbox-container .clsA")
        self.top_holdings_checkbox: Locator = page.locator(".th-wrap.th-Top .checkbox-container .clsA")
        self.proposed_accounts_estimated_yield_checkbox: Locator = page.locator(".th-wrap.th-Proposed .checkbox-container .clsA")
        self.hypothetical_historical_performance_checkbox: Locator = page.locator(".th-wrap.th-Hypothetical .checkbox-container .clsA").first
        self.hypothetical_growth_checkbox: Locator = page.locator(".th-wrap.th-Hypothetical .checkbox-container .clsA").nth(1)
        self.hypothetical_growth_of_proposed_accounts_checkbox: Locator = page.locator(".th-wrap.th-Hypothetical .checkbox-container .clsA").nth(1)
        self.rates_checkbox: Locator = page.locator(".th-wrap.th-Rates .checkbox-container .clsA")
        self.calendar_year_returns_checkbox: Locator = page.locator(".th-wrap.th-Calendar .checkbox-container .clsA")
        self.historical_cumulative_performance_checkbox: Locator = page.locator(".th-wrap.th-Historical .checkbox-container .clsA")
        self.risk_versus_return_checkbox: Locator = page.locator(".th-wrap.th-Risk .checkbox-container .clsA")
        self.annual_portfolio_fees_checkbox: Locator = page.locator(".th-wrap.th-Fee .checkbox-container .clsA").first
        self.tiered_fee_schedule_checkbox: Locator = page.locator(".th-wrap.th-Tiered .checkbox-container .clsA")
        self.estimate_expense_checkbox: Locator = page.locator(".th-wrap.th-Estimated .checkbox-container .clsA")
        self.client_signature_checkbox: Locator = page.locator(".th-wrap.th-Client .checkbox-container .clsA")
        self.investment_policy_statement_checkbox: Locator = page.locator(".th-wrap.th-Investment .checkbox-container .clsA")

        # DROPDOWN ICONS
        self.pursuing_your_goals_dropdown_icon: Locator = page.locator(".th-wrap.th-Investing .icon-holder i")
        self.recommended_portfolio_dropdown_icon: Locator = page.locator(".th-wrap.th-Recommended .icon-holder i").first
        self.recommended_investment_portfolio_dropdown_icon: Locator = page.locator(".th-wrap.th-Recommended .icon-holder i").first
        self.hypothetical_dropdown_icon: Locator = page.locator(".th-wrap.th-Hypothetical .icon-holder i").first
        self.hypothetical_historical_performance_dropdown_icon: Locator = page.locator(".th-wrap.th-Hypothetical .icon-holder i").first
        self.annual_fees_dropdown_icon: Locator = page.locator(".th-wrap.th-Fee .icon-holder i").first
        self.annual_portfolio_fees_dropdown_icon: Locator = page.locator(".th-wrap.th-Fee .icon-holder i").first

        # CANVAS ELEMENTS - Content Locators for Proposal Document Sections
        self.preview_layout_content_first: Locator = page.locator(".page-component:not(.fainted) canvas").first
        self.table_of_contents_content: Locator = page.locator(".page-wrap.Table:not(.fainted) canvas")
        self.introduction_content: Locator = page.locator(".page-wrap.Introduction-page-component-wrap:not(.fainted) canvas")
        self.investing_content: Locator = page.locator(".page-wrap.Investing:not(.fainted) canvas")
        self.growth_content_first: Locator = page.locator(".page-wrap.Growth:not(.fainted) canvas").first
        self.the_content: Locator = page.locator(".page-wrap.The:not(.fainted) canvas")
        self.growth_content_second: Locator = page.locator(".page-wrap.Growth:not(.fainted) canvas").nth(1)
        self.your_content_canvas: Locator = page.locator(".page-wrap.Your:not(.fainted) canvas").first
        self.portfolio_content: Locator = page.locator(".page-wrap.Portfolio:not(.fainted) canvas")
        self.custodian_content: Locator = page.locator(".page-wrap.Custodian:not(.fainted) canvas")
        self.ongoing_content: Locator = page.locator(".page-wrap.Ongoing:not(.fainted) canvas")
        self.your_financial_content: Locator = page.locator(".page-wrap.Your.Financial:not(.fainted) canvas")
        self.recommended_content: Locator = page.locator(".page-wrap.Recommended:not(.fainted) canvas")
        self.allocation_content: Locator = page.locator(".page-wrap.Allocation:not(.fainted) canvas")
        self.top_holdings_content: Locator = page.locator(".page-wrap.Top:not(.fainted) canvas")
        self.proposed_content_first: Locator = page.locator(".page-wrap.Proposed:not(.fainted) canvas").first
        self.hypothetical_content: Locator = page.locator(".page-wrap.Hypothetical:not(.fainted) canvas")
        self.rates_content: Locator = page.locator(".page-wrap.Rates:not(.fainted) canvas")
        self.calendar_content: Locator = page.locator(".page-wrap.Calendar:not(.fainted) canvas")
        self.historical_content: Locator = page.locator(".page-wrap.Historical:not(.fainted) canvas")
        self.risk_content: Locator = page.locator(".page-wrap.Risk:not(.fainted) canvas")
        self.fee_content_first: Locator = page.locator(".page-wrap.Fee:not(.fainted) canvas").first
        self.tiered_content: Locator = page.locator(".page-wrap.Tiered:not(.fainted) canvas")
        self.estimated_expense_canvas: Locator = page.locator(".page-wrap.Estimated.Expense:not(.fainted) canvas")
        self.important_information_canvas: Locator = page.locator(".page-wrap.Important.Information:not(.fainted) canvas")
        self.disclosures_canvas: Locator = page.locator(".page-wrap.Disclosures:not(.fainted) canvas")
        self.tax_management_services_canvas: Locator = page.locator(".page-wrap.Tax.Management.Services-page-component-wrap:not(.fainted) canvas")
        self.client_signature_canvas: Locator = page.locator(".page-wrap.Client:not(.fainted) canvas")
        self.investment_policy_canvas: Locator = page.locator(".page-wrap.Investment.Policy:not(.fainted) canvas")
        
        # PROPOSAL DOCUMENT VERIFICATION ELEMENTS
        self.cover_page_header: Locator = page.locator(".th-header").first
        self.pursue_your_goals_text: Locator = page.get_by_text("Pursue Your Goals", exact=True)
        self.table_of_contents_text: Locator = page.get_by_text("Table Of Contents", exact=True)
        self.introduction_header: Locator = page.get_by_role("heading", name="Introduction").or_(page.locator(".th-wrap.th-Introduction-wrap .th-header"))
        self.investing_is_personal_text: Locator = page.get_by_text("Investing is Personal", exact=True)
        self.equities_vs_bonds_title: Locator = page.locator(".th-wrap.th-Growth .th-title").filter(has_text="Equities vs. Bonds")
        self.cycle_of_emotions_header: Locator = page.get_by_text("Cycle of Emotions", exact=True).or_(page.locator(".th-wrap.th-The.Cycle .th-header"))
        self.staying_invested_title: Locator = page.locator(".th-wrap.th-Growth .th-title").filter(has_text="Staying Invested")
        self.your_investment_team_div: Locator = page.get_by_text("Your Investment Team (3)")
        self.portfolio_strategists_section: Locator = page.locator(".th-wrap.th-Portfolio")
        self.custodian_selection_header: Locator = page.get_by_role("heading", name="Custodian Selection").or_(page.locator(".th-wrap.th-Custodian .th-header"))
        self.ongoing_review_text: Locator = page.get_by_text("Ongoing Review of Your Portfolio", exact=True)
        self.your_financial_analysis_header: Locator = page.locator(".th-wrap.th-Your.Financial")
        self.recommended_portfolio_div: Locator = page.locator(".th-title.th-listview-title.listview-child").filter(has_text="Recommended Portfolio")
        self.allocation_by_asset_class_header: Locator = page.get_by_role("heading", name="Allocation by Asset Class").or_(page.locator(".th-wrap.th-Allocation .th-header"))
        self.top_holdings_text: Locator = page.get_by_text("Top Holdings").first
        self.proposed_accounts_title: Locator = page.locator(".th-wrap.th-Proposed .th-title")
        self.hypothetical_historical_performance_div: Locator = page.locator(".th-wrap.th-Hypothetical .th-title").filter(has_text="Hypothetical Historical Performance").first
        self.hypothetical_section_title: Locator = page.locator(".th-wrap.th-Hypothetical .th-title").filter(has_text="Hypothetical Historical Performance").last
        self.rates_header: Locator = page.get_by_role("heading", name="Rates").or_(page.locator(".th-wrap.th-Rates .th-header"))
        self.calendar_year_returns_text: Locator = page.locator(".th-wrap.th-Calendar .th-header")
        self.historical_cumulative_text: Locator = page.locator(".th-wrap.th-Historical > .th-header > .th-title").filter(has_text="Historical Cumulative")
        self.risk_versus_return_section: Locator = page.locator(".th-wrap.th-Risk")
        self.fee_schedule_div: Locator = page.locator("div").filter(has_text="Annual Portfolio Fees (3)").first
        self.tiered_fee_schedule_header: Locator = page.get_by_role("heading", name="Tiered Fee Schedule").or_(page.locator(".th-wrap.th-Tiered .th-header"))
        self.estimate_expense_title: Locator = page.locator(".th-wrap.th-Estimated .th-title")
        self.important_information_text: Locator = page.get_by_text("Important Information and Standardized Performance Returns", exact=True)
        self.disclosures_title: Locator = page.locator(".th-wrap.th-Disclosures .th-title")
        self.tax_management_services_text: Locator = page.locator(".th-wrap.th-Tax.Management.Services-wrap .th-title")
        self.client_signature_text: Locator = page.get_by_text("Client Signature", exact=True)
        self.investment_policy_statement_text: Locator = page.get_by_text("Investment Policy Statement", exact=True)

        # WIDGETS
        self.widget_selection_dropdown_button: Locator = page.locator("header").get_by_role("button").filter(has=page.locator('svg path[d*="M10 13.5a3.5"]'))
        self.performance_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Performance").locator("span").first
        self.drawdown_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Drawdown").locator("span").first
        self.summary_statistics_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Summary Statistics").locator("span").first
        self.risk_vs_return_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Risk vs Return").locator("span").first
        self.asset_allocation_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Asset Allocation & Holdings").locator("span").first
        self.stress_test_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Stress Test").locator("span").first
        self.return_by_strategy_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Return by Strategy").locator("span").first
        self.investment_approach_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Investment Approach").locator("span").first
        self.upside_downside_widget_checkbox: Locator = page.locator('[class*="menu-component__item"]').filter(has_text="Upside/Downside Capture").locator("span").first

        # WIDGET GRAPH CONTAINERS
        self.performance_graph_container: Locator = page.locator("article").filter(has_text="Performance").first.locator('div[class*="widget-component__content"]')
        self.drawdown_graph_container: Locator = page.locator("article").filter(has_text="Drawdown").first.locator('div[class*="widget-component__content"]')
        self.summary_statistics_graph_container: Locator = page.locator("article").filter(has_text="Summary Statistics").first.locator('div[class*="widget-component__content"]')
        self.risk_vs_return_graph_container: Locator = page.locator("article").filter(has_text="Risk vs Return").first.locator('div[class*="widget-component__content"]')
        self.asset_allocation_graph_container: Locator = page.locator("article").filter(has_text="Asset Allocation & Holdings").first.locator('div[class*="widget-component__content"]')
        self.stress_test_graph_container: Locator = page.locator("article").filter(has_text="Stress Test").first.locator('div[class*="widget-component__content"]')
        self.return_by_strategy_graph_container: Locator = page.locator("article").filter(has_text="Return by Strategy").first.locator('div[class*="widget-component__content"]')
        self.investment_approach_graph_container: Locator = page.locator("article").filter(has_text="Investment Approach").first.locator('div[class*="widget-component__content"]')
        self.upside_downside_graph_container: Locator = page.locator("article").filter(has_text="Upside/Downside Capture").first.locator('div[class*="widget-component__content"]')

        # WIDGET GRAPH CONTENT
        self.performance_graph_content: Locator = self.performance_graph_container.locator("svg text")
        self.drawdown_graph_content: Locator = self.drawdown_graph_container.locator("tbody tr")
        self.summary_statistics_graph_content: Locator = self.summary_statistics_graph_container.locator("tbody tr")
        self.risk_vs_return_graph_content: Locator = self.risk_vs_return_graph_container.locator("svg circle")
        self.asset_allocation_graph_content: Locator = self.asset_allocation_graph_container.locator('svg path[class*="recharts-sector"]')
        self.stress_test_graph_content: Locator = self.stress_test_graph_container.locator('div[class*="tick"]')
        self.return_by_strategy_graph_content: Locator = self.return_by_strategy_graph_container.locator("svg rect")
        self.investment_approach_graph_content: Locator = self.investment_approach_graph_container.locator('svg path[class*="recharts-sector"]')
        self.upside_downside_graph_content: Locator = self.upside_downside_graph_container.locator("svg rect")

        # CLIENT SEARCH
        self.loading_image_modal: Locator = page.locator("#loadingImageModal")
        self.client_search_input: Locator = page.get_by_role("textbox", name="client_search_input").or_(page.locator("#client_search_input"))
        self.search_button: Locator = page.get_by_role("button", name="search").or_(page.locator("#searchbutton"))
        self.no_clients_found_message: Locator = page.get_by_text("No search results were found.")
        self.no_results_message: Locator = page.get_by_text("No search results were found")
        self.client_collapsed_link: Locator = page.locator('td[role="gridcell"][aria-describedby="ClientListGrid_clientName"]')
        self.view_document_history_link: Locator = page.get_by_role("link", name="View Document History")
        self.portfolio_details_link: Locator = page.get_by_role("link", name="Portfolio Details")
        self.delete_client_link: Locator = page.get_by_role("link", name="Delete Client")
        self.new_client_experience_decline: Locator = page.get_by_role("button", name="No, Thank You")
        self.ok_button: Locator = page.get_by_role("button", name="OK")
        self.privacy_policy_button: Locator = page.get_by_role("button", name="I Agree")

        # PORTFOLIO DELETION
        self.portfolio_delete_control_button: Locator = page.locator('[class*="popup-component"]').locator('button[class*="button-icon"]').filter(has=page.locator('svg[viewBox="0 0 17 17"]')).first
        self.portfolio_delete_text: Locator = page.locator('[class*="popover-controls-component__action"]').get_by_text("Delete", exact=True)
        self.portfolio_delete_confirm_button: Locator = page.get_by_role("button", name="Delete")

        # STRATEGY DISPLAY TEXT
        self.asset_mark_income_builder_text: Locator = page.locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]').filter(has_text="AssetMark Income Builder, Profile 2, Conservative")
        self.black_rock_equity_dividend_text: Locator = page.locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]').filter(has_text="BlackRock Equity Dividend")
        self.savos_us_risk_text: Locator = page.locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]').filter(has_text="Savos US Risk Controlled Strategy, Profile 6")
        self.alpha_simplex_text: Locator = page.locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]').filter(has_text="AlphaSimplex, Alternative Model Portfolio, Profile 5, Growth")
        self.jp_morgan_absolute_return_text: Locator = page.locator('[class*="portfolio-sidebar-toggle_toggleDataWrapper"]').filter(has_text="JPMorgan Absolute Return - Profile 1")
        self.savos_personal_strategy_text: Locator = page.get_by_text("Savos Personal Portfolio Custom", exact=True)

        # ASSET ALLOCATION SUMMARY
        self.core_markets_row: Locator = page.locator("#asset-allocation-summary-widget .asset-class").nth(0)
        self.tactical_enhanced_return_row: Locator = page.locator("#asset-allocation-summary-widget .asset-class").nth(1)
        self.tactical_limit_loss_row: Locator = page.locator("#asset-allocation-summary-widget .asset-class").nth(2)
        self.diversifying_equity_alternatives_row: Locator = page.locator("#asset-allocation-summary-widget .asset-class").nth(3)
        self.diversifying_bonds_row: Locator = page.locator("#asset-allocation-summary-widget .asset-class").nth(4)
        self.additional_investments_row: Locator = page.locator("#asset-allocation-summary-widget .asset-class").nth(5)

        # PRIVACY
        self.privacy_dialog_reject_button: Locator = page.locator('button:has-text("Reject All")')

    # EXISTING METHODS
    def search_for_client(self, client_name: str) -> None:
        self.client_search_input.fill(client_name)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")

    def delete_client(self) -> None:
        self.delete_client_link.click()
        confirm_button = self.page.get_by_role("button", name="Delete")
        confirm_button.click()
        self.page.wait_for_load_state("networkidle")

    def dismiss_privacy_dialog(self) -> None:
        try:
            # Increase timeout to 10 seconds to allow dialog to load before trying to dismiss
            self.privacy_dialog_reject_button.click(timeout=10000)
            self.page.wait_for_timeout(500)
        except Exception:
            pass

    def navigate_to_portfolio_engine(self) -> Page:
        """
        Navigate to Portfolio Engine via 3-step flow:
        1. Click Investments link
        2. Click PortfolioEngine link
        3. Wait for popup and click Launch Portfolio Engine image
        4. Return the new Portfolio Engine page
        
        Returns:
            The Portfolio Engine page object (new tab/popup)
        """
        # Step 1: Click Investments link
        self.investments_link.click(timeout=5000)
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        
        # Step 2: Click PortfolioEngine link
        self.portfolio_engine_link.click(timeout=5000)
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        
        # Step 3: Set up popup listener, click Launch Portfolio Engine, get new page
        with self.page.context.expect_page() as popup_info:
            self.launch_portfolio_engine_img.click(timeout=5000)
        
        # Get the new popup page
        portfolio_engine_page = popup_info.value
        portfolio_engine_page.wait_for_load_state("load", timeout=20000)
        
        return portfolio_engine_page

    def validate_canvas(self, canvas: Locator) -> bool:
        """
        Validate that a canvas element has rendered content (actual pixel data).
        Checks canvas dimensions and pixel data to ensure content is rendered.
        
        Args:
            canvas: The canvas locator to validate
            
        Returns:
            bool: True if canvas has rendered content, False otherwise
        """
        try:
            has_rendered_content = canvas.evaluate(
                """(el) => {
                if (!el) return false;
                const ctx = el.getContext("2d");
                if (!ctx) return false;
                
                // Check dimensions
                if (el.width === 0 || el.height === 0) return false;
                
                // Check if canvas has actual pixel data (not blank)
                const imageData = ctx.getImageData(0, 0, el.width, el.height);
                const pixelData = imageData.data;
                
                // Check if any pixel is non-transparent or non-white
                for (let i = 0; i < pixelData.length; i += 4) {
                    const alpha = pixelData[i + 3];
                    if (alpha > 0) {
                        // Found a non-transparent pixel, canvas has content
                        return true;
                    }
                }
                
                return false; // Canvas is completely transparent/blank
            }"""
            )
            return bool(has_rendered_content)
        except Exception as e:
            logger.error(f"Error validating canvas: {e}")
            return False

    def verify_proposal_section(
        self, 
        section_element: Locator, 
        content_element: Locator, 
        checkbox: Locator | None = None
    ) -> bool:
        """
        Verify a proposal section by clicking the element and validating its content.
        Ensures the content is visually enabled (not greyed out) and contains rendered data.
        
        Implements same logic as TypeScript verifyProposalSection():
        - Clicks the section element to activate it
        - Checks checkbox state if provided
        - Retries canvas validation with backoff for rendering delays
        - Falls back to checking parent container for 'fainted' (disabled) class
        
        Args:
            section_element: The element to click (trigger/header)
            content_element: The content locator to verify (canvas or HTML content)
            checkbox: Optional checkbox locator to verify/check
            
        Returns:
            bool: True if section is verified and enabled, False otherwise
        """
        try:
            # Get section name for logging
            try:
                section_name = section_element.evaluate(
                    "(el) => (el.textContent || '').trim()"
                ) or "Unknown section"
            except Exception:
                section_name = "Unknown section"
            
            logger.debug(f"Verifying section: {section_name}")
            
            # Click into PDF section
            section_element.click()
            
            # Ensure we have the checkbox locator and check state
            if checkbox:
                try:
                    currently_checked = checkbox.is_checked()
                except Exception:
                    currently_checked = False
                
                if not currently_checked:
                    checkbox.check()
            
            # Retry canvas validation a few times to allow client-side rendering
            # This matches TypeScript logic with exponential backoff
            attempts = 3
            for i in range(attempts):
                valid = self.validate_canvas(content_element)
                if valid:
                    logger.debug(f"Canvas validation passed for {section_name}")
                    return True
                
                # Small backoff between attempts with exponential increase
                delay_ms = 200 + (i * 100)
                self.page.evaluate(
                    f"() => new Promise(resolve => setTimeout(resolve, {delay_ms}))"
                )
            
            # Check parent containers for 'fainted' class after canvas retries
            try:
                parent_class = content_element.evaluate(
                    """(el) => {
                        const parent = el.closest('.page-component') || 
                                     el.closest('.page-wrap') || 
                                     el.parentElement;
                        return parent ? parent.className || '' : '';
                    }"""
                ) or ""
            except Exception:
                parent_class = ""
            
            if "fainted" in str(parent_class):
                # If parent has 'fainted' class, section appears to be disabled
                failure_msg = f"Section appears to not be selected: {section_name}"
                logger.warning(failure_msg)
                return False
            
            # Canvas didn't contain rendered pixels
            failure_msg = f"Canvas content validation failed for section: {section_name}"
            logger.warning(failure_msg)
            return False
            
        except Exception as e:
            logger.error(f"Error verifying proposal section: {e}")
            return False

    def click_and_wait_for_expansion(self, dropdown_element: Locator) -> None:
        dropdown_element.click()
        self.page.wait_for_timeout(100)

    # NEW METHODS (11 ADDED)
    def add_strategy_to_portfolio(self, strategy_name: str) -> None:
        """Add a strategy to the portfolio by name."""
        self.strategy_search_box.fill(strategy_name)
        self.add_to_portfolio_text.click()

    def fill_new_client_info(self, first_name: str, last_name: str) -> None:
        """Fill in new client first and last names."""
        self.first_name_textbox.fill(first_name)
        self.last_name_textbox.fill(last_name)

    def select_risk_profile(self) -> None:
        """Select moderate risk profile with specified preferences."""
        self.moderate_risk_radio.check()
        self.time_horizon_nine_years_radio.check()
        self.decline_fifty_percent_radio.check()
        self.risk_tolerance_moderate_radio.check()

    def select_all_strategies(self) -> None:
        """Select all available strategies."""
        self.asset_mark_income_builder_checkbox.click()
        self.black_rock_equity_dividend_checkbox.click()
        self.savos_us_risk_checkbox.click()
        self.alpha_simplex_checkbox.click()
        self.jp_morgan_absolute_return_checkbox.click()

    def set_all_proposal_sections(self) -> None:
        """Enable all proposal document sections."""
        checkboxes = [
            self.introduction_checkbox, self.pursuing_your_goals_checkbox,
            self.investing_is_personal_checkbox, self.equities_vs_bonds_checkbox,
            self.cycle_of_emotions_checkbox, self.staying_invested_checkbox,
            self.your_investment_team_checkbox_top, self.portfolio_strategists_checkbox,
            self.custodian_selection_checkbox, self.ongoing_review_checkbox,
            self.recommended_investment_portfolio_checkbox, self.allocation_by_asset_class_checkbox,
            self.top_holdings_checkbox, self.proposed_accounts_estimated_yield_checkbox,
            self.hypothetical_historical_performance_checkbox, self.hypothetical_growth_checkbox,
            self.rates_checkbox, self.calendar_year_returns_checkbox,
            self.historical_cumulative_performance_checkbox, self.risk_versus_return_checkbox,
            self.annual_portfolio_fees_checkbox, self.tiered_fee_schedule_checkbox,
            self.estimate_expense_checkbox, self.client_signature_checkbox,
            self.investment_policy_statement_checkbox
        ]

        # Expand all dropdown sections
        self.click_and_wait_for_expansion(self.pursuing_your_goals_dropdown_icon)
        self.click_and_wait_for_expansion(self.recommended_portfolio_dropdown_icon)
        self.click_and_wait_for_expansion(self.hypothetical_dropdown_icon)
        self.click_and_wait_for_expansion(self.annual_fees_dropdown_icon)

        # Click all checkboxes
        for checkbox in checkboxes:
            try:
                is_checked = checkbox.is_checked()
                if not is_checked:
                    checkbox.click()
                    self.page.wait_for_timeout(100)
            except Exception as e:
                logger.warning(f"Error checking checkbox: {e}")
                checkbox.click()

        self.page.wait_for_load_state()

    def select_registration_type(self, registration_type: str) -> None:
        """Select registration type from dropdown with support for simple and nested options."""
        logger.debug(f"Selecting registration type: {registration_type}")
        
        # First click the dropdown itself to open the options
        self.registration_type_dropdown.click()
        self.page.wait_for_timeout(500)  # Wait for dropdown to open
        
        # Check if it's a simple top-level option (like "Select", "Trust")
        simple_options = self.page.locator('[class*="accounts-select-dropdown_parentList"]').locator("p")
        for i in range(simple_options.count()):
            if simple_options.nth(i).text_content() == registration_type:
                logger.debug(f"Found simple option for {registration_type}, clicking it")
                simple_options.nth(i).click()
                return
        
        # Map of registration types to their parent categories for nested options
        category_map = {
            "Individual": "Individual",
            "Individual TOD": "Individual",
            "Community Property": "Joint",
            "Community Property with Rights of Survivorship": "Joint",
            "Joint Tenants": "Joint",
            "Joint Tenants in Common": "Joint",
            "Joint Tenants with Rights of Survivorship": "Joint",
            "Trust": "Trust",
            "Corporate": "Business Accounts",
            "Partnership": "Business Accounts",
            "LLC": "Business Accounts",
            "S-Corp": "Business Accounts",
            "C-Corp": "Business Accounts",
            "Foundation": "Organizations",
            "Charity/Non-Profit": "Organizations",
            "Government": "Organizations",
        }
        
        category = category_map.get(registration_type)
        if not category:
            raise ValueError(f"Registration type '{registration_type}' not found in category map")
        
        # Find the category group and click its header to expand nested options
        logger.debug(f"Looking for nested option {registration_type} in category {category}")
        category_groups = self.page.locator('[class*="accounts-select-dropdown_group"]')
        
        for i in range(category_groups.count()):
            category_p = category_groups.nth(i).locator("p").first
            if category_p.text_content().strip() == category:
                # Click the category header to expand nested options
                category_p.click()
                self.page.wait_for_timeout(300)
                
                # Now click the specific registration type from the nested list
                nested_items = category_groups.nth(i).locator('[class*="accounts-select-dropdown_nestedListItem"]')
                for j in range(nested_items.count()):
                    if nested_items.nth(j).text_content().strip() == registration_type:
                        logger.debug(f"Found nested option {registration_type}, clicking it")
                        nested_items.nth(j).click()
                        return
        
        logger.warning(f"Could not find registration type: {registration_type}")

    def navigate_to_client_portfolio_details(self) -> None:
        """Navigate to portfolio details from document history."""
        select_if_visible(self.view_document_history_link)
        self.portfolio_details_link.click()

    def select_all_widgets_if_needed(self) -> None:
        """Select all available widgets from the widget menu if not already selected."""
        self.widget_selection_dropdown_button.click()
        widgets = [
            self.performance_widget_checkbox, self.drawdown_widget_checkbox,
            self.summary_statistics_widget_checkbox, self.risk_vs_return_widget_checkbox,
            self.asset_allocation_widget_checkbox, self.stress_test_widget_checkbox,
            self.return_by_strategy_widget_checkbox, self.investment_approach_widget_checkbox,
            self.upside_downside_widget_checkbox,
        ]
        
        for widget in widgets:
            try:
                # Check multiple conditions for widget selection status
                is_checked = widget.evaluate("""el => {
                    const listItem = el.closest('li');
                    return (
                        listItem?.classList.contains('selected') ||
                        listItem?.classList.contains('checked') ||
                        el.getAttribute('aria-checked') === 'true' ||
                        window.getComputedStyle(el).opacity === '1'
                    );
                }""")
                
                if not is_checked:
                    widget.click()
            except Exception as e:
                # If evaluation fails, click to ensure it's selected
                widget.click()

    def delete_portfolio(self, names: List[str] | None = None) -> None:
        """Delete specific portfolios by name via API.
        Raises on API or network failure so callers can handle it.
        """
        names = names or []
        if not names:
            logger.info("No portfolio names provided for deletion")
            return

        from urllib.parse import urlparse
        parsed = urlparse(self.page.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        logger.info(f"Fetching portfolios from API: {base_url}/api/pe/v2/portfolios")

        resp = self.page.request.get(f"{base_url}/api/pe/v2/portfolios")
        logger.info(f"Portfolio fetch response status: {resp.status}")
        if not resp.ok:
            raise RuntimeError(f"Portfolio fetch failed: {resp.status}")

        data = resp.json()
        portfolios = data if isinstance(data, list) else [data]
        logger.info(f"Found {len(portfolios)} total portfolios, looking for: {names}")

        for p in portfolios:
            if p.get("name") in names:
                logger.info(f"Deleting portfolio: {p['name']} (ID: {p['id']})")
                del_resp = self.page.request.delete(f"{base_url}/api/pe/v2/portfolio/{p['id']}")
                if del_resp.ok:
                    logger.info(f"Successfully deleted portfolio: {p['name']}")
                else:
                    logger.warning(f"Delete failed for {p['name']}: {del_resp.status}")

    def delete_all_portfolios(self) -> None:
        """Delete all old portfolios (created before 2025) via API."""
        try:
            base_url = str(self.page.url()).split("/AccountsAnalysis")[0]
            resp = self.page.request.get(f"{base_url}/api/pe/v2/portfolios")
            if resp.ok:
                data = resp.json()
                portfolios = data if isinstance(data, list) else [data]
                for p in portfolios:
                    created = p.get("createdOn", "2025")
                    if int(created[:4]) < 2025:
                        del_resp = self.page.request.delete(f"{base_url}/api/pe/v2/portfolio/{p['id']}")
                        if del_resp.ok:
                            logger.info(f"Deleted old portfolio: {p.get('name')}")
        except Exception as e:
            logger.error(f"Error in delete_all_portfolios: {e}")

    def get_allocation_textbox(self, index: int) -> Locator:
        """Get allocation textbox by index (0-based)."""
        return self.page.locator('[class*="portfolio-valid-item"]').locator('input[type="text"]').nth(index)

