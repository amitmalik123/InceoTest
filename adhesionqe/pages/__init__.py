"""
Page Objects Package

This module exports all page object classes for easy importing.
Instead of: from pages.login_page import LoginPage
You can use: from pages import LoginPage
"""

from pages.account_detail_page import AccountDetailPage
from pages.account_list_page import AccountListPage
from pages.account_wizard_page import AccountWizardPage
from pages.adhesion_login_page import AdhesionLoginPage
from pages.apro_proposals_page import AproProposalsPage
from pages.apro_step_allocation import ProposalAllocationPage
from pages.apro_step_details import ProposalDetailsPage
from pages.apro_step_fees import ProposalFeesPage
from pages.apro_step_generate import ProposalGeneratePage
from pages.apro_step_history import ProposalHistoryPage
from pages.apro_step_holdings import ProposalHoldingsPage
from pages.apro_step_risk import ProposalRiskPage
from pages.apro_step_tax_management import ProposalTaxManagementPage
from pages.base_smart_filter_page import BaseSmartFilterPage
from pages.global_navigation_page import GlobalNavigationPage
from pages.prospects_list_page import ProspectsListPage
from pages.api_utility_page import APIUtilityPage
from pages.auto_healing_page import AutoHealingPage
from pages.base_page import BasePage
from pages.login_page import LoginPage

__all__ = [
    "AccountDetailPage",
    "AccountListPage",
    "AccountWizardPage",
    "APIUtilityPage",
    "AdhesionLoginPage",
    "AutoHealingPage",
    "BasePage",
    "BaseSmartFilterPage",
    "LoginPage",
    "GlobalNavigationPage",
    "AproProposalsPage",
    "ProposalAllocationPage",
    "ProposalDetailsPage",
    "ProposalFeesPage",
    "ProposalGeneratePage",
    "ProposalHistoryPage",
    "ProposalHoldingsPage",
    "ProposalRiskPage",
    "ProposalTaxManagementPage",
    "ProspectsListPage",
]
