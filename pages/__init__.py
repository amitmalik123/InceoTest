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
from pages.api_utility_page import APIUtilityPage
from pages.apro_proposals_page import AproProposalsPage
from pages.auto_healing_page import AutoHealingPage
from pages.base_page import BasePage
from pages.clients_page import ClientsPage
from pages.dmtool_page import DMToolPage
from pages.global_navigation_page import GlobalNavigationPage
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
    "AutoHealingPage",
    "BasePage",
    "ClientsPage",
    "DMToolPage",
    "LoginPage",
    "ManageInstruction1Page",
    "ManageInstruction2Page",
    "RothConversionPage",
    "TrackingCenterPage",
    "GlobalNavigationPage",
    "AproProposalsPage",
]
