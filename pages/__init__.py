"""
Page Objects Package

This module exports all page object classes for easy importing.
Instead of: from pages.login_page import LoginPage
You can use: from pages import LoginPage
"""

from pages.account_detail_page import AccountDetailPage
from pages.account_list_page import AccountListPage
from pages.account_wizard_page import AccountWizardPage
from pages.add_ach_instruction import AddACHInstructionPage
from pages.Adhesion.adhesion_login_page import AdhesionLoginPage
from pages.Adhesion.apro_proposals_page import AproProposalsPage
from pages.Adhesion.apro_step_allocation import ProposalAllocationPage
from pages.Adhesion.apro_step_details import ProposalDetailsPage
from pages.Adhesion.apro_step_fees import ProposalFeesPage
from pages.Adhesion.apro_step_generate import ProposalGeneratePage
from pages.Adhesion.apro_step_history import ProposalHistoryPage
from pages.Adhesion.apro_step_holdings import ProposalHoldingsPage
from pages.Adhesion.apro_step_risk import ProposalRiskPage
from pages.Adhesion.apro_step_tax_management import ProposalTaxManagementPage
from pages.Adhesion.base_smart_filter_page import BaseSmartFilterPage
from pages.Adhesion.global_navigation_page import GlobalNavigationPage
from pages.Adhesion.prospects_list_page import ProspectsListPage
from pages.api_utility_page import APIUtilityPage
from pages.auto_healing_page import AutoHealingPage
from pages.base_page import BasePage
from pages.clients_page import ClientsPage
from pages.dmtool_page import DMToolPage
from pages.login_page import LoginPage
from pages.manage_instruction_1_page import ManageInstruction1Page
from pages.manage_instruction_2_page import ManageInstruction2Page
from pages.roth_conversion_page import RothConversionPage
from pages.tracking_center_page import TrackingCenterPage

__all__ = [
    "AccountDetailPage",
    "AccountListPage",
    "AccountWizardPage",
    "AddACHInstructionPage",
    "APIUtilityPage",
    "AdhesionLoginPage",
    "AutoHealingPage",
    "BasePage",
    "BaseSmartFilterPage",
    "ClientsPage",
    "DMToolPage",
    "LoginPage",
    "ManageInstruction1Page",
    "ManageInstruction2Page",
    "RothConversionPage",
    "TrackingCenterPage",
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
